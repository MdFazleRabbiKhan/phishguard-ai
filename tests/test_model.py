import pytest

from src.predict import PredictionError, predict_url
from src.security import URLValidationError


class FakeModel:
    """Small fake model used only for automated tests."""

    classes_ = [0, 1]

    def __init__(self, phishing_probability):
        self.phishing_probability = phishing_probability
        self.received_urls = []

    def predict_proba(self, values):
        self.received_urls.extend(values)

        return [
            [
                1.0 - self.phishing_probability,
                self.phishing_probability,
            ]
        ]


def test_predicts_high_risk_phishing_url():
    model = FakeModel(0.88)

    result = predict_url("https://example.com/login", model=model)

    assert result.label == "phishing"
    assert result.is_phishing is True
    assert result.phishing_probability == pytest.approx(0.88)
    assert result.risk_level == "high"


def test_normalizes_url_before_prediction():
    model = FakeModel(0.20)

    result = predict_url("example.com/home", model=model)

    assert result.url.normalized == "https://example.com/home"
    assert model.received_urls == ["https://example.com/home"]


def test_predicts_low_risk_legitimate_url():
    model = FakeModel(0.10)

    result = predict_url("https://example.com", model=model)

    assert result.label == "legitimate"
    assert result.is_phishing is False
    assert result.legitimate_probability == pytest.approx(0.90)
    assert result.confidence == pytest.approx(0.90)
    assert result.risk_level == "low"


def test_reports_medium_risk():
    model = FakeModel(0.45)

    result = predict_url("https://example.com", model=model)

    assert result.label == "phishing"
    assert result.risk_level == "medium"


def test_rejects_unsafe_url_before_using_model():
    model = FakeModel(0.90)

    with pytest.raises(URLValidationError):
        predict_url("file:///etc/passwd", model=model)

    assert model.received_urls == []


def test_rejects_invalid_model_probability():
    model = FakeModel(1.50)

    with pytest.raises(PredictionError):
        predict_url("https://example.com", model=model)