"""Safe prediction service for phishing URLs."""

from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path

import joblib

from src.security import ValidatedURL, validate_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = PROJECT_ROOT / "models" / "phishguard_pipeline.joblib"
PHISHING_THRESHOLD = 0.50


class PredictionError(RuntimeError):
    """Raised when the model cannot produce a valid prediction."""


class ModelNotReadyError(PredictionError):
    """Raised when the trained model is unavailable."""


@dataclass(frozen=True)
class PredictionResult:
    """Safe and structured prediction result."""

    url: ValidatedURL
    label: str
    is_phishing: bool
    phishing_probability: float
    legitimate_probability: float
    confidence: float
    risk_level: str


@lru_cache(maxsize=1)
def load_model():
    """Load only the locally trained model."""

    if not MODEL_FILE.is_file():
        raise ModelNotReadyError(
            "Trained model not found. Run: python -m src.train"
        )

    try:
        model = joblib.load(MODEL_FILE)
    except Exception as error:
        raise ModelNotReadyError(
            "The trained model could not be loaded."
        ) from error

    if not hasattr(model, "predict_proba"):
        raise ModelNotReadyError(
            "The model does not support probability predictions."
        )

    return model


def _get_risk_level(phishing_probability: float) -> str:
    if phishing_probability >= 0.75:
        return "high"

    if phishing_probability >= 0.40:
        return "medium"

    return "low"


def predict_url(value: str, model=None) -> PredictionResult:
    """Validate and classify URL text without visiting the website."""

    validated_url = validate_url(value)
    predictor = model if model is not None else load_model()

    if not hasattr(predictor, "predict_proba"):
        raise PredictionError(
            "The supplied model cannot calculate probabilities."
        )

    classes = list(getattr(predictor, "classes_", []))

    if 1 not in classes:
        raise PredictionError(
            "The model does not contain the phishing class."
        )

    phishing_index = classes.index(1)

    try:
        probabilities = predictor.predict_proba(
            [validated_url.normalized]
        )
        phishing_probability = float(
            probabilities[0][phishing_index]
        )
    except Exception as error:
        raise PredictionError(
            "The model could not classify this URL."
        ) from error

    if (
        not math.isfinite(phishing_probability)
        or not 0.0 <= phishing_probability <= 1.0
    ):
        raise PredictionError(
            "The model returned an invalid probability."
        )

    legitimate_probability = 1.0 - phishing_probability
    is_phishing = phishing_probability >= PHISHING_THRESHOLD

    return PredictionResult(
        url=validated_url,
        label="phishing" if is_phishing else "legitimate",
        is_phishing=is_phishing,
        phishing_probability=phishing_probability,
        legitimate_probability=legitimate_probability,
        confidence=max(
            phishing_probability,
            legitimate_probability,
        ),
        risk_level=_get_risk_level(phishing_probability),
    )