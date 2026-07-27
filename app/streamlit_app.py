"""Streamlit interface for PhishGuard AI."""

import streamlit as st

from src.predict import (
    ModelNotReadyError,
    PredictionError,
    load_model,
    predict_url,
)


st.set_page_config(
    page_title="PhishGuard AI",
    page_icon="🛡️",
    layout="centered",
)


@st.cache_resource(show_spinner=False)
def get_model():
    """Load and cache the locally trained model."""

    return load_model()


st.title("🛡️ PhishGuard AI")

st.write(
    "Analyze URL text with a locally trained machine-learning model."
)

st.info(
    "The website is never opened or visited. "
    "Only the URL text is analyzed."
)

with st.form("url_analysis_form"):
    url_value = st.text_input(
        "Enter a URL",
        placeholder="https://www.example.com/login",
        max_chars=2048,
        help="Enter an HTTP or HTTPS URL.",
    )

    submitted = st.form_submit_button("Analyze URL")


if submitted:
    if not url_value.strip():
        st.warning("Please enter a URL.")

    else:
        try:
            with st.spinner("Analyzing URL text..."):
                result = predict_url(
                    url_value,
                    model=get_model(),
                )

        except ValueError as error:
            st.warning(f"Invalid URL: {error}")

        except ModelNotReadyError:
            st.error(
                "The trained model was not found. "
                "Run: python -m src.train"
            )

        except PredictionError:
            st.error(
                "The model could not analyze this URL."
            )

        except Exception:
            st.error(
                "An unexpected error occurred. "
                "No website was opened."
            )

        else:
            if result.is_phishing:
                st.error(
                    f"Result: Likely phishing — "
                    f"{result.risk_level.upper()} risk"
                )
            else:
                st.success(
                    f"Result: Likely legitimate — "
                    f"{result.risk_level.upper()} risk"
                )

            probability_column, confidence_column = st.columns(2)

            probability_column.metric(
                "Phishing probability",
                f"{result.phishing_probability:.2%}",
            )

            confidence_column.metric(
                "Model confidence",
                f"{result.confidence:.2%}",
            )

            st.write("Phishing-risk score")

            st.progress(result.phishing_probability)

            st.write("Normalized URL text")

            # Display as plain code, never as a clickable link.
            st.code(
                result.url.normalized,
                language=None,
            )

            st.caption(
                "The result is decision support, not a security "
                "guarantee. Do not open suspicious websites."
            )


st.divider()

st.subheader("Security and privacy")

st.markdown(
    """
- The application does not visit submitted websites.
- No DNS lookup or network request is performed.
- URL length and format are validated.
- Submitted URLs are not permanently stored.
- Do not submit URLs containing passwords or private tokens.
"""
)

st.subheader("Current model limitation")

st.write(
    "The hostname-separated evaluation achieved 87.99% accuracy "
    "and 76.25% phishing recall. Therefore, some phishing URLs "
    "may not be detected."
)