# pages/2_Procedure_Demand.py

import streamlit as st
import pandas as pd
import plotly.express as px

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

        # Apply multiplier if available
        if 'multiplier' in st.session_state:
            multiplier = st.session_state.multiplier
            projected_demand_cases = total_demand_cases * multiplier
            projected_demand_minutes = total_demand_minutes * multiplier

            st.write(f"**Projected Demand for Next Year (Cases):** {projected_demand_cases:.0f}")
            st.write(f"**Projected Demand for Next Year (Minutes):** {projected_demand_minutes:.0f}")

            # Save projected demand to session state
            st.session_state.projected_demand_cases = projected_demand_cases
            st.session_state.projected_demand_minutes = projected_demand_minutes
    else:
        st.error("Uploaded file does not contain the required columns.")
else:
    st.write("Please upload the Procedure Data CSV file on the **Home** page.")

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

            # --- NEW PART: Calculate the error between actual and predicted demand ---
            actual_baseline_demand = baseline_df['additions to waiting list']
            error = actual_baseline_demand - predicted_baseline_demand
            mae = np.mean(np.abs(error))  # Mean Absolute Error

            # --- NEW PART: Create a DataFrame for plotting the predicted vs actual baseline demand ---
            prediction_df = pd.DataFrame({
                'month': baseline_df['month'],
                'actual_demand': actual_baseline_demand,
                'predicted_demand': predicted_baseline_demand,
                'error': error
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

            # Add the predicted demand trace
            fig_baseline.add_trace(go.Scatter(
                x=prediction_df['month'],
                y=prediction_df['predicted_demand'],
                mode='lines',
                name='Predicted Demand',
                line=dict(dash='dash')
            ))

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
                    text=f"Mean Absolute Error: {mae:.2f}",
                    xref="paper",
                    yref="paper"
                )]
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig_baseline, use_container_width=True)

        # --- END OF NEW PART ---

        # Filter data based on baseline dates for trend analysis
        filtered_df = waiting_list_specialty_df[
            (waiting_list_specialty_df['month'] >= pd.to_datetime(st.session_state.baseline_start_date)) &
            (waiting_list_specialty_df['month'] <= pd.to_datetime(st.session_state.baseline_end_date))
        ]
        
        # Sort by month
        filtered_df = filtered_df.sort_values('month')
        
        # Extract months and demand data
        months = filtered_df['month']
        demand = filtered_df['additions to waiting list']
        
        # Convert months to ordinal for regression analysis
        months_ordinal = months.map(pd.Timestamp.toordinal)
        
        # Perform linear regression to assess trend
        slope, intercept, r_value, p_value, std_err = linregress(months_ordinal, demand)
        
        # Calculate the predicted demand using the regression model
        predicted_demand = intercept + slope * months_ordinal
        
        # Create a DataFrame for plotting
        regression_df = pd.DataFrame({
            'month': months,
            'demand': demand,
            'predicted_demand': predicted_demand
        })

        # Plot the demand and predicted demand
        fig_demand = go.Figure()

        # Add the actual demand trace
        fig_demand.add_trace(go.Scatter(
            x=regression_df['month'],
            y=regression_df['demand'],
            mode='lines+markers',
            name='Additions to Waiting List',
            line=dict(color='#f5136f')
        ))

        # Add the predicted demand trace
        fig_demand.add_trace(go.Scatter(
            x=regression_df['month'],
            y=regression_df['predicted_demand'],
            mode='lines',
            name='Predicted Demand'
        ))

        # Update the layout with title and labels
        fig_demand.update_layout(
            title='Monthly Demand with Regression Line',
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
