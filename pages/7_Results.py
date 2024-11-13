import streamlit as st

st.title("Results")

st.write("""
This section summarises the key results from the previous sections.
""")

# Define the expected keys
required_keys = [
    'total_demand_cases', 'total_demand_minutes', 'total_sessions_12_months',
    'session_minutes_next_year', 'waiting_list_start', 'waiting_list_end',
    'required_sessions_next_year', 'sessions_per_week_next_year'
]

# Check if necessary data is available in session state and use a fallback value if any are missing
total_demand_cases = st.session_state.get('total_demand_cases', "")
total_demand_minutes = st.session_state.get('total_demand_minutes', "")
baseline_capacity_sessions = st.session_state.get('total_sessions_12_months', "")
session_minutes_next_year = st.session_state.get('session_minutes_next_year', "")
waiting_list_start = st.session_state.get('waiting_list_start', "")
waiting_list_end = st.session_state.get('waiting_list_end', "")
required_sessions_next_year = st.session_state.get('required_sessions_next_year', "")
sessions_per_week_next_year = st.session_state.get('sessions_per_week_next_year', "")

# Baseline Metrics
st.header("Baseline Metrics")
st.write(f"**Baseline Demand (Cases):** {total_demand_cases}")
st.write(f"**Baseline Capacity (Sessions in 12-Month Equivalent):** {baseline_capacity_sessions}")
st.write(f"**Baseline Demand (Minutes):** {total_demand_minutes}")

# Predicted Metrics for Next Year
st.header("Predicted Metrics for Next Year")
st.write(f"**Predicted Demand (Cases):** {total_demand_cases}")
st.write(f"**Session Model Planned (Sessions per Week):** {sessions_per_week_next_year}")
st.write(f"**Predicted Capacity (Total Minutes Available):** {session_minutes_next_year}")

# Waiting List Metrics
st.header("Waiting List Metrics")
st.write(f"**Predicted Waiting List at Start of Year:** {waiting_list_start}")
st.write(f"**Predicted Waiting List at End of Year:** {waiting_list_end}")

# Determine if waiting list is expected to grow, shrink, or maintain
if waiting_list_start != "" and waiting_list_end != "":
    change_in_waiting_list = waiting_list_end - waiting_list_start
    if change_in_waiting_list > 0:
        st.write(f"**Waiting List Expected to Grow:** {change_in_waiting_list:.0f} cases")
    elif change_in_waiting_list < 0:
        st.write(f"**Waiting List Expected to Shrink:** {-change_in_waiting_list:.0f} cases")
    else:
        st.write(f"**Waiting List Expected to Maintain:** No change expected")

# Required Sessions to Meet Demand
st.header("Required Sessions to Meet Demand")
st.write(f"**Sessions per Week Required to Meet Referral Demand:** {required_sessions_next_year:.0f}")
st.write(f"**Sessions per Week Planned Next Year:** {sessions_per_week_next_year}")

# Difference Between Required and Planned Sessions
if required_sessions_next_year != "" and sessions_per_week_next_year != "":
    difference_sessions = required_sessions_next_year - sessions_per_week_next_year
    if difference_sessions > 0:
        st.write(f"**Difference Between Required and Planned Sessions per Week (Shortfall):** {difference_sessions:.2f}")
    elif difference_sessions < 0:
        st.write(f"**Difference Between Required and Planned Sessions per Week (Surplus):** {abs(difference_sessions):.2f}")
    else:
        st.write(f"**Difference Between Required and Planned Sessions per Week:** No difference")

# Determine if capacity meets demand
if sessions_per_week_next_year != "" and required_sessions_next_year != "":
    st.header("Capacity vs. Demand")
    if sessions_per_week_next_year >= required_sessions_next_year:
        st.success("The planned capacity meets or exceeds the demand.")
    else:
        st.warning("The planned capacity does not meet the demand.")
