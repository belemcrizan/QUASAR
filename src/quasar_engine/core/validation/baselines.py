"""Transparent baseline probability mappings."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def residual_only_probability(residual_score: float) -> float:
    return _sigmoid(9.0 * (residual_score - 0.42))


def change_point_probability(change_score: float) -> float:
    return _sigmoid(10.0 * (change_score - 0.36))


def constant_base_rate_probability(rate: float) -> float:
    return min(max(float(rate), 1e-6), 1.0 - 1e-6)


def _average_path_adjustment(size: int) -> float:
    if size <= 1:
        return 0.0
    if size == 2:
        return 1.0
    euler_gamma = 0.5772156649015329
    return 2.0 * (math.log(size - 1) + euler_gamma) - 2.0 * (size - 1) / size


@dataclass(slots=True)
class _IsolationNode:
    size: int
    feature: int | None = None
    split: float | None = None
    left: "_IsolationNode | None" = None
    right: "_IsolationNode | None" = None


class IsolationForestBaseline:
    """Dependency-free Isolation Forest baseline for research comparison.

    The implementation follows the original random isolation principle. It is
    intentionally compact and should be compared against a maintained library
    implementation before publication claims are made.
    """

    def __init__(
        self,
        n_estimators: int = 64,
        sample_size: int = 128,
        seed: int = 42,
    ) -> None:
        if n_estimators < 1 or sample_size < 2:
            raise ValueError("Isolation Forest requires estimators >= 1 and sample_size >= 2")
        self.n_estimators = n_estimators
        self.sample_size = sample_size
        self.seed = seed
        self._trees: list[_IsolationNode] = []
        self._effective_sample_size = sample_size

    def fit(self, features: np.ndarray) -> "IsolationForestBaseline":
        matrix = np.asarray(features, dtype=float)
        if matrix.ndim != 2 or len(matrix) < 2:
            raise ValueError("features must be a two-dimensional array with at least two rows")
        if not np.all(np.isfinite(matrix)):
            raise ValueError("Isolation Forest features must be finite")
        rng = np.random.default_rng(self.seed)
        self._effective_sample_size = min(self.sample_size, len(matrix))
        max_depth = int(math.ceil(math.log2(self._effective_sample_size)))
        self._trees = []
        for _ in range(self.n_estimators):
            indices = rng.choice(len(matrix), size=self._effective_sample_size, replace=False)
            self._trees.append(self._build(matrix[indices], 0, max_depth, rng))
        return self

    def _build(
        self,
        matrix: np.ndarray,
        depth: int,
        max_depth: int,
        rng: np.random.Generator,
    ) -> _IsolationNode:
        node = _IsolationNode(size=len(matrix))
        if depth >= max_depth or len(matrix) <= 1:
            return node
        low = np.min(matrix, axis=0)
        high = np.max(matrix, axis=0)
        valid = np.flatnonzero(high > low)
        if len(valid) == 0:
            return node
        feature = int(rng.choice(valid))
        split = float(rng.uniform(low[feature], high[feature]))
        left_mask = matrix[:, feature] < split
        if not np.any(left_mask) or np.all(left_mask):
            return node
        node.feature = feature
        node.split = split
        node.left = self._build(matrix[left_mask], depth + 1, max_depth, rng)
        node.right = self._build(matrix[~left_mask], depth + 1, max_depth, rng)
        return node

    def _path_length(self, row: np.ndarray, node: _IsolationNode, depth: int = 0) -> float:
        if node.feature is None or node.left is None or node.right is None:
            return depth + _average_path_adjustment(node.size)
        branch = node.left if row[node.feature] < float(node.split) else node.right
        return self._path_length(row, branch, depth + 1)

    def score_samples(self, features: np.ndarray) -> list[float]:
        if not self._trees:
            raise RuntimeError("Isolation Forest must be fitted before scoring")
        matrix = np.asarray(features, dtype=float)
        normalization = max(_average_path_adjustment(self._effective_sample_size), 1e-9)
        scores: list[float] = []
        for row in matrix:
            mean_path = sum(self._path_length(row, tree) for tree in self._trees) / len(self._trees)
            scores.append(float(2.0 ** (-mean_path / normalization)))
        return scores
