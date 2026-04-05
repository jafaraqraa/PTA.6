"""
Calibration script – PTA Simulator Response Engine (v3)
=======================================================
Tests the REAL engine (not a standalone simulation) to confirm the
psychometric curve is correct for various threshold levels.

Usage
-----
    cd backend
    python -m scripts.calibrate_response_engine
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.response_engine import ResponseEngine
from app.schemas.patient_schema import PatientDTO, EarDTO, AudiogramPointDTO
from app.schemas.attempt_schema import AttemptCreateDTO
from app.models.enums import EarSideEnum, TestTypeEnum, ResponseEnum, PatientSourceEnum

# ── Clinically correct psychometric windows ──────────────────────────────────
# SL = intensity - threshold
TARGET = {
    -10: (0.00, 0.05),
     -5: (0.02, 0.12),
      0: (0.45, 0.60),
     +5: (0.90, 0.99),
    +10: (0.98, 1.00),
}

TRIALS = 1000   # per SL level per patient (fast enough, statistically sound)


def make_patient(patient_id: int, threshold_db: float) -> PatientDTO:
    """Build a minimal PatientDTO with one AC point at 1000 Hz."""
    return PatientDTO(
        id=patient_id,
        source_type=PatientSourceEnum.SYNTHETIC,
        ears=[
            EarDTO(
                side=EarSideEnum.RIGHT,
                audiogram_points=[
                    AudiogramPointDTO(
                        test_type=TestTypeEnum.AC,
                        frequency=1000,
                        threshold_db=threshold_db,
                        is_no_response=False,
                    )
                ],
            )
        ],
    )


def simulate_rate(patient: PatientDTO, intensity: float, trials: int) -> float:
    heard = 0
    for i in range(trials):
        attempt = AttemptCreateDTO(
            session_id=1,
            ear_side=EarSideEnum.RIGHT,
            test_type=TestTypeEnum.AC,
            frequency=1000,
            intensity=intensity,
        )
        # attempt_history length = i  → unique seed per trial
        fake_history = [None] * i   # length only matters for seed; type not validated here
        response = ResponseEngine.evaluate_tone(patient, attempt, fake_history)
        if response == ResponseEnum.HEARD:
            heard += 1
    return heard / trials


def run_for_threshold(patient_id: int, threshold: float) -> dict[int, float]:
    patient = make_patient(patient_id, threshold)
    rates = {}
    for sl in TARGET:
        intensity = threshold + sl
        rates[sl] = simulate_rate(patient, intensity, TRIALS)
    return rates


def print_results(threshold: float, rates: dict[int, float]) -> int:
    violations = 0
    print(f"\n  Threshold = {threshold:.0f} dB")
    print(f"  {'SL':>5}  {'Rate':>7}  {'Target':^14}  {'OK?':^4}")
    print("  " + "─" * 38)
    for sl, (lo, hi) in sorted(TARGET.items()):
        p = rates[sl]
        ok = "✓" if lo <= p <= hi else "✗"
        if ok == "✗":
            violations += 1
        print(f"  {sl:>+4} dB  {p:>6.1%}  [{lo:.0%} – {hi:.0%}]   {ok}")
    return violations


def main():
    # Test multiple threshold levels to confirm engine works universally
    test_cases = [
        (1,  5,   "Normal"),
        (2,  35,  "Mild"),
        (3,  55,  "Moderate"),
        (4,  75,  "Severe"),
        (5,  100, "Profound"),
    ]

    print("=" * 55)
    print("  PTA Response Engine – Psychometric Curve Verification")
    print(f"  ({TRIALS} trials per SL level)")
    print("=" * 55)

    total_violations = 0
    for patient_id, threshold, label in test_cases:
        print(f"\n[{label}]")
        rates = run_for_threshold(patient_id, threshold)
        total_violations += print_results(threshold, rates)

    print("\n" + "=" * 55)
    if total_violations == 0:
        print("  ✅  All windows satisfied across all patient types.")
    else:
        print(f"  ⚠️   {total_violations} violation(s) detected. Review engine parameters.")
    print("=" * 55)


if __name__ == "__main__":
    main()