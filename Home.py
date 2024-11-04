# Home.py

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title='Admitted Demand and Capacity Analysis',
    page_icon='📈',
    layout='wide'
)

st.title('Welcome to the Admitted Demand and Capacity Analysis App')

st.write("""
This application allows you to analyze procedure demand, capacity, and waiting list dynamics.

Use the navigation on the left to select different sections of the analysis.
""")

# Initialize session state variables if they don't exist
if 'waiting_list_df' not in st.session_state:
    st.session_state.waiting_list_df = None

if 'procedure_df' not in st.session_state:
    st.session_state.procedure_df = None

if 'selected_specialty' not in st.session_state:
    st.session_state.selected_specialty = None

# Sidebar Uploaders
st.sidebar.header('Upload Data Files')

waiting_list_file = st.sidebar.file_uploader(
    "Upload Waiting List Data CSV",
    type='csv',
    key='waiting_list_file'
)

procedure_data_file = st.sidebar.file_uploader(
    "Upload Procedure Data CSV",
    type='csv',
    key='procedure_data_file'
)

# Save uploaded files to session state
if waiting_list_file is not None:
    st.session_state.waiting_list_df = pd.read_csv(waiting_list_file)

    # Display the head of the waiting list data
    st.subheader("Waiting List Data Preview")
    st.write("Here are the first few rows of the Waiting List Data:")
    st.dataframe(st.session_state.waiting_list_df.head())

else:
    st.write("Please upload the **Waiting List Data CSV** file in the sidebar.")

if procedure_data_file is not None:
    st.session_state.procedure_df = pd.read_csv(procedure_data_file)

    # Display the head of the procedure data
    st.subheader("Procedure Data Preview")
    st.write("Here are the first few rows of the Procedure Data:")
    st.dataframe(st.session_state.procedure_df.head())

else:
    st.write("Please upload the **Procedure Data CSV** file in the sidebar.")
