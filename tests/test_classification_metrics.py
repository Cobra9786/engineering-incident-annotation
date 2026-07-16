import pytest

from incident_intelligence.classification_metrics import (
    INVALID_PREDICTION_LABEL,
    build_confusion_matrix,
    calculate_classification_report,
    harmonic_f1,
    safe_divide,
)


def test_safe_divide_handles_zero_denominator() -> None:
    assert safe_divide(4, 0) == 0.0


def test_harmonic_f1() -> None:
    assert harmonic_f1(0.5, 0.5) == 0.5


def test_confusion_matrix_uses_actual_rows() -> None:
    actual = ["leak", "leak", "sensor"]
    predicted = ["leak", "sensor", "sensor"]
    labels = ["leak", "sensor"]

    matrix = build_confusion_matrix(
        actual,
        predicted,
        labels,
    )

    assert matrix == [
        [1, 1],
        [0, 1],
    ]


def test_binary_class_metrics() -> None:
    report = calculate_classification_report(
        actual=["critical", "critical", "normal", "normal"],
        predicted=["critical", "normal", "critical", "normal"],
    )

    critical = report.per_class["critical"]

    assert critical.true_positive == 1
    assert critical.false_positive == 1
    assert critical.false_negative == 1
    assert critical.precision == 0.5
    assert critical.recall == 0.5
    assert critical.f1 == 0.5


def test_invalid_prediction_reduces_recall() -> None:
    report = calculate_classification_report(
        actual=["signal_loss", "signal_loss"],
        predicted=[
            "signal_loss",
            INVALID_PREDICTION_LABEL,
        ],
    )

    metrics = report.per_class["signal_loss"]

    assert metrics.precision == 1.0
    assert metrics.recall == 0.5
    assert metrics.f1 == pytest.approx(2.0 / 3.0)


def test_macro_average_uses_ground_truth_classes() -> None:
    report = calculate_classification_report(
        actual=["seal_leak", "signal_loss"],
        predicted=[
            "seal_leak",
            INVALID_PREDICTION_LABEL,
        ],
    )

    assert report.evaluated_labels == [
        "seal_leak",
        "signal_loss",
    ]

    assert (
        INVALID_PREDICTION_LABEL
        not in report.evaluated_labels
    )


def test_empty_input_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="empty",
    ):
        calculate_classification_report(
            actual=[],
            predicted=[],
        )