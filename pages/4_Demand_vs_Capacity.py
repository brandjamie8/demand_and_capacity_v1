# pages/4_Demand_vs_Capacity.py

import streamlit as st
import pandas as pd
import plotly.express as px
import random

st.title("Demand vs Capacity")

# Sidebar Uploaders
st.sidebar.header('Upload Data Files')

procedure_data_file = st.sidebar.file_uploader(
    "Upload Procedure Data CSV",
    type='csv',
    key='procedure_data_file'
)

if procedure_data_file is not None:
    procedure_df = pd.read_csv(procedure_data_file)
    
    # Ensure required columns are present
    required_columns = ['specialty', 'procedure', 'total referrals', 'average duration']
    if all(column in procedure_df.columns for column in required_columns):
        # Select specialty
        specialties = procedure_df['specialty'].unique()
        selected_specialty = st.selectbox('Select Specialty', specialties)
        
        # Filter data based on selected specialty
        procedure_specialty_df = procedure_df[procedure_df['specialty'] == selected_specialty]
        
        # Calculate demand minutes
        procedure_specialty_df['demand minutes'] = procedure_specialty_df['total referrals'] * procedure_specialty_df['average duration']
        
        # Input capacity variables
        st.header("Input Capacity Variables")
        
        weeks_next_year = st.number_input("Weeks per Year (Next Year)", min_value=1, max_value=52, value=48)
        sessions_per_week_next_year = st.number_input("Sessions per Week (Next Year)", min_value=0.0, value=10.0, step=0.1)
        utilisation_next_year = st.slider("Utilisation Percentage (Next Year)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)
        session_duration_hours = st.number_input("Session Duration (Hours)", min_value=0.0, value=4.0, step=0.5)
        
        # Calculate total sessions and session minutes next year
        total_sessions_next_year = weeks_next_year * sessions_per_week_next_year
        session_minutes_next_year = total_sessions_next_year * session_duration_hours * 60 * utilisation_next_year
        
        st.write(f"**Total Sessions Next Year:** {total_sessions_next_year:.2f}")
        st.write(f"**Total Session Minutes Next Year (after Utilisation):** {session_minutes_next_year:.0f}")
        
        # Total demand
        total_demand_cases = procedure_specialty_df['total referrals'].sum()
        total_demand_minutes = procedure_specialty_df['demand minutes'].sum()
        
        st.write(f"**Total Demand (Cases):** {total_demand_cases:.0f}")
        st.write(f"**Total Demand (Minutes):** {total_demand_minutes:.0f}")
        
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
        required_sessions_next_year = total_demand_minutes / (session_duration_hours * 60 * utilisation_next_year) / weeks_next_year
        
        st.write(f"**Sessions per Week Required to Meet Demand:** {required_sessions_next_year:.2f}")
        st.write(f"**Sessions per Week Planned Next Year:** {sessions_per_week_next_year:.2f}")
        
        # Determine if capacity meets demand
        if sessions_per_week_next_year >= required_sessions_next_year:
            st.success("The planned capacity meets or exceeds the demand.")
        else:
            st.warning("The planned capacity does not meet the demand.")
        
    else:
        st.error("Uploaded file does not contain the required columns.")
else:
    st.write("Please upload the Procedure Data CSV file in the sidebar.")
