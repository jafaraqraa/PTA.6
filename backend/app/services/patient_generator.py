from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.patient_repository import PatientRepository
from app.schemas.patient_schema import PatientDTO, EarDTO, AudiogramPointDTO, ALLOWED_FREQUENCIES
from app.models.enums import (
    EarSideEnum,
    TestTypeEnum,
    HearingTypeEnum,
    PatientSourceEnum,
)


MAX_DB = 120.0
# Based on provided clinical criteria: normal is -10 to 20 dB, ABG > 10 dB
NORMAL_THRESHOLD_DB = 20.0
ABG_NORMAL_MAX = 10.0
ABG_CONDUCTIVE_MIN = 10.0
PCA_VARIANCE_TARGET = 0.95
GMM_MAX_COMPONENTS = 4
GMM_MAX_ITER = 200
GMM_TOL = 1e-4
GMM_REG = 1e-3
NR_BIN_SIZE = 10.0
NR_MIN_BIN_COUNT = 3
NR_SMOOTH_ALPHA = 1.0
LOW_FREQS = (125, 250, 500)
MID_FREQS = (750, 1000, 1500, 2000)
HIGH_FREQS = (3000, 4000, 6000, 8000)


class PatientGenerator:
    """
    Data-driven virtual patient generator.
    - Uses real patient audiograms as the empirical distribution.
    - Generates ear-pairs jointly (left+right together) to preserve clinical realism.
    - Learns per pair-type distributions using PCA + GMM.
    """
    _MODEL_CACHE: "_Model | None" = None
    _MODEL_CACHE_KEY: tuple | None = None

    @staticmethod
    async def generate_patientX(db: AsyncSession) -> int | None:
        profiles = await PatientRepository.get_profiles(db)
        dto = PatientGenerator._generate_patient_dto(profiles)
        if dto is None:
            return None
        saved_patient = await PatientRepository.save_patient(db, dto)
        return saved_patient.id
    
    @staticmethod
    async def generate_patient(db: AsyncSession) -> int | None:
        profiles = await PatientRepository.get_profiles(db)
        if not profiles:
            return None
        dto = PatientGenerator._clone_patient_as_synthetic(random.choice(profiles))
        saved_patient = await PatientRepository.save_patient(db, dto)
        return saved_patient.id
    
    @staticmethod
    async def generate_patient_preview(db: AsyncSession) -> PatientDTO | None:
        """
        Build a synthetic patient DTO without saving it.
        Useful to preview generated patients in development/UI.
        """
        profiles = await PatientRepository.get_profiles(db)
        return PatientGenerator._generate_patient_dto(profiles)

    # ----------------------------
    # Internal modeling utilities
    # ----------------------------

    @dataclass
    class _EarStats:
        ear: EarDTO
        hearing_type: HearingTypeEnum
        hearing_profile: dict[int, HearingTypeEnum]
        signature: tuple[str, ...]
        ac_points: dict[int, float]
        bc_points: dict[int, float]
        ac_masked_points: dict[int, float]
        bc_masked_points: dict[int, float]
        ac_nr: dict[int, bool]
        bc_nr: dict[int, bool]
        ac_masked_nr: dict[int, bool]
        bc_masked_nr: dict[int, bool]

    @dataclass
    class _PCA:
        mean: np.ndarray
        scale: np.ndarray
        components: np.ndarray

        def transform(self, x: np.ndarray) -> np.ndarray:
            return ((x - self.mean) / self.scale) @ self.components.T

        def inverse(self, z: np.ndarray) -> np.ndarray:
            return (z @ self.components) * self.scale + self.mean

    @dataclass
    class _GMM:
        weights: np.ndarray
        means: np.ndarray
        covs: np.ndarray

    @dataclass
    class _EarModel:
        freqs_ac: list[int]
        freqs_bc: list[int]
        pca: "PatientGenerator._PCA"
        gmm: "PatientGenerator._GMM"
        nr_prob: dict[TestTypeEnum, dict[int, float]]

    @dataclass
    class _JointModel:
        freqs_left_ac: list[int]
        freqs_left_bc: list[int]
        freqs_right_ac: list[int]
        freqs_right_bc: list[int]
        pca: "PatientGenerator._PCA"
        gmm: "PatientGenerator._GMM"
        nr_prob: dict[EarSideEnum, dict[TestTypeEnum, dict[int, float]]]
        nr_bins: dict[EarSideEnum, dict[TestTypeEnum, dict[int, dict[int, tuple[int, int]]]]]
        nr_global: dict[EarSideEnum, dict[TestTypeEnum, float]]

    @dataclass
    class _PairModel:
        joint_model: "PatientGenerator._JointModel"
        masked_deltas: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, list[float]]]]
        masked_prob: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, float]]]
        masked_nr_prob: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, float]]]

    @dataclass
    class _Model:
        pair_buckets: dict[tuple[tuple[str, ...], tuple[str, ...]], list[tuple["PatientGenerator._EarStats", "PatientGenerator._EarStats"]]]
        pair_models: dict[tuple[tuple[str, ...], tuple[str, ...]], "PatientGenerator._PairModel"]

    @staticmethod
    def _generate_patient_dto(profiles: list[PatientDTO]) -> PatientDTO | None:
        if not profiles:
            return None

        # Use only real patients as the empirical distribution when available.
        real_profiles = [
            p for p in profiles if p.source_type == PatientSourceEnum.REAL
        ]
        if real_profiles:
            profiles = real_profiles

        model = PatientGenerator._get_or_build_model(profiles)
        if not model.pair_buckets:
            return None

        rng = random.Random()
        return PatientGenerator._generate_patient_from_model(model, rng)

    @staticmethod
    def _clone_patient_as_synthetic(patient: PatientDTO) -> PatientDTO:
        return PatientDTO(
            source_type=PatientSourceEnum.SYNTHETIC,
            image_ref=patient.image_ref,
            ears=[
                EarDTO(
                    side=ear.side,
                    hearing_type=ear.hearing_type,
                    hearing_profile=dict(ear.hearing_profile or {}),
                    hearing_tags=list(ear.hearing_tags or []),
                    audiogram_points=[
                        AudiogramPointDTO(
                            test_type=point.test_type,
                            frequency=point.frequency,
                            threshold_db=point.threshold_db,
                            is_no_response=point.is_no_response,
                        )
                        for point in ear.audiogram_points
                    ],
                )
                for ear in patient.ears
            ],
        )

    @staticmethod
    def _generate_patient_from_model(model: "_Model", rng: random.Random) -> PatientDTO:
        pair_key, left_stats, right_stats = PatientGenerator._sample_pair(model, rng)
        pair_model = model.pair_models[pair_key]

        left_ear, right_ear = PatientGenerator._generate_ears_joint(
            pair_model,
            left_stats.hearing_type,
            right_stats.hearing_type,
            left_stats.signature,
            right_stats.signature,
            rng,
        )

        return PatientDTO(
            source_type=PatientSourceEnum.SYNTHETIC,
            ears=[left_ear, right_ear]
        )

    @staticmethod
    def _build_model(profiles: list[PatientDTO]) -> "_Model":
        pair_buckets: dict[tuple[tuple[str, ...], tuple[str, ...]], list[tuple[PatientGenerator._EarStats, PatientGenerator._EarStats]]] = {}

        for patient in profiles:
            left = next((e for e in patient.ears if e.side == EarSideEnum.LEFT), None)
            right = next((e for e in patient.ears if e.side == EarSideEnum.RIGHT), None)
            if not left or not right:
                continue

            left_stats = PatientGenerator._ear_stats(left)
            right_stats = PatientGenerator._ear_stats(right)
            if not left_stats or not right_stats:
                continue

            pair_key = (left_stats.signature, right_stats.signature)
            pair_buckets.setdefault(pair_key, []).append((left_stats, right_stats))

        pair_models: dict[tuple[tuple[str, ...], tuple[str, ...]], PatientGenerator._PairModel] = {}
        for pair_key, pairs in pair_buckets.items():
            pair_models[pair_key] = PatientGenerator._build_pair_model(pairs)

        return PatientGenerator._Model(
            pair_buckets=pair_buckets,
            pair_models=pair_models,
        )

    @staticmethod
    def _profiles_signature(profiles: list[PatientDTO]) -> tuple:
        items: list[tuple] = []
        for p in profiles:
            for ear in p.ears:
                for point in ear.audiogram_points:
                    items.append(
                        (
                            p.id,
                            ear.side.value,
                            point.test_type.value,
                            point.frequency,
                            round(float(point.threshold_db), 1),
                            bool(getattr(point, "is_no_response", False)),
                        )
                    )
        return (len(profiles), len(items), hash(tuple(sorted(items))))

    @staticmethod
    def _get_or_build_model(profiles: list[PatientDTO]) -> "_Model":
        key = PatientGenerator._profiles_signature(profiles)
        if PatientGenerator._MODEL_CACHE is not None and PatientGenerator._MODEL_CACHE_KEY == key:
            return PatientGenerator._MODEL_CACHE
        model = PatientGenerator._build_model(profiles)
        PatientGenerator._MODEL_CACHE = model
        PatientGenerator._MODEL_CACHE_KEY = key
        return model

    @staticmethod
    def _build_pair_model(
        pairs: list[tuple["_EarStats", "_EarStats"]]
    ) -> "_PairModel":
        joint_model = PatientGenerator._build_joint_model(pairs)

        masked_deltas: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, list[float]]]] = {}
        masked_counts: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, int]]] = {}
        total_counts: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, int]]] = {}
        masked_nr_counts: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, int]]] = {}

        for left_stats, right_stats in pairs:
            for stats in (left_stats, right_stats):
                sig = stats.signature
                masked_deltas.setdefault(sig, {})
                masked_counts.setdefault(sig, {})
                total_counts.setdefault(sig, {})
                masked_nr_counts.setdefault(sig, {})

                for masked_type, masked_points, masked_nr, base_points, base_nr in (
                    (TestTypeEnum.AC_MASKED, stats.ac_masked_points, stats.ac_masked_nr, stats.ac_points, stats.ac_nr),
                    (TestTypeEnum.BC_MASKED, stats.bc_masked_points, stats.bc_masked_nr, stats.bc_points, stats.bc_nr),
                ):
                    masked_deltas[sig].setdefault(masked_type, {})
                    masked_counts[sig].setdefault(masked_type, {})
                    total_counts[sig].setdefault(masked_type, {})
                    masked_nr_counts[sig].setdefault(masked_type, {})

                    for freq in base_points.keys():
                        total_counts[sig][masked_type][freq] = (
                            total_counts[sig][masked_type].get(freq, 0) + 1
                        )
                        if freq in masked_points:
                            base_is_nr = base_nr.get(freq, False)
                            masked_is_nr = masked_nr.get(freq, False)
                            if not base_is_nr and not masked_is_nr:
                                delta = masked_points[freq] - base_points[freq]
                                masked_deltas[sig][masked_type].setdefault(freq, []).append(delta)
                            masked_counts[sig][masked_type][freq] = (
                                masked_counts[sig][masked_type].get(freq, 0) + 1
                            )
                            if masked_is_nr:
                                masked_nr_counts[sig][masked_type][freq] = (
                                    masked_nr_counts[sig][masked_type].get(freq, 0) + 1
                                )

        masked_prob: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, float]]] = {}
        masked_nr_prob: dict[tuple[str, ...], dict[TestTypeEnum, dict[int, float]]] = {}
        for sig, by_type in total_counts.items():
            masked_prob.setdefault(sig, {})
            masked_nr_prob.setdefault(sig, {})
            for test_type, freq_counts in by_type.items():
                masked_prob[sig].setdefault(test_type, {})
                masked_nr_prob[sig].setdefault(test_type, {})
                for freq, total in freq_counts.items():
                    masked = masked_counts.get(sig, {}).get(test_type, {}).get(freq, 0)
                    masked_prob[sig][test_type][freq] = masked / total if total else 0.0
                    masked_nr = masked_nr_counts.get(sig, {}).get(test_type, {}).get(freq, 0)
                    masked_nr_prob[sig][test_type][freq] = masked_nr / masked if masked else 0.0

        return PatientGenerator._PairModel(
            joint_model=joint_model,
            masked_deltas=masked_deltas,
            masked_prob=masked_prob,
            masked_nr_prob=masked_nr_prob,
        )

    @staticmethod
    def _build_joint_model(
        pairs: list[tuple["_EarStats", "_EarStats"]]
    ) -> "_JointModel":
        freqs_left_ac = sorted({f for l, _ in pairs for f in l.ac_points.keys()} or ALLOWED_FREQUENCIES)
        freqs_left_bc = sorted({f for l, _ in pairs for f in l.bc_points.keys()} or ALLOWED_FREQUENCIES)
        freqs_right_ac = sorted({f for _, r in pairs for f in r.ac_points.keys()} or ALLOWED_FREQUENCIES)
        freqs_right_bc = sorted({f for _, r in pairs for f in r.bc_points.keys()} or ALLOWED_FREQUENCIES)

        nr_prob: dict[EarSideEnum, dict[TestTypeEnum, dict[int, float]]] = {
            EarSideEnum.LEFT: {TestTypeEnum.AC: {}, TestTypeEnum.BC: {}},
            EarSideEnum.RIGHT: {TestTypeEnum.AC: {}, TestTypeEnum.BC: {}},
        }
        nr_bins: dict[EarSideEnum, dict[TestTypeEnum, dict[int, dict[int, tuple[int, int]]]]] = {
            EarSideEnum.LEFT: {TestTypeEnum.AC: {}, TestTypeEnum.BC: {}},
            EarSideEnum.RIGHT: {TestTypeEnum.AC: {}, TestTypeEnum.BC: {}},
        }
        nr_global_counts: dict[EarSideEnum, dict[TestTypeEnum, list[int]]] = {
            EarSideEnum.LEFT: {TestTypeEnum.AC: [0, 0], TestTypeEnum.BC: [0, 0]},
            EarSideEnum.RIGHT: {TestTypeEnum.AC: [0, 0], TestTypeEnum.BC: [0, 0]},
        }

        data_rows: list[list[float]] = []
        for left_stats, right_stats in pairs:
            row: list[float] = []
            for freq in freqs_left_ac:
                if freq in left_stats.ac_points:
                    val = left_stats.ac_points[freq]
                    if left_stats.ac_nr.get(freq, False):
                        val = MAX_DB
                    row.append(float(val))
                else:
                    row.append(float("nan"))
            for freq in freqs_left_bc:
                if freq in left_stats.bc_points:
                    val = left_stats.bc_points[freq]
                    if left_stats.bc_nr.get(freq, False):
                        val = MAX_DB
                    row.append(float(val))
                else:
                    row.append(float("nan"))
            for freq in freqs_right_ac:
                if freq in right_stats.ac_points:
                    val = right_stats.ac_points[freq]
                    if right_stats.ac_nr.get(freq, False):
                        val = MAX_DB
                    row.append(float(val))
                else:
                    row.append(float("nan"))
            for freq in freqs_right_bc:
                if freq in right_stats.bc_points:
                    val = right_stats.bc_points[freq]
                    if right_stats.bc_nr.get(freq, False):
                        val = MAX_DB
                    row.append(float(val))
                else:
                    row.append(float("nan"))
            data_rows.append(row)

        data = np.array(data_rows, dtype=float)
        if data.size == 0:
            data = np.zeros((1, len(freqs_left_ac) + len(freqs_left_bc) + len(freqs_right_ac) + len(freqs_right_bc)), dtype=float)
        col_means = np.nanmean(data, axis=0)
        col_means = np.where(np.isnan(col_means), 0.0, col_means)
        inds = np.where(np.isnan(data))
        data[inds] = np.take(col_means, inds[1])

        # NR probabilities per side/freq for AC/BC
        for freq in freqs_left_ac:
            total = sum(1 for l, _ in pairs if freq in l.ac_points)
            nr = sum(1 for l, _ in pairs if l.ac_nr.get(freq, False))
            nr_prob[EarSideEnum.LEFT][TestTypeEnum.AC][freq] = (nr / total) if total else 0.0
        for freq in freqs_left_bc:
            total = sum(1 for l, _ in pairs if freq in l.bc_points)
            nr = sum(1 for l, _ in pairs if l.bc_nr.get(freq, False))
            nr_prob[EarSideEnum.LEFT][TestTypeEnum.BC][freq] = (nr / total) if total else 0.0
        for freq in freqs_right_ac:
            total = sum(1 for _, r in pairs if freq in r.ac_points)
            nr = sum(1 for _, r in pairs if r.ac_nr.get(freq, False))
            nr_prob[EarSideEnum.RIGHT][TestTypeEnum.AC][freq] = (nr / total) if total else 0.0
        for freq in freqs_right_bc:
            total = sum(1 for _, r in pairs if freq in r.bc_points)
            nr = sum(1 for _, r in pairs if r.bc_nr.get(freq, False))
            nr_prob[EarSideEnum.RIGHT][TestTypeEnum.BC][freq] = (nr / total) if total else 0.0

        # NR conditional bins per side/test/freq (count, nr_count)
        for left_stats, right_stats in pairs:
            for side, stats in ((EarSideEnum.LEFT, left_stats), (EarSideEnum.RIGHT, right_stats)):
                for test_type, points, nr_map in (
                    (TestTypeEnum.AC, stats.ac_points, stats.ac_nr),
                    (TestTypeEnum.BC, stats.bc_points, stats.bc_nr),
                ):
                    for freq, val in points.items():
                        bin_id = int(math.floor(float(val) / NR_BIN_SIZE))
                        freq_bins = nr_bins[side][test_type].setdefault(freq, {})
                        count, nr_count = freq_bins.get(bin_id, (0, 0))
                        count += 1
                        if nr_map.get(freq, False):
                            nr_count += 1
                        freq_bins[bin_id] = (count, nr_count)

                        nr_global_counts[side][test_type][0] += 1
                        if nr_map.get(freq, False):
                            nr_global_counts[side][test_type][1] += 1

        nr_global: dict[EarSideEnum, dict[TestTypeEnum, float]] = {
            EarSideEnum.LEFT: {TestTypeEnum.AC: 0.0, TestTypeEnum.BC: 0.0},
            EarSideEnum.RIGHT: {TestTypeEnum.AC: 0.0, TestTypeEnum.BC: 0.0},
        }
        for side in (EarSideEnum.LEFT, EarSideEnum.RIGHT):
            for test_type in (TestTypeEnum.AC, TestTypeEnum.BC):
                total, nr = nr_global_counts[side][test_type]
                nr_global[side][test_type] = (nr / total) if total else 0.0

        pca = PatientGenerator._fit_pca(data)
        z = pca.transform(data)
        gmm = PatientGenerator._fit_gmm(z)

        return PatientGenerator._JointModel(
            freqs_left_ac=freqs_left_ac,
            freqs_left_bc=freqs_left_bc,
            freqs_right_ac=freqs_right_ac,
            freqs_right_bc=freqs_right_bc,
            pca=pca,
            gmm=gmm,
            nr_prob=nr_prob,
            nr_bins=nr_bins,
            nr_global=nr_global,
        )

    @staticmethod
    def _build_ear_model(ears: list["_EarStats"]) -> "_EarModel":
        freqs_ac = sorted({f for e in ears for f in e.ac_points.keys()} or ALLOWED_FREQUENCIES)
        freqs_bc = sorted({f for e in ears for f in e.bc_points.keys()} or ALLOWED_FREQUENCIES)

        nr_prob: dict[TestTypeEnum, dict[int, float]] = {
            TestTypeEnum.AC: {},
            TestTypeEnum.BC: {},
        }

        data_rows: list[list[float]] = []
        for stats in ears:
            row: list[float] = []
            for freq in freqs_ac:
                if freq in stats.ac_points:
                    val = stats.ac_points[freq]
                    if stats.ac_nr.get(freq, False):
                        val = MAX_DB
                    row.append(float(val))
                else:
                    row.append(float("nan"))
            for freq in freqs_bc:
                if freq in stats.bc_points:
                    val = stats.bc_points[freq]
                    if stats.bc_nr.get(freq, False):
                        val = MAX_DB
                    row.append(float(val))
                else:
                    row.append(float("nan"))
            data_rows.append(row)

        data = np.array(data_rows, dtype=float)

        # Impute missing values with per-frequency mean (computed on available values)
        if data.size == 0:
            data = np.zeros((1, len(freqs_ac) + len(freqs_bc)), dtype=float)
        col_means = np.nanmean(data, axis=0)
        # If a column is entirely NaN, fall back to 0
        col_means = np.where(np.isnan(col_means), 0.0, col_means)
        inds = np.where(np.isnan(data))
        data[inds] = np.take(col_means, inds[1])

        # NR probabilities per freq for AC/BC
        for freq in freqs_ac:
            total = sum(1 for e in ears if freq in e.ac_points)
            nr = sum(1 for e in ears if e.ac_nr.get(freq, False))
            nr_prob[TestTypeEnum.AC][freq] = (nr / total) if total else 0.0
        for freq in freqs_bc:
            total = sum(1 for e in ears if freq in e.bc_points)
            nr = sum(1 for e in ears if e.bc_nr.get(freq, False))
            nr_prob[TestTypeEnum.BC][freq] = (nr / total) if total else 0.0

        pca = PatientGenerator._fit_pca(data)
        z = pca.transform(data)
        gmm = PatientGenerator._fit_gmm(z)

        return PatientGenerator._EarModel(
            freqs_ac=freqs_ac,
            freqs_bc=freqs_bc,
            pca=pca,
            gmm=gmm,
            nr_prob=nr_prob,
        )

    @staticmethod
    def _fit_pca(data: np.ndarray) -> "_PCA":
        mean = data.mean(axis=0)
        scale = data.std(axis=0, ddof=0)
        scale = np.where(scale == 0, 1.0, scale)
        centered = (data - mean) / scale
        if centered.shape[0] <= 1:
            components = np.eye(centered.shape[1])[:1]
            return PatientGenerator._PCA(mean=mean, scale=scale, components=components)

        u, s, vt = np.linalg.svd(centered, full_matrices=False)
        var = (s ** 2) / max(centered.shape[0] - 1, 1)
        total_var = var.sum()
        if total_var == 0:
            components = np.eye(centered.shape[1])[:1]
            return PatientGenerator._PCA(mean=mean, scale=scale, components=components)

        explained = var / total_var
        cum = np.cumsum(explained)
        k = int(np.searchsorted(cum, PCA_VARIANCE_TARGET) + 1)
        k = max(2, min(k, vt.shape[0]))
        components = vt[:k]
        return PatientGenerator._PCA(mean=mean, scale=scale, components=components)

    @staticmethod
    def _fit_gmm(z: np.ndarray) -> "_GMM":
        n, d = z.shape
        if n <= 1:
            return PatientGenerator._GMM(
                weights=np.array([1.0]),
                means=np.zeros((1, d)),
                covs=np.array([np.eye(d)])
            )

        k_max = min(GMM_MAX_COMPONENTS, n)
        best_gmm: PatientGenerator._GMM | None = None
        best_bic = float("inf")

        for k in range(1, k_max + 1):
            gmm = PatientGenerator._fit_gmm_fixed_k(z, k)
            ll = PatientGenerator._gmm_log_likelihood(z, gmm)
            bic = PatientGenerator._gmm_bic(ll, n, d, k)
            if bic < best_bic:
                best_bic = bic
                best_gmm = gmm

        return best_gmm if best_gmm is not None else PatientGenerator._fit_gmm_fixed_k(z, 1)

    @staticmethod
    def _fit_gmm_fixed_k(z: np.ndarray, k: int) -> "_GMM":
        n, d = z.shape
        rng = np.random.default_rng()

        # Initialize
        indices = rng.choice(n, size=k, replace=False) if n >= k else rng.choice(n, size=k, replace=True)
        means = z[indices].copy()
        covs = np.array([np.cov(z.T) + np.eye(d) * GMM_REG for _ in range(k)])
        weights = np.ones(k) / k

        prev_ll = None
        for _ in range(GMM_MAX_ITER):
            # E-step
            log_resp = np.zeros((n, k))
            for j in range(k):
                log_resp[:, j] = math.log(weights[j] + 1e-12) + PatientGenerator._log_gaussian(z, means[j], covs[j])
            log_norm = PatientGenerator._logsumexp(log_resp, axis=1)
            resp = np.exp(log_resp - log_norm[:, None])

            # M-step
            nk = resp.sum(axis=0) + 1e-12
            weights = nk / n
            means = (resp.T @ z) / nk[:, None]

            for j in range(k):
                diff = z - means[j]
                cov = (resp[:, j][:, None] * diff).T @ diff / nk[j]
                cov += np.eye(d) * GMM_REG
                covs[j] = cov

            ll = log_norm.sum()
            if prev_ll is not None and abs(ll - prev_ll) < GMM_TOL:
                break
            prev_ll = ll

        return PatientGenerator._GMM(weights=weights, means=means, covs=covs)

    @staticmethod
    def _gmm_log_likelihood(z: np.ndarray, gmm: "_GMM") -> float:
        n, _ = z.shape
        k = gmm.weights.shape[0]
        log_resp = np.zeros((n, k))
        for j in range(k):
            log_resp[:, j] = math.log(gmm.weights[j] + 1e-12) + PatientGenerator._log_gaussian(z, gmm.means[j], gmm.covs[j])
        log_norm = PatientGenerator._logsumexp(log_resp, axis=1)
        return float(log_norm.sum())

    @staticmethod
    def _gmm_bic(log_likelihood: float, n: int, d: int, k: int) -> float:
        params = (k - 1) + k * d + k * (d * (d + 1) / 2)
        return -2 * log_likelihood + params * math.log(max(n, 1))

    @staticmethod
    def _log_gaussian(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
        d = x.shape[1]
        sign, logdet = np.linalg.slogdet(cov)
        if sign <= 0:
            cov = cov + np.eye(d) * GMM_REG
            sign, logdet = np.linalg.slogdet(cov)
        inv = np.linalg.inv(cov)
        diff = x - mean
        quad = np.einsum("ij,ij->i", diff @ inv, diff)
        return -0.5 * (d * math.log(2 * math.pi) + logdet + quad)

    @staticmethod
    def _logsumexp(a: np.ndarray, axis: int = 0) -> np.ndarray:
        a_max = np.max(a, axis=axis, keepdims=True)
        res = a_max + np.log(np.sum(np.exp(a - a_max), axis=axis, keepdims=True))
        return res.squeeze(axis=axis)

    @staticmethod
    def _sample_gmm(gmm: "_GMM", rng: np.random.Generator, n: int = 1) -> np.ndarray:
        k = gmm.weights.shape[0]
        comps = rng.choice(k, size=n, p=gmm.weights)
        samples = []
        for c in comps:
            samples.append(rng.multivariate_normal(gmm.means[c], gmm.covs[c]))
        return np.array(samples)

    @staticmethod
    def _ear_stats(ear: EarDTO) -> "_EarStats" | None:
        ac_points, ac_nr = PatientGenerator._extract_points(ear, TestTypeEnum.AC)
        bc_points, bc_nr = PatientGenerator._extract_points(ear, TestTypeEnum.BC)
        if not ac_points or not bc_points:
            return None

        ac_masked_points, ac_masked_nr = PatientGenerator._extract_points(ear, TestTypeEnum.AC_MASKED)
        bc_masked_points, bc_masked_nr = PatientGenerator._extract_points(ear, TestTypeEnum.BC_MASKED)
        hearing_profile = ear.hearing_profile or PatientGenerator._infer_hearing_profile(ac_points, bc_points, ac_nr, bc_nr)
        hearing_type = ear.hearing_type or PatientGenerator._summarize_hearing_type(hearing_profile)
        signature = PatientGenerator._profile_signature(hearing_profile)

        return PatientGenerator._EarStats(
            ear=ear,
            hearing_type=hearing_type,
            hearing_profile=hearing_profile,
            signature=signature,
            ac_points=ac_points,
            bc_points=bc_points,
            ac_masked_points=ac_masked_points,
            bc_masked_points=bc_masked_points,
            ac_nr=ac_nr,
            bc_nr=bc_nr,
            ac_masked_nr=ac_masked_nr,
            bc_masked_nr=bc_masked_nr,
        )

    @staticmethod
    def _extract_points(ear: EarDTO, test_type: TestTypeEnum) -> tuple[dict[int, float], dict[int, bool]]:
        # For AC/BC clinical inference, prefer masked thresholds at the same
        # frequency when available; otherwise fall back to the unmasked value.
        if test_type == TestTypeEnum.AC:
            masked_type = TestTypeEnum.AC_MASKED
        elif test_type == TestTypeEnum.BC:
            masked_type = TestTypeEnum.BC_MASKED
        else:
            masked_type = None

        points: dict[int, float] = {}
        nr: dict[int, bool] = {}
        for p in ear.audiogram_points:
            if p.test_type != test_type:
                continue
            points[p.frequency] = float(p.threshold_db)
            nr[p.frequency] = bool(getattr(p, "is_no_response", False))

        if masked_type is None:
            return points, nr

        for p in ear.audiogram_points:
            if p.test_type != masked_type:
                continue
            points[p.frequency] = float(p.threshold_db)
            nr[p.frequency] = bool(getattr(p, "is_no_response", False))

        return points, nr

    @staticmethod
    def _infer_hearing_profile(
        ac_points: dict[int, float],
        bc_points: dict[int, float],
        ac_nr: dict[int, bool] | None = None,
        bc_nr: dict[int, bool] | None = None,
    ) -> dict[int, HearingTypeEnum]:
        profile: dict[int, HearingTypeEnum] = {}
        for freq in sorted(ALLOWED_FREQUENCIES):
            if freq not in ac_points or freq not in bc_points:
                continue
            if ac_nr and ac_nr.get(freq, False):
                continue
            if bc_nr and bc_nr.get(freq, False):
                continue
            ac_val = ac_points[freq]
            bc_val = bc_points[freq]
            abg = ac_val - bc_val

            if ac_val <= NORMAL_THRESHOLD_DB and bc_val <= NORMAL_THRESHOLD_DB and abg < ABG_NORMAL_MAX:
                profile[freq] = HearingTypeEnum.NORMAL
            elif bc_val <= NORMAL_THRESHOLD_DB and abg >= ABG_CONDUCTIVE_MIN:
                profile[freq] = HearingTypeEnum.CONDUCTIVE
            elif bc_val > NORMAL_THRESHOLD_DB and abg < ABG_NORMAL_MAX:
                profile[freq] = HearingTypeEnum.SENSORINEURAL
            else:
                profile[freq] = HearingTypeEnum.MIXED
        return profile

    @staticmethod
    def _profile_signature(profile: dict[int, HearingTypeEnum]) -> tuple[str, ...]:
        def band_type(freqs: Iterable[int]) -> str:
            band_profile = {f: profile[f] for f in freqs if f in profile}
            if not band_profile:
                return "Unknown"
            return PatientGenerator._summarize_hearing_type(band_profile).value

        return (
            band_type(LOW_FREQS),
            band_type(MID_FREQS),
            band_type(HIGH_FREQS),
        )

    @staticmethod
    def _summarize_hearing_type(profile: dict[int, HearingTypeEnum]) -> HearingTypeEnum:
        if not profile:
            return HearingTypeEnum.NORMAL
        types_present = {t for t in profile.values() if t is not None}
        if not types_present or types_present == {HearingTypeEnum.NORMAL}:
            return HearingTypeEnum.NORMAL
        if types_present <= {HearingTypeEnum.SENSORINEURAL, HearingTypeEnum.NORMAL}:
            return HearingTypeEnum.SENSORINEURAL
        if types_present <= {HearingTypeEnum.CONDUCTIVE, HearingTypeEnum.NORMAL}:
            return HearingTypeEnum.CONDUCTIVE
        if types_present == {HearingTypeEnum.MIXED}:
            return HearingTypeEnum.MIXED
        return HearingTypeEnum.MIXED

    @staticmethod
    def _infer_hearing_tags(
        ac_points: dict[int, float],
        bc_points: dict[int, float],
        ac_nr: dict[int, bool] | None,
        bc_nr: dict[int, bool] | None,
        profile: dict[int, HearingTypeEnum],
    ) -> list[str]:
        tags: list[str] = []

        def band_avg(freqs: Iterable[int]) -> float | None:
            vals = [
                ac_points[f]
                for f in freqs
                if f in ac_points and not (ac_nr and ac_nr.get(f, False))
            ]
            if not vals:
                return None
            return sum(vals) / len(vals)

        low_avg = band_avg(LOW_FREQS)
        mid_avg = band_avg(MID_FREQS)
        high_avg = band_avg(HIGH_FREQS)

        if low_avg is not None and low_avg > NORMAL_THRESHOLD_DB:
            tags.append("lf_loss")
        if high_avg is not None and high_avg > NORMAL_THRESHOLD_DB:
            tags.append("hf_loss")

        if low_avg is not None and high_avg is not None:
            if abs(high_avg - low_avg) <= 10 and max(low_avg, high_avg) > NORMAL_THRESHOLD_DB:
                tags.append("flat")
            elif high_avg - low_avg >= 15:
                tags.append("sloping")

        if 4000 in ac_points and 2000 in ac_points and 6000 in ac_points:
            if ac_nr and (ac_nr.get(4000, False) or ac_nr.get(2000, False) or ac_nr.get(6000, False)):
                pass
            else:
                notch_ref = (ac_points[2000] + ac_points[6000]) / 2
                if ac_points[4000] - notch_ref >= 15:
                    tags.append("notch_4k")

        if ac_points:
            worst_vals = [
                v for f, v in ac_points.items()
                if not (ac_nr and ac_nr.get(f, False))
            ]
            worst = max(worst_vals) if worst_vals else None
        else:
            worst = None

        if worst is not None:
            if 26 <= worst <= 40:
                tags.append("mild")
            elif 41 <= worst <= 55:
                tags.append("moderate")
            elif 56 <= worst <= 70:
                tags.extend(["moderate", "severe"])
            elif 71 <= worst <= 90:
                tags.append("severe")
            elif worst > 90:
                tags.append("profound")

        # Ensure uniqueness and stable order
        return list(dict.fromkeys(tags))

    @staticmethod
    def _infer_hearing_type(ac_points: dict[int, float], bc_points: dict[int, float]) -> HearingTypeEnum:
        # PTA using 500/1000/2000 when available.
        def pta(points: dict[int, float]) -> float:
            core = [f for f in (500, 1000, 2000) if f in points]
            if not core:
                vals = list(points.values())
                return sum(vals) / len(vals)
            vals = [points[f] for f in core]
            return sum(vals) / len(vals)

        ac_pta = pta(ac_points)
        bc_pta = pta(bc_points)
        abg = ac_pta - bc_pta

        if ac_pta <= NORMAL_THRESHOLD_DB and bc_pta <= NORMAL_THRESHOLD_DB and abg < ABG_NORMAL_MAX:
            return HearingTypeEnum.NORMAL
        if bc_pta <= NORMAL_THRESHOLD_DB and abg >= ABG_CONDUCTIVE_MIN:
            return HearingTypeEnum.CONDUCTIVE
        if bc_pta > NORMAL_THRESHOLD_DB and abg < ABG_NORMAL_MAX:
            return HearingTypeEnum.SENSORINEURAL
        return HearingTypeEnum.MIXED

    @staticmethod
    def _mean_and_tilt(points: dict[int, float]) -> tuple[float, float]:
        if not points:
            return 0.0, 0.0
        freqs = sorted(points)
        vals = [points[f] for f in freqs]
        mean = sum(vals) / len(vals)
        if len(freqs) < 2:
            return mean, 0.0

        xs = [math.log2(float(f)) for f in freqs]
        x_mean = sum(xs) / len(xs)
        y_mean = mean
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, vals))
        den = sum((x - x_mean) ** 2 for x in xs)
        tilt = num / den if den else 0.0
        return mean, tilt

    @staticmethod
    def _sample_pair(model: "_Model", rng: random.Random) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], "_EarStats", "_EarStats"]:
        # Randomly choose a pair type uniformly, then sample from all patients in that pair type.
        buckets = list(model.pair_buckets.items())
        pair_key, bucket = rng.choice(buckets)
        left_stats, right_stats = rng.choice(bucket)
        return pair_key, left_stats, right_stats

    @staticmethod
    def _generate_ears_joint(
        model: "_PairModel",
        left_type: HearingTypeEnum,
        right_type: HearingTypeEnum,
        left_signature: tuple[str, ...],
        right_signature: tuple[str, ...],
        rng: random.Random
    ) -> tuple[EarDTO, EarDTO]:
        joint = model.joint_model

        np_rng = np.random.default_rng(int(rng.random() * 1_000_000_000))
        z = PatientGenerator._sample_gmm(joint.gmm, np_rng, n=1)
        vec = joint.pca.inverse(z)[0]

        left_ac: dict[int, float] = {}
        left_bc: dict[int, float] = {}
        right_ac: dict[int, float] = {}
        right_bc: dict[int, float] = {}
        left_ac_nr: dict[int, bool] = {}
        left_bc_nr: dict[int, bool] = {}
        right_ac_nr: dict[int, bool] = {}
        right_bc_nr: dict[int, bool] = {}

        idx = 0
        for freq in joint.freqs_left_ac:
            val = PatientGenerator._clamp_db(float(vec[idx]))
            is_nr = rng.random() < PatientGenerator._nr_prob_from_bins(
                joint, EarSideEnum.LEFT, TestTypeEnum.AC, freq, val
            )
            if is_nr:
                val = MAX_DB
            left_ac[freq] = val
            left_ac_nr[freq] = is_nr
            idx += 1
        for freq in joint.freqs_left_bc:
            val = PatientGenerator._clamp_db(float(vec[idx]))
            is_nr = rng.random() < PatientGenerator._nr_prob_from_bins(
                joint, EarSideEnum.LEFT, TestTypeEnum.BC, freq, val
            )
            if is_nr:
                val = MAX_DB
            left_bc[freq] = val
            left_bc_nr[freq] = is_nr
            idx += 1
        for freq in joint.freqs_right_ac:
            val = PatientGenerator._clamp_db(float(vec[idx]))
            is_nr = rng.random() < PatientGenerator._nr_prob_from_bins(
                joint, EarSideEnum.RIGHT, TestTypeEnum.AC, freq, val
            )
            if is_nr:
                val = MAX_DB
            right_ac[freq] = val
            right_ac_nr[freq] = is_nr
            idx += 1
        for freq in joint.freqs_right_bc:
            val = PatientGenerator._clamp_db(float(vec[idx]))
            is_nr = rng.random() < PatientGenerator._nr_prob_from_bins(
                joint, EarSideEnum.RIGHT, TestTypeEnum.BC, freq, val
            )
            if is_nr:
                val = MAX_DB
            right_bc[freq] = val
            right_bc_nr[freq] = is_nr
            idx += 1

        PatientGenerator._enforce_constraints_per_frequency(
            left_signature,
            left_type,
            left_ac,
            left_bc,
            left_ac_nr,
            left_bc_nr,
            rng,
        )
        PatientGenerator._enforce_constraints_per_frequency(
            right_signature,
            right_type,
            right_ac,
            right_bc,
            right_ac_nr,
            right_bc_nr,
            rng,
        )

        left_points: list[AudiogramPointDTO] = []
        for freq, value in left_ac.items():
            left_points.append(
                AudiogramPointDTO(
                    test_type=TestTypeEnum.AC,
                    frequency=freq,
                    threshold_db=PatientGenerator._clamp_db(value),
                    is_no_response=left_ac_nr.get(freq, False),
                )
            )
        for freq, value in left_bc.items():
            left_points.append(
                AudiogramPointDTO(
                    test_type=TestTypeEnum.BC,
                    frequency=freq,
                    threshold_db=PatientGenerator._clamp_db(value),
                    is_no_response=left_bc_nr.get(freq, False),
                )
            )

        right_points: list[AudiogramPointDTO] = []
        for freq, value in right_ac.items():
            right_points.append(
                AudiogramPointDTO(
                    test_type=TestTypeEnum.AC,
                    frequency=freq,
                    threshold_db=PatientGenerator._clamp_db(value),
                    is_no_response=right_ac_nr.get(freq, False),
                )
            )
        for freq, value in right_bc.items():
            right_points.append(
                AudiogramPointDTO(
                    test_type=TestTypeEnum.BC,
                    frequency=freq,
                    threshold_db=PatientGenerator._clamp_db(value),
                    is_no_response=right_bc_nr.get(freq, False),
                )
            )

        left_points.extend(
            PatientGenerator._generate_masked_points(
                model,
                left_signature,
                left_ac,
                left_bc,
                left_ac_nr,
                left_bc_nr,
                rng
            )
        )
        right_points.extend(
            PatientGenerator._generate_masked_points(
                model,
                right_signature,
                right_ac,
                right_bc,
                right_ac_nr,
                right_bc_nr,
                rng
            )
        )

        left_profile = PatientGenerator._infer_hearing_profile(left_ac, left_bc, left_ac_nr, left_bc_nr)
        right_profile = PatientGenerator._infer_hearing_profile(right_ac, right_bc, right_ac_nr, right_bc_nr)
        left_tags = PatientGenerator._infer_hearing_tags(left_ac, left_bc, left_ac_nr, left_bc_nr, left_profile)
        right_tags = PatientGenerator._infer_hearing_tags(right_ac, right_bc, right_ac_nr, right_bc_nr, right_profile)

        left_ear = EarDTO(
            side=EarSideEnum.LEFT,
            hearing_type=PatientGenerator._summarize_hearing_type(left_profile),
            hearing_profile=left_profile,
            hearing_tags=left_tags,
            audiogram_points=left_points,
        )
        right_ear = EarDTO(
            side=EarSideEnum.RIGHT,
            hearing_type=PatientGenerator._summarize_hearing_type(right_profile),
            hearing_profile=right_profile,
            hearing_tags=right_tags,
            audiogram_points=right_points,
        )

        return left_ear, right_ear

    @staticmethod
    def _nr_prob_from_bins(
        joint: "_JointModel",
        side: EarSideEnum,
        test_type: TestTypeEnum,
        freq: int,
        value_db: float
    ) -> float:
        bin_id = int(math.floor(float(value_db) / NR_BIN_SIZE))
        freq_bins = joint.nr_bins.get(side, {}).get(test_type, {}).get(freq, {})
        if bin_id in freq_bins:
            count, nr_count = freq_bins[bin_id]
            if count >= NR_MIN_BIN_COUNT:
                return (nr_count + NR_SMOOTH_ALPHA) / (count + 2 * NR_SMOOTH_ALPHA)

        # Fallback to per-frequency unconditional NR prob
        freq_prob = joint.nr_prob.get(side, {}).get(test_type, {}).get(freq)
        if freq_prob is not None:
            return freq_prob

        # Final fallback to global per side/test
        return joint.nr_global.get(side, {}).get(test_type, 0.0)

    @staticmethod
    def _enforce_constraints(
        hearing_type: HearingTypeEnum,
        ac: dict[int, float],
        bc: dict[int, float],
        ac_nr: dict[int, bool],
        bc_nr: dict[int, bool],
        rng: random.Random
    ) -> None:
        for freq in list(ac.keys()):
            if ac_nr.get(freq, False) or bc_nr.get(freq, False):
                # Keep NR points as-is
                continue

            ac_val = ac.get(freq)
            bc_val = bc.get(freq)
            if bc_val is None:
                continue

            abg = ac_val - bc_val

            if hearing_type == HearingTypeEnum.NORMAL:
                bc_val = min(bc_val, NORMAL_THRESHOLD_DB)
                ac_val = min(ac_val, NORMAL_THRESHOLD_DB)
                if abg > ABG_NORMAL_MAX:
                    ac_val = bc_val + rng.uniform(0, ABG_NORMAL_MAX)
            elif hearing_type == HearingTypeEnum.SENSORINEURAL:
                if abg > ABG_NORMAL_MAX:
                    ac_val = bc_val + rng.uniform(0, ABG_NORMAL_MAX)
                if bc_val - ac_val > 5:
                    bc_val = ac_val + rng.uniform(0, 5)
            elif hearing_type == HearingTypeEnum.CONDUCTIVE:
                if bc_val > NORMAL_THRESHOLD_DB:
                    bc_val = rng.uniform(10, NORMAL_THRESHOLD_DB)
                if abg < ABG_CONDUCTIVE_MIN:
                    ac_val = bc_val + rng.uniform(ABG_CONDUCTIVE_MIN, 30)
            elif hearing_type == HearingTypeEnum.MIXED:
                if bc_val <= NORMAL_THRESHOLD_DB:
                    bc_val = rng.uniform(30, 50)
                if abg < ABG_CONDUCTIVE_MIN:
                    ac_val = bc_val + rng.uniform(ABG_CONDUCTIVE_MIN, 40)

            # Ensure AC is not unrealistically better than BC
            if ac_val + 5 < bc_val:
                ac_val = bc_val + rng.uniform(0, 5)

            ac[freq] = PatientGenerator._clamp_db(ac_val)
            bc[freq] = PatientGenerator._clamp_db(bc_val)

    @staticmethod
    def _enforce_constraints_per_frequency(
        signature: tuple[str, ...],
        fallback_type: HearingTypeEnum,
        ac: dict[int, float],
        bc: dict[int, float],
        ac_nr: dict[int, bool],
        bc_nr: dict[int, bool],
        rng: random.Random,
    ) -> None:
        def band_label(freq: int) -> str:
            if freq in LOW_FREQS:
                return signature[0] if len(signature) > 0 else "Unknown"
            if freq in MID_FREQS:
                return signature[1] if len(signature) > 1 else "Unknown"
            if freq in HIGH_FREQS:
                return signature[2] if len(signature) > 2 else "Unknown"
            return "Unknown"

        freqs = sorted(ALLOWED_FREQUENCIES)
        for freq in freqs:
            if freq not in ac or freq not in bc:
                continue
            if ac_nr.get(freq, False) or bc_nr.get(freq, False):
                continue
            sig_val = band_label(freq)
            try:
                target_type = HearingTypeEnum(sig_val)
            except Exception:
                target_type = fallback_type

            ac_val = ac.get(freq)
            bc_val = bc.get(freq)
            if ac_val is None or bc_val is None:
                continue
            abg = ac_val - bc_val

            if target_type == HearingTypeEnum.NORMAL:
                bc_val = min(bc_val, NORMAL_THRESHOLD_DB)
                ac_val = min(ac_val, NORMAL_THRESHOLD_DB)
                if abg > ABG_NORMAL_MAX:
                    ac_val = bc_val + rng.uniform(0, ABG_NORMAL_MAX)
            elif target_type == HearingTypeEnum.SENSORINEURAL:
                if bc_val <= NORMAL_THRESHOLD_DB:
                    bc_val = rng.uniform(NORMAL_THRESHOLD_DB + 1, max(NORMAL_THRESHOLD_DB + 1, ac_val))
                if abg > ABG_NORMAL_MAX:
                    ac_val = bc_val + rng.uniform(0, ABG_NORMAL_MAX)
            elif target_type == HearingTypeEnum.CONDUCTIVE:
                if bc_val > NORMAL_THRESHOLD_DB:
                    bc_val = rng.uniform(10, NORMAL_THRESHOLD_DB)
                if abg < ABG_CONDUCTIVE_MIN:
                    ac_val = bc_val + rng.uniform(ABG_CONDUCTIVE_MIN, 30)
            elif target_type == HearingTypeEnum.MIXED:
                if bc_val <= NORMAL_THRESHOLD_DB:
                    bc_val = rng.uniform(30, 50)
                if abg < ABG_CONDUCTIVE_MIN:
                    ac_val = bc_val + rng.uniform(ABG_CONDUCTIVE_MIN, 40)

            if ac_val + 5 < bc_val:
                ac_val = bc_val + rng.uniform(0, 5)

            ac[freq] = PatientGenerator._clamp_db(ac_val)
            bc[freq] = PatientGenerator._clamp_db(bc_val)

    @staticmethod
    def _clamp_db(value: float) -> float:
        return max(-10.0, min(MAX_DB, float(value)))

    @staticmethod
    def _generate_masked_points(
        model: "_PairModel",
        signature: tuple[str, ...],
        ac: dict[int, float],
        bc: dict[int, float],
        ac_nr: dict[int, bool],
        bc_nr: dict[int, bool],
        rng: random.Random
    ) -> list[AudiogramPointDTO]:
        points: list[AudiogramPointDTO] = []

        for test_type, base_points, base_nr in (
            (TestTypeEnum.AC_MASKED, ac, ac_nr),
            (TestTypeEnum.BC_MASKED, bc, bc_nr),
        ):
            prob_map = model.masked_prob.get(signature, {}).get(test_type, {})
            delta_map = model.masked_deltas.get(signature, {}).get(test_type, {})
            nr_prob_map = model.masked_nr_prob.get(signature, {}).get(test_type, {})

            for freq, base_val in base_points.items():
                if base_nr.get(freq, False):
                    continue
                prob = prob_map.get(freq, 0.0)
                if rng.random() > prob:
                    continue

                is_nr = rng.random() < nr_prob_map.get(freq, 0.0)
                if is_nr:
                    masked_val = MAX_DB
                else:
                    deltas = delta_map.get(freq, [])
                    if deltas:
                        masked_val = base_val + rng.choice(deltas)
                    else:
                        # If no delta distribution exists, keep it close to base.
                        masked_val = base_val

                points.append(
                    AudiogramPointDTO(
                        test_type=test_type,
                        frequency=freq,
                        threshold_db=PatientGenerator._clamp_db(masked_val),
                        is_no_response=is_nr,
                    )
                )

        return points
