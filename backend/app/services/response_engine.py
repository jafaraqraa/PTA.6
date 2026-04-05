"""
PTA Simulator - Final Optimal Response Engine
===========================================
This engine is designed to balance two strict requirements:

1. FAIRNESS TO THE STUDENT: The stored threshold in the database is treated as
   the "clinical threshold" (the level where the patient responds ~90% of the time).
   If a student correctly follows the Hughson-Westlake protocol, they will reliably
   find the exact stored threshold, avoiding frustrating +/- 5dB errors.
   
2. HUMAN BEHAVIOR: Real patients are not robots. They have lapses in concentration 
   (lapse_rate), they occasionally guess (guess_rate), and they get tired (fatigue).
   However, these behaviors only cause temporary missed responses or false positive
   responses. They DO NOT permanently shift the patient's actual hearing threshold.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from app.models.enums import ResponseEnum, TestTypeEnum
from app.schemas.attempt_schema import AttemptCreateDTO, AttemptDTO


class ResponseEngine:
    """Stateless, pure-function response engine."""

    _CACHED_CONFIG: "dict | None" = None

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    @staticmethod
    def evaluate_tone(
        patient,
        attempt: AttemptCreateDTO,
        attempt_history: Iterable[AttemptDTO] | None = None,
        session_start_time: datetime | None = None,
    ) -> ResponseEnum:
        """Return HEARD or NOT_HEARD for one tone presentation."""

        history = list(attempt_history or [])

        # 1. True threshold from audiogram (ground truth, NO SHIFTS APPLIED)
        threshold = ResponseEngine._get_threshold_db(patient, attempt)
        is_nr = threshold is None
        if is_nr:
            # No-response patient: effectively out of bounds for the audiometer
            nr_rng = random.Random(
                ResponseEngine._patient_seed(patient) + attempt.frequency
            )
            threshold = nr_rng.uniform(130.0, 145.0)

        # 2. Raw Sensation Level (SL)
        sl = attempt.intensity - threshold

        # 3. Patient personality (deterministic from patient ID)
        profile = ResponseEngine._get_profile(patient)

        # 4. Base probability of detecting the tone
        # profile.clinical_offset_db ensures that at sl == 0 (the exact threshold),
        # the detection probability is ~90%. At sl == -5, it drops to ~5%.
        effective_sl = sl + profile.clinical_offset_db
        p_base = ResponseEngine._logistic(effective_sl, profile.sigma_db)

        # 5. Calculate human factors: Fatigue and Boredom
        # Fatigue gradually builds up as more attempts are made.
        fatigue = len(history) * profile.fatigue_rate
        
        # Boredom builds if the student repeats the same frequency/intensity multiple times in a row.
        repeat_count = 0
        for past in reversed(history[-5:]):
            if (past.frequency == attempt.frequency and
                past.ear_side == attempt.ear_side and
                past.test_type == attempt.test_type):
                repeat_count += 1
            else:
                break
        boredom = repeat_count * profile.boredom_rate

        # 6. Apply human behavior probabilities
        # Lapse: Patient forgets to press the button even if they detected the tone.
        # It increases with fatigue/boredom, but is capped so it's not overly punishing.
        lapse = min(0.15, profile.lapse_rate + fatigue + boredom)
        
        # Guess: Patient presses the button falsely (phantom sound).
        guess = profile.guess_rate

        # Combine logic:
        # Final probability = (Probability they press when they shouldn't) + 
        #                     (Probability they detect it AND don't lapse)
        p = p_base * (1.0 - lapse) + (1.0 - p_base) * guess

        p = max(0.0, min(1.0, p))

        # 7. Draw outcome using a deterministic seed (same patient + attempt = same result)
        seed = ResponseEngine._attempt_seed(patient, attempt, len(history))
        rng = random.Random(seed)
        return ResponseEnum.HEARD if rng.random() < p else ResponseEnum.NOT_HEARD

    # ------------------------------------------------------------------ #
    #  Psychometric function
    # ------------------------------------------------------------------ #

    @staticmethod
    def _logistic(sl: float, sigma: float) -> float:
        """Standard logistic function. Sigma controls the slope steepness."""
        sigma = max(0.5, sigma)
        x = max(-25.0, min(25.0, sl / sigma))
        return 1.0 / (1.0 + math.exp(-x))

    # ------------------------------------------------------------------ #
    #  Threshold lookup
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_threshold_db(patient, attempt: AttemptCreateDTO) -> float | None:
        """Find the exact ground truth threshold from the database."""
        ear = next((e for e in patient.ears if e.side == attempt.ear_side), None)
        if ear is None:
            return 40.0

        def nr(pt) -> bool:
            return bool(getattr(pt, "is_no_response", False))

        # 1. Exact match
        for pt in ear.audiogram_points:
            if pt.test_type == attempt.test_type and pt.frequency == attempt.frequency:
                return None if nr(pt) else float(pt.threshold_db)

        # 2. Unmasked fallback
        fb = {
            TestTypeEnum.AC_MASKED: TestTypeEnum.AC,
            TestTypeEnum.BC_MASKED: TestTypeEnum.BC,
        }.get(attempt.test_type, attempt.test_type)

        for pt in ear.audiogram_points:
            if pt.test_type == fb and pt.frequency == attempt.frequency:
                return None if nr(pt) else float(pt.threshold_db)

        # 3. Interpolation between nearest frequencies
        # Keep ALL points in full_pool to check if bounds are No Response
        full_pool = sorted(
            [p for p in ear.audiogram_points if p.test_type == fb],
            key=lambda p: p.frequency,
        )
        lo = next((p for p in reversed(full_pool) if p.frequency < attempt.frequency), None)
        hi = next((p for p in full_pool if p.frequency > attempt.frequency), None)
        if lo and hi:
            if nr(lo) or nr(hi):
                return None  # Direct No Response if adjacent is NR
            
            t = (attempt.frequency - lo.frequency) / (hi.frequency - lo.frequency)
            return float(lo.threshold_db + t * (hi.threshold_db - lo.threshold_db))

        # 4. Median
        # Median uses only actual numeric thresholds
        valid_pool = [p for p in full_pool if not nr(p)]
        vals = sorted(float(p.threshold_db) for p in valid_pool)
        if vals:
            return vals[len(vals) // 2]

        return 40.0

    # ------------------------------------------------------------------ #
    #  Patient profile
    # ------------------------------------------------------------------ #

    @dataclass(frozen=True)
    class _Profile:
        sigma_db:           float   # Psychometric slope (~1.0)
        clinical_offset_db: float   # Shift to make 0 dB SL = ~90% prob (~2.2 dB)
        lapse_rate:         float   # Base rate of missed button presses
        guess_rate:         float   # Base false alarm rate
        fatigue_rate:       float   # Fatigue modifier per attempt
        boredom_rate:       float   # Boredom modifier per repeated frequency

    @staticmethod
    def _get_profile(patient) -> "_Profile":
        cfg = ResponseEngine._load_config()
        rng = random.Random(ResponseEngine._patient_seed(patient))

        def u(key: str) -> float:
            return rng.uniform(cfg[key]["min"], cfg[key]["max"])

        return ResponseEngine._Profile(
            sigma_db           = u("sigma_db"),
            clinical_offset_db = u("clinical_offset_db"),
            lapse_rate         = u("lapse_rate"),
            guess_rate         = u("guess_rate"),
            fatigue_rate       = u("fatigue_rate"),
            boredom_rate       = u("boredom_rate"),
        )

    # ------------------------------------------------------------------ #
    #  Config
    # ------------------------------------------------------------------ #

    _DEFAULTS: dict = {
        "sigma_db":           {"min": 0.8, "max": 1.2},
        "clinical_offset_db": {"min": 2.0, "max": 2.5},
        "lapse_rate":         {"min": 0.01, "max": 0.03},
        "guess_rate":         {"min": 0.01, "max": 0.03},
        "fatigue_rate":       {"min": 0.0005, "max": 0.0015},
        "boredom_rate":       {"min": 0.01, "max": 0.02},
    }

    @staticmethod
    def _load_config() -> dict:
        if ResponseEngine._CACHED_CONFIG is not None:
            return ResponseEngine._CACHED_CONFIG

        path = (
            Path(__file__).resolve().parents[1]
            / "config" / "response_engine_params.json"
        )
        cfg = {k: dict(v) for k, v in ResponseEngine._DEFAULTS.items()}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for key in ResponseEngine._DEFAULTS:
                    if key in data and isinstance(data[key], dict):
                        cfg[key] = data[key]
            except Exception:
                pass

        ResponseEngine._CACHED_CONFIG = cfg
        return cfg

    # ------------------------------------------------------------------ #
    #  Seeds
    # ------------------------------------------------------------------ #

    @staticmethod
    def _patient_seed(patient) -> int:
        return (patient.id or 1) * 1_000_003

    @staticmethod
    def _attempt_seed(patient, attempt: AttemptCreateDTO, history_len: int) -> int:
        return (
            ResponseEngine._patient_seed(patient)
            + attempt.session_id * 997
            + history_len * 9_173
            + int(attempt.intensity * 100)
            + attempt.frequency * 13
        )