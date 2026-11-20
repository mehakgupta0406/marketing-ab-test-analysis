# Marketing Campaign A/B Test Analysis

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mehakgupta0406/marketing-ab-test-analysis/blob/main/Marketing_ab_testing.ipynb)

Analyzing whether users shown a marketing advertisement converted at a higher rate than users shown a public service announcement (PSA), using Python and SQLite.

**Status:** In progress. Data inspection, SQL aggregation, and descriptive lift calculations are implemented. Statistical inference, visualizations, and the final business recommendation are planned.

## Business question

Does the advertising group have a higher conversion rate than the PSA comparison group, and is the difference large enough to inform a campaign decision?

The primary metric is **user conversion rate**: the number of users who converted divided by the total number of users in each group. The dataset records conversion as a Boolean; this project does not assume a specific purchase action or revenue value.

## Preliminary results

The saved notebook outputs report the following:

| Group | Users | Conversions | Conversion rate |
| --- | ---: | ---: | ---: |
| Marketing ad (`ad`) | 564,577 | 14,423 | 2.55% |
| Public service announcement (`psa`) | 23,524 | 420 | 1.79% |
| **Total** | **588,101** | **14,843** | |

- **Absolute difference:** +0.77 percentage points for the ad group.
- **Relative lift:** +43.09% compared with the PSA group.

Lift is calculated from the unrounded rates:

```text
Absolute difference = ad conversion rate − PSA conversion rate
Relative lift (%)   = (ad conversion rate / PSA conversion rate − 1) × 100
```

These are descriptive findings from the existing notebook outputs. Statistical significance and confidence intervals have not yet been evaluated. A rollout or budget recommendation will require assessment of experiment validity, uncertainty, and campaign economics.

## Dataset

**Source:** [Marketing A/B Testing by Favio Vázquez on Kaggle](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing)  
**Input file:** `marketing_AB.csv`  
**Size shown in the notebook:** 588,101 rows, with six analytical fields after removing the exported index column.

| Original column | Description |
| --- | --- |
| `user id` | User identifier |
| `test group` | Group label: `ad` or `psa` |
| `converted` | Whether the user converted |
| `total ads` | Recorded number of ads shown to the user |
| `most ads day` | Day on which the user saw the most ads |
| `most ads hour` | Hour at which the user saw the most ads |

The source CSV is not included in this repository. Download it from Kaggle to reproduce the analysis.

## Work completed

1. Loaded the CSV and inspected its dimensions, data types, and non-null counts.
2. Removed the exported index column, `Unnamed: 0`.
3. Checked duplicate rows, duplicate user IDs, and group labels.
4. Loaded the data into an in-memory SQLite database.
5. Used SQL to aggregate users, conversions, and conversion rates by group.
6. Calculated absolute and relative conversion lift in Python.

**Tools used:** Python, pandas, SQLite through Python's `sqlite3` module, and Google Colab.

## Run the current analysis

1. Open the notebook using the **Open in Colab** button above.
2. Save a copy to your Google Drive if you want to edit it.
3. Download and extract the dataset from Kaggle. Sign in if prompted.
4. Upload `marketing_AB.csv` to the Colab runtime using the Files panel.
5. Confirm that the file is in the runtime's working directory, matching:
   ```python
   df = pd.read_csv("marketing_AB.csv")
   ```
6. Start a fresh runtime and run the notebook cells in order.

The notebook imports `pandas` and `sqlite3`; SQLite support is included with Python. The database exists only in memory. Colab runtime files must be uploaded again when the runtime is reset.

## Next steps

- [ ] Add a written experiment setup, hypotheses, and a predefined significance level.
- [ ] Add explicit validation checks for missing values, allowed labels, unique users, and valid field ranges.
- [ ] Assess the unequal group sizes against the intended allocation, if that information is available.
- [ ] Run a two-proportion test and calculate a 95% confidence interval for the conversion-rate difference.
- [ ] Create charts showing group sizes and conversion rates with uncertainty.
- [ ] Explore day, hour, and exposure patterns, labeling these analyses as exploratory.
- [ ] Explain practical impact, limitations, and the evidence needed for a campaign decision.
- [ ] Add dependency versions and verify that the notebook runs from beginning to end in a fresh environment.
- [ ] Update this README with verified final results and selected charts.

## Interpretation and limitations

- The groups have substantially different sample sizes. Unequal allocation alone does not establish a problem; the intended allocation is needed to assess a sample-ratio mismatch.
- Causal conclusions depend on valid random assignment and independent observations. These assumptions need to be assessed using the available experiment documentation.
- Ad exposure, day, and hour describe observed activity. Associations with conversion should not be treated as causal targeting recommendations.
- Campaign costs and conversion values are not analyzed, so conversion lift alone does not establish profitability.
- Statistical significance, practical value, and generalizability must be considered separately when writing the final recommendation.
