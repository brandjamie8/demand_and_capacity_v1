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

        col1, _, _ = st.columns(3)
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

        ### **1. Additions and Removals Plot (fig1)**
        st.subheader("Additions and Removals from Waiting List Over Time")
        fig1 = px.line(
            waiting_list_specialty_df,
            x='month',
            y=['additions to waiting list', 'removals from waiting list'],
            labels={'value': 'Number of Patients', 'variable': 'Legend'},
            title='Additions and Removals from Waiting List',
            height=600  # Adjust the height as needed
        )

        # Display fig1 before the baseline date selections
        fig1_placeholder = st.empty()
        fig1_placeholder.plotly_chart(fig1, use_container_width=True)

        ### **2. Baseline Period Selection**
        st.subheader("Baseline Period Selection")

        col1, col2, _, _ = st.columns(4)
        with col1:
            baseline_start_date = st.date_input(
                'Baseline Start Date',
                value=waiting_list_specialty_df['month'].max()
            )
        with col2:
            baseline_end_date = st.date_input(
                'Baseline End Date',
                value=waiting_list_specialty_df['month'].max()
            )

        # Convert selected dates to datetime
        baseline_start_date = pd.to_datetime(baseline_start_date)
        baseline_end_date = pd.to_datetime(baseline_end_date)

        # Update fig1 to highlight the baseline period if dates are selected
        if baseline_start_date != baseline_end_date:
            fig1.add_vrect(
                x0=baseline_start_date,
                x1=baseline_end_date,
                fillcolor="LightGrey",
                opacity=0.5,
                layer="below",
                line_width=0,
            )
            # Re-display fig1 with the baseline highlight
            fig1_placeholder.plotly_chart(fig1, use_container_width=True)

        ### **3. Waiting List Over Time Plot (fig2)**
        st.subheader("Total Size of the Waiting List Over Time")

        # Initialize fig2 without predictions
        fig2 = px.line(
            waiting_list_specialty_df,
            x='month',
            y='total waiting list',
            labels={'total waiting list': 'Total Waiting List'},
            title='Total Size of the Waiting List',
            height=600  # Adjust the height as needed
        )

        # Display fig2
        fig2_placeholder = st.empty()
        fig2_placeholder.plotly_chart(fig2, use_container_width=True)

        ### **4. Modeling Start Date Input and Automatic Prediction Length Calculation**
        st.subheader("Modeling Start Date")

        model_start_date = st.date_input(
            'Start Date for Modeling',
            value=waiting_list_specialty_df['month'].max()
        )

        # Convert modeling start date to datetime
        model_start_date = pd.to_datetime(model_start_date)

        # Latest month in the data
        latest_month_in_data = waiting_list_specialty_df['month'].max()

        ### **5. Add Prediction Line to fig2 and Print Prediction Message**
        if model_start_date > latest_month_in_data:
            # Calculate the number of months to predict
            num_future_months = (model_start_date.year - latest_month_in_data.year) * 12 + \
                                (model_start_date.month - latest_month_in_data.month)

            # Proceed with prediction if the number of months is positive
            if num_future_months > 0:
                # Filter the baseline data
                baseline_data = waiting_list_specialty_df[
                    (waiting_list_specialty_df['month'] >= baseline_start_date) &
                    (waiting_list_specialty_df['month'] <= baseline_end_date)
                ]

                if baseline_data.empty:
                    st.error("No data available in the selected baseline period.")
                else:
                    # Get the last known total waiting list size
                    last_total_waiting_list = waiting_list_specialty_df.iloc[-1]['total waiting list']

                    # Create date range for future months, including the modeling start date
                    future_months = pd.date_range(
                        start=latest_month_in_data + pd.offsets.MonthBegin(1),
                        end=model_start_date,
                        freq='MS'
                    )
                    
                    # Initialize a DataFrame to store total waiting list sizes for each simulation
                    simulation_results = pd.DataFrame({'month': future_months})

                    num_simulations = 50
                    
                    for sim in range(num_simulations):
                        current_total = last_total_waiting_list
                        predicted_totals = []
                        for month in future_months:
                            sampled_addition = baseline_data['additions to waiting list'].sample(n=1).values[0]
                            sampled_removal = baseline_data['removals from waiting list'].sample(n=1).values[0]
                            current_total = current_total + sampled_addition - sampled_removal
                            predicted_totals.append(current_total)
                        # Add the predicted totals to the DataFrame
                        simulation_results[f'simulation_{sim+1}'] = predicted_totals
                    
                    # Calculate the average predicted total waiting list size for each month
                    simulation_results['average_total_waiting_list'] = simulation_results.filter(like='simulation_').mean(axis=1)
                    
                    # Create the final predictions DataFrame
                    predictions_df = simulation_results[['month', 'average_total_waiting_list']].rename(columns={'average_total_waiting_list': 'total waiting list'})
                    predictions_df['Data Type'] = 'Predicted'


                    # Prepare combined data
                    actual_data = waiting_list_specialty_df.copy()
                    actual_data['Data Type'] = 'Actual'

                    combined_df = pd.concat([actual_data, predictions_df], ignore_index=True)

                    # Update fig2 with predictions
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

                    # Re-display fig2 with predictions
                    fig2_placeholder.plotly_chart(fig2, use_container_width=True)

                    # Print the prediction message
                    predicted_starting_waiting_list_size = predictions_df.iloc[-1]['total waiting list']
                    st.write(f"")
                    st.write(f"Predicted starting waiting list size for {model_start_date.strftime('%b-%Y')} is: **{predicted_starting_waiting_list_size:.0f}**.")
                    st.write(f"This will be the starting position for modelling the impact of future capacity.")

    else:
        st.error("Uploaded files do not contain the required columns.")
else:
    st.write("Please upload both the Waiting List Data CSV and the Procedure Data CSV files in the sidebar on the **Home** page.")
