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

# Define file paths
WAITING_LIST_FILE_PATH = "data/waiting_list.csv"
PROCEDURE_DATA_FILE_PATH = "data/procedure_data.csv"

try:
    # Load data from file paths
    waiting_list_df = pd.read_csv(WAITING_LIST_FILE_PATH)
    procedure_df = pd.read_csv(PROCEDURE_DATA_FILE_PATH)

    # Save data to session state
    st.session_state.waiting_list_df = waiting_list_df
    st.session_state.procedure_df = procedure_df

    # Initialize selected specialty if not already set
    if 'selected_specialty' not in st.session_state:
        st.session_state.selected_specialty = None

    # Set available specialties from the waiting list data
    specialties = waiting_list_df['specialty'].unique()

    # Let the user select a specialty
    if st.session_state.selected_specialty is None:
        st.session_state.selected_specialty = specialties[0]  # Default to the first specialty

    selected_specialty = st.selectbox('Select Specialty', specialties, index=list(specialties).index(st.session_state.selected_specialty))
    
    # Save the selected specialty to session state
    st.session_state.selected_specialty = selected_specialty

    # Display previews of the datasets
    st.subheader("Waiting List Data Preview")
    st.write("Here are the first few rows of the Waiting List Data:")
    st.dataframe(waiting_list_df.head())

    st.subheader("Procedure Data Preview")
    st.write("Here are the first few rows of the Procedure Data:")
    st.dataframe(procedure_df.head())

except FileNotFoundError as e:
    st.error(f"Error loading data: {e}. Please ensure the CSV files are located at the correct file paths.")

st.sidebar.header('Data Files Loaded Successfully')
