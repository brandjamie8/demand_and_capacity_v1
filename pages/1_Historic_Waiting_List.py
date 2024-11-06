# pages/1_Waiting_List_Analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Historic Waiting List")

# Check if data is available in session state
if st.session_state.waiting_list_df is not None and st.session_state.procedure_df is not None:
    waiting_list_df = st.session_state.waiting_list_df
    procedure_df = st.session_state.procedure_df

    # Ensure required columns are present
    waiting_list_required_columns = ['month', 'specialty', 'additions to waiting list', 'removals from waiting list', 'total waiting list']
    procedure_required_columns = ['specialty', 'procedure', 'total referrals', 'average duration']

    if all(column in waiting_list_df.columns for column in waiting_list_required_columns) and \
       all(column in procedure_df.columns for column in procedure_required_columns):

        # Select specialty
        specialties = waiting_list_df['specialty'].unique()
        if st.session_state.selected_specialty is None:
            st.session_state.selected_specialty = specialties[0]

        selected_specialty = st.selectbox('Select Specialty', specialties, index=list(specialties).index(st.session_state.selected_specialty), key='specialty_select')

        # Save the selected specialty to session state
        st.session_state.selected_specialty = selected_specialty

        # Filter data based on selected specialty
        waiting_list_specialty_df = waiting_list_df[waiting_list_df['specialty'] == selected_specialty]
        procedure_specialty_df = procedure_df[procedure_df['specialty'] == selected_specialty]

        # Convert 'month' column to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(waiting_list_specialty_df['month']):
            waiting_list_specialty_df['month'] = pd.to_datetime(waiting_list_specialty_df['month'])

        # Sort by month
        waiting_list_specialty_df = waiting_list_specialty_df.sort_values('month')

        # Create charts

        # Chart 1: Additions to waiting list and removals from waiting list on the same chart
        st.subheader("Additions and Removals from Waiting List Over Time")
        fig1 = px.line(
            waiting_list_specialty_df,
            x='month',
            y=['additions to waiting list', 'removals from waiting list'],
            labels={'value': 'Number of Patients', 'variable': 'Legend'},
            title='Additions and Removals from Waiting List'
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: Total size of the waiting list
        st.subheader("Total Size of the Waiting List Over Time")
        fig2 = px.line(
            waiting_list_specialty_df,
            x='month',
            y='total waiting list',
            labels={'total waiting list': 'Total Waiting List'},
            title='Total Size of the Waiting List'
        )
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.error("Uploaded files do not contain the required columns.")
else:
    st.write("Please upload both the Waiting List Data CSV and the Procedure Data CSV files in the sidebar on the **Home** page.")
