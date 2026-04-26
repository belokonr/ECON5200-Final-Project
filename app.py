import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Remote Work & Real Estate: Causal Analysis", layout="wide")
st.title("Does Remote Work Reduce Housing Prices?")
st.markdown("""This dashboard presents the causal analysis of how remote work adoption 
affects state-level house price indices, using Double Machine Learning (DML) to 
isolate the true effect from confounders like income and unemployment.""")

# --- Sidebar: What-If Controls ---
st.sidebar.header("What-If Scenarios")

wfh_increase = st.sidebar.slider(
    "Additional WFH rate increase (pp)",
    min_value=0.0, max_value=20.0, value=5.0, step=0.5,
    help="Simulate what happens if WFH rates rise by this many percentage points"
)

confidence_level = st.sidebar.selectbox(
    "Confidence level", ["90%", "95%", "99%"], index=1
)
z_map = {"90%": 1.645, "95%": 1.96, "99%": 2.576}
z_val = z_map[confidence_level]

# --- Pre-computed results from DML (replace with your actual values) ---
baseline_ate = 673.02     # TODO: Replace with your causal_estimate_scalar
baseline_se = 167.86        # TODO: Replace with your standard error

# --- Compute What-If Estimate ---
# ATE is per 1-unit (100pp) change in WFH rate, so scale by pp/100
predicted_hpi_change = baseline_ate * (wfh_increase / 100)
predicted_se = baseline_se * (wfh_increase / 100)
ci_lower = predicted_hpi_change - z_val * predicted_se
ci_upper = predicted_hpi_change + z_val * predicted_se

# --- Display Results ---
st.subheader("Estimated Impact")
col1, col2, col3 = st.columns(3)
col1.metric("Predicted HPI Change", f"{predicted_hpi_change:.1f} pts")
col2.metric(f"{confidence_level} CI Lower", f"{ci_lower:.1f} pts")
col3.metric(f"{confidence_level} CI Upper", f"{ci_upper:.1f} pts")

st.markdown(f"""
> **Interpretation:** If state-level WFH rates increase by an additional 
> {wfh_increase:.1f} percentage points, we estimate the FHFA House Price Index 
> would change by **{predicted_hpi_change:.1f} points** 
> ({confidence_level} CI: [{ci_lower:.1f}, {ci_upper:.1f}]).
""")

# --- Sensitivity Visualization ---
st.subheader("Sensitivity: HPI Impact Across WFH Scenarios")
wfh_range = np.arange(0, 21, 0.5)
hpi_changes = baseline_ate * (wfh_range / 100)
se_range = baseline_se * (wfh_range / 100)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=wfh_range, y=hpi_changes + z_val * se_range,
    mode="lines", line=dict(width=0), showlegend=False
))
fig.add_trace(go.Scatter(
    x=wfh_range, y=hpi_changes - z_val * se_range,
    mode="lines", line=dict(width=0), fill="tonexty",
    fillcolor="rgba(26,35,126,0.2)", name=f"{confidence_level} CI"
))
fig.add_trace(go.Scatter(
    x=wfh_range, y=hpi_changes,
    mode="lines", line=dict(color="#1a237e", width=2), name="Estimated Effect"
))
fig.add_vline(x=wfh_increase, line_dash="dash", line_color="red",
              annotation_text=f"Selected: +{wfh_increase:.1f}pp")
fig.add_hline(y=0, line_dash="dot", line_color="gray")
fig.update_layout(
    title="What-If: HPI Impact vs. WFH Rate Increase",
    xaxis_title="Additional WFH Rate Increase (percentage points)",
    yaxis_title="Estimated HPI Change (index points)",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# --- Explicit Counterfactual Scenario ---
st.subheader("Counterfactual Scenario")
counterfactual_pp = 10.0  # fixed scenario: WFH rises 10pp
cf_effect = baseline_ate * (counterfactual_pp / 100)
cf_se = baseline_se * (counterfactual_pp / 100)
cf_ci_lower = cf_effect - 1.96 * cf_se
cf_ci_upper = cf_effect + 1.96 * cf_se

st.markdown(f"""
> **Counterfactual:** If remote work rates increase by {counterfactual_pp:.0f} percentage points 
> nationwide (roughly a doubling of the post-pandemic shift), the estimated effect on 
> the FHFA House Price Index would be **{cf_effect:.1f} points** 
> (95% CI: [{cf_ci_lower:.1f}, {cf_ci_upper:.1f}]).
""")

cf_col1, cf_col2, cf_col3 = st.columns(3)
cf_col1.metric("Scenario", f"+{counterfactual_pp:.0f} pp WFH")
cf_col2.metric("Predicted HPI Impact", f"{cf_effect:.1f} pts")
cf_col3.metric("95% CI", f"[{cf_ci_lower:.1f}, {cf_ci_upper:.1f}]")

# --- Method Note ---
st.subheader("Methodology")
st.markdown("""
- **Method:** Double Machine Learning (LinearDML from EconML)
- **Treatment:** State-level WFH rate (Census ACS)
- **Outcome:** FHFA All-Transactions House Price Index
- **Controls:** Unemployment rate, per-capita income, population
- **Panel:** 51 states x 5 years (2018-2019, 2021-2023)
- **Key assumption:** Conditional independence after controlling for state economic conditions
""")
