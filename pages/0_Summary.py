import streamlit as st
import pandas as pd

st.title("Specialty Summary Table")

# Ensure waiting list data is available
if 'waiting_list_df' not in st.session_state or st.session_state.waiting_list_df is None:
    st.error("Waiting list data is not available. Please upload the data in the previous section.")
    st.stop()

waiting_list_df = st.session_state.waiting_list_df

# Convert the 'month' column to datetime if not already
if not pd.api.types.is_datetime64_any_dtype(waiting_list_df['month']):
    waiting_list_df['month'] = pd.to_datetime(waiting_list_df['month'])

# User input for baseline period
st.subheader("Select Baseline Period")
min_date = waiting_list_df['month'].min()
max_date = waiting_list_df['month'].max()

col1, col2, _, _ = st.columns(4)
with col1:
    baseline_start = st.date_input("Baseline Start Month", min_date, min_value=min_date, max_value=max_date)
with col2:
    baseline_end = st.date_input("Baseline End Month", max_date, min_value=baseline_start, max_value=max_date)

# Validate baseline period
if baseline_start > baseline_end:
    st.error("Baseline start date must be before or equal to the end date.")
    st.stop()

# Filter waiting list data for the baseline period
baseline_start = pd.to_datetime(baseline_start).to_period('M').to_timestamp('M')
baseline_end = pd.to_datetime(baseline_end).to_period('M').to_timestamp('M')

baseline_df = waiting_list_df[(waiting_list_df['month'] >= baseline_start) & (waiting_list_df['month'] <= baseline_end)]

# Get the number of months in the baseline period
num_baseline_months = baseline_df['month'].nunique()

# Check if there is sufficient data
if baseline_df.empty:
    st.error("No data available for the selected baseline period.")
    st.stop()

# Get waiting list size for start and end months of the baseline period
april_size = waiting_list_df[
    (waiting_list_df['month'] == baseline_start)
].groupby('specialty')['total waiting list'].sum()

september_size = waiting_list_df[
    (waiting_list_df['month'] == baseline_end)
].groupby('specialty')['total waiting list'].sum()

# Calculate change in waiting list size
waiting_list_change = (september_size - april_size).reset_index()
waiting_list_change.columns = ['specialty', 'Waiting List Change']

# Group by specialty and calculate baseline metrics
specialty_summary = baseline_df.groupby('specialty').agg({
    'additions to waiting list': 'sum',
    'removals from waiting list': 'sum',
    'sessions': 'sum',
    'cancelled sessions': 'sum',
    'minutes utilised': 'sum',
    'cases': 'sum'
}).reset_index()

# Merge waiting list size data
specialty_summary = specialty_summary.merge(april_size.reset_index(), on='specialty', how='left')
specialty_summary = specialty_summary.merge(september_size.reset_index(), on='specialty', how='left')
specialty_summary = specialty_summary.merge(waiting_list_change, on='specialty', how='left')

specialty_summary.rename(columns={
    'total waiting list_x': 'Waiting List Size (Start)',
    'total waiting list_y': 'Waiting List Size (End)'
}, inplace=True)

# Calculate extrapolated values
scaling_factor = 12 / num_baseline_months
specialty_summary['Additions (12-Month)'] = specialty_summary['additions to waiting list'] * scaling_factor
specialty_summary['Removals (12-Month)'] = specialty_summary['removals from waiting list'] * scaling_factor
specialty_summary['Cases (12-Month)'] = specialty_summary['cases'] * scaling_factor

# Calculate deficit
specialty_summary['Deficit (12-Month)'] = specialty_summary['Additions (12-Month)'] - specialty_summary['Removals (12-Month)']

# Add a message about the expected change to the waiting list
specialty_summary['Expected Change'] = specialty_summary.apply(
    lambda row: (
        f"Increase in waiting list by {row['Deficit (12-Month)']:.0f}" if row['Deficit (12-Month)'] > 0 else
        f"Decrease in waiting list by {-row['Deficit (12-Month)']:.0f}" if row['Deficit (12-Month)'] < 0 else
        "No change in waiting list"
    ),
    axis=1
)

# Add a comparison between waiting list change and deficit
specialty_summary['Change vs. Deficit'] = specialty_summary.apply(
    lambda row: row['Waiting List Change'] - row['Deficit (12-Month)'],
    axis=1
)

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
    'additions to waiting list',
    'cases',
    'removals from waiting list',
    'Expected Change',
    'Waiting List Size (Start)',
    'Waiting List Size (End)',
    'Waiting List Change',  
    'Additions (12-Month)',
    'Removals (12-Month)',
    'Capacity Status'
]

# Rename columns for better readability
specialty_summary_display = specialty_summary[columns_to_display].rename(columns={
    'specialty': 'Specialty',
    'additions to waiting list': 'Additions (Baseline)',
    'removals from waiting list': 'Removals (Baseline)',
    'cases': 'Cases (Baseline)',
    'Additions (12-Month)': 'Additions (12M)',
    'Removals (12-Month)': 'Removals (12M)',
    'Expected Change': 'Expected WL Change',
    'Change vs. Deficit': 'Change vs. Deficit (12M)'
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
