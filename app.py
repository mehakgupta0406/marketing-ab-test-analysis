"""Run with: streamlit run app.py"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from dashboard_data import DAYS, aggregate, comparisons, overall_metrics, rates, read_users, roi_table, saved_results

st.set_page_config(page_title="Campaign Lab | Marketing A/B Analysis", page_icon="📊", layout="wide")
st.markdown("**CAMPAIGN LAB · MARKETING ANALYTICS**")
st.title("Did the advertising make a difference?")
st.caption("Explore conversion, behavioral segments, and the financial assumptions behind a campaign decision.")


@st.cache_data(show_spinner=False)
def parse_upload(content):
    return read_users(content)


@st.cache_data(show_spinner=False)
def summarize_users(df, cutoff):
    return aggregate(df, cutoff)


with st.sidebar:
    st.header("Your data")
    mode = st.radio("Data source", ["Project results", "Upload CSV"])
    st.caption("Project results reproduce saved notebook summaries. Upload the original CSV to explore user filters.")

if mode == "Project results":
    data = saved_results()
    st.info("Showing the project's saved results for 588,101 users. No synthetic user records are included.")
else:
    uploaded = st.sidebar.file_uploader("Upload marketing_AB.csv", type=["csv"])
    if uploaded is None:
        st.info("Upload the Marketing A/B Testing CSV to begin. Required columns: user id, test group, converted, total ads, most ads day, most ads hour.")
        st.link_button("Get the source dataset", "https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing")
        st.stop()
    try:
        df = parse_upload(uploaded.getvalue())
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    cutoff = float(df["total ads"].median())
    with st.sidebar:
        st.header("Explore a cohort")
        selected_days = st.multiselect("Most ads day", DAYS, default=DAYS)
        selected_hours = st.slider("Most ads hour", 0, 23, (0, 23))
        exposure_filter = st.selectbox("Ad exposure", ["All", "Light", "Heavy"])
        st.caption(f"Exposure uses the uploaded dataset median: Light ≤ {cutoff:g}; Heavy > {cutoff:g}. The cutoff stays fixed when filtering.")
    mask = df["most ads day"].isin(selected_days) & df["most ads hour"].between(*selected_hours)
    if exposure_filter == "Light":
        mask &= df["total ads"] <= cutoff
    elif exposure_filter == "Heavy":
        mask &= df["total ads"] > cutoff
    filtered = df.loc[mask]
    if filtered.empty:
        st.warning("No users match these filters. Select another cohort.")
        st.stop()
    data = summarize_users(filtered, cutoff)
    st.info(f"Uploaded data · {len(filtered):,} of {len(df):,} users selected. Results below use this cohort.")
    if len(filtered) != len(df):
        st.caption("Filtered comparisons are exploratory. The displayed p-value and interval are nominal and do not adjust for searching across cohorts.")

summary = rates(data["overall"])
metrics = overall_metrics(summary)
if metrics is None:
    st.warning("This cohort needs users from both Ad and PSA for lift, statistical comparison, and ROI.")
    st.dataframe(summary, hide_index=True)
    st.stop()

cards = st.columns(4)
cards[0].metric("Users analyzed", f'{int(summary["users"].sum()):,}')
cards[1].metric("Ad conversion", f'{metrics["ad"]:.2%}')
cards[2].metric("PSA conversion", f'{metrics["psa"]:.2%}')
cards[3].metric("Relative lift", f'{metrics["lift"]:+.2f}%' if metrics["lift"] is not None else "Undefined")

overview, segments, financial = st.tabs(["Campaign results", "Behavioral segments", "ROI scenarios"])

with overview:
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Conversion by group")
        fig, ax = plt.subplots(figsize=(7, 4))
        ordered = summary.set_index("test_group").reindex(["ad", "psa"])
        bars = ax.bar(["Ad", "PSA"], ordered["conversion_rate_pct"], color=["#237a91", "#e6a34a"])
        ax.bar_label(bars, fmt="%.2f%%", padding=4)
        ax.set_ylabel("Conversion rate (%)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.margins(y=0.2)
        st.pyplot(fig)
        plt.close(fig)
    with right:
        st.subheader("Evidence and effect size")
        st.metric("Ad minus PSA", f'{metrics["difference"] * 100:+.3f} percentage points')
        st.write(f'95% confidence interval: **{metrics["ci_low"] * 100:.3f} to {metrics["ci_high"] * 100:.3f} percentage points**')
        st.write(f'Two-sided two-proportion z-test: **p = {metrics["p_value"]:.3g}**')
        st.caption("Confidence interval: Newcombe method. Statistical significance does not establish profitability or validate random assignment.")
    st.dataframe(summary.rename(columns={"test_group": "Group", "users": "Users", "conversions": "Conversions", "conversion_rate_pct": "Conversion rate (%)"}).round(3), hide_index=True)
    st.caption("Unequal group sizes alone are not evidence of an error. The intended allocation is unavailable, so sample-ratio mismatch cannot be validated.")

with segments:
    st.subheader("Where do conversion patterns differ?")
    choice = st.selectbox("Compare users by", ["Most ads day", "Most ads hour", "Ad exposure"])
    key, order = {"Most ads day": ("day", DAYS), "Most ads hour": ("hour", list(range(24))), "Ad exposure": ("exposure", ["Light", "Heavy"])}[choice]
    table = comparisons(data[key], key, order)
    st.caption(f'Light exposure: ≤ {data["cutoff"]:g} ads · Heavy exposure: > {data["cutoff"]:g} ads. Day/hour refer to peak ad activity, not conversion timing.')
    if table[["ad", "psa"]].notna().any().any():
        fig, ax = plt.subplots(figsize=(11, 4))
        table[["ad", "psa"]].plot.bar(ax=ax, color=["#237a91", "#e6a34a"], width=0.8)
        ax.set_ylabel("Conversion rate (%)")
        ax.set_xlabel(choice)
        ax.legend(["Ad", "PSA"])
        ax.tick_params(axis="x", rotation=45 if key == "day" else 0)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    st.dataframe(table.round(2))
    st.caption("ad/psa columns are conversion percentages; difference_pp is percentage points. Missing relative lift means no PSA baseline or a zero PSA rate.")
    with st.expander("Check users and conversions in each segment"):
        st.dataframe(rates(data[key]).round(3), hide_index=True)
    st.warning("Exploratory associations only. Segment significance has not been tested; small comparison groups can produce unstable lift. Exposure is not a randomized treatment.")
    st.download_button("Download segment comparison", table.to_csv().encode("utf-8"), file_name=f"{key}_comparison.csv", mime="text/csv")

with financial:
    st.subheader("What would make the campaign worthwhile?")
    st.info("Illustrative assumptions in INR — not actual costs, financial returns, or industry benchmarks.")
    st.caption("Contribution per conversion = revenue minus variable product/service costs, before campaign spend and fixed expenses.")
    cost_col, value_col = st.columns(2)
    cost = cost_col.number_input("Your assumed campaign spend (INR)", min_value=0.0, value=400000.0, step=10000.0)
    contribution = value_col.number_input("Your assumed contribution per conversion (INR)", min_value=0.0, value=150.0, step=10.0)
    st.metric("Estimated additional conversions", f'{metrics["additional"]:,.2f}')
    st.caption("(Ad rate − PSA rate) × selected Ad users. A fractional estimate is expected. Financial inputs must cover the same cohort and campaign period.")
    roi = roi_table(metrics["additional"], cost, contribution)
    st.dataframe(roi.round(2), hide_index=True)
    if cost == 0:
        st.warning("Your ROI is undefined at zero campaign spend; net contribution is still shown.")
    if metrics["additional"] < 0:
        st.warning("The observed conversion difference is negative. No nonnegative break-even spend exists when incremental contribution is negative.")
    valid = roi.dropna(subset=["Estimated ROI (%)"])
    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(valid["Scenario"], valid["Estimated ROI (%)"], color=["#237a91" if value >= 0 else "#e6a34a" for value in valid["Estimated ROI (%)"]])
    ax.axhline(0, color="#475569", linewidth=1)
    ax.bar_label(bars, fmt="%.1f%%", padding=4)
    ax.set_ylabel("Estimated ROI (%)")
    ax.set_title("ROI under illustrative assumptions")
    ax.margins(y=0.25)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Break-even spend equals estimated incremental contribution, before fixed expenses. Both financial inputs vary across scenarios. These point estimates assume a valid campaign effect and do not incorporate sampling uncertainty.")
    st.download_button("Download ROI scenarios", roi.to_csv(index=False).encode("utf-8"), file_name="roi_scenarios.csv", mime="text/csv")

st.divider()
st.caption("Source: Marketing A/B Testing by Favio Vázquez on Kaggle · Python, SQLite, and Streamlit")
st.link_button("View the analysis on GitHub", "https://github.com/mehakgupta0406/marketing-ab-test-analysis")
