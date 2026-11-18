# Marketing Campaign A/B Test Analysis

This project compares conversion rates in two groups from a marketing campaign. A conversion occurs when a user completes the action tracked by the campaign.

## Business question

Did users who saw the marketing ad convert at a higher rate than users who saw a public service announcement (PSA)?

## Dataset

[Marketing A/B Testing on Kaggle](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing)

| Column | Meaning |
| --- | --- |
| `user id` | Identifies each user |
| `test group` | `ad` for the marketing ad group, or `psa` for the comparison group |
| `converted` | `True` if the user converted, or `False` otherwise |

## Analysis plan

1. Load the CSV in Google Colab and check for missing values, duplicate users, and unexpected group labels.
2. Use SQLite to count users and conversions in each group and calculate each group’s conversion rate.
3. Use Python to estimate the difference in conversion rates and its uncertainty.
4. Visualize the results and explain what they suggest about the campaign.
