import streamlit as st
import pandas as pd

st.title("Sessions Last Year")

st.write("""
In this section, you can input variables related to last year's sessions,
such as weeks per year, sessions per week, utilisation percentage, and session duration.
The app will calculate the total sessions and session minutes for last year.
""")

# Load the waiting list data from session state
if 'waiting_list_df' not in st.session_state or st.session_state.waiting_list_df is None:
    st.error("Waiting list data is not available. Please upload the data in the previous section.")
    st.stop()

waiting_list_df = st.session_state.waiting_list_df

# Retrieve baseline period from session state and ensure they are consistent
if 'baseline_start_date' not in st.session_state or 'baseline_end_date' not in st.session_state:
    st.error("Baseline period not found. Please set the baseline period in the previous page.")
    st.stop()

# Convert the baseline dates to month-end Timestamps
baseline_start = pd.to_datetime(st.session_state.baseline_start_date).to_period('M').to_timestamp('M')
baseline_end = pd.to_datetime(st.session_state.baseline_end_date).to_period('M').to_timestamp('M')

# Filter data for the baseline period
waiting_list_df['month'] = pd.to_datetime(waiting_list_df['month']) + pd.offsets.MonthEnd(0)
baseline_df = waiting_list_df[(waiting_list_df['month'] >= baseline_start) & (waiting_list_df['month'] <= baseline_end)]

# Calculate the number of months in the baseline period
num_baseline_months = len(pd.date_range(start=baseline_start, end=baseline_end, freq='M'))

# Calculate total cases, sessions, and minutes utilised in the baseline period
total_cases_baseline = baseline_df['additions to waiting list'].sum()
total_sessions_baseline = baseline_df['sessions'].sum()  # Use sessions from waiting_list_df
session_duration_hours = 4

# Calculate minutes utilised
total_minutes_utilised_baseline = baseline_df['minutes utilised'].sum() 

# Calculate baseline utilisation
total_minutes_possible_baseline = total_sessions_baseline * session_duration_hours * 60
baseline_utilisation = total_minutes_utilised_baseline / total_minutes_possible_baseline if total_minutes_possible_baseline > 0 else 0

# Scale up to equivalent 12-month period
scaling_factor = 12 / num_baseline_months
total_cases_12_months = total_cases_baseline * scaling_factor
total_sessions_12_months = total_sessions_baseline * scaling_factor
total_minutes_12_months = total_minutes_utilised_baseline * scaling_factor

# Display baseline statistics
st.header("Baseline Period Statistics")
st.write(f"**Baseline Period:** {baseline_start.strftime('%b %Y')} to {baseline_end.strftime('%b %Y')}")
st.write(f"**Number of Months in Baseline Period:** {num_baseline_months}")
st.write(f"**Total Cases in Baseline Period:** {total_cases_baseline:.0f}")
st.write(f"**Total Sessions in Baseline Period:** {total_sessions_baseline:.2f}")
st.write(f"**Total Minutes Utilised in Baseline Period:** {total_minutes_utilised_baseline:.0f}")
st.write(f"**Baseline Utilisation Percentage:** {baseline_utilisation:.2%}")

# Display scaled-up values equivalent to 12 months
st.header("Equivalent 12-Month Period Statistics")
st.write(f"**Total Cases (12-Month Equivalent):** {total_cases_12_months:.0f}")
st.write(f"**Total Sessions (12-Month Equivalent):** {total_sessions_12_months:.2f}")
st.write(f"**Total Minutes Utilised (12-Month Equivalent):** {total_minutes_12_months:.0f}")

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

# Use unique keys for widgets to avoid conflicts
weeks_last_year = st.number_input(
    "Weeks per Year (Last Year)",
    min_value=1,
    max_value=52,
    value=st.session_state.weeks_last_year,
    key='input_weeks_last_year'
)
sessions_per_week_last_year = st.number_input(
    "Sessions per Week (Last Year)",
    min_value=0.0,
    value=st.session_state.sessions_per_week_last_year,
    step=0.1,
    key='input_sessions_per_week_last_year'
)
utilisation_last_year = st.slider(
    "Utilisation Percentage (Last Year)",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.utilisation_last_year,
    step=0.01,
    key='input_utilisation_last_year'
)
session_duration_hours = st.number_input(
    "Session Duration (Hours)",
    min_value=0.0,
    value=st.session_state.session_duration_hours,
    step=0.5,
    key='input_session_duration_hours'
)

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
