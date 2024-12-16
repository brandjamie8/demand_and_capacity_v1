# pages/2_Procedure_Demand.py




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
        procedure_specialty_df['demand minutes'] = procedure_specialty_df['total referrals'] * procedure_specialty_df['average duration']

        procedure_specialty_df['month'] = pd.to_datetime(procedure_specialty_df['month'])
        
        # Save the filtered DataFrame in session state for use in other pages
        st.session_state.procedure_specialty_df = procedure_specialty_df

        # Ensure baseline dates are set
        baseline_start = pd.to_datetime(st.session_state.baseline_start_date)
        baseline_end = pd.to_datetime(st.session_state.baseline_end_date)
        num_baseline_months = (baseline_end.to_period('M') - baseline_start.to_period('M')).n + 1

        st.write(f"**Baseline Period:** {baseline_start.strftime('%B %Y')} to {baseline_end.strftime('%B %Y')}")
        st.write(f"**Number of Months in Baseline:** {num_baseline_months} months")

        # --- Calculate DTAs (Decisions to Admit) ---
        baseline_procedure_df = procedure_specialty_df[
            (procedure_specialty_df['month'] >= baseline_start) &
            (procedure_specialty_df['month'] <= baseline_end)
        ]
        baseline_total_dtas = baseline_procedure_df['total referrals'].sum()
        baseline_scaled_dtas = (baseline_total_dtas / num_baseline_months) * 12
        st.write(f"**Decisions to Admit (DTAs) in Baseline Period (Scaled to Year):** {baseline_scaled_dtas:.0f}")

        # --- Calculate Additions to Waiting List ---
        if 'waiting_list_df' in st.session_state:
            waiting_list_df = st.session_state.waiting_list_df
            waiting_list_specialty_df = waiting_list_df[waiting_list_df['specialty'] == selected_specialty]
            baseline_waiting_list_df = waiting_list_specialty_df[
                (waiting_list_specialty_df['month'] >= baseline_start) &
                (waiting_list_specialty_df['month'] <= baseline_end)
            ]

            baseline_total_additions = baseline_waiting_list_df['additions to waiting list'].sum()
            baseline_scaled_additions = (baseline_total_additions / num_baseline_months) * 12
            percent_dtas_to_additions = (baseline_scaled_additions / baseline_scaled_dtas) * 100
            st.write(f"**Additions to Waiting List (Scaled to Year):** {baseline_scaled_additions:.0f} ({percent_dtas_to_additions:.2f}% of DTAs)")

            # --- Calculate Theatre Cases ---
            baseline_total_cases = baseline_waiting_list_df['cases'].sum()
            baseline_scaled_cases = (baseline_total_cases / num_baseline_months) * 12
            percent_additions_to_cases = (baseline_scaled_cases / baseline_scaled_additions) * 100
            st.write(f"**Theatre Cases (Scaled to Year):** {baseline_scaled_cases:.0f} ({percent_additions_to_cases:.2f}% of Additions)")
        else:
            st.error("Waiting list data is not available. Please upload it in the previous sections.")

        # --- Time Series Analysis and Prediction ---
        st.subheader("Time Series Analysis")

        # Filter pre-baseline data
        start_12_months_prior = baseline_start - pd.DateOffset(months=12)
        pre_baseline_df = waiting_list_specialty_df[
            (waiting_list_specialty_df['month'] >= start_12_months_prior) &
            (waiting_list_specialty_df['month'] < baseline_start)
        ]

        if not pre_baseline_df.empty:
            # Perform regression analysis
            pre_months = pre_baseline_df['month']
            pre_demand = pre_baseline_df['additions to waiting list']
            pre_months_ordinal = pre_months.map(pd.Timestamp.toordinal)
            slope, intercept, _, _, _ = linregress(pre_months_ordinal, pre_demand)

            # Predict DTAs for future months
            future_months = pd.date_range(
                start=st.session_state.model_start_date + pd.DateOffset(months=1),
                periods=12,
                freq='M'
            )
            if 'use_average_for_prediction' in st.session_state:
                baseline_scaled_monthly_dtas = baseline_scaled_dtas / 12
                predicted_dtas = [baseline_scaled_monthly_dtas] * len(future_months)
            else:
                future_months_ordinal = future_months.map(pd.Timestamp.toordinal)
                predicted_dtas = intercept + slope * future_months_ordinal

            predicted_additions = [dta * (percent_dtas_to_additions / 100) for dta in predicted_dtas]
            predicted_cases = [addition * (percent_additions_to_cases / 100) for addition in predicted_additions]

            # --- Plotting ---
            fig_demand = go.Figure()

            # Actual DTAs
            fig_demand.add_trace(go.Scatter(
                x=procedure_specialty_df['month'],
                y=procedure_specialty_df['total referrals'],
                mode='lines+markers',
                name='Actual DTAs',
                line=dict(color='orange')
            ))

            # Predicted DTAs
            fig_demand.add_trace(go.Scatter(
                x=future_months,
                y=predicted_dtas,
                mode='lines+markers',
                name='Predicted DTAs',
                line=dict(dash='dash', color='green')
            ))

            # Update layout
            fig_demand.update_layout(
                title='Predicted vs Actual DTAs',
                xaxis_title='Month',
                yaxis_title='Demand',
                legend_title='Legend'
            )

            st.plotly_chart(fig_demand, use_container_width=True)

            # Summary of Predictions
            st.write(f"**Predicted Additions to Waiting List over Next 12 Months:** {sum(predicted_additions):.0f}")
            st.write(f"**Predicted Theatre Cases over Next 12 Months:** {sum(predicted_cases):.0f}")
        else:
            st.warning("Not enough data in the 12 months before the baseline for trend analysis.")

else:
    st.error("Procedure data is missing. Please upload the required data.")


