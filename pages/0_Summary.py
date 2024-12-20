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
min_date = waiting_list_df['month'].min().date()
max_date = waiting_list_df['month'].max().date()

col1, col2, _, _ = st.columns(4)
with col1:
    baseline_start = st.date_input("Baseline Start Month", '2024-04-30', min_value=min_date, max_value=max_date)
with col2:
    baseline_end = st.date_input("Baseline End Month", '2024-09-30', min_value=baseline_start, max_value=max_date)

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
specialty_summary['Deficit (12-Month)'] = specialty_summary['additions to waiting list'] - specialty_summary['removals from waiting list']

specialty_summary['Expected Change'] = specialty_summary.apply(
    lambda row: (
        f"⬆ Increase by {row['Deficit (12-Month)']:.0f}" if row['Deficit (12-Month)'] > 0 else
        f"⬇ Decrease by {-row['Deficit (12-Month)']:.0f}" if row['Deficit (12-Month)'] < 0 else
        "➡ No change"
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

specialty_summary['Cases (12M)'] = (
    specialty_summary['Removals (12-Month)'] *
    (specialty_summary['cases'] / specialty_summary['removals from waiting list'])
)

# Replace NaN or infinite values caused by division by zero with 0
specialty_summary['Cases (12M)'] = specialty_summary['Cases (12M)'].fillna(0).replace([float('inf'), float('-inf')], 0)

# Calculate Cases Needed for Additions (12M)
specialty_summary['Cases to Meet Demand (12M)'] = (
    specialty_summary['Cases (12M)'] *
    (specialty_summary['Additions (12-Month)'] / specialty_summary['Removals (12-Month)'])
)

# Replace NaN or infinite values caused by division by zero with 0 for Cases Needed for Additions (12M)
specialty_summary['Cases to Meet Demand (12M)'] = specialty_summary['Cases to Meet Demand (12M)'].fillna(0).replace([float('inf'), float('-inf')], 0)





# Select relevant columns to display
columns_to_display = [
    'specialty', 
    'additions to waiting list',
    'removals from waiting list',
    'cases',
    'Expected Change',
    'Waiting List Size (Start)',
    'Waiting List Size (End)',
    'Waiting List Change',  
    'Additions (12-Month)',
    'Removals (12-Month)',
    'Cases (12M)',
    'Cases to Meet Demand (12M)'
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






# Calculate the total row
total_row = specialty_summary_display.sum(numeric_only=True)
total_row['Specialty'] = 'Total'
total_row = pd.DataFrame(total_row).T

# Combine the total row with the original table
specialty_summary_display_with_total = pd.concat([specialty_summary_display, total_row], ignore_index=True)

# Format the numbers to zero decimal places
def format_numbers(val):
    if pd.isna(val):  # Check for NaN values
        return "0"  # Replace NaN with '0'
    if isinstance(val, (int, float)):
        return f"{int(val):,}"  # Add commas for thousands separator
    return val

# Highlight the total row
def highlight_total_row(row):
    if row.name == len(specialty_summary_display):  # Check if it's the last row (total row)
        return ['background-color: whitesmoke; font-weight: bold' for _ in row]
    return ['' for _ in row]

# Apply formatting and styling
styled_table = (
    specialty_summary_display_with_total.style
    .apply(highlight_total_row, axis=1)
    .format(format_numbers)
)

# Display the styled table
st.header("Specialty Summary")
st.write(styled_table)

# Add a download button for the table without styling
st.download_button(
    label="Download Specialty Summary",
    data=specialty_summary_display_with_total.fillna(0).to_csv(index=False),  # Replace NaN for download
    file_name="specialty_summary_with_total.csv",
    mime="text/csv"
)


