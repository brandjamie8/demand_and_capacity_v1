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
        
        col1, _ = st.columns([1,4])
        with col1:
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

        # Baseline period selection
        st.subheader("Baseline Period Selection")

        col1, col2 = st.columns(2)
        with col1:
            baseline_start_date = st.date_input(
                'Baseline Start Date',
                value=waiting_list_specialty_df['month'].min()
            )
        with col2:
            baseline_end_date = st.date_input(
                'Baseline End Date',
                value=waiting_list_specialty_df['month'].max()
            )

        # Modeling start date
        st.subheader("Modeling Start Date")

        model_start_date = st.date_input(
            'Start Date for Modeling',
            value=waiting_list_specialty_df['month'].max()
        )

        # Convert selected dates to datetime
        baseline_start_date = pd.to_datetime(baseline_start_date)
        baseline_end_date = pd.to_datetime(baseline_end_date)
        model_start_date = pd.to_datetime(model_start_date)

        # Filter the baseline data
        baseline_data = waiting_list_specialty_df[
            (waiting_list_specialty_df['month'] >= baseline_start_date) &
            (waiting_list_specialty_df['month'] <= baseline_end_date)
        ]

        # Chart 1: Adjusted height
        st.subheader("Additions and Removals from Waiting List Over Time")
        fig1 = px.line(
            waiting_list_specialty_df,
            x='month',
            y=['additions to waiting list', 'removals from waiting list'],
            labels={'value': 'Number of Patients', 'variable': 'Legend'},
            title='Additions and Removals from Waiting List',
            height=600  # Adjust as needed
        )
        st.plotly_chart(fig1, use_container_width=True)

        if baseline_data.empty:
            st.error("No data available in the selected baseline period.")
        else:
            # Number of months to predict forward
            num_future_months = st.number_input(
                'Number of Months to Predict Forward',
                min_value=1,
                max_value=60,
                value=12
            )

            # Get the last known total waiting list size before the modeling start date
            last_known_data = waiting_list_specialty_df[waiting_list_specialty_df['month'] <= model_start_date]
            if not last_known_data.empty:
                last_total_waiting_list = last_known_data.iloc[-1]['total waiting list']
            else:
                st.error("No data available before the modeling start date.")
                last_total_waiting_list = 0  # Handle appropriately

            # Create date range for future months
            future_months = pd.date_range(
                start=model_start_date + pd.offsets.MonthBegin(1),
                periods=num_future_months,
                freq='MS'
            )

            # Initialize predicted data
            predicted_total_waiting_list = []
            current_total = last_total_waiting_list

            # Random sampling for predictions
            for month in future_months:
                sampled_addition = baseline_data['additions to waiting list'].sample(n=1).values[0]
                sampled_removal = baseline_data['removals from waiting list'].sample(n=1).values[0]
                current_total = current_total + sampled_addition - sampled_removal
                predicted_total_waiting_list.append({
                    'month': month,
                    'total waiting list': current_total
                })

            # Create DataFrame of predictions
            predictions_df = pd.DataFrame(predicted_total_waiting_list)

            # Prepare actual data up to the modeling start date
            actual_data = waiting_list_specialty_df[waiting_list_specialty_df['month'] <= model_start_date]

            # Concatenate actual data and predictions
            combined_df = pd.concat([actual_data, predictions_df], ignore_index=True)

            # Add a 'Data Type' column to distinguish between actual and predicted
            combined_df['Data Type'] = ['Actual'] * len(actual_data) + ['Predicted'] * len(predictions_df)

            # Chart 2: Total size of the waiting list with predictions
            st.subheader("Total Size of the Waiting List Over Time with Predictions")
            fig2 = px.line(
                combined_df,
                x='month',
                y='total waiting list',
                color='Data Type',
                line_dash='Data Type',
                labels={'total waiting list': 'Total Waiting List', 'month': 'Month'},
                title='Total Size of the Waiting List with Predictions',
                height=600  # Adjust as needed
            )

            # Customize line styles
            fig2.update_traces(
                line=dict(width=3),
                selector=dict(mode='lines')
            )

            fig2.update_traces(
                line=dict(dash='dash', width=2),
                selector=dict(name='Predicted')
            )

            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.error("Uploaded files do not contain the required columns.")
else:
    st.write("Please upload both the Waiting List Data CSV and the Procedure Data CSV files in the sidebar on the **Home** page.")
