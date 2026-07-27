# Domain-Separated Evaluation

## Purpose

This evaluation prevents the same hostname from appearing in both
training and testing data. It provides a harder test on unseen websites.

## Dataset Split

- Training records: 60,000
- Testing records: 47,072
- Training hostnames: 57,268
- Testing hostnames: 44,008
- Overlapping hostnames: 0
- Training phishing rate: 0.4270
- Testing phishing rate: 0.4270

## Metrics

| Metric | Result |
|---|---:|
| Majority baseline accuracy | 0.5730 |
| Accuracy | 0.9949 |
| Balanced accuracy | 0.9940 |
| Phishing precision | 1.0000 |
| Phishing recall | 0.9880 |
| Phishing F1 score | 0.9939 |
| ROC AUC | 0.9984 |

## Confusion Matrix

| Actual / Predicted | Legitimate | Phishing |
|---|---:|---:|
| Legitimate | 26,970 | 0 |
| Phishing | 242 | 19,860 |

## Interpretation

This test is more realistic than a normal random split because test
hostnames are not present in the training data. Results may still vary
on new phishing campaigns and real-world data.
