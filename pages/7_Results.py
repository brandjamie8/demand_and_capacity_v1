# pages/6_Results.py

import streamlit as st

st.title("Results")

st.write("""
This section summarizes the key results from the previous sections.
""")

# Check if necessary data is available
if all(key in st.session_state for key in [
    'total_demand_cases',
    'total_demand_minutes',
    'session_minutes_next_year',
    'waiting_list_start',
    'waiting_list_end',
    'required_sessions_next_year',
    'sessions_per_week_next_year'
]):
    total_demand_cases = st.session_state.total_demand_cases
    total_demand_minutes = st.session_state.total_demand_minutes
    session_minutes_next_year = st.session_state.session_minutes_next_year
    waiting_list_start = st.session_state.waiting_list_start
    waiting_list_end = st.session_state.waiting_list_end
    required_sessions_next_year = st.session_state.required_sessions_next_year
    sessions_per_week_next_year = st.session_state.sessions_per_week_next_year

    # Expected change in waiting list next year – start and finish (and backlog)
    change_in_waiting_list = waiting_list_end - waiting_list_start

    st.write(f"**Total Demand (Cases):** {total_demand_cases:.0f}")
    st.write(f"**Total Demand (Minutes):** {total_demand_minutes:.0f}")
    st.write(f"**Total Capacity Minutes Next Year:** {session_minutes_next_year:.0f}")

    st.write(f"**Waiting List at Start of Year:** {waiting_list_start:.0f}")
    st.write(f"**Waiting List at End of Year:** {waiting_list_end:.0f}")
    st.write(f"**Change in Waiting List:** {change_in_waiting_list:.0f}")

    st.write(f"**Sessions per Week Required to Meet Demand:** {required_sessions_next_year:.2f}")
    st.write(f"**Sessions per Week Planned Next Year:** {sessions_per_week_next_year:.2f}")

    difference_sessions = required_sessions_next_year - sessions_per_week_next_year
    st.write(f"**Difference between Required and Planned Sessions per Week Next Year:** {difference_sessions:.2f}")

    # Determine if capacity meets demand
    if sessions_per_week_next_year >= required_sessions_next_year:
        st.success("The planned capacity meets or exceeds the demand.")
    else:
        st.warning("The planned capacity does not meet the demand.")

else:
    st.write("Please ensure you have completed all previous sections to view the results.")
