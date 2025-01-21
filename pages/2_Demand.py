# pages/2_Procedure_Demand.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress
import numpy as np

st.title("Demand")

# Check if data is available in session state
if 'procedure_df' in st.session_state and st.session_state.procedure_df is not None:
    procedure_df = st.session_state.procedure_df

    # Ensure required columns are present
    required_columns = ['specialty', 'procedure', 'total referrals', 'average duration']
    if all(column in procedure_df.columns for column in required_columns):
        specialties = procedure_df['specialty'].unique()
        if 'selected_specialty' not in st.session_state or st.session_state.selected_specialty not in specialties:
            st.session_state.selected_specialty = specialties[0]

        col1, _, _ = st.columns(3)
        with col1:
            selected_specialty = st.selectbox(
                'Select Specialty',
                specialties,
                index=list(specialties).index(st.session_state.selected_specialty),
                key='procedure_demand_specialty_select'
            )

        # Save the selected specialty to session state
        st.session_state.selected_specialty = selected_specialty

        # Filter data based on selected specialty
        procedure_specialty_df = procedure_df[procedure_df['specialty'] == selected_specialty]
          
        
        # Calculate demand minutes
        procedure_specialty_df['demand minutes'] = procedure_specialty_df['total referrals'] * procedure_specialty_df['average duration']

        procedure_specialty_df['month'] = pd.to_datetime(procedure_specialty_df['month'])
        
        # Save the filtered DataFrame in session state for use in other pages
        st.session_state.procedure_specialty_df = procedure_specialty_df

        # --- NEW PART: Display Baseline Period Information ---
        baseline_start = pd.to_datetime(st.session_state.baseline_start_date)
        baseline_end = pd.to_datetime(st.session_state.baseline_end_date)
        num_baseline_months = (baseline_end.to_period('M') - baseline_start.to_period('M')).n + 1

        
        # Calculate total referrals during the baseline period from the procedure DataFrame
        baseline_procedure_df = procedure_specialty_df[
            (procedure_specialty_df['month'] >= baseline_start) &
            (procedure_specialty_df['month'] <= baseline_end)
        ]
        total_referrals_baseline = baseline_procedure_df['total referrals'].sum()
        
import plotly.graph_objects as go
from scipy.stats import linregress
import numpy as np

st.subheader("Baseline Analysis")        

# Check if necessary data is available
if ('waiting_list_df' in st.session_state and st.session_state.waiting_list_df is not None) and \
   ('procedure_specialty_df' in st.session_state and st.session_state.procedure_specialty_df is not None):
    
    waiting_list_df = st.session_state.waiting_list_df
    procedure_specialty_df = st.session_state.procedure_specialty_df

    # Ensure required columns are present
    waiting_list_required_columns = ['month', 'specialty', 'additions to waiting list']
    if all(column in waiting_list_df.columns for column in waiting_list_required_columns):
        # Use selected specialty from session state
        # Initialize baseline dates in session state if they don't exist
        if 'baseline_start_date' not in st.session_state:
            st.session_state.baseline_start_date = pd.to_datetime(waiting_list_df['month']).min().date()
        
        if 'baseline_end_date' not in st.session_state:
            st.session_state.baseline_end_date = pd.to_datetime(waiting_list_df['month']).max().date()
        
        # Adjust baseline start and end dates to be at month end
        st.session_state.baseline_start_date = pd.to_datetime(st.session_state.baseline_start_date) + pd.offsets.MonthEnd(0)
        st.session_state.baseline_end_date = pd.to_datetime(st.session_state.baseline_end_date) + pd.offsets.MonthEnd(0)

        # Allow the user to adjust baseline dates
        col1, col2, _, _ = st.columns(4)
        with col1:
            st.session_state.baseline_start_date = st.date_input("Baseline Start Date (Month End)", value=st.session_state.baseline_start_date)
        with col2:
            st.session_state.baseline_end_date = st.date_input("Baseline End Date (Month End)", value=st.session_state.baseline_end_date)

        baseline_start_date = st.session_state.baseline_start_date
        baseline_end_date = st.session_state.baseline_end_date
        
        baseline_start = pd.to_datetime(baseline_start_date).to_period('M').to_timestamp('M')
        baseline_end = pd.to_datetime(baseline_end_date).to_period('M').to_timestamp('M')

        baseline_start = pd.to_datetime(st.session_state.baseline_start_date)
        baseline_end = pd.to_datetime(st.session_state.baseline_end_date)
        
        # Require a baseline period of at least 6 months
        if baseline_end <= baseline_start + pd.DateOffset(months=4):
            st.warning("The baseline period must be at least 6 months.")
        else:
            # Filter waiting list data based on selected specialty
            selected_specialty = st.session_state.selected_specialty
            waiting_list_specialty_df = waiting_list_df[waiting_list_df['specialty'] == selected_specialty]
            
            # Convert 'month' column to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(waiting_list_specialty_df['month']):
                waiting_list_specialty_df['month'] = pd.to_datetime(waiting_list_specialty_df['month'])

            # Adjust 'month' column to month end
            waiting_list_specialty_df['month'] = waiting_list_specialty_df['month'] + pd.offsets.MonthEnd(0)

            # Sort by month
            waiting_list_specialty_df = waiting_list_specialty_df.sort_values('month')


            # --- Baseline Analysis ---
            st.write(f"**Baseline Period:** {baseline_start.strftime('%B %Y')} to {baseline_end.strftime('%B %Y')}")
            st.write(f"**Number of Months in Baseline:** {num_baseline_months} months")
            
            # Calculate DTAs from procedure DataFrame
            baseline_procedure_df = procedure_specialty_df[
                (procedure_specialty_df['month'] >= baseline_start) & 
                (procedure_specialty_df['month'] <= baseline_end)
            ]
            baseline_total_dtas = baseline_procedure_df['total referrals'].sum()
            baseline_scaled_dtas = (baseline_total_dtas / num_baseline_months) * 12
            
            # Filter baseline data for waiting list additions and cases
            baseline_waiting_list_df = waiting_list_specialty_df[
                (waiting_list_specialty_df['month'] >= baseline_start) & 
                (waiting_list_specialty_df['month'] <= baseline_end)
            ]
            
            # Calculate total additions to the waiting list in the baseline period
            baseline_total_additions = baseline_waiting_list_df['additions to waiting list'].sum()
            num_baseline_months = len(pd.date_range(start=baseline_start, end=baseline_end, freq='M'))
            
            # Scale additions to 12 months
            baseline_scaled_additions = (baseline_total_additions / num_baseline_months) * 12
            st.write(f"**Additions to the Waiting List (Scaled to Year):** {baseline_scaled_additions:.0f}")
            
            # Calculate total cases (theatre) and removals
            baseline_total_cases = baseline_waiting_list_df['cases'].sum()
            baseline_total_removals = baseline_waiting_list_df['removals from waiting list'].sum()
            
            # Calculate % of additions that result in cases
            percent_additions_to_cases = (baseline_total_cases / baseline_total_additions) if baseline_total_additions > 0 else 0
            st.write(f"**Percentage of Additions Resulting in Cases:** {percent_additions_to_cases:.2%}")
            
            # Calculate cases needed to remove all additions
            cases_needed_per_addition = percent_additions_to_cases
            baseline_scaled_cases_needed = baseline_scaled_additions * cases_needed_per_addition
            
            st.write(f"**Theatre Cases Needed to Remove Demand (Scaled to Year):** {baseline_scaled_cases_needed:.0f}")
            

            start_12_months_prior = baseline_start - pd.DateOffset(months=12)
            pre_baseline_df = waiting_list_specialty_df[
                (waiting_list_specialty_df['month'] >= start_12_months_prior) &
                (waiting_list_specialty_df['month'] < baseline_start)
            ]

            # Ensure there are enough data points for regression
            if len(pre_baseline_df) < 2:
                st.warning("Not enough data points in the 12 months before the baseline start date for regression analysis.")
            else:
                pre_months = pre_baseline_df['month']
                pre_demand = pre_baseline_df['additions to waiting list']

                # Convert months to ordinal for regression analysis
                pre_months_ordinal = pre_months.map(pd.Timestamp.toordinal)
                slope, intercept, r_value, p_value, std_err = linregress(pre_months_ordinal, pre_demand)

                baseline_df = waiting_list_specialty_df[
                    (waiting_list_specialty_df['month'] >= baseline_start) &
                    (waiting_list_specialty_df['month'] <= baseline_end)
                ]

                baseline_months_ordinal = baseline_df['month'].map(pd.Timestamp.toordinal)
                predicted_baseline_demand = intercept + slope * baseline_months_ordinal

                average_demand = pre_demand.mean()
                predicted_baseline_average = [average_demand] * len(baseline_months_ordinal)

                actual_baseline_demand = baseline_df['additions to waiting list']
                error_regression = np.abs(actual_baseline_demand - predicted_baseline_demand).mean()
                error_average = np.abs(actual_baseline_demand - predicted_baseline_average).mean()

                # Determine which method is more predictive
                use_average_for_prediction = error_average < error_regression

                prediction_df = pd.DataFrame({
                    'month': waiting_list_specialty_df['month'],
                    'actual_demand': waiting_list_specialty_df['additions to waiting list']
                })

                historic_months_ordinal = pre_months_ordinal
                fitted_historic_demand = intercept + slope * historic_months_ordinal
                
                fig_baseline = go.Figure()
                # Add the actual demand trace
                fig_baseline.add_trace(go.Scatter(
                    x=prediction_df['month'],
                    y=prediction_df['actual_demand'],
                    mode='lines+markers',
                    name='Actual Demand',
                    line=dict(color='#f5136f')
                ))
                # Add a trace for the average line in the historical data
                fig_baseline.add_trace(go.Scatter(
                    x=pre_months,
                    y=[average_demand] * len(pre_months),
                    mode='lines',
                    name='Average Line (Historical)',
                    line=dict(color='orange')
                ))           
                # Add the predicted demand trace for average in the baseline period
                fig_baseline.add_trace(go.Scatter(
                    x=baseline_df['month'],
                    y=predicted_baseline_average,
                    mode='lines',
                    name='Predicted Demand (Average)',
                    line=dict(dash='dash', color='orange')
                ))                
                fig_baseline.add_trace(go.Scatter(
                    x=pre_months,
                    y=fitted_historic_demand,
                    mode='lines',
                    name='Fitted Regression Line (Historical)',
                    line=dict(color='blue')
                ))

                # Add the predicted demand trace for regression in the baseline period
                fig_baseline.add_trace(go.Scatter(
                    x=baseline_df['month'],
                    y=predicted_baseline_demand,
                    mode='lines',
                    name='Predicted Demand (Regression)',
                    line=dict(color='blue', dash='dash')
                ))

                # Highlight the baseline period
                if baseline_start != baseline_end:
                    fig_baseline.add_vrect(
                        x0=baseline_start,
                        x1=baseline_end,
                        fillcolor="LightGrey",
                        opacity=0.5,
                        layer="below",
                        line_width=0,
                    )
                    fig_baseline.add_trace(
                        go.Scatter(
                            x=[baseline_start, baseline_end],
                            y=[None, None],
                            mode='markers',
                            marker=dict(color='LightGrey'),
                            name='Baseline Period',
                            showlegend=True
                        )
                    )

                # Update the layout with title and labels
                fig_baseline.update_layout(
                    title='Predicted vs Actual Demand for Baseline Period',
                    xaxis_title='Month',
                    yaxis_title='Demand',
                    legend_title='Legend'
                )

                # Display the chart in Streamlit
                st.plotly_chart(fig_baseline, use_container_width=True)

                # --- Display Errors and Conclusion ---
                st.write(f"**Mean Absolute Error for Regression:** {error_regression:.2f}")
                st.write(f"**Mean Absolute Error for Baseline Average:** {error_average:.2f}")
                if use_average_for_prediction:
                    st.write("**Conclusion:** The historic average predicts the baseline better.")
                else:
                    st.write("**Conclusion:** The regression line predicts the baseline better so incorporating a trend may help predict future demand.")

                st.subheader("Choose Prediction Model")
                selected_model = st.radio(
                    "Select the model to generate the predicted trend for the next 12 months:",
                    options=["Average (Baseline)", "Regression"],
                    index=0 if use_average_for_prediction else 1
                )

            future_months = pd.date_range(
                start=st.session_state.model_start_date + pd.DateOffset(months=1),
                periods=12,
                freq='M'
            )
            
            # Use baseline data scaled to 12 months for prediction when using the average
            if selected_model == "Average (Baseline)":
                # Calculate the average additions per month from the baseline and scale to 12 months
                baseline_total_additions = baseline_procedure_df['total referrals'].sum()
                baseline_scaled_monthly_additions = baseline_total_additions / num_baseline_months
                future_demand = [baseline_scaled_monthly_additions] * len(future_months)
                ###################################################
                st.df(baseline_procedure_df)
                ###################################################
                prediction_method = "Average (Baseline)"
            else:
                # Use regression-based prediction if average is not chosen
                future_months_ordinal = future_months.map(pd.Timestamp.toordinal)
                future_demand = intercept + slope * future_months_ordinal
                prediction_method = "Regression"
            
            # Create a DataFrame for future predictions
            future_df = pd.DataFrame({
                'month': future_months,
                'predicted_demand': future_demand
            })

            # Plot the demand and predicted trend for the entire period, highlighting the baseline and future predictions
            fig_demand = go.Figure()

            # Add the actual demand trace for the entire available period
            fig_demand.add_trace(go.Scatter(
                x=waiting_list_specialty_df['month'],
                y=waiting_list_specialty_df['additions to waiting list'],
                mode='lines+markers',
                name='Actual Demand',
                line=dict(color='#f5136f')
            ))

            # Add the predicted future demand trace
            fig_demand.add_trace(go.Scatter(
                x=future_df['month'],
                y=future_df['predicted_demand'],
                mode='lines+markers',
                name=f'Predicted Demand ({prediction_method})'
            ))

            # Highlight the baseline period
            if baseline_start != baseline_end:
                fig_demand.add_vrect(
                    x0=baseline_start,
                    x1=baseline_end,
                    fillcolor="LightGrey",
                    opacity=0.5,
                    layer="below",
                    line_width=0,
                )
                fig_demand.add_trace(
                    go.Scatter(
                        x=[baseline_start, baseline_end],
                        y=[None, None],
                        mode='markers',
                        marker=dict(color='LightGrey'),
                        name='Baseline Period',
                        showlegend=True
                    )
                )

            # Update the layout with title and labels
            fig_demand.update_layout(
                title='Monthly Demand with Predicted Trend for Next 12 Months',
                xaxis_title='Month',
                yaxis_title='Demand',
                legend_title='Legend'
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig_demand, use_container_width=True)

            # Summary of Total Predicted Demand
            total_predicted_demand = future_df['predicted_demand'].sum()
            st.write(f"**Total Predicted Waiting List Referral Demand over Next 12 Months:** {total_predicted_demand:.0f}")

            total_predicted_cases = total_predicted_demand * percent_additions_to_cases
            st.markdown(f"### Total Predicted Waiting List Theatre Case Demand over Next 12 Months: {total_predicted_cases:.0f}")

            st.session_state.total_predicted_cases = total_predicted_cases
       
    else:
        st.error("Waiting list data does not contain the required columns.")

else:
    st.write("Please ensure you have uploaded the required data and completed previous sections.")

#st.subheader("Planned Procedure Demand")

# Convert 'month' column to datetime
#if not pd.api.types.is_datetime64_any_dtype(waiting_list_df['month']):
#    waiting_list_df['month'] = pd.to_datetime(waiting_list_df['month'])

# Filter data for planned procedures and procedure demand
#if 'planned procedures' in waiting_list_df.columns:
#    demand_comparison_df = waiting_list_df[
#        (waiting_list_df['month'] >= baseline_start) & 
#        (waiting_list_df['specialty'] == selected_specialty)
#    ]

    # Ensure required columns are available
#    if 'additions to waiting list' in demand_comparison_df.columns:
#        # Create a stacked column chart
#        fig_demand_comparison = px.bar(
#            demand_comparison_df,
#            x='month',
#            y=['planned procedures', 'additions to waiting list'],
#            labels={'value': 'Number of Procedures', 'variable': 'Type'},
#            title="Planned Procedures vs Total Procedure Demand",
#            barmode='stack',
#            height=600
#        )

        # Update layout for better clarity
#        fig_demand_comparison.update_layout(
#            xaxis_title="Month",
#            yaxis_title="Number of Procedures",
#            legend_title="Procedure Type"
#        )

        # Display the chart in Streamlit
#        st.plotly_chart(fig_demand_comparison, use_container_width=True)

        # Calculate the percentage of planned procedures in total demand
#        total_planned = demand_comparison_df['planned procedures'].sum()
#        total_demand = demand_comparison_df['additions to waiting list'].sum()

#        if total_demand > 0:  # To avoid division by zero
#            planned_percentage = (total_planned / total_demand) * 100
#            st.write(f"On average, planned procedures make up **{planned_percentage:.2f}%** of total procedure demand.")
#            planned_cases = (planned_percentage / 100) * total_predicted_cases
#            st.write(f"This translates to **{planned_cases:.0f}** cases over the next 12 months.")
            
#        else:
#            st.write("No data available to calculate the contribution of planned procedures.")

