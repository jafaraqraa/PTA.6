from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.models.enums import (
    HearingConfigurationEnum,
    HearingSeverityEnum,
    HearingTypeEnum,
    ResponseEnum,
    TestTypeEnum,
)
from app.schemas.attempt_schema import AttemptDTO
from app.schemas.evaluation_schema import (
    EarInterpretationEvaluationDTO,
    EvaluationSummaryDTO,
    InterpretationFieldScoreDTO,
    ProtocolMetricDTO,
    SessionEvaluationDTO,
    ThresholdComparisonDTO,
)
from app.schemas.final_interpretation_schema import FinalInterpretationDTO
from app.schemas.patient_schema import AudiogramPointDTO, EarDTO, PatientDTO
from app.schemas.session_schema import SessionFullDTO
from app.schemas.stored_threshold_schema import StoredThresholdDTO


class EvaluationEngine:
    OFFICIAL_SCORE_WEIGHTS = {
        "thresholds": 0.45,
        "interpretation": 0.25,
    }

    PROTOCOL_WEIGHTS = {
        "coverage": 0.35,
        "step_adherence": 0.35,
        "threshold_confirmation": 0.30,
    }

    INTERPRETATION_WEIGHTS = {
        "overall_type": 0.35,
        "severity": 0.25,
        "configuration": 0.25,
        "affected_frequencies_hz": 0.15,
    }

    SEVERITY_ORDER = [
        HearingSeverityEnum.NORMAL.value,
        HearingSeverityEnum.MILD.value,
        HearingSeverityEnum.MODERATE.value,
        HearingSeverityEnum.MODERATELY_SEVERE.value,
        HearingSeverityEnum.SEVERE.value,
        HearingSeverityEnum.PROFOUND.value,
        HearingSeverityEnum.UNDETERMINED.value,
    ]

    @staticmethod
    def evaluate_session(session: SessionFullDTO) -> SessionEvaluationDTO:
        patient = session.patient
        if patient is None:
            raise ValueError("Session has no patient attached")

        attempts = sorted(session.attempts, key=lambda item: item.created_at)
        final_thresholds = EvaluationEngine._get_final_thresholds(session.stored_thresholds)
        reference_points = EvaluationEngine._get_reference_points(patient)

        protocol_metrics = EvaluationEngine._evaluate_protocol(
            attempts,
            reference_points,
            final_thresholds,
        )
        threshold_comparisons = EvaluationEngine._evaluate_threshold_accuracy(
            reference_points,
            final_thresholds,
        )
        interpretation_evaluations = EvaluationEngine._evaluate_interpretations(
            patient,
            session.final_interpretations,
        )

        protocol_score = EvaluationEngine._weighted_average(
            [
                (metric.score, EvaluationEngine.PROTOCOL_WEIGHTS.get(metric.code, 0.0))
                for metric in protocol_metrics
            ]
        )
        threshold_score = EvaluationEngine._average_score(item.score for item in threshold_comparisons)
        interpretation_score = EvaluationEngine._average_score(
            item.score
            for item in interpretation_evaluations
            if item.scorable_fields
        )

        overall_score = EvaluationEngine._weighted_average(
            [
                (
                    threshold_score,
                    EvaluationEngine.OFFICIAL_SCORE_WEIGHTS["thresholds"],
                ),
                (
                    interpretation_score,
                    EvaluationEngine.OFFICIAL_SCORE_WEIGHTS["interpretation"],
                ),
            ]
        )

        summary = EvaluationSummaryDTO(
            session_id=session.id,
            patient_id=patient.id,
            duration_seconds=EvaluationEngine._duration_seconds(session),
            overall_score=EvaluationEngine._round_score(overall_score),
            threshold_accuracy_score=EvaluationEngine._round_score(threshold_score),
            interpretation_score=EvaluationEngine._round_score(interpretation_score),
            protocol_feedback_summary=EvaluationEngine._build_protocol_feedback_summary(
                protocol_metrics
            ),
            strengths=EvaluationEngine._build_strengths(
                threshold_score,
                interpretation_score,
                protocol_metrics,
            ),
            improvement_points=EvaluationEngine._build_improvement_points(
                protocol_metrics,
                threshold_comparisons,
                interpretation_evaluations,
            ),
        )

        return SessionEvaluationDTO(
            summary=summary,
            protocol_metrics=protocol_metrics,
            threshold_comparisons=threshold_comparisons,
            interpretation_evaluations=interpretation_evaluations,
        )

    @staticmethod
    def _evaluate_protocol(
        attempts: list[AttemptDTO],
        reference_points: list[tuple[EarDTO, AudiogramPointDTO]],
        final_thresholds: dict[tuple[Any, Any, int], StoredThresholdDTO],
    ) -> list[ProtocolMetricDTO]:
        reference_slots = {
            EvaluationEngine._slot_key(ear.side, point.test_type, point.frequency)
            for ear, point in reference_points
        }

        coverage_hits = sum(1 for key in reference_slots if key in final_thresholds)
        coverage_total = len(reference_slots)
        coverage_score = (coverage_hits / coverage_total) * 100 if coverage_total else 0.0

        grouped_attempts = EvaluationEngine._group_attempts_by_slot(attempts)
        step_scores: list[float] = []
        for slot_attempts in grouped_attempts.values():
            for previous, current in zip(slot_attempts, slot_attempts[1:]):
                if previous.response is None:
                    continue
                step_scores.append(EvaluationEngine._score_step_transition(previous, current))
        step_adherence_score = EvaluationEngine._average_fraction(step_scores) * 100

        confirmation_scores: list[float] = []
        for stored in final_thresholds.values():
            history = [
                attempt
                for attempt in grouped_attempts.get(
                    EvaluationEngine._slot_key(stored.ear_side, stored.test_type, stored.frequency),
                    [],
                )
                if attempt.created_at <= stored.created_at
            ]
            confirmation_scores.append(
                EvaluationEngine._score_threshold_confirmation(history, stored)
            )
        threshold_confirmation_score = EvaluationEngine._average_fraction(confirmation_scores) * 100

        return [
            ProtocolMetricDTO(
                code="coverage",
                label="Exam Coverage",
                score=EvaluationEngine._round_score(coverage_score),
                status=EvaluationEngine._score_status(coverage_score),
                details=(
                    f"Stored {coverage_hits} final thresholds out of "
                    f"{coverage_total} reference audiogram slots."
                ),
            ),
            ProtocolMetricDTO(
                code="step_adherence",
                label="Intensity Step Adherence",
                score=EvaluationEngine._round_score(step_adherence_score),
                status=EvaluationEngine._score_status(step_adherence_score),
                details=(
                    "Checks whether level changes followed the expected search pattern "
                    "(typically down after heard, up after not heard)."
                ),
            ),
            ProtocolMetricDTO(
                code="threshold_confirmation",
                label="Threshold Confirmation",
                score=EvaluationEngine._round_score(threshold_confirmation_score),
                status=EvaluationEngine._score_status(threshold_confirmation_score),
                details=(
                    "Looks for evidence that each stored threshold was supported by "
                    "responses around the decision point."
                ),
            ),
        ]

    @staticmethod
    def _evaluate_threshold_accuracy(
        reference_points: list[tuple[EarDTO, AudiogramPointDTO]],
        final_thresholds: dict[tuple[Any, Any, int], StoredThresholdDTO],
    ) -> list[ThresholdComparisonDTO]:
        comparisons: list[ThresholdComparisonDTO] = []

        sorted_reference_points = sorted(
            reference_points,
            key=lambda item: (item[0].side.value, item[1].test_type.value, item[1].frequency),
        )

        for ear, point in sorted_reference_points:
            key = EvaluationEngine._slot_key(ear.side, point.test_type, point.frequency)
            detected = final_thresholds.get(key)

            if detected is None:
                comparisons.append(
                    ThresholdComparisonDTO(
                        ear_side=ear.side,
                        test_type=point.test_type,
                        frequency=point.frequency,
                        true_threshold_db=point.threshold_db,
                        detected_threshold_db=None,
                        true_is_no_response=point.is_no_response,
                        detected_is_no_response=False,
                        absolute_error_db=None,
                        score=0.0,
                        status="missing",
                        note="No final threshold was stored for this expected slot.",
                    )
                )
                continue

            comparisons.append(EvaluationEngine._build_threshold_comparison(ear, point, detected))

        return comparisons

    @staticmethod
    def _evaluate_interpretations(
        patient: PatientDTO,
        submitted: list[FinalInterpretationDTO],
    ) -> list[EarInterpretationEvaluationDTO]:
        submitted_by_ear = {item.ear_side: item for item in submitted}
        evaluations: list[EarInterpretationEvaluationDTO] = []

        for ear in sorted(patient.ears, key=lambda item: item.side.value):
            reference_context = EvaluationEngine._build_reference_interpretation_context(patient, ear.side)
            reference = reference_context["values"]
            scorable_fields = reference_context["scorable_fields"]
            undetermined_fields = reference_context["undetermined_fields"]
            current = submitted_by_ear.get(ear.side)
            field_scores: list[InterpretationFieldScoreDTO] = []
            weighted_scores: list[tuple[float, float]] = []

            for field_name, weight in EvaluationEngine.INTERPRETATION_WEIGHTS.items():
                expected = reference.get(field_name)
                observed = getattr(current, field_name, None) if current else None
                if field_name not in scorable_fields:
                    field_scores.append(
                        InterpretationFieldScoreDTO(
                            field_name=field_name,
                            expected_value=expected,
                            submitted_value=EvaluationEngine._serialize_value(observed),
                            score=0.0,
                            is_scorable=False,
                            status="undetermined",
                            note=undetermined_fields.get(
                                field_name,
                                "Field was excluded from scoring for this patient.",
                            ),
                        )
                    )
                    continue

                score, note, status = EvaluationEngine._score_interpretation_field(
                    field_name,
                    expected,
                    observed,
                )
                field_scores.append(
                    InterpretationFieldScoreDTO(
                        field_name=field_name,
                        expected_value=expected,
                        submitted_value=EvaluationEngine._serialize_value(observed),
                        score=EvaluationEngine._round_score(score),
                        status=status,
                        note=note,
                    )
                )
                weighted_scores.append((score, weight))

            evaluations.append(
                EarInterpretationEvaluationDTO(
                    ear_side=ear.side,
                    score=EvaluationEngine._round_score(
                        EvaluationEngine._weighted_average(weighted_scores)
                    ),
                    scorable_fields=scorable_fields,
                    undetermined_fields=undetermined_fields,
                    reference_summary=reference,
                    submitted_summary=(
                        EvaluationEngine._serialize_interpretation(current)
                        if current is not None
                        else None
                    ),
                    field_scores=field_scores,
                )
            )

        return evaluations

    @staticmethod
    def _build_threshold_comparison(
        ear: EarDTO,
        point: AudiogramPointDTO,
        detected: StoredThresholdDTO,
    ) -> ThresholdComparisonDTO:
        if point.is_no_response != detected.is_no_response:
            return ThresholdComparisonDTO(
                ear_side=ear.side,
                test_type=point.test_type,
                frequency=point.frequency,
                true_threshold_db=point.threshold_db,
                detected_threshold_db=detected.threshold_db,
                true_is_no_response=point.is_no_response,
                detected_is_no_response=detected.is_no_response,
                absolute_error_db=abs(point.threshold_db - detected.threshold_db),
                score=0.0,
                status="incorrect",
                note="No-response classification does not match the reference patient.",
            )

        if point.is_no_response and detected.is_no_response:
            error = abs(point.threshold_db - detected.threshold_db)
            if error <= 5:
                score = 100.0
                note = "No-response classification is correct and stored level is aligned."
                status = "correct"
            elif error <= 10:
                score = 90.0
                note = "No-response classification is correct with a small level offset."
                status = "close"
            else:
                score = 75.0
                note = "No-response classification is correct but stored level is noticeably offset."
                status = "approximate"
            return ThresholdComparisonDTO(
                ear_side=ear.side,
                test_type=point.test_type,
                frequency=point.frequency,
                true_threshold_db=point.threshold_db,
                detected_threshold_db=detected.threshold_db,
                true_is_no_response=True,
                detected_is_no_response=True,
                absolute_error_db=error,
                score=score,
                status=status,
                note=note,
            )

        error = abs(point.threshold_db - detected.threshold_db)
        if error <= 5:
            score = 100.0
            status = "correct"
            note = "Threshold is clinically aligned with the reference value."
        elif error <= 10:
            score = 80.0
            status = "close"
            note = "Threshold is acceptable but outside the ideal 5 dB range."
        elif error <= 15:
            score = 60.0
            status = "fair"
            note = "Threshold is partially correct but clinically imprecise."
        elif error <= 20:
            score = 40.0
            status = "weak"
            note = "Threshold is far enough to affect interpretation quality."
        else:
            score = 0.0
            status = "incorrect"
            note = "Threshold differs substantially from the reference value."

        return ThresholdComparisonDTO(
            ear_side=ear.side,
            test_type=point.test_type,
            frequency=point.frequency,
            true_threshold_db=point.threshold_db,
            detected_threshold_db=detected.threshold_db,
            true_is_no_response=False,
            detected_is_no_response=False,
            absolute_error_db=error,
            score=score,
            status=status,
            note=note,
        )

    @staticmethod
    def _score_step_transition(previous: AttemptDTO, current: AttemptDTO) -> float:
        delta = current.intensity - previous.intensity
        if previous.response == ResponseEnum.HEARD:
            if delta == -10:
                return 1.0
            if delta < 0 and abs(delta + 10) <= 5:
                return 0.85
            if delta < 0:
                return 0.60
            return 0.0

        if previous.response == ResponseEnum.NOT_HEARD:
            if delta == 5:
                return 1.0
            if 0 < delta <= 10:
                return 0.75
            if delta > 0:
                return 0.50
            return 0.0

        return 0.0

    @staticmethod
    def _score_threshold_confirmation(
        attempts: list[AttemptDTO],
        stored: StoredThresholdDTO,
    ) -> float:
        if not attempts:
            return 0.0

        if stored.is_no_response:
            not_heard_near_store = sum(
                1
                for attempt in attempts
                if attempt.response == ResponseEnum.NOT_HEARD
                and attempt.intensity >= stored.threshold_db - 5
            )
            if not_heard_near_store >= 2:
                return 1.0
            if not_heard_near_store == 1:
                return 0.6
            return 0.0

        heard_at_level = sum(
            1
            for attempt in attempts
            if attempt.response == ResponseEnum.HEARD
            and abs(attempt.intensity - stored.threshold_db) <= 0.1
        )
        heard_above = sum(
            1
            for attempt in attempts
            if attempt.response == ResponseEnum.HEARD
            and stored.threshold_db <= attempt.intensity <= stored.threshold_db + 10
        )
        not_heard_below = sum(
            1
            for attempt in attempts
            if attempt.response == ResponseEnum.NOT_HEARD
            and abs(attempt.intensity - (stored.threshold_db - 5)) <= 0.1
        )

        if heard_at_level >= 2 and not_heard_below >= 1:
            return 1.0
        if heard_at_level >= 1 and not_heard_below >= 1:
            return 0.8
        if heard_above >= 1 and not_heard_below >= 1:
            return 0.65
        if heard_at_level >= 1:
            return 0.4
        return 0.0

    @staticmethod
    def _build_reference_interpretation_context(
        patient: PatientDTO,
        ear_side: Any,
    ) -> dict[str, Any]:
        ear = EvaluationEngine._get_ear(patient, ear_side)
        if ear is None:
            undetermined = {
                field_name: "Ear data is missing for this patient."
                for field_name in EvaluationEngine.INTERPRETATION_WEIGHTS
            }
            return {
                "values": {},
                "scorable_fields": [],
                "undetermined_fields": undetermined,
            }

        air_points = EvaluationEngine._select_best_points(
            ear,
            [TestTypeEnum.AC_MASKED, TestTypeEnum.AC],
        )
        bone_points = EvaluationEngine._select_best_points(
            ear,
            [TestTypeEnum.BC_MASKED, TestTypeEnum.BC],
        )
        affected_frequencies, affected_scorable, affected_reason = (
            EvaluationEngine._derive_affected_frequencies_reference(air_points)
        )
        overall_type, overall_scorable, overall_reason = EvaluationEngine._derive_overall_type_reference(
            ear,
            air_points,
            bone_points,
        )
        severity, severity_scorable, severity_reason = EvaluationEngine._derive_severity_reference(
            air_points,
        )
        configuration, configuration_scorable, configuration_reason = (
            EvaluationEngine._derive_configuration_reference(
                air_points,
                affected_frequencies,
                overall_type,
            )
        )

        scorable_fields: list[str] = []
        undetermined_fields: dict[str, str] = {}

        field_states = {
            "overall_type": (overall_scorable, overall_reason),
            "severity": (severity_scorable, severity_reason),
            "configuration": (configuration_scorable, configuration_reason),
            "affected_frequencies_hz": (affected_scorable, affected_reason),
        }

        for field_name, (is_scorable, reason) in field_states.items():
            if is_scorable:
                scorable_fields.append(field_name)
            else:
                undetermined_fields[field_name] = reason or "Field could not be determined from patient data."

        return {
            "values": {
                "overall_type": overall_type,
                "severity": severity,
                "configuration": configuration,
                "affected_frequencies_hz": affected_frequencies,
            },
            "scorable_fields": scorable_fields,
            "undetermined_fields": undetermined_fields,
        }

    @staticmethod
    def _derive_overall_type(
        ear: EarDTO,
        air_points: dict[int, AudiogramPointDTO],
        bone_points: dict[int, AudiogramPointDTO],
        air_bone_gap_present: bool,
    ) -> str | None:
        if ear.hearing_type is not None:
            return ear.hearing_type.value

        air_abnormal = EvaluationEngine._has_elevated_thresholds(air_points)
        bone_abnormal = EvaluationEngine._has_elevated_thresholds(bone_points)

        if not air_abnormal and not bone_abnormal:
            return HearingTypeEnum.NORMAL.value
        if air_bone_gap_present and not bone_abnormal:
            return HearingTypeEnum.CONDUCTIVE.value
        if air_bone_gap_present and bone_abnormal:
            return HearingTypeEnum.MIXED.value
        if air_abnormal or bone_abnormal:
            return HearingTypeEnum.SENSORINEURAL.value
        return None

    @staticmethod
    def _derive_overall_type_reference(
        ear: EarDTO,
        air_points: dict[int, AudiogramPointDTO],
        bone_points: dict[int, AudiogramPointDTO],
    ) -> tuple[str | None, bool, str | None]:
        if ear.hearing_type is not None:
            return ear.hearing_type.value, True, None

        if len(air_points) < 2:
            return None, False, "Not enough air-conduction data to determine hearing-loss type."

        air_abnormal = EvaluationEngine._has_elevated_thresholds(air_points)
        comparable_bone_points = EvaluationEngine._count_comparable_bone_points(air_points, bone_points)

        if not air_abnormal:
            return HearingTypeEnum.NORMAL.value, True, None

        if comparable_bone_points == 0:
            return None, False, "Bone-conduction data is insufficient to determine hearing-loss type."

        derived = EvaluationEngine._derive_overall_type(
            ear,
            air_points,
            bone_points,
            EvaluationEngine._has_air_bone_gap(air_points, bone_points),
        )
        if derived is None:
            return None, False, "Hearing-loss type could not be determined from the available data."
        return derived, True, None

    @staticmethod
    def _derive_severity(air_points: dict[int, AudiogramPointDTO]) -> str | None:
        pta_frequencies = [500, 1000, 2000]
        pta_values = [
            air_points[freq].threshold_db
            for freq in pta_frequencies
            if freq in air_points and not air_points[freq].is_no_response
        ]

        if len(pta_values) < 2:
            fallback = [
                point.threshold_db
                for _, point in sorted(air_points.items())
                if not point.is_no_response
            ]
            pta_values = fallback[:3]

        if not pta_values:
            return HearingSeverityEnum.UNDETERMINED.value

        pta = sum(pta_values) / len(pta_values)
        if pta <= 25:
            return HearingSeverityEnum.NORMAL.value
        if pta <= 40:
            return HearingSeverityEnum.MILD.value
        if pta <= 55:
            return HearingSeverityEnum.MODERATE.value
        if pta <= 70:
            return HearingSeverityEnum.MODERATELY_SEVERE.value
        if pta <= 90:
            return HearingSeverityEnum.SEVERE.value
        return HearingSeverityEnum.PROFOUND.value

    @staticmethod
    def _derive_severity_reference(
        air_points: dict[int, AudiogramPointDTO],
    ) -> tuple[str | None, bool, str | None]:
        core_pta_count = sum(
            1
            for freq in (500, 1000, 2000)
            if freq in air_points and not air_points[freq].is_no_response
        )
        if core_pta_count < 2:
            return None, False, "At least two core PTA frequencies (500, 1000, 2000 Hz) are required."

        severity = EvaluationEngine._derive_severity(air_points)
        if severity is None:
            return None, False, "Severity could not be derived from the available thresholds."
        return severity, True, None

    @staticmethod
    def _derive_configuration(
        air_points: dict[int, AudiogramPointDTO],
        affected_frequencies: list[int],
    ) -> str | None:
        if not air_points:
            return HearingConfigurationEnum.UNDETERMINED.value
        if not affected_frequencies:
            return HearingConfigurationEnum.UNDETERMINED.value
        if len(affected_frequencies) == 1:
            return HearingConfigurationEnum.SINGLE_FREQUENCY.value
        if EvaluationEngine._is_notch_pattern(air_points):
            return HearingConfigurationEnum.NOTCH_PATTERN.value
        if len(affected_frequencies) == len(air_points):
            return HearingConfigurationEnum.ALL_FREQUENCIES.value

        low = sum(1 for freq in affected_frequencies if freq <= 500)
        mid = sum(1 for freq in affected_frequencies if 750 <= freq <= 2000)
        high = sum(1 for freq in affected_frequencies if freq >= 3000)
        total = len(affected_frequencies)

        if low / total >= 0.6 and high == 0:
            return HearingConfigurationEnum.LOW_FREQUENCIES.value
        if high / total >= 0.6 and low == 0:
            return HearingConfigurationEnum.HIGH_FREQUENCIES.value
        if mid / total >= 0.6 and low == 0 and high == 0:
            return HearingConfigurationEnum.MID_FREQUENCIES.value
        return HearingConfigurationEnum.OTHER.value

    @staticmethod
    def _derive_configuration_reference(
        air_points: dict[int, AudiogramPointDTO],
        affected_frequencies: list[int],
        overall_type: str | None,
    ) -> tuple[str | None, bool, str | None]:
        if len(air_points) < 2:
            return None, False, "Not enough air-conduction frequency coverage to determine configuration."

        if overall_type == HearingTypeEnum.NORMAL.value:
            return None, False, "Configuration is not scored when hearing is within normal limits."

        if not affected_frequencies:
            return None, False, "No affected frequencies were identified to support a configuration label."

        configuration = EvaluationEngine._derive_configuration(air_points, affected_frequencies)
        if configuration is None:
            return None, False, "Configuration could not be determined from the available data."
        return configuration, True, None

    @staticmethod
    def _derive_affected_frequencies(air_points: dict[int, AudiogramPointDTO]) -> list[int]:
        return sorted(
            freq
            for freq, point in air_points.items()
            if point.is_no_response or point.threshold_db > 25
        )

    @staticmethod
    def _derive_affected_frequencies_reference(
        air_points: dict[int, AudiogramPointDTO],
    ) -> tuple[list[int], bool, str | None]:
        if len(air_points) < 2:
            return [], False, "Not enough tested frequencies to determine affected-frequency coverage."
        return EvaluationEngine._derive_affected_frequencies(air_points), True, None

    @staticmethod
    def _score_interpretation_field(
        field_name: str,
        expected: Any,
        observed: Any,
    ) -> tuple[float, str, str]:
        expected_value = EvaluationEngine._serialize_value(expected)
        observed_value = EvaluationEngine._serialize_value(observed)

        if observed_value is None:
            return 0.0, "Field was not provided.", "missing"

        if field_name == "affected_frequencies_hz":
            expected_set = set(expected_value or [])
            observed_set = set(observed_value or [])
            if not expected_set and not observed_set:
                return 100.0, "Affected-frequency set matches the reference.", "scored"
            union = expected_set | observed_set
            intersection = expected_set & observed_set
            score = (len(intersection) / len(union)) * 100 if union else 100.0
            if score == 100.0:
                note = "Affected-frequency set matches the reference."
            elif score >= 60:
                note = "Affected-frequency set partially matches the reference."
            else:
                note = "Affected-frequency set differs substantially from the reference."
            return score, note, "scored"

        if field_name == "severity":
            if expected_value == observed_value:
                return 100.0, "Severity classification matches the reference.", "scored"
            if (
                expected_value in EvaluationEngine.SEVERITY_ORDER
                and observed_value in EvaluationEngine.SEVERITY_ORDER
            ):
                distance = abs(
                    EvaluationEngine.SEVERITY_ORDER.index(expected_value)
                    - EvaluationEngine.SEVERITY_ORDER.index(observed_value)
                )
                if distance == 1:
                    return 65.0, "Severity is close but one category away.", "scored"
                if distance == 2:
                    return 30.0, "Severity is directionally reasonable but still far.", "scored"
            return 0.0, "Severity classification does not match the reference.", "scored"

        if field_name == "overall_type":
            if expected_value == observed_value:
                return 100.0, "Hearing-loss type matches the reference.", "scored"
            if expected_value == HearingTypeEnum.MIXED.value and observed_value in {
                HearingTypeEnum.CONDUCTIVE.value,
                HearingTypeEnum.SENSORINEURAL.value,
            }:
                return 50.0, "Type is partially correct but misses the mixed component.", "scored"
            if observed_value == HearingTypeEnum.MIXED.value and expected_value in {
                HearingTypeEnum.CONDUCTIVE.value,
                HearingTypeEnum.SENSORINEURAL.value,
            }:
                return 50.0, "Type is directionally close but overstates the pathology.", "scored"
            return 0.0, "Hearing-loss type does not match the reference.", "scored"

        if expected_value == observed_value:
            return 100.0, "Field matches the reference.", "scored"
        return 0.0, "Field does not match the reference.", "scored"

    @staticmethod
    def _select_best_points(
        ear: EarDTO,
        preference_order: list[TestTypeEnum],
    ) -> dict[int, AudiogramPointDTO]:
        selected: dict[int, AudiogramPointDTO] = {}
        for test_type in preference_order:
            for point in ear.audiogram_points:
                if point.test_type == test_type and point.frequency not in selected:
                    selected[point.frequency] = point
        return selected

    @staticmethod
    def _is_notch_pattern(air_points: dict[int, AudiogramPointDTO]) -> bool:
        frequencies = sorted(air_points)
        if len(frequencies) < 3:
            return False

        for index in range(1, len(frequencies) - 1):
            current_freq = frequencies[index]
            if current_freq not in {3000, 4000, 6000}:
                continue
            lower = air_points[frequencies[index - 1]].threshold_db
            current = air_points[current_freq].threshold_db
            higher = air_points[frequencies[index + 1]].threshold_db
            if current >= lower + 15 and current >= higher + 15:
                return True
        return False

    @staticmethod
    def _has_air_bone_gap(
        air_points: dict[int, AudiogramPointDTO],
        bone_points: dict[int, AudiogramPointDTO],
    ) -> bool:
        for freq, air_point in air_points.items():
            bone_point = bone_points.get(freq)
            if bone_point is None:
                continue
            if air_point.is_no_response or bone_point.is_no_response:
                continue
            if air_point.threshold_db - bone_point.threshold_db >= 15:
                return True
        return False

    @staticmethod
    def _has_elevated_thresholds(points: dict[int, AudiogramPointDTO]) -> bool:
        return any(point.is_no_response or point.threshold_db > 25 for point in points.values())

    @staticmethod
    def _count_comparable_bone_points(
        air_points: dict[int, AudiogramPointDTO],
        bone_points: dict[int, AudiogramPointDTO],
    ) -> int:
        return sum(
            1
            for freq, air_point in air_points.items()
            if freq in bone_points
            and not air_point.is_no_response
            and not bone_points[freq].is_no_response
        )

    @staticmethod
    def _get_reference_points(patient: PatientDTO) -> list[tuple[EarDTO, AudiogramPointDTO]]:
        items: list[tuple[EarDTO, AudiogramPointDTO]] = []
        for ear in patient.ears:
            for point in ear.audiogram_points:
                items.append((ear, point))
        return items

    @staticmethod
    def _get_final_thresholds(
        thresholds: list[StoredThresholdDTO],
    ) -> dict[tuple[Any, Any, int], StoredThresholdDTO]:
        final_map: dict[tuple[Any, Any, int], StoredThresholdDTO] = {}
        finals = sorted(
            (item for item in thresholds if item.is_final),
            key=lambda item: item.created_at,
        )
        for item in finals:
            final_map[EvaluationEngine._slot_key(item.ear_side, item.test_type, item.frequency)] = item
        return final_map

    @staticmethod
    def _group_attempts_by_slot(
        attempts: list[AttemptDTO],
    ) -> dict[tuple[Any, Any, int], list[AttemptDTO]]:
        grouped: dict[tuple[Any, Any, int], list[AttemptDTO]] = defaultdict(list)
        for attempt in sorted(attempts, key=lambda item: item.created_at):
            grouped[
                EvaluationEngine._slot_key(
                    attempt.ear_side,
                    attempt.test_type,
                    attempt.frequency,
                )
            ].append(attempt)
        return grouped

    @staticmethod
    def _duration_seconds(session: SessionFullDTO) -> float | None:
        if session.end_time is None:
            return None
        return round((session.end_time - session.start_time).total_seconds(), 2)

    @staticmethod
    def _average_score(values: Any) -> float:
        values_list = list(values)
        if not values_list:
            return 0.0
        return sum(values_list) / len(values_list)

    @staticmethod
    def _average_fraction(values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def _weighted_average(values: list[tuple[float, float]]) -> float:
        total_weight = sum(weight for _, weight in values)
        if total_weight == 0:
            return 0.0
        return sum(score * weight for score, weight in values) / total_weight

    @staticmethod
    def _round_score(value: float) -> float:
        return round(value, 2)

    @staticmethod
    def _score_status(score: float) -> str:
        if score >= 85:
            return "strong"
        if score >= 60:
            return "acceptable"
        return "needs_improvement"

    @staticmethod
    def _slot_key(ear_side: Any, test_type: Any, frequency: int) -> tuple[Any, Any, int]:
        return ear_side, test_type, frequency

    @staticmethod
    def _serialize_interpretation(item: FinalInterpretationDTO) -> dict[str, Any]:
        return {
            "overall_type": EvaluationEngine._serialize_value(item.overall_type),
            "severity": EvaluationEngine._serialize_value(item.severity),
            "configuration": EvaluationEngine._serialize_value(item.configuration),
            "affected_frequencies_hz": item.affected_frequencies_hz,
            "clinical_comment": item.clinical_comment,
        }

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, list):
            return [EvaluationEngine._serialize_value(item) for item in value]
        return getattr(value, "value", value)

    @staticmethod
    def _get_ear(patient: PatientDTO, ear_side: Any) -> EarDTO | None:
        return next((ear for ear in patient.ears if ear.side == ear_side), None)

    @staticmethod
    def _build_strengths(
        threshold_score: float,
        interpretation_score: float,
        protocol_metrics: list[ProtocolMetricDTO],
    ) -> list[str]:
        strengths: list[str] = []
        if threshold_score >= 85:
            strengths.append("Detected thresholds were closely aligned with the reference audiogram.")
        if interpretation_score >= 85:
            strengths.append("Final interpretation was consistent with the reference clinical picture.")
        strong_protocol_metrics = [metric for metric in protocol_metrics if metric.score >= 85]
        for metric in strong_protocol_metrics[:2]:
            strengths.append(f"Protocol feedback: {metric.label} was consistently strong.")
        if not strengths:
            strengths.append("The session contains usable evidence for feedback and focused remediation.")
        return strengths

    @staticmethod
    def _build_protocol_feedback_summary(
        protocol_metrics: list[ProtocolMetricDTO],
    ) -> str | None:
        if not protocol_metrics:
            return None

        needs_improvement = [metric.label for metric in protocol_metrics if metric.score < 60]
        strong = [metric.label for metric in protocol_metrics if metric.score >= 85]

        if needs_improvement:
            joined = ", ".join(needs_improvement)
            return f"Protocol feedback should focus on: {joined}."

        if strong:
            joined = ", ".join(strong)
            return f"Protocol execution was strongest in: {joined}."

        return "Protocol performance was acceptable overall, with room for a more consistent search pattern."

    @staticmethod
    def _build_improvement_points(
        protocol_metrics: list[ProtocolMetricDTO],
        threshold_comparisons: list[ThresholdComparisonDTO],
        interpretation_evaluations: list[EarInterpretationEvaluationDTO],
    ) -> list[str]:
        improvements: list[str] = []

        weak_metrics = [item for item in protocol_metrics if item.score < 60]
        for metric in weak_metrics:
            improvements.append(f"Protocol: {metric.label} needs improvement.")

        missing_thresholds = sum(1 for item in threshold_comparisons if item.status == "missing")
        if missing_thresholds:
            improvements.append(
                f"Thresholds: {missing_thresholds} expected audiogram slots were left without a final stored value."
            )

        inaccurate_thresholds = sum(1 for item in threshold_comparisons if item.score < 60)
        if inaccurate_thresholds:
            improvements.append(
                f"Thresholds: {inaccurate_thresholds} stored thresholds were clinically imprecise or incorrect."
            )

        weak_interpretations = [
            item for item in interpretation_evaluations
            if item.scorable_fields and item.score < 60
        ]
        for item in weak_interpretations:
            improvements.append(
                f"Interpretation: {item.ear_side.value} ear interpretation should be reviewed against the derived reference."
            )

        return improvements[:6]
