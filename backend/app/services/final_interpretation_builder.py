from app.schemas.final_interpretation_schema import FinalInterpretationCreateDTO


class FinalInterpretationBuilder:
    @staticmethod
    def build_clinical_comment(item: FinalInterpretationCreateDTO) -> str | None:
        parts: list[str] = []
        ear_label = item.ear_side.value.capitalize()

        diagnosis = FinalInterpretationBuilder._build_diagnosis_phrase(item)
        if diagnosis:
            parts.append(f"{ear_label} ear: {diagnosis}.")

        frequency_phrase = FinalInterpretationBuilder._build_frequency_phrase(item)
        if frequency_phrase:
            parts.append(frequency_phrase)

        comment = " ".join(parts).strip()
        return comment or None

    @staticmethod
    def _build_diagnosis_phrase(item: FinalInterpretationCreateDTO) -> str:
        diagnosis_parts: list[str] = []

        if item.severity is not None:
            diagnosis_parts.append(item.severity.value)

        if item.overall_type is not None:
            if item.overall_type.value == "Normal":
                diagnosis_parts.append("hearing sensitivity")
            else:
                diagnosis_parts.append(f"{item.overall_type.value.lower()} hearing loss")

        if item.configuration is not None:
            diagnosis_parts.append(f"with {item.configuration.value.lower()} pattern")

        return " ".join(diagnosis_parts).strip()

    @staticmethod
    def _build_frequency_phrase(item: FinalInterpretationCreateDTO) -> str | None:
        if item.affected_frequencies_hz:
            frequencies = ", ".join(str(freq) for freq in item.affected_frequencies_hz)
            return f"Affected frequencies: {frequencies} Hz."

        if item.overall_type is not None and item.overall_type.value == "Normal":
            return "Thresholds are within normal limits across the tested frequencies."

        return None
