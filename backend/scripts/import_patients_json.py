import argparse
import asyncio
import json
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import AsyncSessionLocal
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient_schema import PatientDTO, EarDTO, AudiogramPointDTO
from app.models.enums import PatientSourceEnum, TestTypeEnum
from app.services.patient_generator import PatientGenerator


def _build_ear(ear_data: dict) -> EarDTO:
    points = [
        AudiogramPointDTO.model_validate(p)
        for p in ear_data.get("audiogram_points", [])
    ]
    ear = EarDTO(
        side=ear_data["side"],
        hearing_type=ear_data.get("hearing_type"),
        hearing_profile=ear_data.get("hearing_profile"),
        hearing_tags=ear_data.get("hearing_tags", []),
        audiogram_points=points,
    )

    if ear.hearing_profile is None or ear.hearing_type is None or not ear.hearing_tags:
        ac_points, ac_nr = PatientGenerator._extract_points(ear, test_type=TestTypeEnum.AC)
        bc_points, bc_nr = PatientGenerator._extract_points(ear, test_type=TestTypeEnum.BC)

        if ear.hearing_profile is None:
            ear.hearing_profile = PatientGenerator._infer_hearing_profile(
                ac_points, bc_points, ac_nr, bc_nr
            )
        if ear.hearing_type is None:
            ear.hearing_type = PatientGenerator._summarize_hearing_type(
                ear.hearing_profile
            )
        if not ear.hearing_tags:
            ear.hearing_tags = PatientGenerator._infer_hearing_tags(
                ac_points, bc_points, ac_nr, bc_nr, ear.hearing_profile
            )

    return ear


def _build_patient(patient_data: dict) -> PatientDTO:
    ears = [_build_ear(e) for e in patient_data.get("ears", [])]
    source = patient_data.get("source_type", PatientSourceEnum.REAL)
    return PatientDTO(
        source_type=source,
        image_ref=patient_data.get("image_ref"),
        ears=ears,
    )


async def _import_patients(path: Path) -> int:
    raw = json.loads(path.read_text(encoding="utf-8"))
    patients_data = raw if isinstance(raw, list) else [raw]

    count = 0
    async with AsyncSessionLocal() as session:
        for idx, patient_data in enumerate(patients_data, start=1):
            try:
                dto = _build_patient(patient_data)
                await PatientRepository.save_patient(session, dto)
                count += 1
            except Exception as exc:
                raise RuntimeError(f"Failed at patient #{idx}: {exc}") from exc
    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import patients from JSON and derive hearing profile/type/tags."
    )
    parser.add_argument("json_path", help="Path to patients JSON file.")
    args = parser.parse_args()

    path = Path(args.json_path)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    count = asyncio.run(_import_patients(path))
    print(f"Imported {count} patients.")


if __name__ == "__main__":
    main()
