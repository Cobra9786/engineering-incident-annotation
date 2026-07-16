from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Hashable, Sequence


Label = Hashable
INVALID_PREDICTION_LABEL = "__invalid__"


@dataclass(frozen=True)
class ClassMetrics:
    label: str
    true_positive: int
    false_positive: int
    false_negative: int
    support: int
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class AggregateMetrics:
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class ClassificationReport:
    labels: list[str]
    evaluated_labels: list[str]
    per_class: dict[str, ClassMetrics]
    macro_average: AggregateMetrics
    weighted_average: AggregateMetrics
    exact_match_rate: float
    confusion_matrix: list[list[int]]

    def to_dict(self) -> dict[str, object]:
        return {
            "labels": self.labels,
            "evaluated_labels": self.evaluated_labels,
            "per_class": {
                label: asdict(metrics)
                for label, metrics in self.per_class.items()
            },
            "macro_average": asdict(self.macro_average),
            "weighted_average": asdict(self.weighted_average),
            "exact_match_rate": self.exact_match_rate,
            "confusion_matrix": self.confusion_matrix,
        }


def safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


def harmonic_f1(
    precision: float,
    recall: float,
) -> float:
    if precision + recall == 0.0:
        return 0.0

    return (
        2.0
        * precision
        * recall
        / (precision + recall)
    )


def stable_labels(
    actual: Sequence[str],
    predicted: Sequence[str],
) -> list[str]:
    labels = sorted(set(actual) | set(predicted))

    if INVALID_PREDICTION_LABEL in labels:
        labels.remove(INVALID_PREDICTION_LABEL)
        labels.append(INVALID_PREDICTION_LABEL)

    return labels


def build_confusion_matrix(
    actual: Sequence[str],
    predicted: Sequence[str],
    labels: Sequence[str],
) -> list[list[int]]:
    if len(actual) != len(predicted):
        raise ValueError(
            "actual and predicted lengths must match"
        )

    label_to_index = {
        label: index
        for index, label in enumerate(labels)
    }

    matrix = [
        [0 for _ in labels]
        for _ in labels
    ]

    for actual_label, predicted_label in zip(
        actual,
        predicted,
        strict=True,
    ):
        row = label_to_index[actual_label]
        column = label_to_index[predicted_label]
        matrix[row][column] += 1

    return matrix


def calculate_classification_report(
    *,
    actual: Sequence[str],
    predicted: Sequence[str],
) -> ClassificationReport:
    if len(actual) != len(predicted):
        raise ValueError(
            "actual and predicted lengths must match"
        )

    if not actual:
        raise ValueError(
            "cannot evaluate an empty classification result"
        )

    labels = stable_labels(actual, predicted)

    # Macro and weighted averages are computed over classes
    # that genuinely occur in the ground-truth benchmark.
    evaluated_labels = sorted(set(actual))

    matrix = build_confusion_matrix(
        actual,
        predicted,
        labels,
    )

    label_to_index = {
        label: index
        for index, label in enumerate(labels)
    }

    per_class: dict[str, ClassMetrics] = {}

    for label in labels:
        index = label_to_index[label]

        true_positive = matrix[index][index]

        false_positive = sum(
            matrix[row][index]
            for row in range(len(labels))
            if row != index
        )

        false_negative = sum(
            matrix[index][column]
            for column in range(len(labels))
            if column != index
        )

        support = sum(matrix[index])

        precision = safe_divide(
            true_positive,
            true_positive + false_positive,
        )

        recall = safe_divide(
            true_positive,
            true_positive + false_negative,
        )

        f1 = harmonic_f1(
            precision,
            recall,
        )

        per_class[label] = ClassMetrics(
            label=label,
            true_positive=true_positive,
            false_positive=false_positive,
            false_negative=false_negative,
            support=support,
            precision=precision,
            recall=recall,
            f1=f1,
        )

    macro_average = AggregateMetrics(
        precision=sum(
            per_class[label].precision
            for label in evaluated_labels
        )
        / len(evaluated_labels),
        recall=sum(
            per_class[label].recall
            for label in evaluated_labels
        )
        / len(evaluated_labels),
        f1=sum(
            per_class[label].f1
            for label in evaluated_labels
        )
        / len(evaluated_labels),
    )

    total_support = sum(
        per_class[label].support
        for label in evaluated_labels
    )

    weighted_average = AggregateMetrics(
        precision=sum(
            per_class[label].precision
            * per_class[label].support
            for label in evaluated_labels
        )
        / total_support,
        recall=sum(
            per_class[label].recall
            * per_class[label].support
            for label in evaluated_labels
        )
        / total_support,
        f1=sum(
            per_class[label].f1
            * per_class[label].support
            for label in evaluated_labels
        )
        / total_support,
    )

    exact_matches = sum(
        actual_label == predicted_label
        for actual_label, predicted_label in zip(
            actual,
            predicted,
            strict=True,
        )
    )

    return ClassificationReport(
        labels=labels,
        evaluated_labels=evaluated_labels,
        per_class=per_class,
        macro_average=macro_average,
        weighted_average=weighted_average,
        exact_match_rate=exact_matches / len(actual),
        confusion_matrix=matrix,
    )