# Model Evaluation

## Dataset Split

- Available clean records: 235,362
- Training records used: 60,000
- Testing records used: 47,073
- Positive class: phishing

## Metrics

| Metric | Result |
|---|---:|
| Majority baseline accuracy | 0.5729 |
| Accuracy | 0.9952 |
| Balanced accuracy | 0.9944 |
| Phishing precision | 1.0000 |
| Phishing recall | 0.9888 |
| Phishing F1 score | 0.9944 |
| ROC AUC | 0.9984 |

## Confusion Matrix

| Actual / Predicted | Legitimate | Phishing |
|---|---:|---:|
| Legitimate | 26,970 | 0 |
| Phishing | 225 | 19,878 |

## Current Limitations

- This is the first baseline model.
- The evaluation uses a random stratified split.
- Similar domains may exist in both training and testing data.
- A future robustness test should separate records by domain.
- The prediction score should not be treated as a security guarantee.
