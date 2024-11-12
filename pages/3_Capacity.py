import streamlit as st
import pandas as pd

st.title("Capacity")

st.write("""
In this section, you can look at the number of cases and sessions in the baseline period, 
what this would mean in whole-year terms and build a session model based on weeks per year, sessions per week and utilisation percentage.
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

specialties = waiting_list_df['specialty'].unique()
if 'selected_specialty' not in st.session_state or st.session_state.selected_specialty not in specialties:
    st.session_state.selected_specialty = specialties[0]

col1, _ = st.columns(2)
with col1:
    selected_specialty = st.selectbox(
        'Select Specialty',
        specialties,
        index=list(specialties).index(st.session_state.selected_specialty),
        key='procedure_demand_specialty_select'
    )

# Save the selected specialty to session state
st.session_state.selected_specialty = selected_specialty

# Filter data for the baseline period
waiting_list_df['month'] = pd.to_datetime(waiting_list_df['month']) + pd.offsets.MonthEnd(0)
baseline_df = waiting_list_df[(waiting_list_df['month'] >= baseline_start) & (waiting_list_df['month'] <= baseline_end) & (waiting_list_df['specialty'] == selected_specialty)] 

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

# Calculate ACPL
cases_per_session = total_cases_baseline / total_sessions_baseline

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
st.write(f"**Total Sessions in Baseline Period:** {total_sessions_baseline:.0f}")
st.write(f"**Total Minutes Utilised in Baseline Period:** {total_minutes_utilised_baseline:.0f}")
st.write(f"**Baseline Utilisation Percentage:** {baseline_utilisation:.2%}")
st.write(f"**Baseline Average Cases Per Session:** {cases_per_session:.2f}")

# Display scaled-up values equivalent to 12 months
st.header("Equivalent 12-Month Period Statistics")
st.write(f"**Total Cases (12-Month Equivalent):** {total_cases_12_months:.0f}")
st.write(f"**Total Sessions (12-Month Equivalent):** {total_sessions_12_months:.0f}")
st.write(f"**Total Minutes Utilised (12-Month Equivalent):** {total_minutes_12_months:.0f}")


# Calculate the sessions per week on weeks model
sessions_in_42wk_model = total_sessions_12_months / 42
sessions_in_45wk_model = total_sessions_12_months / 45
sessions_in_48wk_model = total_sessions_12_months / 48

st.write(f"{total_sessions_12_months:.0f} sessions in 12 months translated into weekly operating models:")

col1, _, _ = st.columns(3)
with col1:
    # Get custom weeks input
    custom_weeks = st.number_input(
        "Enter Custom Number of Weeks",
        min_value=1,
        max_value=52,
        value=52,
        step=1,
        key='input_custom_weeks'
    )
sessions_in_custom_weeks_model = total_sessions_12_months / custom_weeks

# Create a DataFrame to display the results in a table
summary_data = {
    'Operating Model': ['42 weeks of year', '45 weeks of year', '48 weeks of year', f'{custom_weeks} weeks of year (custom)'],
    'Sessions per Week': [round(sessions, 1) for sessions in [sessions_in_42wk_model, sessions_in_45wk_model, sessions_in_48wk_model, sessions_in_custom_weeks_model]]
}

summary_df = pd.DataFrame(summary_data)

col1, _ = st.columns(2)
col1 = st.dataframe(summary_df)


# Initialise session state variables if they don't exist
if 'weeks_last_year' not in st.session_state:
    st.session_state.weeks_last_year = 48

if 'sessions_per_week_last_year' not in st.session_state:
    st.session_state.sessions_per_week_last_year = 10.0

if 'utilisation_last_year' not in st.session_state:
    st.session_state.utilisation_last_year = 0.80

if 'session_duration_hours' not in st.session_state:
    st.session_state.session_duration_hours = 4.0

# Input variables for last year
st.header("Input Variables to Create a Session Model")

col1, col2, _ = st.columns(3)

with col1:
    weeks_last_year = st.number_input(
        "Weeks per Year",
        min_value=1,
        max_value=52,
        value=st.session_state.weeks_last_year,
        key='input_weeks_last_year'
    )
with col2:
    sessions_per_week_last_year = st.number_input(
        "Sessions per Week",
        min_value=0.0,
        value=st.session_state.sessions_per_week_last_year,
        step=0.1,
        key='input_sessions_per_week_last_year'
    )
utilisation_last_year = st.slider(
    "Utilisation Percentage",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.utilisation_last_year,
    step=0.01,
    key='input_utilisation_last_year'
)
session_duration_hours = 4

# Save inputs to session state
st.session_state.weeks_last_year = weeks_last_year
st.session_state.sessions_per_week_last_year = sessions_per_week_last_year
st.session_state.utilisation_last_year = utilisation_last_year
st.session_state.session_duration_hours = session_duration_hours

# Calculate total sessions and session minutes last year
total_sessions_last_year = weeks_last_year * sessions_per_week_last_year
session_minutes_last_year = total_sessions_last_year * session_duration_hours * 60 * utilisation_last_year

st.write(f"**Total Sessions in Model:** {total_sessions_last_year:.0f}")
st.write(f"**Total Session Minutes in Model (after Utilisation):** {session_minutes_last_year:.0f}")

# Save calculations to session state
st.session_state.total_sessions_last_year = total_sessions_last_year
st.session_state.session_minutes_last_year = session_minutes_last_year
