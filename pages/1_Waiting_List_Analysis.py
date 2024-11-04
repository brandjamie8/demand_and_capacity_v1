# pages/1_Waiting_List_Analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Waiting List Analysis")

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

if waiting_list_file is not None and procedure_data_file is not None:
    # Read the data
    waiting_list_df = pd.read_csv(waiting_list_file)
    procedure_df = pd.read_csv(procedure_data_file)
    
    # Ensure required columns are present
    waiting_list_required_columns = ['month', 'specialty', 'additions to waiting list', 'removals from waiting list', 'total waiting list']
    procedure_required_columns = ['specialty', 'procedure', 'total referrals', 'average duration']
    
    if all(column in waiting_list_df.columns for column in waiting_list_required_columns) and \
       all(column in procedure_df.columns for column in procedure_required_columns):
        
        # Select specialty
        specialties = waiting_list_df['specialty'].unique()
        selected_specialty = st.selectbox('Select Specialty', specialties)
        
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
        
        # Below, side by side charts for procedure data
        st.subheader("Top 10 Procedures by Demand")
        col1, col2 = st.columns(2)
        
        # Ensure 'average duration' is numeric
        procedure_specialty_df['average duration'] = pd.to_numeric(procedure_specialty_df['average duration'], errors='coerce')
        
        # Calculate demand minutes
        procedure_specialty_df['demand minutes'] = procedure_specialty_df['total referrals'] * procedure_specialty_df['average duration']
        
        # Top 10 procedures by total referrals
        top10_referrals = procedure_specialty_df.nlargest(10, 'total referrals')
        
        with col1:
            st.write("Top 10 Procedures by Total Referrals")
            fig3 = px.bar(
                top10_referrals,
                x='procedure',
                y='total referrals',
                labels={'procedure': 'Procedure', 'total referrals': 'Total Referrals'},
                title='Top 10 Procedures by Total Referrals'
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # Top 10 procedures by demand minutes
        top10_demand_minutes = procedure_specialty_df.nlargest(10, 'demand minutes')
        
        with col2:
            st.write("Top 10 Procedures by Demand Minutes")
            fig4 = px.bar(
                top10_demand_minutes,
                x='procedure',
                y='demand minutes',
                labels={'procedure': 'Procedure', 'demand minutes': 'Demand Minutes'},
                title='Top 10 Procedures by Demand Minutes'
            )
            st.plotly_chart(fig4, use_container_width=True)
        
    else:
        st.error("Uploaded files do not contain the required columns.")
else:
    st.write("Please upload both the Waiting List Data CSV and the Procedure Data CSV files in the sidebar.")
