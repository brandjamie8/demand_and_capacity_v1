st.title("Demand vs Capacity")

# Check if necessary data is available
if ('procedure_specialty_df' in st.session_state and st.session_state.procedure_specialty_df is not None) and \
   ('procedures_from_acpl' in st.session_state) and ('total_predicted_cases' in st.session_state):
    
    procedure_specialty_df = st.session_state.procedure_specialty_df

    # Select specialty
    specialties = procedure_specialty_df['specialty'].unique()
    selected_specialty = st.selectbox("Select Specialty:", specialties)

    # Filter data for the selected specialty
    filtered_df = procedure_specialty_df[procedure_specialty_df['specialty'] == selected_specialty]

    # Calculate Demand and Capacity (Cases)
    total_demand_cases = st.session_state.total_predicted_cases
    total_capacity_cases = st.session_state.procedures_from_acpl

    st.write(f"**Total Demand (Cases) for {selected_specialty}:** {total_demand_cases:.0f}")
    st.write(f"**Total Capacity (Cases) for {selected_specialty}:** {total_capacity_cases:.0f}")

    # Compare demand and capacity
    st.header("Demand vs Capacity Comparison (Cases)")

    demand_vs_capacity_df = pd.DataFrame({
        'Category': ['Total Demand Cases', 'Total Capacity Cases'],
        'Cases': [total_demand_cases, total_capacity_cases]
    })

    fig_demand_vs_capacity = px.bar(
        demand_vs_capacity_df,
        x='Category',
        y='Cases',
        title=f'Demand vs Capacity in Cases for {selected_specialty}',
        text='Cases'
    )
    st.plotly_chart(fig_demand_vs_capacity, use_container_width=True)

    # Determine if capacity meets demand
    st.header("Capacity Check")

    if total_capacity_cases >= total_demand_cases:
        st.success("The planned capacity meets or exceeds the demand.")
    else:
        st.warning("The planned capacity does not meet the demand.")
else:
    st.write("Please ensure you have completed the required sections and loaded all necessary data into session state.")
