import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Waiting List Dynamics")

st.write("""
Analyse the dynamics of the waiting list over the year, including backlog and future demand.
""")

# Check if required session state variables exist
if 'procedure_specialty_df' in st.session_state and 'weeks_last_year' in st.session_state and 'acpl' in st.session_state:
    
    # Select specialty
    specialties = st.session_state.procedure_specialty_df['specialty'].unique()
    selected_specialty = st.selectbox("Select Specialty:", specialties)

    # Filter data by selected specialty
    filtered_df = st.session_state.procedure_specialty_df[st.session_state.procedure_specialty_df['specialty'] == selected_specialty]

    # Inputs for waiting list dynamics
    st.header("Input Waiting List Variables")

    if 'waiting_list_start' not in st.session_state:
        st.session_state.waiting_list_start = 500

    waiting_list_start = st.number_input(
        'Waiting List at the Start of the Year',
        min_value=0,
        value=int(st.session_state.waiting_list_start),
        key='input_waiting_list_start'
    )

    waiting_list_additions = st.session_state.total_predicted_cases  # Demand for the year
    waiting_list_removals = st.session_state.procedures_from_acpl  # Capacity for the year

    # Save to session state
    st.session_state.waiting_list_start = waiting_list_start
    st.session_state.waiting_list_additions = waiting_list_additions
    st.session_state.waiting_list_removals = waiting_list_removals

    # End of Year Waiting List
    waiting_list_end = waiting_list_start + waiting_list_additions - waiting_list_removals
    st.write(f"**Waiting List at End of Year:** {waiting_list_end:.0f}")

    # Add Backlog from Latest Month
    st.header("Backlog Integration")

    # Assume 'waiting_list_data' exists in session state
    if 'waiting_list_df' in st.session_state:
        waiting_list_data = st.session_state.waiting_list_df

        # Get latest month's backlog
        latest_month_data = waiting_list_data.iloc[-1]
        backlog_18_plus = latest_month_data['18+']
        backlog_40_plus = latest_month_data['40+']
        backlog_52_plus = latest_month_data['52+']

        st.write(f"**Backlog (18+ weeks):** {backlog_18_plus:.0f}")
        st.write(f"**Backlog (40+ weeks):** {backlog_40_plus:.0f}")
        st.write(f"**Backlog (52+ weeks):** {backlog_52_plus:.0f}")

        # Calculate total demand including backlog
        demand_18_plus = waiting_list_additions + backlog_18_plus
        demand_40_plus = waiting_list_additions + backlog_40_plus
        demand_52_plus = waiting_list_additions + backlog_52_plus

        st.write(f"**Demand + Backlog (18+ weeks):** {demand_18_plus:.0f}")
        st.write(f"**Demand + Backlog (40+ weeks):** {demand_40_plus:.0f}")
        st.write(f"**Demand + Backlog (52+ weeks):** {demand_52_plus:.0f}")

        # Calculate sessions needed
        average_cases_per_list = st.session_state.acpl
        weeks_in_year = st.session_state.weeks_last_year

        sessions_required_18 = demand_18_plus / average_cases_per_list / weeks_in_year
        sessions_required_40 = demand_40_plus / average_cases_per_list / weeks_in_year
        sessions_required_52 = demand_52_plus / average_cases_per_list / weeks_in_year

        sessions_planned = st.session_state.sessions_per_week_last_year

        # Display results
        st.subheader("Sessions Needed to Clear Backlog + Demand")
        st.write(f"- **Sessions per Week (18+ weeks):** {sessions_required_18:.2f}")
        st.write(f"- **Sessions per Week (40+ weeks):** {sessions_required_40:.2f}")
        st.write(f"- **Sessions per Week (52+ weeks):** {sessions_required_52:.2f}")
        st.write(f"- **Sessions Planned per Week:** {sessions_planned:.2f}")

        # Highlight mismatch
        st.header("Mismatch Analysis")
        if sessions_planned >= sessions_required_18:
            st.success("The planned capacity can clear the 18+ backlog and demand.")
        else:
            st.warning("The planned capacity is insufficient to clear the 18+ backlog and demand.")

        if sessions_planned >= sessions_required_40:
            st.success("The planned capacity can clear the 40+ backlog and demand.")
        else:
            st.warning("The planned capacity is insufficient to clear the 40+ backlog and demand.")

        if sessions_planned >= sessions_required_52:
            st.success("The planned capacity can clear the 52+ backlog and demand.")
        else:
            st.warning("The planned capacity is insufficient to clear the 52+ backlog and demand.")

        # Waterfall Chart for Waiting List Dynamics
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

    else:
        st.error("Waiting list backlog data is not available. Please ensure it is loaded into session state.")
else:
    st.error("Please ensure you have completed the required sections and loaded all necessary data into session state.")
