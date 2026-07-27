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
| Accuracy | 0.8799 |
| Balanced accuracy | 0.8649 |
| Phishing precision | 0.9458 |
| Phishing recall | 0.7625 |
| Phishing F1 score | 0.8443 |
| ROC AUC | 0.9305 |

## Confusion Matrix

| Actual / Predicted | Legitimate | Phishing |
|---|---:|---:|
| Legitimate | 26,091 | 879 |
| Phishing | 4,775 | 15,327 |

## Interpretation

This test is more realistic than a normal random split because test
hostnames are not present in the training data. Results may still vary
on new phishing campaigns and real-world data.
