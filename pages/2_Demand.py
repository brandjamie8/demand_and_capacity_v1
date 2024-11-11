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
        
        # Filter data based on baseline dates
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
        
        # Calculate the percentage increase over the period
        start_demand = demand.iloc[:3].mean() if len(demand) >= 3 else demand.iloc[0]
        end_demand = demand.iloc[-3:].mean() if len(demand) >= 3 else demand.iloc[-1]
        percentage_increase = ((end_demand - start_demand) / start_demand) * 100
        
        # Suggest a multiplier based on the percentage increase
        number_of_periods = len(demand)
        average_monthly_increase = percentage_increase / number_of_periods
        projected_multiplier = 1 + (average_monthly_increase / 100) * 12  # Projecting over 12 months
        
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

        st.write(f"Average demand in first 3 months: {start_demand:.0f}")
        st.write(f"Average demand in last 3 months: {end_demand:.0f}")
        st.write(f"Percentage difference between start and end of year: {percentage_increase:.2f}%")

        # Assess statistical significance
        st.write(f"Linear Regression Results:")

        col1, col2, col3 = st.columns(3)

        with col1:
           st.write(f"Slope: {slope:.3f}")
           st.write(f"Intercept: {intercept:.3f}")
        with col2:
           st.write(f"R-squared: {r_value**2:.3f}")
           st.write(f"P-value: {p_value:.3e}")

        if p_value < 0.05:
            st.write("The trend is **statistically significant** (p < 0.05).")
            st.write("This means you should change the expected demand for next year.")
            st.write(f"Suggested multiplier for next year's demand: {projected_multiplier:.2f}")
        else:
            st.write("The trend is **not statistically significant** (p >= 0.05).")
            st.write("This means you may want change the expected demand for next year if you think it will be different.")
            st.write(f"Suggested multiplier for next year's demand: Between 1 and {projected_multiplier:.2f}")
        

        # Allow user to adjust the multiplier
        multiplier = st.number_input(
            "Adjust the Multiplier for Next Year's Demand",
            min_value=0.0,
            value=round(projected_multiplier, 2),
            step=0.1,
            key='demand_multiplier'
        )

        # Calculate projected demand for next year
        total_demand_current_year = demand.sum()
        projected_demand_next_year = int(round(total_demand_current_year * multiplier))
        
        st.write(f"")
        st.write(f"**Total Demand for Current Year:** {total_demand_current_year:.0f}")
        st.write(f"**Projected Demand for Next Year (Rounded to Whole Number):** {projected_demand_next_year}")

        # Save projected demand to session state
        st.session_state.multiplier = multiplier
        st.session_state.total_demand_current_year = total_demand_current_year
        st.session_state.projected_demand_next_year = projected_demand_next_year

        # Calculate additional demand
        additional_demand = projected_demand_next_year - total_demand_current_year
        st.write(f"**Additional Demand for Next Year:** {additional_demand}")

        # Distribute additional demand among procedures based on their probability distribution
        procedure_specialty_df = procedure_specialty_df.copy()
        total_referrals = procedure_specialty_df['total referrals'].sum()
        procedure_specialty_df['probability'] = procedure_specialty_df['total referrals'] / total_referrals

        # Calculate additional cases per procedure
        procedure_specialty_df['additional cases'] = procedure_specialty_df['probability'] * additional_demand
        procedure_specialty_df['additional cases'] = procedure_specialty_df['additional cases'].round().astype(int)

        # Ensure the sum of additional cases equals the additional demand
        total_additional_cases = procedure_specialty_df['additional cases'].sum()
        difference = additional_demand - total_additional_cases

        # Adjust for any rounding differences
        if difference != 0:
            indices = procedure_specialty_df.index.tolist()
            for i in range(abs(difference)):
                idx = indices[i % len(indices)]
                if difference > 0:
                    procedure_specialty_df.at[idx, 'additional cases'] += 1
                else:
                    if procedure_specialty_df.at[idx, 'additional cases'] > 0:
                        procedure_specialty_df.at[idx, 'additional cases'] -= 1

        # Calculate additional minutes per procedure
        procedure_specialty_df['additional minutes'] = procedure_specialty_df['additional cases'] * procedure_specialty_df['average duration']

        # Save the updated DataFrame to session state
        st.session_state.procedure_specialty_df = procedure_specialty_df

        # Display bar chart comparing current year and next year's projected demand
        st.subheader("Current Year Demand vs. Projected Next Year Demand")
        demand_comparison_df = pd.DataFrame({
            'Year': ['Current Year', 'Next Year (Projected)'],
            'Total Demand': [total_demand_current_year, projected_demand_next_year]
        })
        fig_comparison = px.bar(
            demand_comparison_df,
            x='Year',
            y='Total Demand',
            text='Total Demand',
            title='Demand Comparison'
        )
        st.plotly_chart(fig_comparison, use_container_width=True)


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
        st.error("Waiting list data does not contain the required columns.")
else:
    st.write("Please ensure you have uploaded the required data and completed previous sections.")


