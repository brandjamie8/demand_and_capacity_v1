# pages/5_Waiting_List_Dynamics.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Waiting List Dynamics")

st.write("""
Analyze the dynamics of the waiting list over the year.
""")

# Check if total demand cases are available
if 'total_demand_cases' in st.session_state:
    total_demand_cases = st.session_state.total_demand_cases
else:
    total_demand_cases = None

# Input variables
st.header("Input Waiting List Variables")

if 'waiting_list_start' not in st.session_state:
    st.session_state.waiting_list_start = 500

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
