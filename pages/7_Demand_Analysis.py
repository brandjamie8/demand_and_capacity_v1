# pages/7_Demand_Analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import linregress

st.title("Demand Analysis")

# Check if necessary data is available
if 'waiting_list_df' in st.session_state and st.session_state.waiting_list_df is not None:
    waiting_list_df = st.session_state.waiting_list_df

    # Ensure required columns are present
    waiting_list_required_columns = ['month', 'specialty', 'additions to waiting list']
    if all(column in waiting_list_df.columns for column in waiting_list_required_columns):
        # Use selected specialty from session state
        specialties = waiting_list_df['specialty'].unique()
        if 'selected_specialty' not in st.session_state or st.session_state.selected_specialty not in specialties:
            st.session_state.selected_specialty = specialties[0]

        selected_specialty = st.selectbox(
            'Select Specialty',
            specialties,
            index=list(specialties).index(st.session_state.selected_specialty),
            key='demand_specialty_select'
        )

        # Save the selected specialty to session state
        st.session_state.selected_specialty = selected_specialty

        # Filter data based on selected specialty
        waiting_list_specialty_df = waiting_list_df[waiting_list_df['specialty'] == selected_specialty]

        # Convert 'month' column to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(waiting_list_specialty_df['month']):
            waiting_list_specialty_df['month'] = pd.to_datetime(waiting_list_specialty_df['month'])

        # Sort by month
        waiting_list_specialty_df = waiting_list_specialty_df.sort_values('month')

        # Extract months and demand data
        months = waiting_list_specialty_df['month'].map(pd.Timestamp.toordinal)
        demand = waiting_list_specialty_df['additions to waiting list']

        # Perform linear regression to assess trend
        slope, intercept, r_value, p_value, std_err = linregress(months, demand)

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
        st.write(f"Suggested Multiplier for Next Year's Demand: {projected_multiplier:.2f}")

        # Allow user to adjust the multiplier
        multiplier = st.number_input(
            "Adjust the Multiplier for Next Year's Demand",
            min_value=0.0,
            value=projected_multiplier,
            step=0.1,
            key='demand_multiplier'
        )

        # Calculate projected demand for next year
        total_demand_current_year = demand.sum()
        projected_demand_next_year = total_demand_current_year * multiplier

        st.write(f"**Total Demand for Current Year:** {total_demand_current_year:.0f}")
        st.write(f"**Projected Demand for Next Year:** {projected_demand_next_year:.0f}")

        # Save projected demand to session state
        st.session_state.multiplier = multiplier
        st.session_state.total_demand_current_year = total_demand_current_year
        st.session_state.projected_demand_next_year = projected_demand_next_year

        # Display charts
        st.subheader("Demand Over the Current Year")
        fig_demand = px.line(
            waiting_list_specialty_df,
            x='month',
            y='additions to waiting list',
            labels={'additions to waiting list': 'Additions to Waiting List'},
            title='Monthly Demand Over the Current Year'
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
    st.write("Please upload the Waiting List Data CSV file on the **Home** page.")
