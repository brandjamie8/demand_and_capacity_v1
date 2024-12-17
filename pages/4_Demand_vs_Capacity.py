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
   ('acpl' in st.session_state):

    procedure_specialty_df = st.session_state.procedure_specialty_df

    # Select specialty
    specialties = procedure_specialty_df['specialty'].unique()
    selected_specialty = st.selectbox("Select Specialty:", specialties)

    # Filter data for the selected specialty
    filtered_df = procedure_specialty_df[procedure_specialty_df['specialty'] == selected_specialty]

    # Demand and Capacity (Cases)
    total_demand_cases = st.session_state.total_predicted_cases
    total_capacity_cases = st.session_state.procedures_from_acpl
    average_cases_per_list = st.session_state.acpl  # Average cases per session/list
    weeks_in_year = st.session_state.weeks_last_year

    # Calculate sessions
    total_sessions_required = total_demand_cases / average_cases_per_list
    sessions_per_week_required = total_sessions_required / weeks_in_year
    sessions_per_week_planned = st.session_state.sessions_per_week_last_year

    st.write(f"**Total Demand (Cases) for {selected_specialty}:** {total_demand_cases:.0f}")
    st.write(f"**Total Capacity (Cases) for {selected_specialty}:** {total_capacity_cases:.0f}")
    st.write(f"**Average Cases Per List:** {average_cases_per_list:.2f}")

    # Compare Demand and Capacity
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

    st.write(f"**Sessions Planned Per Week:** {sessions_per_week_planned:.2f}")
    st.write(f"**Sessions Required Per Week to Meet Demand:** {sessions_per_week_required:.2f}")
    st.write(f"**Total Sessions Required for the Year:** {total_sessions_required:.0f}")
    st.write(f"**Total Sessions Planned for the Year:** {sessions_per_week_planned * weeks_in_year:.0f}")

    difference = total_capacity_cases - total_demand_cases
    if difference >= 0:
        st.success(
            f"The capacity exceeds the demand by **{difference:.0f} cases**, which should help reduce the waiting list backlog."
        )
    else:
        shortfall_sessions = abs(total_sessions_required - sessions_per_week_planned * weeks_in_year)
        st.warning(
            f"The demand exceeds the capacity by **{abs(difference):.0f} cases**, indicating a shortfall. "
            f"This is equivalent to **{shortfall_sessions:.0f} sessions for the year**, or an additional **{sessions_per_week_required - sessions_per_week_planned:.2f} sessions per week** needed. "
            f"Without addressing this, the waiting list is expected to grow."
        )

    # Summary of Findings
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
