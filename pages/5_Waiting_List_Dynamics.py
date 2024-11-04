# pages/5_Waiting_List_Dynamics.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Waiting List Dynamics")

st.write("""
Analyze the dynamics of the waiting list over the year.
""")

# Input variables
st.header("Input Waiting List Variables")

waiting_list_start = st.number_input('Waiting List at the Start of the Year', min_value=0, value=500)
waiting_list_additions = st.number_input('Number Added to Waiting List During the Year', min_value=0, value=1000)
waiting_list_removals = st.number_input('Number Removed from Waiting List During the Year', min_value=0, value=800)

# Calculate end of year waiting list
waiting_list_end = waiting_list_start + waiting_list_additions - waiting_list_removals

st.write(f"**Waiting List at End of Year:** {waiting_list_end:.0f}")

# Waterfall chart for waiting list dynamics
st.subheader('Waterfall Chart: Waiting List Dynamics')

measure = ["absolute", "relative", "relative", "total"]

x = ["Start of Year Waiting List", "Additions", "Removals", "End of Year Waiting List"]
y = [waiting_list_start, waiting_list_additions, -waiting_list_removals, waiting_list_end]

text = [f"{val:.0f}" for val in y]

waterfall_fig = go.Figure(go.Waterfall(
    name = "Waiting List",
    orientation = "v",
    measure = measure,
    x = x,
    y = y,
    textposition = "outside",
    text = text,
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
    decreasing={"marker":{"color":"green"}},
    increasing={"marker":{"color":"red"}},
    totals={"marker":{"color":"blue"}}
))

waterfall_fig.update_layout(
    title = "Waiting List Dynamics Over the Year",
    showlegend = False
)

st.plotly_chart(waterfall_fig, use_container_width=True)
