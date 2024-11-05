# pages/7_Demand_Analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import linregress
import numpy as np

st.title("Demand Analysis")

# Check if necessary data is available
if ('waiting_list_df' in st.session_state and st.session_state.waiting_list_df is not None) and \
   ('procedure_specialty_df' in st.session_state and st.session_state.procedure_specialty_df is not None):
    
    waiting_list_df = st.session_state.waiting_list_df
    procedure_specialty_df = st.session_state.procedure_specialty_df

    # Ensure required columns are present
    waiting_list_required_columns = ['month', 'specialty', 'additions to waiting list']
    if all(column in waiting_list_df.columns for column in waiting_list_required_columns):
        # Use selected specialty from session state
        selected_specialty = st.session_state.selected_specialty

        # Filter data based on selected specialty
        waiting_list_specialty_df = waiting_list_df[waiting_list_df['specialty'] == selected_specialty]

        # Convert 'month' column to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(waiting_list_specialty_df['month']):
            waiting_list_specialty_df['month'] = pd.to_datetime(waiting_list_specialty_df['month'])

        # Sort by month
        waiting_list_specialty_df = waiting_list_specialty_df.sort_values('month')

        # Extract months and demand data
        months = waiting_list_specialty_df['month']
        demand = waiting_list_specialty_df['additions to waiting list']

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
        start_demand = demand.iloc[0]
        end_demand = demand.iloc[-1]
        percentage_increase = ((end_demand - start_demand) / start_demand) * 100

        # Suggest a multiplier based on the percentage increase
        number_of_periods = len(demand)
        average_monthly_increase = percentage_increase / number_of_periods
        projected_multiplier = 1 + (average_monthly_increase / 100) * 12  # Projecting over 12 months

        st.write(f"**Demand Trend Analysis for {selected_specialty}**")
        st.write(f"Start of Year Demand: {start_demand:.0f}")
        st.write(f"End of Year Demand: {end_demand:.0f}")
        st.write(f"Total Percentage Increase Over the Year: {percentage_increase:.2f}%")

        # Assess statistical significance
        st.write(f"**Linear Regression Results:**")
        st.write(f"Slope: {slope:.4f}")
        st.write(f"Intercept: {intercept:.4f}")
        st.write(f"R-squared: {r_value**2:.4f}")
        st.write(f"P-value: {p_value:.4e}")

        if p_value < 0.05:
            st.write("The trend is **statistically significant** (p < 0.05).")
        else:
            st.write("The trend is **not statistically significant** (p >= 0.05).")

        st.write(f"Suggested Multiplier for Next Year's Demand: {projected_multiplier:.2f}")

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

        # Display the additional demand distribution
        st.subheader("Additional Demand Distribution Among Procedures")
        st.dataframe(procedure_specialty_df[['procedure', 'additional cases', 'additional minutes']])

        # Display charts
        st.subheader("Demand Over the Current Year with Regression Line")
        fig_demand = px.scatter(
            regression_df,
            x='month',
            y='demand',
            labels={'demand': 'Additions to Waiting List'},
            title='Monthly Demand with Regression Line',
            mode='lines',
            line=dict(color='#f5136f')
        )
        fig_demand.add_traces(
            px.line(
                regression_df,
                x='month',
                y='predicted_demand',
                labels={'predicted_demand': 'Predicted Demand'}
            ).data
        )
        st.plotly_chart(fig_demand, use_container_width=True)

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

    else:
        st.error("Waiting list data does not contain the required columns.")
else:
    st.write("Please ensure you have uploaded the required data and completed previous sections.")
