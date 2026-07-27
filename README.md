# PhishGuard AI

PhishGuard AI is a machine-learning cybersecurity application that estimates whether a URL is legitimate or potentially used for phishing.

The application analyzes URL text locally. It never opens or visits the submitted website.

## Cybersecurity Problem

Phishing websites imitate legitimate websites to steal passwords, banking information, and other sensitive data.

Manually checking every URL is difficult and potentially unsafe. PhishGuard AI provides an automated risk prediction to support security awareness and investigation.

## Minimum Viable Product

The first working version will:

- Accept a URL through a Streamlit interface.
- Validate the URL safely.
- Convert URL character patterns into machine-learning features.
- Predict whether the URL may be phishing.
- Display a phishing probability and risk level.
- Show understandable warning signs.
- Include automated tests using pytest.
- Avoid permanently storing submitted URLs.

## Machine-Learning Approach

The project will use:

- Character-level TF-IDF to convert URL text into numerical features.
- Logistic Regression as an interpretable classification model.
- A secure scikit-learn pipeline to combine transformation and prediction.

The model analyzes text patterns only. It does not connect to the submitted website.

## Technology Stack

- Python
- pandas
- scikit-learn
- Streamlit
- pytest
- joblib
- Git and GitHub

## Dataset

The project uses the public [PhiUSIIL Phishing URL Dataset](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset) from the UCI Machine Learning Repository.

Dataset preparation results:

- Original records: 235,795
- Invalid-length records removed: 8
- Duplicate URLs removed: 425
- Conflicting labels: 0
- Final records: 235,362
- Legitimate records: 134,850
- Phishing records: 100,512

Dataset URLs remain local and are excluded from GitHub.

## Planned Workflow

1. Download the public dataset.
2. Validate and clean URL text.
3. Split the data into training and testing sets.
4. Convert URL text into character-level TF-IDF features.
5. Train and evaluate a Logistic Regression model.
6. Build the Streamlit interface.
7. Add security controls and automated tests.
8. Document results, limitations, and ethical considerations.

## Security and Privacy

- Submitted URLs are never opened automatically.
- Submitted URLs are not permanently stored.
- Dataset files are excluded from Git.
- Input length and format will be validated.
- The interface will not display URLs as clickable links.
- The model provides decision support, not a security guarantee.
- No live malware or private user data is used.

## Project Status

Project structure and the safe data pipeline are complete.

The next step is model training and evaluation.