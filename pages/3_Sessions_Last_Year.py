# pages/3_Sessions_Last_Year.py

import streamlit as st

st.title("Sessions Last Year")

st.write("""
In this section, you can input variables related to last year's sessions,
such as weeks per year, sessions per week, utilisation percentage, and session duration.
The app will calculate the total sessions and session minutes for last year.
""")

# Initialize session state variables if they don't exist
if 'weeks_last_year' not in st.session_state:
    st.session_state.weeks_last_year = 48

if 'sessions_per_week_last_year' not in st.session_state:
    st.session_state.sessions_per_week_last_year = 10.0

if 'utilisation_last_year' not in st.session_state:
    st.session_state.utilisation_last_year = 0.80

if 'session_duration_hours' not in st.session_state:
    st.session_state.session_duration_hours = 4.0

# Input variables for last year
st.header("Input Last Year's Session Variables")

weeks_last_year = st.number_input("Weeks per Year (Last Year)", min_value=1, max_value=52, value=st.session_state.weeks_last_year, key='weeks_last_year')
sessions_per_week_last_year = st.number_input("Sessions per Week (Last Year)", min_value=0.0, value=st.session_state.sessions_per_week_last_year, step=0.1, key='sessions_per_week_last_year')
utilisation_last_year = st.slider("Utilisation Percentage (Last Year)", min_value=0.0, max_value=1.0, value=st.session_state.utilisation_last_year, step=0.01, key='utilisation_last_year')
session_duration_hours = st.number_input("Session Duration (Hours)", min_value=0.0, value=st.session_state.session_duration_hours, step=0.5, key='session_duration_hours')

# Save inputs to session state
st.session_state.weeks_last_year = weeks_last_year
st.session_state.sessions_per_week_last_year = sessions_per_week_last_year
st.session_state.utilisation_last_year = utilisation_last_year
st.session_state.session_duration_hours = session_duration_hours

# Calculate total sessions and session minutes last year
total_sessions_last_year = weeks_last_year * sessions_per_week_last_year
session_minutes_last_year = total_sessions_last_year * session_duration_hours * 60 * utilisation_last_year

st.write(f"**Total Sessions Last Year:** {total_sessions_last_year:.2f}")
st.write(f"**Total Session Minutes Last Year (after Utilisation):** {session_minutes_last_year:.0f}")

# Save calculations to session state
st.session_state.total_sessions_last_year = total_sessions_last_year
st.session_state.session_minutes_last_year = session_minutes_last_year
