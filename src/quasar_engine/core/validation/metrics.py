"""Dependency-light validation metrics."""

from __future__ import annotations

import math

import numpy as np


def _validate(probabilities: list[float], labels: list[int]) -> tuple[np.ndarray, np.ndarray]:
    if len(probabilities) != len(labels) or not probabilities:
        raise ValueError("non-empty probabilities and labels must have equal length")
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(labels, dtype=int)
    if np.any((p < 0) | (p > 1)) or np.any((y != 0) & (y != 1)):
        raise ValueError("probabilities must be in [0,1] and labels must be binary")
    return p, y


def brier_score(probabilities: list[float], labels: list[int]) -> float:
    p, y = _validate(probabilities, labels)
    return float(np.mean((p - y) ** 2))


def log_loss(probabilities: list[float], labels: list[int]) -> float:
    p, y = _validate(probabilities, labels)
    p = np.clip(p, 1e-9, 1.0 - 1e-9)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def expected_calibration_error(
    probabilities: list[float], labels: list[int], bins: int = 10
) -> float:
    p, y = _validate(probabilities, labels)
    edges = np.linspace(0.0, 1.0, bins + 1)
    error = 0.0
    for index in range(bins):
        if index == bins - 1:
            mask = (p >= edges[index]) & (p <= edges[index + 1])
        else:
            mask = (p >= edges[index]) & (p < edges[index + 1])
        if np.any(mask):
            error += float(np.mean(mask)) * abs(float(np.mean(p[mask])) - float(np.mean(y[mask])))
    return error


def roc_auc(probabilities: list[float], labels: list[int]) -> float:
    p, y = _validate(probabilities, labels)
    positives = p[y == 1]
    negatives = p[y == 0]
    if len(positives) == 0 or len(negatives) == 0:
        return math.nan
    wins = sum(float(pos > neg) + 0.5 * float(pos == neg) for pos in positives for neg in negatives)
    return wins / (len(positives) * len(negatives))


def average_precision(probabilities: list[float], labels: list[int]) -> float:
    p, y = _validate(probabilities, labels)
    positives = int(y.sum())
    if positives == 0:
        return math.nan
    order = np.argsort(-p, kind="stable")
    sorted_y = y[order]
    cumulative = np.cumsum(sorted_y)
    precision_at_k = cumulative / (np.arange(len(y)) + 1)
    return float(np.sum(precision_at_k * sorted_y) / positives)


def classification_metrics(
    probabilities: list[float], labels: list[int], threshold: float = 0.5
) -> dict[str, float]:
    p, y = _validate(probabilities, labels)
    predicted = p >= threshold
    tp = int(np.sum(predicted & (y == 1)))
    fp = int(np.sum(predicted & (y == 0)))
    tn = int(np.sum(~predicted & (y == 0)))
    fn = int(np.sum(~predicted & (y == 1)))
    return {
        "precision": tp / max(1, tp + fp),
        "recall": tp / max(1, tp + fn),
        "fpr": fp / max(1, fp + tn),
        "accuracy": (tp + tn) / max(1, len(y)),
        "tp": float(tp),
        "fp": float(fp),
        "tn": float(tn),
        "fn": float(fn),
    }


def probabilistic_metrics(
    probabilities: list[float], labels: list[int], bins: int = 10
) -> dict[str, float]:
    return {
        "brier": brier_score(probabilities, labels),
        "log_loss": log_loss(probabilities, labels),
        "ece": expected_calibration_error(probabilities, labels, bins),
        "auroc": roc_auc(probabilities, labels),
        "auprc": average_precision(probabilities, labels),
    }


def empirical_coverage(intervals: list[tuple[float, float]], labels: list[int]) -> float:
    if len(intervals) != len(labels) or not intervals:
        raise ValueError("non-empty intervals and labels must have equal length")
    return sum(lower <= label <= upper for (lower, upper), label in zip(intervals, labels, strict=True)) / len(labels)


def lead_time_steps(
    probabilities: list[float], event_now: list[int], horizon: int, threshold: float = 0.5
) -> float:
    """Average earliest warning before each event episode, in observation steps."""
    if len(probabilities) != len(event_now) or not probabilities:
        raise ValueError("probabilities and event_now must align")
    starts = [index for index, flag in enumerate(event_now) if flag and (index == 0 or not event_now[index - 1])]
    leads: list[int] = []
    for start in starts:
        begin = max(0, start - horizon)
        warnings = [index for index in range(begin, start + 1) if probabilities[index] >= threshold]
        if warnings:
            leads.append(start - min(warnings))
    return float(np.mean(leads)) if leads else 0.0

