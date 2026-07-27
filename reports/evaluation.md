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
| Accuracy | 0.8855 |
| Balanced accuracy | 0.8718 |
| Phishing precision | 0.9444 |
| Phishing recall | 0.7776 |
| Phishing F1 score | 0.8530 |
| ROC AUC | 0.9331 |

## Confusion Matrix

| Actual / Predicted | Legitimate | Phishing |
|---|---:|---:|
| Legitimate | 26,050 | 920 |
| Phishing | 4,470 | 15,633 |

## Current Limitations

- This is the first baseline model.
- The evaluation uses a random stratified split.
- Similar domains may exist in both training and testing data.
- A future robustness test should separate records by domain.
- The prediction score should not be treated as a security guarantee.
