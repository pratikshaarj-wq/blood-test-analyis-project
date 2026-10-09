import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Set Page Configuration
st.set_page_config(page_title="Blood Test Analysis Dashboard", page_icon="🩸", layout="wide")

# Standard Medical/Clinical Reference Ranges
REF_RANGES = {
    'Hemoglobin_g_dL': {'min': 12.0, 'max': 17.5, 'unit': 'g/dL', 'label': 'Hemoglobin'},
    'Blood_Glucose_mg_dL': {'min': 70.0, 'max': 99.0, 'unit': 'mg/dL', 'label': 'Blood Glucose'},
    'Cholesterol_mg_dL': {'min': 125.0, 'max': 200.0, 'unit': 'mg/dL', 'label': 'Cholesterol'},
    'WBC_Count_cells_uL': {'min': 4500, 'max': 11000, 'unit': 'cells/µL', 'label': 'WBC Count'},
    'Platelet_Count_per_uL': {'min': 150000, 'max': 450000, 'unit': '/µL', 'label': 'Platelet Count'},
    'Vitamin_B12_pg_mL': {'min': 200.0, 'max': 900.0, 'unit': 'pg/mL', 'label': 'Vitamin B12'},
    'Vitamin_D_ng_mL': {'min': 30.0, 'max': 100.0, 'unit': 'ng/mL', 'label': 'Vitamin D'},
    'Iron_ug_dL': {'min': 60.0, 'max': 170.0, 'unit': 'µg/dL', 'label': 'Iron'},
    'Systolic_BP_mmHg': {'min': 90, 'max': 120, 'unit': 'mmHg', 'label': 'Systolic BP'},
    'Diastolic_BP_mmHg': {'min': 60, 'max': 80, 'unit': 'mmHg', 'label': 'Diastolic BP'},
    'BMI': {'min': 18.5, 'max': 24.9, 'unit': 'kg/m²', 'label': 'BMI'}
}

# Load Dataset
@st.cache_data
def load_data():
    path = "blood_test_results_5000_with_disease_summary.csv"
    df = pd.read_csv(path, index_col=0)
    return df

try:
    blood = load_data()
except Exception as e:
    st.error(f"Could not load CSV file. Ensure 'blood_test_results_5000_with_disease_summary.csv' is in your repository. Error: {e}")
    st.stop()

num_cols = ["Age", "Hemoglobin_g_dL", "Blood_Glucose_mg_dL", "Cholesterol_mg_dL",
            "WBC_Count_cells_uL", "Platelet_Count_per_uL", "Vitamin_B12_pg_mL",
            "Vitamin_D_ng_mL", "Iron_ug_dL", "Systolic_BP_mmHg",
            "Diastolic_BP_mmHg", "BMI"]

graph_cols = ["Hemoglobin_g_dL", "Blood_Glucose_mg_dL", "Cholesterol_mg_dL"]

st.title("🩸 Blood Test Result Analysis & Diagnostics Portal")

# Sidebar Navigation
st.sidebar.header("Navigation Menu")
menu = st.sidebar.selectbox("Choose Option", [
    "1. Color-Coded Patient Assessment",
    "2. View Dataframe & Records",
    "3. DataFrame Statistics",
    "4. Search Data",
    "5. Sorting Records",
    "6. Summary Calculations",
    "7. Data Visualization"
])

# 1. COLOR-CODED PATIENT REPORT CARD
if menu == "1. Color-Coded Patient Assessment":
    st.header("📋 Interactive Color-Coded Health Assessment")
    st.markdown("Select a patient to generate an instant color-coded diagnostic evaluation against clinical healthy ranges.")

    pid = st.selectbox("Select Patient ID", blood.index.unique())

    if pid in blood.index:
        patient = blood.loc[pid]

        st.subheader(f"Patient File: {pid} — {patient['Name']}")
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        col_a.metric("Age", f"{patient['Age']} yrs")
        col_b.metric("Gender", patient['Gender'])
        col_c.metric("City", patient['City'])
        col_d.metric("Test Date", patient['Test_Date'])
        col_e.metric("Diagnosed Condition", patient['Disease'])

        st.divider()
        st.subheader("🩸 Lab Test Breakdown & Color Alerts")

        c1, c2, c3 = st.columns(3)
        metric_keys = list(REF_RANGES.keys())

        for idx, key in enumerate(metric_keys):
            val = patient[key]
            ref = REF_RANGES[key]
            min_val, max_val = ref['min'], ref['max']
            unit = ref['unit']
            label = ref['label']

            if val < min_val:
                status_str = f"🔴 LOW ({val} {unit}) | Safe: {min_val}–{max_val}"
            elif val > max_val:
                status_str = f"🔴 HIGH ({val} {unit}) | Safe: {min_val}–{max_val}"
            else:
                status_str = f"🟢 NORMAL ({val} {unit}) | Safe: {min_val}–{max_val}"

            target_col = c1 if idx % 3 == 0 else (c2 if idx % 3 == 1 else c3)
            with target_col:
                st.write(f"**{label}**")
                if "NORMAL" in status_str:
                    st.success(status_str)
                else:
                    st.error(status_str)

        st.divider()

        st.subheader("🎯 Blood Glucose Dial Indicator")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=patient['Blood_Glucose_mg_dL'],
            title={'text': "Blood Glucose (mg/dL)"},
            gauge={
                'axis': {'range': [50, 250]},
                'bar': {'color': "#1a237e"},
                'steps': [
                    {'range': [50, 99], 'color': "#c8e6c9"},
                    {'range': [99, 125], 'color': "#fff9c4"},
                    {'range': [125, 250], 'color': "#ffcdd2"}
                ]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

# 2. VIEW DATAFRAME & RECORDS
elif menu == "2. View Dataframe & Records":
    st.header("📄 Dataset Overview & Records")
    st.dataframe(blood)

    st.subheader("Head / Tail Records")
    num_rows = st.number_input("Number of records to show:", min_value=1, max_value=100, value=5)
    tab1, tab2 = st.tabs(["Top Records (Head)", "Bottom Records (Tail)"])
    with tab1:
        st.table(blood.head(num_rows))
    with tab2:
        st.table(blood.tail(num_rows))

# 3. DATAFRAME STATISTICS
elif menu == "3. DataFrame Statistics":
    st.header("📊 DataFrame Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", blood.shape[0])
    col2.metric("Total Columns", blood.shape[1])
    col3.metric("Total Elements", blood.size)

    st.subheader("Column Names")
    st.write(list(blood.columns))

    st.subheader("Data Types")
    st.write(blood.dtypes.astype(str))

    st.subheader("Summary Statistics")
    st.dataframe(blood[num_cols].describe())

# 4. SEARCH DATA
elif menu == "4. Search Data":
    st.header("🔍 Search Specific Records")
    search_type = st.radio("Search Option:", ["Patient ID (Row)", "Column", "Specific Cell"])
    
    if search_type == "Patient ID (Row)":
        s_pid = st.text_input("Enter Patient ID (e.g., BT00001):")
        if s_pid:
            if s_pid in blood.index:
                st.write(blood.loc[s_pid])
            else:
                st.error("Patient ID not found.")

    elif search_type == "Column":
        col_name = st.selectbox("Select Column:", blood.columns)
        st.write(blood[col_name])

    elif search_type == "Specific Cell":
        s_pid = st.text_input("Enter Patient ID:")
        col_name = st.selectbox("Select Column:", blood.columns)
        if s_pid and col_name:
            if s_pid in blood.index:
                st.info(f"{col_name} for {s_pid}: **{blood.loc[s_pid, col_name]}**")
            else:
                st.error("Patient ID not found.")

# 5. SORTING RECORDS
elif menu == "5. Sorting Records":
    st.header("🔃 Sort Dataset")
    sort_col = st.selectbox("Select Column to Sort By:", num_cols)
    order = st.radio("Order:", ["Ascending", "Descending"])
    ascending_flag = True if order == "Ascending" else False

    sorted_df = blood.sort_values(by=sort_col, ascending=ascending_flag)
    st.dataframe(sorted_df)

# 6. SUMMARY CALCULATIONS
elif menu == "6. Summary Calculations":
    st.header("🧮 Column Calculations")
    calc_col = st.selectbox("Select Numeric Column:", num_cols)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sum", f"{blood[calc_col].sum():,.2f}")
    c2.metric("Average (Mean)", f"{blood[calc_col].mean():,.2f}")
    c3.metric("Minimum", f"{blood[calc_col].min():,.2f}")
    c4.metric("Maximum", f"{blood[calc_col].max():,.2f}")

# 7. DATA VISUALIZATION
elif menu == "7. Data Visualization":
    st.header("📈 Data Visualization (Matplotlib)")
    
    graph_type = st.radio("Select Graph Type:", ["Line Graph", "Vertical Bar Graph", "Horizontal Bar Graph"])
    n_pts = st.slider("Select number of patients to plot from top:", min_value=5, max_value=50, value=10)
    
    sub_df = blood.head(n_pts)
    fig, ax = plt.subplots(figsize=(10, 5))

    if graph_type == "Line Graph":
        ax.plot(sub_df.index, sub_df["Hemoglobin_g_dL"], marker='o', label="Hemoglobin")
        ax.plot(sub_df.index, sub_df["Blood_Glucose_mg_dL"], marker='s', label="Blood Glucose")
        ax.plot(sub_df.index, sub_df["Cholesterol_mg_dL"], marker='^', label="Cholesterol")
        ax.set_title("Line Graph representing Blood Test Results")
        ax.set_xlabel("Patient ID")
        ax.set_ylabel("Test Values")
        plt.xticks(rotation=45)
        ax.legend()

    elif graph_type == "Vertical Bar Graph":
        sub_df[graph_cols].plot(kind='bar', ax=ax)
        ax.set_title("Bar Graph representing Blood Test Results")
        ax.set_xlabel("Patient ID")
        ax.set_ylabel("Test Values")
        plt.xticks(rotation=45)

    elif graph_type == "Horizontal Bar Graph":
        sub_df[graph_cols].plot(kind='barh', ax=ax)
        ax.set_title("Horizontal Bar Graph representing Blood Test Results")
        ax.set_xlabel("Test Values")
        ax.set_ylabel("Patient ID")

    st.pyplot(fig)
