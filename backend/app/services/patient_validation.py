from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.patient_repository import PatientRepository
from app.schemas.patient_schema import PatientDTO, EarDTO
from app.models.enums import HearingTypeEnum, TestTypeEnum, PatientSourceEnum, EarSideEnum
from app.services.patient_generator import PatientGenerator


@dataclass(frozen=True)
class _EarMetrics:
    hearing_type: HearingTypeEnum
    pta_ac: float
    pta_bc: float
    abg: float
    tilt_ac: float
    tilt_bc: float
    ac_points: dict[int, float]
    bc_points: dict[int, float]
    ac_masked_points: dict[int, float]
    bc_masked_points: dict[int, float]


class PatientValidation:
    """
    Statistical validation of generated patients vs real patients.
    Produces distributional metrics (KS, total variation, masking prevalence).
    """

    @staticmethod
    async def validate_generator(
        db: AsyncSession,
        sample_size: int = 200,
        use_existing_synthetic: bool = False
    ) -> dict:
        profiles = await PatientRepository.get_profiles(db)
        if not profiles:
            return {"error": "no_profiles"}

        real_profiles = [
            p for p in profiles if p.source_type == PatientSourceEnum.REAL
        ]
        if not real_profiles:
            real_profiles = profiles

        synthetic_profiles: list[PatientDTO] = []
        if use_existing_synthetic:
            synthetic_profiles = [
                p for p in profiles if p.source_type == PatientSourceEnum.SYNTHETIC
            ]

        if len(synthetic_profiles) < sample_size:
            model = PatientGenerator._build_model(real_profiles)
            rng = random.Random(1337)
            needed = sample_size - len(synthetic_profiles)
            for _ in range(needed):
                synthetic_profiles.append(
                    PatientGenerator._generate_patient_from_model(model, rng)
                )

        real_ears = PatientValidation._collect_ear_metrics(real_profiles)
        synth_ears = PatientValidation._collect_ear_metrics(synthetic_profiles)

        pair_tv, pair_dist = PatientValidation._pair_type_total_variation(
            real_profiles, synthetic_profiles
        )

        results = {
            "real_patients": len(real_profiles),
            "synthetic_patients": len(synthetic_profiles),
            "pair_type_total_variation": pair_tv,
            "pair_type_distribution": pair_dist,
            "pta_ac_ks": PatientValidation._ks_stat(
                [e.pta_ac for e in real_ears],
                [e.pta_ac for e in synth_ears]
            ),
            "pta_bc_ks": PatientValidation._ks_stat(
                [e.pta_bc for e in real_ears],
                [e.pta_bc for e in synth_ears]
            ),
            "abg_ks": PatientValidation._ks_stat(
                [e.abg for e in real_ears],
                [e.abg for e in synth_ears]
            ),
            "tilt_ac_ks": PatientValidation._ks_stat(
                [e.tilt_ac for e in real_ears],
                [e.tilt_ac for e in synth_ears]
            ),
            "tilt_bc_ks": PatientValidation._ks_stat(
                [e.tilt_bc for e in real_ears],
                [e.tilt_bc for e in synth_ears]
            ),
            "masking_presence_l1": PatientValidation._masking_presence_l1(
                real_ears, synth_ears
            ),
            "per_hearing_type": PatientValidation._per_type_metrics(
                real_ears, synth_ears
            ),
        }

        return results

    # ----------------------------
    # Metric helpers
    # ----------------------------

    @staticmethod
    def _collect_ear_metrics(patients: Iterable[PatientDTO]) -> list[_EarMetrics]:
        ears: list[_EarMetrics] = []
        for patient in patients:
            left = next((e for e in patient.ears if e.side == EarSideEnum.LEFT), None)
            right = next((e for e in patient.ears if e.side == EarSideEnum.RIGHT), None)
            for ear in (left, right):
                if not ear:
                    continue
                metrics = PatientValidation._ear_metrics(ear)
                if metrics:
                    ears.append(metrics)
        return ears

    @staticmethod
    def _ear_metrics(ear: EarDTO) -> _EarMetrics | None:
        ac_points, _ = PatientGenerator._extract_points(ear, TestTypeEnum.AC)
        bc_points, _ = PatientGenerator._extract_points(ear, TestTypeEnum.BC)
        if not ac_points or not bc_points:
            return None

        ac_masked, _ = PatientGenerator._extract_points(ear, TestTypeEnum.AC_MASKED)
        bc_masked, _ = PatientGenerator._extract_points(ear, TestTypeEnum.BC_MASKED)

        profile = ear.hearing_profile or PatientGenerator._infer_hearing_profile(ac_points, bc_points)
        hearing_type = ear.hearing_type or PatientGenerator._summarize_hearing_type(profile)

        pta_ac = PatientValidation._pta(ac_points)
        pta_bc = PatientValidation._pta(bc_points)
        abg = pta_ac - pta_bc

        _, tilt_ac = PatientGenerator._mean_and_tilt(ac_points)
        _, tilt_bc = PatientGenerator._mean_and_tilt(bc_points)

        return _EarMetrics(
            hearing_type=hearing_type,
            pta_ac=pta_ac,
            pta_bc=pta_bc,
            abg=abg,
            tilt_ac=tilt_ac,
            tilt_bc=tilt_bc,
            ac_points=ac_points,
            bc_points=bc_points,
            ac_masked_points=ac_masked,
            bc_masked_points=bc_masked,
        )

    @staticmethod
    def _pta(points: dict[int, float]) -> float:
        core = [f for f in (500, 1000, 2000) if f in points]
        if core:
            vals = [points[f] for f in core]
        else:
            vals = list(points.values())
        return sum(vals) / len(vals) if vals else 0.0

    @staticmethod
    def _pair_type_total_variation(
        real: list[PatientDTO],
        synth: list[PatientDTO]
    ) -> tuple[float, dict[str, dict[str, float]]]:
        real_dist = PatientValidation._pair_distribution(real)
        synth_dist = PatientValidation._pair_distribution(synth)
        keys = set(real_dist) | set(synth_dist)

        tv = 0.0
        for k in keys:
            tv += abs(real_dist.get(k, 0.0) - synth_dist.get(k, 0.0))
        tv *= 0.5

        dist = {
            k: {"real": real_dist.get(k, 0.0), "synthetic": synth_dist.get(k, 0.0)}
            for k in sorted(keys)
        }
        return tv, dist

    @staticmethod
    def _pair_distribution(patients: list[PatientDTO]) -> dict[str, float]:
        counts: dict[str, int] = {}
        total = 0
        for patient in patients:
            left = next((e for e in patient.ears if e.side == EarSideEnum.LEFT), None)
            right = next((e for e in patient.ears if e.side == EarSideEnum.RIGHT), None)
            if not left or not right:
                continue
            left_ac, _ = PatientGenerator._extract_points(left, TestTypeEnum.AC)
            left_bc, _ = PatientGenerator._extract_points(left, TestTypeEnum.BC)
            right_ac, _ = PatientGenerator._extract_points(right, TestTypeEnum.AC)
            right_bc, _ = PatientGenerator._extract_points(right, TestTypeEnum.BC)
            if not left_ac or not left_bc or not right_ac or not right_bc:
                continue

            left_profile = left.hearing_profile or PatientGenerator._infer_hearing_profile(left_ac, left_bc)
            right_profile = right.hearing_profile or PatientGenerator._infer_hearing_profile(right_ac, right_bc)
            left_sig = PatientGenerator._profile_signature(left_profile)
            right_sig = PatientGenerator._profile_signature(right_profile)
            key = f"{left_sig}/{right_sig}"
            counts[key] = counts.get(key, 0) + 1
            total += 1

        if total == 0:
            return {}
        return {k: v / total for k, v in counts.items()}

    @staticmethod
    def _masking_presence_l1(
        real_ears: list[_EarMetrics],
        synth_ears: list[_EarMetrics],
    ) -> dict[str, float | None]:
        def presence_map(ears: list[_EarMetrics], masked_type: TestTypeEnum) -> dict[int, float]:
            counts: dict[int, int] = {}
            totals: dict[int, int] = {}
            for e in ears:
                base_points = e.ac_points if masked_type == TestTypeEnum.AC_MASKED else e.bc_points
                masked_points = e.ac_masked_points if masked_type == TestTypeEnum.AC_MASKED else e.bc_masked_points
                for freq in base_points.keys():
                    totals[freq] = totals.get(freq, 0) + 1
                    if freq in masked_points:
                        counts[freq] = counts.get(freq, 0) + 1
            probs: dict[int, float] = {}
            for freq, total in totals.items():
                probs[freq] = counts.get(freq, 0) / total if total else 0.0
            return probs

        def l1(a: dict[int, float], b: dict[int, float]) -> float | None:
            keys = set(a) | set(b)
            if not keys:
                return None
            return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys) / len(keys)

        real_ac = presence_map(real_ears, TestTypeEnum.AC_MASKED)
        synth_ac = presence_map(synth_ears, TestTypeEnum.AC_MASKED)
        real_bc = presence_map(real_ears, TestTypeEnum.BC_MASKED)
        synth_bc = presence_map(synth_ears, TestTypeEnum.BC_MASKED)

        return {
            "AC_MASKED": l1(real_ac, synth_ac),
            "BC_MASKED": l1(real_bc, synth_bc),
        }

    @staticmethod
    def _ks_stat(a: list[float], b: list[float]) -> float | None:
        if len(a) < 2 or len(b) < 2:
            return None
        a_sorted = sorted(a)
        b_sorted = sorted(b)
        n = len(a_sorted)
        m = len(b_sorted)
        i = 0
        j = 0
        d = 0.0
        while i < n and j < m:
            if a_sorted[i] <= b_sorted[j]:
                i += 1
            else:
                j += 1
            d = max(d, abs(i / n - j / m))
        return d

    @staticmethod
    def _per_type_metrics(
        real_ears: list[_EarMetrics],
        synth_ears: list[_EarMetrics],
    ) -> dict[str, dict[str, float | None]]:
        results: dict[str, dict[str, float | None]] = {}
        types = {e.hearing_type for e in real_ears} | {e.hearing_type for e in synth_ears}
        for htype in types:
            real = [e for e in real_ears if e.hearing_type == htype]
            synth = [e for e in synth_ears if e.hearing_type == htype]
            if len(real) < 5 or len(synth) < 5:
                continue
            results[htype.value] = {
                "pta_ac_ks": PatientValidation._ks_stat(
                    [e.pta_ac for e in real],
                    [e.pta_ac for e in synth],
                ),
                "pta_bc_ks": PatientValidation._ks_stat(
                    [e.pta_bc for e in real],
                    [e.pta_bc for e in synth],
                ),
                "abg_ks": PatientValidation._ks_stat(
                    [e.abg for e in real],
                    [e.abg for e in synth],
                ),
                "tilt_ac_ks": PatientValidation._ks_stat(
                    [e.tilt_ac for e in real],
                    [e.tilt_ac for e in synth],
                ),
                "tilt_bc_ks": PatientValidation._ks_stat(
                    [e.tilt_bc for e in real],
                    [e.tilt_bc for e in synth],
                ),
            }
        return results
