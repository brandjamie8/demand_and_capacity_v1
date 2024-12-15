import streamlit as st
import pandas as pd

st.title("Specialty Summary Table")

# Ensure waiting list data is available
if 'waiting_list_df' not in st.session_state or st.session_state.waiting_list_df is None:
    st.error("Waiting list data is not available. Please upload the data in the previous section.")
    st.stop()

waiting_list_df = st.session_state.waiting_list_df

# Retrieve baseline period from session state
if 'baseline_start_date' not in st.session_state or 'baseline_end_date' not in st.session_state:
    st.error("Baseline period not found. Please set the baseline period in the previous page.")
    st.stop()

# Convert baseline dates to month-end Timestamps
baseline_start = pd.to_datetime(st.session_state.baseline_start_date).to_period('M').to_timestamp('M')
baseline_end = pd.to_datetime(st.session_state.baseline_end_date).to_period('M').to_timestamp('M')

# Calculate the number of months in the baseline period
num_baseline_months = len(pd.date_range(start=baseline_start, end=baseline_end, freq='M'))

# Filter baseline data
baseline_df = waiting_list_df[(waiting_list_df['month'] >= baseline_start) & (waiting_list_df['month'] <= baseline_end)]

# Group by specialty and calculate metrics
specialty_summary = baseline_df.groupby('specialty').agg({
    'additions to waiting list': 'sum',
    'removals from waiting list': 'sum',
    'sessions': 'sum',
    'cancelled sessions': 'sum',
    'minutes utilised': 'sum',
    'cases': 'sum'
}).reset_index()

# Calculate extrapolated values
scaling_factor = 12 / num_baseline_months
specialty_summary['Additions (12-Month)'] = specialty_summary['additions to waiting list'] * scaling_factor
specialty_summary['Removals (12-Month)'] = specialty_summary['removals from waiting list'] * scaling_factor
specialty_summary['Cases (12-Month)'] = specialty_summary['cases'] * scaling_factor

# Calculate deficit
specialty_summary['Deficit (12-Month)'] = specialty_summary['Additions (12-Month)'] - specialty_summary['Removals (12-Month)']

# Determine capacity status message
session_duration_hours = 4
specialty_summary['Capacity Status'] = specialty_summary.apply(
    lambda row: (
        "Surplus capacity, waiting list will reduce" if row['Removals (12-Month)'] > row['Additions (12-Month)'] else
        "Sufficient capacity to meet demand" if row['Removals (12-Month)'] == row['Additions (12-Month)'] else
        "Insufficient capacity but more sessions would meet demand" if (row['sessions'] + row['cancelled sessions']) * session_duration_hours * 60 >= row['minutes utilised'] * scaling_factor else
        "Not meeting capacity, waiting list expected to grow"
    ),
    axis=1
)

# Select relevant columns to display
columns_to_display = [
    'specialty', 
    'Additions (12-Month)', 
    'Cases (12-Month)', 
    'Removals (12-Month)', 
    'Deficit (12-Month)', 
    'Capacity Status'
]

# Rename columns for better readability
specialty_summary_display = specialty_summary[columns_to_display].rename(columns={
    'specialty': 'Specialty',
    'Additions (12-Month)': 'Additions (12M)',
    'Cases (12-Month)': 'Cases (12M)',
    'Removals (12-Month)': 'Removals (12M)',
    'Deficit (12-Month)': 'Deficit (12M)',
    'Capacity Status': 'Status'
})

# Display the summary table
st.header("Specialty Summary")
st.dataframe(specialty_summary_display)

# Add a download button for the table
st.download_button(
    label="Download Specialty Summary",
    data=specialty_summary_display.to_csv(index=False),
    file_name="specialty_summary.csv",
    mime="text/csv"
)
