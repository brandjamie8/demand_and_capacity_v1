import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.title("Historic Waiting List")

st.markdown("""
This page analyses the historic waiting list data and provides a predicted starting point for future capacity planning.

- **Baseline Period Selection:** Choose a period that represents typical additions and removals to the waiting list. The model uses data from this period to simulate future changes.
- **Modeling Start Date:** Select a future date after the latest available data. The model predicts the waiting list size up to this date.
""")

# Check if data is available in session state
if st.session_state.waiting_list_df is not None and st.session_state.procedure_df is not None:
    waiting_list_df = st.session_state.waiting_list_df

    # Ensure required columns are present
    waiting_list_required_columns = ['month', 'specialty', 'additions to waiting list', 'removals from waiting list', 'total waiting list']

    if all(column in waiting_list_df.columns for column in waiting_list_required_columns):

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
        # Convert 'month' column to datetime and adjust to end of month
        waiting_list_specialty_df['month'] = pd.to_datetime(waiting_list_specialty_df['month']).dt.to_period('M').dt.to_timestamp('M')
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

        st.subheader("Baseline Period Selection")
        st.write("""
        Select the start and end dates for the baseline period. The model will use data from this period to simulate future additions and removals from the waiting list. The selected period should reflect typical activity.
        """)

           
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
        baseline_start_date = pd.to_datetime(baseline_start_date).to_period('M').to_timestamp('M')
        baseline_end_date = pd.to_datetime(baseline_end_date).to_period('M').to_timestamp('M')

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
            fig1.add_trace(
                go.Scatter(
                    x=[baseline_start_date, baseline_end_date],
                    y=[None, None],
                    mode='markers',
                    marker=dict(color='LightGrey'),
                    name='Baseline Period',
                    showlegend=True
                )
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

        st.subheader("Modeling Start Date")
        st.write("""
        Select the date from which you want the model to start predicting the waiting list size. This date should be after the latest month in the data.
        """)

           
        model_start_date = st.date_input(
            'Start Date for Modeling',
            value=waiting_list_specialty_df['month'].max()
        )

        # Convert modeling start date to datetime
        model_start_date = pd.to_datetime(model_start_date).to_period('M').to_timestamp('M')

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
                        start=latest_month_in_data + pd.offsets.MonthEnd(1),
                        end=model_start_date,
                        freq='M'
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
                    
                    # Calculate percentiles for the predictions
                    percentiles = [5, 25, 50, 75, 95]
                    percentile_values = simulation_results.filter(like='simulation_').quantile(q=[p/100 for p in percentiles], axis=1).T
                    percentile_values.columns = [f'percentile_{p}' for p in percentiles]
    
                    # Merge percentiles with simulation_results
                    simulation_results = pd.concat([simulation_results[['month']], percentile_values], axis=1)
    
                    # Use the 50th percentile (median) as the average prediction
                    predictions_df = simulation_results[['month', 'percentile_50']].rename(columns={'percentile_50': 'total waiting list'})
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
                    # Add shaded areas for the percentiles
                    fig2.add_traces([
                        go.Scatter(
                            name='5th-95th Percentile',
                            x=simulation_results['month'].tolist() + simulation_results['month'][::-1].tolist(),
                            y=simulation_results['percentile_95'].tolist() + simulation_results['percentile_5'][::-1].tolist(),
                            fill='toself',
                            fillcolor='rgba(200, 200, 200, 0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            hoverinfo="skip",
                            showlegend=True
                        ),
                        go.Scatter(
                            name='25th-75th Percentile',
                            x=simulation_results['month'].tolist() + simulation_results['month'][::-1].tolist(),
                            y=simulation_results['percentile_75'].tolist() + simulation_results['percentile_25'][::-1].tolist(),
                            fill='toself',
                            fillcolor='rgba(160, 160, 160, 0.4)',
                            line=dict(color='rgba(255,255,255,0)'),
                            hoverinfo="skip",
                            showlegend=True
                        )
                    ])
                    
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
                    st.write("""
                    The shaded areas in the prediction chart represent the variability in the model's predictions:
                    - **Dark Shaded Area (25th-75th Percentile):** Middle 50% of predicted values.
                    - **Light Shaded Area (5th-95th Percentile):** Represents 90% of predicted values.
                    """)

    else:
        st.error("Uploaded files do not contain the required columns.")
else:
    st.write("Please upload the Waiting List Data in the sidebar on the **Home** page.")
