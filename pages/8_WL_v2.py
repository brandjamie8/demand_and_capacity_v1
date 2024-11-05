import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
st.title("Waiting List Dynamics")
st.write("""
Analyze the dynamics of the waiting list over the year, accounting for patients who will become overdue during the year.
""")
# Check if total demand cases are available
if 'total_demand_cases' in st.session_state:
   total_demand_cases = st.session_state.total_demand_cases
else:
   total_demand_cases = None
# Input variables
st.header("Input Waiting List Variables")
# Use the forecasted starting position from the Demand Analysis page
if 'forecasted_waiting_list_start' in st.session_state:
   default_waiting_list_start = st.session_state.forecasted_waiting_list_start
else:
   default_waiting_list_start = 500  # Default value if forecast is not available
if 'waiting_list_start' not in st.session_state:
   st.session_state.waiting_list_start = default_waiting_list_start
if 'waiting_list_additions' not in st.session_state:
   st.session_state.waiting_list_additions = total_demand_cases if total_demand_cases is not None else 1000
if 'waiting_list_removals' not in st.session_state:
   st.session_state.waiting_list_removals = 800
# Use widgets with unique keys
waiting_list_start = st.number_input(
   'Waiting List at the Start of the Year',
   min_value=0,
   value=st.session_state.waiting_list_start,
   key='input_waiting_list_start'
)
waiting_list_additions = st.number_input(
   'Number Added to Waiting List During the Year',
   min_value=0,
   value=st.session_state.waiting_list_additions,
   key='input_waiting_list_additions'
)
waiting_list_removals = st.number_input(
   'Number Removed from Waiting List During the Year',
   min_value=0,
   value=st.session_state.waiting_list_removals,
   key='input_waiting_list_removals'
)
# Save inputs to session state
st.session_state.waiting_list_start = waiting_list_start
st.session_state.waiting_list_additions = waiting_list_additions
st.session_state.waiting_list_removals = waiting_list_removals
# Calculate end of year waiting list
waiting_list_end = waiting_list_start + waiting_list_additions - waiting_list_removals
st.write(f"**Waiting List at End of Year:** {waiting_list_end:.0f}")
# Save calculation to session state
st.session_state.waiting_list_end = waiting_list_end
# Waterfall chart for waiting list dynamics
st.subheader('Waterfall Chart: Waiting List Dynamics')
measure = ["absolute", "relative", "relative", "total"]
x = ["Start of Year Waiting List", "Additions", "Removals", "End of Year Waiting List"]
y = [waiting_list_start, waiting_list_additions, -waiting_list_removals, waiting_list_end]
text = [f"{val:.0f}" for val in y]
waterfall_fig = go.Figure(go.Waterfall(
   name="Waiting List",
   orientation="v",
   measure=measure,
   x=x,
   y=y,
   textposition="outside",
   text=text,
   connector={"line": {"color": "rgb(63, 63, 63)"}},
   decreasing={"marker": {"color": "green"}},
   increasing={"marker": {"color": "red"}},
   totals={"marker": {"color": "blue"}}
))
waterfall_fig.update_layout(
   title="Waiting List Dynamics Over the Year",
   showlegend=False
)
st.plotly_chart(waterfall_fig, use_container_width=True)

st.header("Overdue Patients Forecasting")

months_in_year = 12

over_18_weeks = np.zeros(months_in_year)
over_52_weeks = np.zeros(months_in_year)

weekly_additions = waiting_list_additions / (months_in_year * 4.345)  # Approximate weeks in a month

current_waiting_list = np.full(52, waiting_list_start / 52)

total_removals = waiting_list_removals
weekly_removals = total_removals / (months_in_year * 4.345)
for week in range(1, months_in_year * 4 + 1):

   month_index = int((week - 1) / 4)

   current_waiting_list = np.roll(current_waiting_list, 1)
   current_waiting_list[0] = weekly_additions

   total_patients = current_waiting_list.sum()
   if total_patients > 0:
       removal_rate = weekly_removals / total_patients
   else:
       removal_rate = 0
   current_waiting_list *= max(0, 1 - removal_rate)

   over_18_weeks[month_index] += current_waiting_list[18:].sum()
   over_52_weeks[month_index] += current_waiting_list[52] if len(current_waiting_list) > 52 else 0

total_patients_over_18_weeks = over_18_weeks.sum()
total_patients_over_52_weeks = over_52_weeks.sum()

target_percent_over_18_weeks = 40.0
target_percent_over_52_weeks = 2.0

end_waiting_list = waiting_list_end
over_18_weeks_target = end_waiting_list * (target_percent_over_18_weeks / 100)
over_52_weeks_target = end_waiting_list * (target_percent_over_52_weeks / 100)

over_18_weeks_end = over_18_weeks[-1]
over_52_weeks_end = over_52_weeks[-1]

patients_to_treat_over_18_weeks = (over_18_weeks_end - over_18_weeks_target) + (total_patients_over_18_weeks - over_18_weeks_end)
patients_to_treat_over_52_weeks = (over_52_weeks_end - over_52_weeks_target) + (total_patients_over_52_weeks - over_52_weeks_end)

patients_to_treat_over_18_weeks = max(patients_to_treat_over_18_weeks, 0)
patients_to_treat_over_52_weeks = max(patients_to_treat_over_52_weeks, 0)

st.subheader("Overdue Cohorts Reduction Plan")
if 'percent_activity_over_18_weeks' not in st.session_state:
   st.session_state.percent_activity_over_18_weeks = 30.0  
if 'percent_activity_over_52_weeks' not in st.session_state:
   st.session_state.percent_activity_over_52_weeks = 10.0  
percent_activity_over_18_weeks = st.number_input(
   'Percentage of Activity Dedicated to Over 18 Weeks Cohort',
   min_value=0.0,
   max_value=100.0,
   value=st.session_state.percent_activity_over_18_weeks,
   step=0.1,
   key='input_percent_activity_over_18_weeks'
)
percent_activity_over_52_weeks = st.number_input(
   'Percentage of Activity Dedicated to Over 52 Weeks Cohort',
   min_value=0.0,
   max_value=100.0,
   value=st.session_state.percent_activity_over_52_weeks,
   step=0.1,
   key='input_percent_activity_over_52_weeks'
)

st.session_state.percent_activity_over_18_weeks = percent_activity_over_18_weeks
st.session_state.percent_activity_over_52_weeks = percent_activity_over_52_weeks

if 'session_duration_hours' in st.session_state and \
  'utilisation_next_year' in st.session_state and \
  'weeks_next_year' in st.session_state and \
  'sessions_per_week_next_year' in st.session_state:
   session_duration_hours = st.session_state.session_duration_hours
   utilisation_next_year = st.session_state.utilisation_next_year
   weeks_next_year = st.session_state.weeks_next_year
   sessions_per_week_next_year = st.session_state.sessions_per_week_next_year
else:
   st.error("Please complete the **Sessions Last Year** and **Demand vs Capacity** sections before proceeding.")
   st.stop()

if 'procedure_specialty_df' in st.session_state:
   procedure_specialty_df = st.session_state.procedure_specialty_df
   if 'average duration' in procedure_specialty_df.columns:
       average_procedure_duration = procedure_specialty_df['average duration'].mean()
   else:
       st.error("Procedure data does not contain 'average duration' column.")
       st.stop()
else:
   st.error("Procedure data is not available.")
   st.stop()

session_capacity_minutes = session_duration_hours * 60 * utilisation_next_year

minutes_needed_over_18_weeks = patients_to_treat_over_18_weeks * average_procedure_duration
minutes_needed_over_52_weeks = patients_to_treat_over_52_weeks * average_procedure_duration

sessions_needed_over_18_weeks = minutes_needed_over_18_weeks / session_capacity_minutes / (percent_activity_over_18_weeks / 100)
sessions_needed_over_52_weeks = minutes_needed_over_52_weeks / session_capacity_minutes / (percent_activity_over_52_weeks / 100)

total_sessions_needed = sessions_needed_over_18_weeks + sessions_needed_over_52_weeks

st.subheader("Sessions Needed to Achieve Target Overdue Cohort Sizes")
st.write(f"**Patients Over 18 Weeks at End of Year:** {over_18_weeks_end:.0f}")
st.write(f"**Target Patients Over 18 Weeks:** {over_18_weeks_target:.0f}")
st.write(f"**Total Patients to Treat Over 18 Weeks Cohort:** {patients_to_treat_over_18_weeks:.0f}")
st.write(f"**Sessions Needed for Over 18 Weeks Cohort:** {sessions_needed_over_18_weeks:.2f}")
st.write(f"**Patients Over 52 Weeks at End of Year:** {over_52_weeks_end:.0f}")
st.write(f"**Target Patients Over 52 Weeks:** {over_52_weeks_target:.0f}")
st.write(f"**Total Patients to Treat Over 52 Weeks Cohort:** {patients_to_treat_over_52_weeks:.0f}")
st.write(f"**Sessions Needed for Over 52 Weeks Cohort:** {sessions_needed_over_52_weeks:.2f}")
st.write(f"**Total Sessions Needed:** {total_sessions_needed:.2f}")

st.session_state.sessions_needed_over_18_weeks = sessions_needed_over_18_weeks
st.session_state.sessions_needed_over_52_weeks = sessions_needed_over_52_weeks
st.session_state.total_sessions_needed = total_sessions_needed
