import json
import os

from openai import AsyncOpenAI

from app.schemas.ai_feedback_schema import AIFeedbackDTO
from app.schemas.evaluation_schema import SessionEvaluationDTO
from app.schemas.session_schema import SessionFullDTO


class AIFeedbackService:
    DEFAULT_MODEL = "gpt-5.4-mini"
    RESPONSE_SCHEMA = {
        "name": "pta_formative_feedback",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "strengths": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "improvement_points": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "next_session_tips": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": [
                "summary",
                "strengths",
                "improvement_points",
                "next_session_tips",
            ],
            "additionalProperties": False,
        },
    }

    SYSTEM_PROMPT = (
        "You are an audiology tutoring assistant generating formative feedback for a PTA simulator. "
        "Use only the provided facts. Do not invent missing findings. "
        "Do not change or recompute official scores. "
        "Do not mention undetermined fields as student mistakes. "
        "Keep feedback concise, educational, and actionable."
    )

    @staticmethod
    async def generate_feedback(
        session: SessionFullDTO,
        evaluation: SessionEvaluationDTO,
    ) -> AIFeedbackDTO:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_FEEDBACK_MODEL", AIFeedbackService.DEFAULT_MODEL)

        if not api_key:
            return AIFeedbackService._build_deterministic_feedback(
                session,
                evaluation,
                status="fallback",
                message="OpenAI feedback is unavailable because OPENAI_API_KEY is not configured.",
            )

        try:
            client = AsyncOpenAI(api_key=api_key)
            response = await client.responses.create(
                model=model,
                input=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": AIFeedbackService.SYSTEM_PROMPT,
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": json.dumps(
                                    AIFeedbackService._build_prompt_payload(session, evaluation),
                                    ensure_ascii=False,
                                ),
                            }
                        ],
                    },
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        **AIFeedbackService.RESPONSE_SCHEMA,
                    }
                },
            )

            content = json.loads(response.output_text or "{}")
            return AIFeedbackDTO(
                status="generated",
                provider="openai",
                model=model,
                summary=content.get("summary"),
                strengths=content.get("strengths", []),
                improvement_points=content.get("improvement_points", []),
                next_session_tips=content.get("next_session_tips", []),
            )
        except Exception as exc:
            return AIFeedbackService._build_deterministic_feedback(
                session,
                evaluation,
                status="fallback",
                message=f"OpenAI feedback failed and a deterministic fallback was used: {exc}",
            )

    @staticmethod
    def _build_prompt_payload(
        session: SessionFullDTO,
        evaluation: SessionEvaluationDTO,
    ) -> dict:
        weak_thresholds = [
            {
                "ear_side": item.ear_side.value,
                "test_type": item.test_type.value,
                "frequency": item.frequency,
                "true_threshold_db": item.true_threshold_db,
                "detected_threshold_db": item.detected_threshold_db,
                "score": item.score,
                "status": item.status,
                "note": item.note,
            }
            for item in evaluation.threshold_comparisons
            if item.score < 100
        ][:8]

        interpretation_findings = []
        for ear_eval in evaluation.interpretation_evaluations:
            interpretation_findings.append(
                {
                    "ear_side": ear_eval.ear_side.value,
                    "score": ear_eval.score,
                    "scorable_fields": ear_eval.scorable_fields,
                    "undetermined_fields": ear_eval.undetermined_fields,
                    "field_scores": [
                        {
                            "field_name": field.field_name,
                            "score": field.score,
                            "status": field.status,
                            "is_scorable": field.is_scorable,
                            "note": field.note,
                        }
                        for field in ear_eval.field_scores
                    ],
                }
            )

        return {
            "session_context": {
                "session_id": session.id,
                "patient_id": session.patient_id,
                "duration_seconds": evaluation.summary.duration_seconds,
                "attempt_count": len(session.attempts),
                "stored_threshold_count": len(session.stored_thresholds),
            },
            "official_scores": {
                "overall_score": evaluation.summary.overall_score,
                "threshold_accuracy_score": evaluation.summary.threshold_accuracy_score,
                "interpretation_score": evaluation.summary.interpretation_score,
            },
            "protocol_metrics": [
                {
                    "code": metric.code,
                    "label": metric.label,
                    "score": metric.score,
                    "status": metric.status,
                    "details": metric.details,
                }
                for metric in evaluation.protocol_metrics
            ],
            "weak_thresholds": weak_thresholds,
            "interpretation_findings": interpretation_findings,
        }

    @staticmethod
    def _build_deterministic_feedback(
        session: SessionFullDTO,
        evaluation: SessionEvaluationDTO,
        status: str,
        message: str,
    ) -> AIFeedbackDTO:
        strengths: list[str] = []
        improvement_points: list[str] = []
        next_session_tips: list[str] = []

        if evaluation.summary.threshold_accuracy_score >= 85:
            strengths.append("Your detected thresholds were closely aligned with the reference audiogram.")
        elif evaluation.summary.threshold_accuracy_score >= 70:
            strengths.append("Most detected thresholds were reasonably close to the reference audiogram.")

        if evaluation.summary.interpretation_score >= 85:
            strengths.append("Your final interpretation was strongly aligned with the reference clinical picture.")
        elif evaluation.summary.interpretation_score >= 70:
            strengths.append("Your final interpretation was generally appropriate with some room for refinement.")

        strong_protocol_metrics = [metric for metric in evaluation.protocol_metrics if metric.score >= 85]
        for metric in strong_protocol_metrics[:2]:
            strengths.append(f"Protocol strength: {metric.label} was consistently strong.")

        weak_thresholds = [item for item in evaluation.threshold_comparisons if item.score < 60]
        if weak_thresholds:
            first = weak_thresholds[0]
            improvement_points.append(
                "Review threshold estimation at "
                f"{first.ear_side.value} {first.test_type.value} {first.frequency} Hz."
            )
            next_session_tips.append(
                "Before storing a threshold, confirm responses around the decision level and re-check close frequencies."
            )

        weak_interpretations = [
            item for item in evaluation.interpretation_evaluations
            if item.scorable_fields and item.score < 60
        ]
        if weak_interpretations:
            first = weak_interpretations[0]
            improvement_points.append(
                f"Revisit the final interpretation for the {first.ear_side.value} ear against the measured thresholds."
            )
            next_session_tips.append(
                "Base the final interpretation on the measured type, severity, configuration, and affected frequencies."
            )

        weak_protocol_metrics = [metric for metric in evaluation.protocol_metrics if metric.score < 60]
        for metric in weak_protocol_metrics[:2]:
            improvement_points.append(f"Protocol: {metric.label} needs a more systematic approach.")

        if weak_protocol_metrics:
            next_session_tips.append(
                "Use a clearer, repeatable search sequence and avoid storing thresholds before enough confirmation."
            )

        if not strengths:
            strengths.append("The session produced enough evidence to support targeted learning feedback.")

        if not improvement_points:
            improvement_points.append("Continue refining consistency so strong results can be reproduced across sessions.")

        if not next_session_tips:
            next_session_tips.append("Keep using the same structured approach and verify each final threshold before storing it.")

        summary = (
            "Feedback was generated from threshold accuracy "
            f"{evaluation.summary.threshold_accuracy_score:.2f}/100 and interpretation "
            f"{evaluation.summary.interpretation_score:.2f}/100, together with protocol observations, "
            f"for a session with {len(session.attempts)} attempts."
        )

        return AIFeedbackDTO(
            status=status,
            provider="local",
            summary=summary,
            strengths=strengths[:3],
            improvement_points=improvement_points[:4],
            next_session_tips=next_session_tips[:3],
            message=message,
        )
