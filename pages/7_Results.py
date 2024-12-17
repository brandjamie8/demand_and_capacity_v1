import streamlit as st
import pandas as pd

st.title("Results")

st.write("""
This section summarises the key results from the previous sections.
""")

# Ensure required keys exist in session state
required_keys = [
    'total_demand_cases', 'total_demand_minutes', 'total_sessions_12_months',
    'session_minutes_next_year', 'waiting_list_start', 'waiting_list_end',
    'required_sessions_next_year', 'sessions_per_week_last_year', 'sessions_per_week_next_year'
]

# Check session state and assign values
total_demand_cases = st.session_state.total_predicted_cases
baseline_capacity_sessions = st.session_state.total_sessions_12_months
waiting_list_start = st.session_state.get('waiting_list_start', 0)
waiting_list_end = st.session_state.get('waiting_list_end', 0)
required_sessions_next_year = st.session_state.get('required_sessions_next_year', 0)
sessions_per_week_next_year = st.session_state.get('sessions_per_week_next_year', 0)
sessions_per_week_last_year = st.session_state.get('sessions_per_week_last_year', 0)

# Predicted Metrics for Next Year
st.header("Predicted Metrics for Next Year")
st.write(f"**Predicted Demand (Cases):** {total_demand_cases:0.f}")
st.write(f"**Baseline Capacity (Sessions in 12-Month Equivalent):** {baseline_capacity_sessions:.0f}")
st.write(f"**Planned Sessions per Week (Next Year):** {sessions_per_week_next_year}")

# Waiting List Metrics
st.header("Waiting List Metrics")
st.write(f"**Predicted Waiting List at Start of Year:** {waiting_list_start}")
st.write(f"**Predicted Waiting List at End of Year:** {waiting_list_end}")

# Determine Waiting List Growth or Shrinkage
if waiting_list_start and waiting_list_end:
    change_in_waiting_list = waiting_list_end - waiting_list_start
    if change_in_waiting_list > 0:
        st.write(f"**Waiting List Expected to Grow:** {change_in_waiting_list:.0f} cases")
    elif change_in_waiting_list < 0:
        st.write(f"**Waiting List Expected to Shrink:** {-change_in_waiting_list:.0f} cases")
    else:
        st.write("**Waiting List Expected to Maintain:** No change expected")

# Required Sessions to Meet Demand
st.header("Required Sessions to Meet Demand")
st.write(f"**Sessions per Week Required to Meet Referral Demand:** {required_sessions_next_year:.2f}")
st.write(f"**Sessions per Week Planned Next Year:** {sessions_per_week_next_year:.2f}")

# Difference Between Required and Planned Sessions
if required_sessions_next_year and sessions_per_week_next_year:
    difference_sessions = required_sessions_next_year - sessions_per_week_next_year
    if difference_sessions > 0:
        st.warning(f"**Shortfall in Planned Capacity:** {difference_sessions:.2f} sessions per week")
    elif difference_sessions < 0:
        st.success(f"**Surplus in Planned Capacity:** {abs(difference_sessions):.2f} sessions per week")
    else:
        st.write("**Capacity Matches Demand:** No difference")

# Conclusion on Capacity vs Demand
st.header("Capacity vs Demand")
if sessions_per_week_next_year >= required_sessions_next_year:
    st.success("The planned capacity meets or exceeds the demand.")
else:
    st.error("The planned capacity does not meet the demand.")

# Prepare Data for Download
st.header("Download Results")
results_data = {
    "Metric": [
        "Baseline Demand (Cases)", "Baseline Capacity (Sessions)",
        "Planned Sessions per Week (Next Year)", "Required Sessions per Week", 
        "Predicted Waiting List Start", "Predicted Waiting List End"
    ],
    "Value": [
        total_demand_cases, baseline_capacity_sessions,
        sessions_per_week_next_year, required_sessions_next_year, 
        waiting_list_start, waiting_list_end
    ]
}

results_df = pd.DataFrame(results_data)

# Allow users to download the results
st.download_button(
    label="Download Results as CSV",
    data=results_df.to_csv(index=False),
    file_name="results_summary.csv",
    mime="text/csv"
)

st.dataframe(results_df)
