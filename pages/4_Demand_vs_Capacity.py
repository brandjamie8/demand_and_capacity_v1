# pages/4_Demand_vs_Capacity.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Demand vs Capacity")

# Check if necessary data is available
if ('procedure_specialty_df' in st.session_state and st.session_state.procedure_specialty_df is not None) and \
   ('session_duration_hours' in st.session_state):
    procedure_specialty_df = st.session_state.procedure_specialty_df
    session_duration_hours = st.session_state.session_duration_hours
 
    # Calculate total sessions and session minutes next year
    total_sessions_next_year = st.session_state.weeks_last_year * st.session_state.sessions_per_week_last_year
    session_minutes_next_year = total_sessions_next_year * session_duration_hours * 60 * st.session_state.utilisation_last_year

    st.write(f"**Total Sessions Next Year:** {total_sessions_next_year:.0f}")
    st.write(f"**Total Session Minutes Next Year (after Utilisation):** {session_minutes_next_year:.0f}")

    # Save calculations to session state
    st.session_state.total_sessions_next_year = total_sessions_next_year
    st.session_state.session_minutes_next_year = session_minutes_next_year

    # Total demand
    total_demand_cases = procedure_specialty_df['total referrals'].sum()
    total_demand_minutes = procedure_specialty_df['demand minutes'].sum()

    st.write(f"**Total Demand (Cases):** {total_demand_cases:.0f}")
    st.write(f"**Total Demand (Minutes):** {total_demand_minutes:.0f}")

    # Save demand calculations to session state
    st.session_state.total_demand_cases = total_demand_cases
    st.session_state.total_demand_minutes = total_demand_minutes

    # Compare demand and capacity
    st.header("Demand vs Capacity Comparison")

    demand_vs_capacity_df = pd.DataFrame({
        'Category': ['Total Demand Minutes', 'Total Capacity Minutes'],
        'Minutes': [total_demand_minutes, session_minutes_next_year]
    })

    fig_demand_vs_capacity = px.bar(
        demand_vs_capacity_df,
        x='Category',
        y='Minutes',
        title='Demand vs Capacity in Minutes',
        text='Minutes'
    )
    st.plotly_chart(fig_demand_vs_capacity, use_container_width=True)

    # Calculate sessions required to meet demand
    required_sessions_next_year = total_demand_minutes / (session_duration_hours * 60 * st.session_state.utilisation_last_year) / st.session_state.weeks_last_year

    st.write(f"**Sessions per Week Required to Meet Demand:** {required_sessions_next_year:.2f}")
    st.write(f"**Sessions per Week Planned Next Year:** {st.session_state.sessions_per_week_last_year:.2f}")

    # Save required sessions to session state
    st.session_state.required_sessions_next_year = required_sessions_next_year

    # Determine if capacity meets demand
    if st.session_state.sessions_per_week_last_year >= required_sessions_next_year:
        st.success("The planned capacity meets or exceeds the demand.")
    else:
        st.warning("The planned capacity does not meet the demand.")
else:
    st.write("Please ensure you have completed the **Procedure Demand** and **Sessions Last Year** sections.")
