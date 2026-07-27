# PhishGuard AI

PhishGuard AI is a beginner-friendly cybersecurity project that uses machine learning to estimate whether a URL is legitimate or potentially a phishing URL.

The application analyzes the URL locally. It does not open or visit the website.

## Cybersecurity Problem

Phishing websites imitate legitimate websites to steal passwords, banking information, and other sensitive data. Manually checking every URL is difficult and unsafe.

PhishGuard AI provides an automated risk prediction to support security awareness and investigation.

## Minimum Viable Product

The first working version will:

- Accept a URL through a Streamlit web interface.
- Validate and safely process the input.
- Extract characteristics from the URL without visiting it.
- Use a trained machine-learning model.
- Display a phishing probability and risk level.
- Explain important warning signs.
- Include automated tests using pytest.
- Avoid storing submitted URLs.

## Technology Stack

- Python
- pandas and NumPy
- scikit-learn
- Streamlit
- pytest
- joblib
- Git and GitHub

## Dataset

We will use the public [PhiUSIIL Phishing URL Dataset from the UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset).

Only safe URL-based characteristics will be used. The application will not connect to suspicious websites.

## Planned Workflow

1. Download the public dataset.
2. Inspect and clean the data.
3. Select URL-based features.
4. Train and compare simple machine-learning models.
5. Evaluate phishing detection performance.
6. Build the Streamlit interface.
7. Add security controls and automated tests.
8. Document the results and limitations.

## Security and Privacy

- The application does not visit submitted URLs.
- Submitted URLs are not permanently stored.
- Input length and format will be validated.
- The model provides decision support, not a guarantee.
- No live malware or private user data is used.

## Project Status

Project setup completed. Dataset preparation is the next step.