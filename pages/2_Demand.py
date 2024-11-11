# pages/2_Procedure_Demand.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress
import numpy as np
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
        st.subheader("Procedure Demand")
        # Use selected specialty from session state
        specialties = procedure_df['specialty'].unique()
        if 'selected_specialty' not in st.session_state or st.session_state.selected_specialty not in specialties:
            st.session_state.selected_specialty = specialties[0]

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
        procedure_specialty_df['demand minutes'] = procedure_specialty_df['total referrals'] * procedure_specialty_df['average duration'] * 60

        # Save the filtered DataFrame in session state for use in other pages
        st.session_state.procedure_specialty_df = procedure_specialty_df

        # Display total demand
        total_demand_cases = procedure_specialty_df['total referrals'].sum()
        total_demand_minutes = procedure_specialty_df['demand minutes'].sum()

        st.write(f"**Total Demand (Cases):** {total_demand_cases:.0f}")
        st.write(f"**Total Demand (Minutes):** {total_demand_minutes:.0f}")

import plotly.graph_objects as go
from scipy.stats import linregress
import numpy as np

st.subheader("Time Series Analysis")

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
        st.session_state.baseline_start_date = st.date_input("Baseline Start Date (Month End)", value=st.session_state.baseline_start_date)
        st.session_state.baseline_end_date = st.date_input("Baseline End Date (Month End)", value=st.session_state.baseline_end_date)

        baseline_start = pd.Timestamp(st.session_state.baseline_start_date)
        baseline_end = pd.Timestamp(st.session_state.baseline_end_date)
        
        # Require a baseline period of at least 6 months
        if baseline_end <= baseline_start + pd.DateOffset(months=5):
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

            # --- NEW PART: Filter data for the 12 months before the baseline start date ---
            start_12_months_prior = st.session_state.baseline_start_date - pd.DateOffset(months=12)
            pre_baseline_df = waiting_list_specialty_df[
                (waiting_list_specialty_df['month'] >= start_12_months_prior) &
                (waiting_list_specialty_df['month'] < st.session_state.baseline_start_date)
            ]

            # Ensure there are enough data points for regression
            if len(pre_baseline_df) < 2:
                st.warning("Not enough data points in the 12 months before the baseline start date for regression analysis.")
            else:
                # --- NEW PART: Extract months and demand data from the 12 months prior to the baseline ---
                pre_months = pre_baseline_df['month']
                pre_demand = pre_baseline_df['additions to waiting list']

                # Convert months to ordinal for regression analysis
                pre_months_ordinal = pre_months.map(pd.Timestamp.toordinal)

                # --- NEW PART: Perform linear regression to assess trend for the pre-baseline period ---
                slope, intercept, r_value, p_value, std_err = linregress(pre_months_ordinal, pre_demand)

                # --- NEW PART: Predict demand for the baseline period using the trained model ---
                baseline_start = st.session_state.baseline_start_date
                baseline_end = st.session_state.baseline_end_date
                baseline_df = waiting_list_specialty_df[
                    (waiting_list_specialty_df['month'] >= baseline_start) &
                    (waiting_list_specialty_df['month'] <= baseline_end)
                ]

                baseline_months_ordinal = baseline_df['month'].map(pd.Timestamp.toordinal)
                predicted_baseline_demand = intercept + slope * baseline_months_ordinal

                # --- NEW PART: Predict using the average from pre-baseline ---
                average_demand = pre_demand.mean()
                predicted_baseline_average = [average_demand] * len(baseline_months_ordinal)

                # --- NEW PART: Calculate the error between actual and predicted demand ---
                actual_baseline_demand = baseline_df['additions to waiting list']
                error_regression = np.abs(actual_baseline_demand - predicted_baseline_demand).mean()
                error_average = np.abs(actual_baseline_demand - predicted_baseline_average).mean()

                # Determine which method is more predictive
                use_average_for_prediction = error_average < error_regression

                # --- NEW PART: Create a DataFrame for plotting the predicted vs actual baseline demand ---
                prediction_df = pd.DataFrame({
                    'month': waiting_list_specialty_df['month'],
                    'actual_demand': waiting_list_specialty_df['additions to waiting list']
                })

                # --- NEW PART: Plot the actual vs predicted demand for the baseline period ---
                fig_baseline = go.Figure()

                # Add the actual demand trace
                fig_baseline.add_trace(go.Scatter(
                    x=prediction_df['month'],
                    y=prediction_df['actual_demand'],
                    mode='lines+markers',
                    name='Actual Demand',
                    line=dict(color='#f5136f')
                ))

                # Add the predicted demand trace for regression in the baseline period
                fig_baseline.add_trace(go.Scatter(
                    x=baseline_df['month'],
                    y=predicted_baseline_demand,
                    mode='lines',
                    name='Predicted Demand (Regression)',
                    line=dict(dash='dash')
                ))

                # Add the predicted demand trace for average in the baseline period
                fig_baseline.add_trace(go.Scatter(
                    x=baseline_df['month'],
                    y=predicted_baseline_average,
                    mode='lines',
                    name='Predicted Demand (Average)',
                    line=dict(dash='dot', color='blue')
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
                st.write(f"**Mean Absolute Error (Regression):** {error_regression:.2f}")
                st.write(f"**Mean Absolute Error (Average):** {error_average:.2f}")
                if use_average_for_prediction:
                    st.write("**Conclusion:** The average demand in the baseline period is more accurate for prediction compared to the trend.")
                else:
                    st.write("**Conclusion:** The trend needs to be accounted for using regression to accurately predict future demand.")

            # --- NEW PART: Predict demand for the next 12 months ---
            future_months = pd.date_range(
                start=st.session_state.baseline_end_date + pd.DateOffset(months=1),
                periods=12,
                freq='M'
            )
            
            if use_average_for_prediction:
                future_demand = [average_demand] * len(future_months)
                prediction_method = "Average"
            else:
                future_months_ordinal = future_months.map(pd.Timestamp.toordinal)
                future_demand = intercept + slope * future_months_ordinal
                prediction_method = "Regression"

            future_df = pd.DataFrame({
                'month': future_months,
                'predicted_demand': future_demand
            })

            # --- END OF NEW PART ---

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
                mode='lines',
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

    else:
        st.error("Waiting list data does not contain the required columns.")
else:
    st.write("Please ensure you have uploaded the required data and completed previous sections.")

st.title("Demand")

# Check if data is available in session state
if 'procedure_df' in st.session_state and st.session_state.procedure_df is not None:
    procedure_df = st.session_state.procedure_df

    # Ensure required columns are present
    required_columns = ['specialty', 'procedure', 'total referrals', 'average duration']
    if all(column in procedure_df.columns for column in required_columns):
        st.subheader("Procedure Demand")
        # Use selected specialty from session state
        specialties = procedure_df['specialty'].unique()
        if 'selected_specialty' not in st.session_state or st.session_state.selected_specialty not in specialties:
            st.session_state.selected_specialty = specialties[0]

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
        procedure_specialty_df['demand minutes'] = procedure_specialty_df['total referrals'] * procedure_specialty_df['average duration'] * 60

        # Save the filtered DataFrame in session state for use in other pages
        st.session_state.procedure_specialty_df = procedure_specialty_df

        # Display total demand
        total_demand_cases = procedure_specialty_df['total referrals'].sum()
        total_demand_minutes = procedure_specialty_df['demand minutes'].sum()

        st.write(f"**Total Demand (Cases):** {total_demand_cases:.0f}")
        st.write(f"**Total Demand (Minutes):** {total_demand_minutes:.0f}")

import plotly.graph_objects as go
from scipy.stats import linregress
import numpy as np

st.subheader("Time Series Analysis")

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
        
        # Allow the user to adjust baseline dates
        st.session_state.baseline_start_date = st.date_input("Baseline Start Date", value=st.session_state.baseline_start_date)
        st.session_state.baseline_end_date = st.date_input("Baseline End Date", value=st.session_state.baseline_end_date)
        
        # Filter waiting list data based on selected specialty
        selected_specialty = st.session_state.selected_specialty
        waiting_list_specialty_df = waiting_list_df[waiting_list_df['specialty'] == selected_specialty]
        
        # Convert 'month' column to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(waiting_list_specialty_df['month']):
            waiting_list_specialty_df['month'] = pd.to_datetime(waiting_list_specialty_df['month'])

        # Sort by month
        waiting_list_specialty_df = waiting_list_specialty_df.sort_values('month')

        # --- NEW PART: Filter data for the 12 months before the baseline start date ---
        start_12_months_prior = pd.to_datetime(st.session_state.baseline_start_date) - pd.DateOffset(months=12)
        pre_baseline_df = waiting_list_specialty_df[
            (waiting_list_specialty_df['month'] >= start_12_months_prior) &
            (waiting_list_specialty_df['month'] < pd.to_datetime(st.session_state.baseline_start_date))
        ]

        # Ensure there are enough data points for regression
        if len(pre_baseline_df) < 2:
            st.warning("Not enough data points in the 12 months before the baseline start date for regression analysis.")
        else:
            # --- NEW PART: Extract months and demand data from the 12 months prior to the baseline ---
            pre_months = pre_baseline_df['month']
            pre_demand = pre_baseline_df['additions to waiting list']

            # Convert months to ordinal for regression analysis
            pre_months_ordinal = pre_months.map(pd.Timestamp.toordinal)

            # --- NEW PART: Perform linear regression to assess trend for the pre-baseline period ---
            slope, intercept, r_value, p_value, std_err = linregress(pre_months_ordinal, pre_demand)

            # --- NEW PART: Predict demand for the baseline period using the trained model ---
            baseline_start = pd.to_datetime(st.session_state.baseline_start_date)
            baseline_end = pd.to_datetime(st.session_state.baseline_end_date)
            baseline_df = waiting_list_specialty_df[
                (waiting_list_specialty_df['month'] >= baseline_start) &
                (waiting_list_specialty_df['month'] <= baseline_end)
            ]

            baseline_months_ordinal = baseline_df['month'].map(pd.Timestamp.toordinal)
            predicted_baseline_demand = intercept + slope * baseline_months_ordinal

            # --- NEW PART: Predict using the average from pre-baseline ---
            average_demand = pre_demand.mean()
            predicted_baseline_average = [average_demand] * len(baseline_months_ordinal)

            # --- NEW PART: Calculate the error between actual and predicted demand ---
            actual_baseline_demand = baseline_df['additions to waiting list']
            error_regression = np.abs(actual_baseline_demand - predicted_baseline_demand).mean()
            error_average = np.abs(actual_baseline_demand - predicted_baseline_average).mean()

            # Determine which method is more predictive
            use_average_for_prediction = error_average < error_regression

            # --- NEW PART: Create a DataFrame for plotting the predicted vs actual baseline demand ---
            prediction_df = pd.DataFrame({
                'month': waiting_list_specialty_df['month'],
                'actual_demand': waiting_list_specialty_df['additions to waiting list']
            })

            # --- NEW PART: Plot the actual vs predicted demand for the baseline period ---
            fig_baseline = go.Figure()

            # Add the actual demand trace
            fig_baseline.add_trace(go.Scatter(
                x=prediction_df['month'],
                y=prediction_df['actual_demand'],
                mode='lines+markers',
                name='Actual Demand',
                line=dict(color='#f5136f')
            ))

            # Add the predicted demand trace for regression in the baseline period
            fig_baseline.add_trace(go.Scatter(
                x=baseline_df['month'],
                y=predicted_baseline_demand,
                mode='lines',
                name='Predicted Demand (Regression)',
                line=dict(dash='dash')
            ))

            # Add the predicted demand trace for average in the baseline period
            fig_baseline.add_trace(go.Scatter(
                x=baseline_df['month'],
                y=predicted_baseline_average,
                mode='lines',
                name='Predicted Demand (Average)',
                line=dict(dash='dot', color='blue')
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
                legend_title='Legend',
                annotations=[dict(
                    x=0.5,
                    y=-0.3,
                    showarrow=False,
                    text=f"MAE (Regression): {error_regression:.2f}, MAE (Average): {error_average:.2f}",
                    xref="paper",
                    yref="paper"
                )]
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig_baseline, use_container_width=True)

        # --- END OF NEW PART ---

        # --- NEW PART: Predict demand for the next 12 months ---
        future_months = pd.date_range(
            start=st.session_state.baseline_end_date + pd.DateOffset(months=1),
            periods=12,
            freq='M'
        )
        
        if use_average_for_prediction:
            future_demand = [average_demand] * len(future_months)
            prediction_method = "Average"
        else:
            future_months_ordinal = future_months.map(pd.Timestamp.toordinal)
            future_demand = intercept + slope * future_months_ordinal
            prediction_method = "Regression"

        future_df = pd.DataFrame({
            'month': future_months,
            'predicted_demand': future_demand
        })

        # --- END OF NEW PART ---

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
            mode='lines',
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

    else:
        st.error("Waiting list data does not contain the required columns.")
else:
    st.write("Please ensure you have uploaded the required data and completed previous sections.")
