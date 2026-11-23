# Marketing Campaign A/B Test Analysis

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mehakgupta0406/marketing-ab-test-analysis/blob/main/Marketing_ab_testing.ipynb)

Analyzing whether users shown a marketing advertisement converted at a higher rate than users shown a public service announcement (PSA), using Python and SQLite.

**Status:** Core analysis complete.

## Business question

Does the advertising group have a higher conversion rate than the PSA comparison group, and is the difference large enough to inform a campaign decision?

The primary metric is **user conversion rate**: the number of users who converted divided by the total number of users in each group. The dataset records conversion as a Boolean; this project does not assume a specific purchase action or revenue value.

## Results

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

The ad group had a higher conversion rate than the PSA group.
A two-sided two-proportion z-test found a statistically significant
difference (z = 7.370, p < 0.001).

The estimated difference was 0.769 percentage points, with a
95% confidence interval of 0.587 to 0.936 percentage points.

Causal interpretation depends on valid experiment design.
Campaign costs and conversion values are needed to assess profitability.

### Conversion-rate chart

![Conversion rates for the Ad and PSA groups](conversion_rates.png)


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
7. Compared conversion rates using a two-sided two-proportion z-test.
8. Calculated a 95% confidence interval for the conversion-rate difference.
9. Visualized conversion rates and group sizes.
10. Documented the business conclusion and analysis limitations.
11. Verified that the notebook runs from beginning to end.
12. Recorded library versions in requirements.txt.

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

### Dependencies

The library versions used in this analysis are recorded in
`requirements.txt`.

To install them locally, run:

```bash
pip install -r requirements.txt
```

## Interpretation and limitations

- The groups have substantially different sample sizes. Unequal allocation alone does not establish a problem; the intended allocation is needed to assess a sample-ratio mismatch.
- Causal conclusions depend on valid random assignment and independent observations. These assumptions need to be assessed using the available experiment documentation.
- Ad exposure, day, and hour describe observed activity. Associations with conversion should not be treated as causal targeting recommendations.
- Campaign costs and conversion values are not analyzed, so conversion lift alone does not establish profitability.
- Statistical significance, practical value, and generalizability must be considered separately when writing the final recommendation.
  
## Skills demonstrated

- Python and pandas for data inspection and validation.
- SQLite for aggregation and conversion-rate calculations.
- Hypothesis testing and confidence intervals.
- Matplotlib for visualizing results.
- Business interpretation and communication of limitations.


## Segment analysis

Exploratory analysis compares Ad and PSA conversion rates by `most ads day`, `most ads hour`, and `total ads`. These findings summarize the updated Colab outputs for all 588,101 users.

### Conversion by most ads day

- Monday had the highest observed Ad conversion rate: **3.32%**, compared with **2.26%** for PSA.
- Tuesday showed the largest observed Ad–PSA difference: **1.60 percentage points**, with **110.69% relative lift**.
- Thursday showed the smallest difference: **0.14 percentage points**, with **6.95% relative lift**.
- Ad conversion rates exceeded PSA rates across all seven days.

### Conversion by most ads hour

- **16:00 (4 PM)** had the highest observed Ad conversion rate: **3.09%**, compared with **2.81%** for PSA.
- **20:00 (8 PM)** had an Ad conversion rate of **3.03%**, compared with **1.76%** for PSA, with a difference of **1.26 percentage points**.
- The largest defined relative lift occurred at **07:00 (7 AM): 119.02%**.
- Ad conversion rates exceeded PSA rates at all hours except **03:00**, when rates were **1.04%** and **1.12%**, respectively.
- Relative lift was undefined (`NaN`) at hours 0, 1, 2, 4, 5, and 6 because the PSA conversion rate was zero.

### Conversion by ad exposure

The median `total ads` value was **13**. The same cutoff was applied to both test groups: **Light exposure = 13 ads or fewer**, and **Heavy exposure = more than 13 ads**. Users tied at the median belong to Light exposure, so segment sizes need not be equal.

| Exposure | Ad conversion rate | PSA conversion rate | Difference (percentage points) | Relative lift |
| --- | ---: | ---: | ---: | ---: |
| Light (≤ 13 ads) | 0.38% | 0.40% | −0.03 | −7.07% |
| Heavy (> 13 ads) | 4.81% | 3.38% | +1.43 | +42.25% |

Relative lift (%) = ((Ad conversion rate − PSA conversion rate) / PSA conversion rate) × 100. Differences and lift were calculated from unrounded rates, so subtracting displayed rates may give slightly different results.

These comparisons are exploratory; statistical significance was not tested within segments. Day and hour describe when users saw the most ads, not when they converted. Exposure is observed activity rather than a randomized treatment, so higher conversion among heavily exposed users does not establish that showing more ads causes more conversions. Check segment user and conversion counts before drawing conclusions, especially for hours with low or zero PSA conversions.
