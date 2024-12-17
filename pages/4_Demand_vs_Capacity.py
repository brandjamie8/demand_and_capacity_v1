import streamlit as st 
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px


st.title("Demand vs Capacity")

# Check if necessary data is available
if ('procedure_specialty_df' in st.session_state and st.session_state.procedure_specialty_df is not None) and \
   ('procedures_from_acpl' in st.session_state) and ('total_predicted_cases' in st.session_state) and \
   ('sessions_per_week_last_year' in st.session_state) and ('weeks_last_year' in st.session_state) and \
   ('session_duration_hours' in st.session_state) and ('utilisation_last_year' in st.session_state):
    
    procedure_specialty_df = st.session_state.procedure_specialty_df

    # Select specialty
    specialties = procedure_specialty_df['specialty'].unique()
    selected_specialty = st.selectbox("Select Specialty:", specialties)

    # Filter data for the selected specialty
    filtered_df = procedure_specialty_df[procedure_specialty_df['specialty'] == selected_specialty]

    # Demand and Capacity (Cases)
    total_demand_cases = st.session_state.total_predicted_cases
    total_capacity_cases = st.session_state.procedures_from_acpl

    st.write(f"**Total Demand (Cases) for {selected_specialty}:** {total_demand_cases:.0f}")
    st.write(f"**Total Capacity (Cases) for {selected_specialty}:** {total_capacity_cases:.0f}")

    # Calculate the number of sessions planned and sessions needed
    sessions_per_week_planned = st.session_state.sessions_per_week_last_year
    total_sessions_planned = sessions_per_week_planned * st.session_state.weeks_last_year

    session_minutes_per_week = st.session_state.session_duration_hours * 60 * st.session_state.utilisation_last_year
    total_session_minutes = total_sessions_planned * session_minutes_per_week
    average_case_minutes = total_session_minutes / total_capacity_cases

    sessions_per_week_required = total_demand_cases * average_case_minutes / session_minutes_per_week

    st.write(f"**Sessions Planned Next Year (Weekly):** {sessions_per_week_planned:.2f}")
    st.write(f"**Sessions Required to Meet Demand (Weekly):** {sessions_per_week_required:.2f}")
    st.write(f"**Total Sessions Planned Next Year:** {total_sessions_planned:.0f}")

    # Compare demand and capacity
    st.header("Demand vs Capacity Comparison (Cases)")

    demand_vs_capacity_df = pd.DataFrame({
        'Category': ['Total Demand Cases', 'Total Capacity Cases'],
        'Cases': [round(total_demand_cases), round(total_capacity_cases)]
    })

    fig_demand_vs_capacity = px.bar(
        demand_vs_capacity_df,
        x='Category',
        y='Cases',
        title=f'Demand vs Capacity in Cases for {selected_specialty}',
        text='Cases'
    )
    fig_demand_vs_capacity.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    st.plotly_chart(fig_demand_vs_capacity, use_container_width=True)

    difference = total_capacity_cases - total_demand_cases
    if difference >= 0:
        st.success(
            f"The capacity exceeds the demand by **{difference:.0f} cases**, which should help reduce the waiting list backlog."
        )
    else:
        st.warning(
            f"The demand exceeds the capacity by **{abs(difference):.0f} cases**, indicating a shortfall. "
            f"This mismatch is equivalent to an additional **{abs(sessions_per_week_required - sessions_per_week_planned):.2f} sessions per week** needed. "
            f"Without addressing this, the waiting list is expected to grow."
        )

    # Summary of findings
    st.write("### Summary")
    st.write(f"- **Planned Capacity:** {total_capacity_cases:.0f} cases with {sessions_per_week_planned:.2f} sessions per week.")
    st.write(f"- **Demand:** {total_demand_cases:.0f} cases requiring {sessions_per_week_required:.2f} sessions per week.")
    st.write(f"- **Difference:** {difference:.0f} cases.")

    if difference < 0:
        st.write("The current capacity is insufficient to meet demand, leading to an expected increase in the waiting list.")
    else:
        st.write("The current capacity is sufficient to meet demand, which should stabilize or reduce the waiting list.")
else:
    st.write("Please ensure you have completed the required sections and loaded all necessary data into session state.")

