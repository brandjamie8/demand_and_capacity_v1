# pages/2_Procedure_Demand.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Procedure Demand")

# Check if data is available in session state
if st.session_state.procedure_df is not None:
    procedure_df = st.session_state.procedure_df

    # Ensure required columns are present
    required_columns = ['specialty', 'procedure', 'total referrals', 'average duration']
    if all(column in procedure_df.columns for column in required_columns):
        # Use selected specialty from session state
        specialties = procedure_df['specialty'].unique()
        if st.session_state.selected_specialty is None:
            st.session_state.selected_specialty = specialties[0]

        selected_specialty = st.selectbox('Select Specialty', specialties, index=list(specialties).index(st.session_state.selected_specialty), key='specialty_select')

        # Save the selected specialty to session state
        st.session_state.selected_specialty = selected_specialty

        # Filter data based on selected specialty
        procedure_specialty_df = procedure_df[procedure_df['specialty'] == selected_specialty]

        # Calculate demand minutes
        procedure_specialty_df['demand minutes'] = procedure_specialty_df['total referrals'] * procedure_specialty_df['average duration']

        # Display total demand
        total_demand_cases = procedure_specialty_df['total referrals'].sum()
        total_demand_minutes = procedure_specialty_df['demand minutes'].sum()

        st.write(f"**Total Demand (Cases):** {total_demand_cases:.0f}")
        st.write(f"**Total Demand (Minutes):** {total_demand_minutes:.0f}")

        # Top 10 procedures by total referrals
        top10_cases = procedure_specialty_df.nlargest(10, 'total referrals')

        # Chart - Top 10 procedure demand in cases
        st.subheader("Top 10 Procedures by Demand in Cases")
        fig_top10_cases = px.bar(
            top10_cases,
            x='procedure',
            y='total referrals',
            title='Top 10 Procedures by Demand in Cases',
            labels={'procedure': 'Procedure', 'total referrals': 'Total Referrals'},
            text='total referrals'
        )
        st.plotly_chart(fig_top10_cases, use_container_width=True)

        # Top 10 procedures by demand minutes
        top10_minutes = procedure_specialty_df.nlargest(10, 'demand minutes')

        # Chart - Top 10 procedure demand in minutes
        st.subheader("Top 10 Procedures by Demand in Minutes")
        fig_top10_minutes = px.bar(
            top10_minutes,
            x='procedure',
            y='demand minutes',
            title='Top 10 Procedures by Demand in Minutes',
            labels={'procedure': 'Procedure', 'demand minutes': 'Demand Minutes'},
            text='demand minutes'
        )
        st.plotly_chart(fig_top10_minutes, use_container_width=True)
    else:
        st.error("Uploaded file does not contain the required columns.")
else:
    st.write("Please upload the Procedure Data CSV file in the sidebar on the **Home** page.")
