import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

st.set_page_config(layout="wide")
st.title("📊 Libre2 CGM Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your CGM CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Convert datetime
    df["Device Timestamp"] = pd.to_datetime(df["Device Timestamp"], errors='coerce')
    df = df.sort_values("Device Timestamp")

    # Glucose unification (pick available column)
    df["Glucose (mmol/L)"] = df["Scan Glucose mmol/L"].combine_first(df["Historic Glucose mmol/L"])

    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    min_date = df["Device Timestamp"].min()
    max_date = df["Device Timestamp"].max()
    date_range = st.sidebar.date_input("Select date range", [min_date, max_date])
    glucose_min = st.sidebar.slider("Minimum Glucose (mmol/L)", 0.0, 20.0, 0.0)
    glucose_max = st.sidebar.slider("Maximum Glucose (mmol/L)", 0.0, 20.0, 20.0)
    keyword = st.sidebar.text_input("Search Notes")

    # Apply filters
    filtered_df = df[
        (df["Device Timestamp"].dt.date >= date_range[0]) &
        (df["Device Timestamp"].dt.date <= date_range[1]) &
        (df["Glucose (mmol/L)"].between(glucose_min, glucose_max))
    ]
    if keyword:
        filtered_df = filtered_df[filtered_df["Notes"].fillna("").str.contains(keyword, case=False)]

    # Layout: Summary
    st.header("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Glucose", f"{filtered_df['Glucose (mmol/L)'].mean():.2f} mmol/L")
    with col2:
        st.metric("Max Glucose", f"{filtered_df['Glucose (mmol/L)'].max():.2f} mmol/L")
    with col3:
        st.metric("Min Glucose", f"{filtered_df['Glucose (mmol/L)'].min():.2f} mmol/L")

    # Glucose Over Time
    st.subheader("📈 Glucose Over Time")
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.lineplot(data=filtered_df, x="Device Timestamp", y="Glucose (mmol/L)", marker="o", ax=ax)
    ax.axhline(7.8, color='orange', linestyle='--', label='Upper Normal (7.8)')
    ax.axhline(3.9, color='red', linestyle='--', label='Lower Normal (3.9)')
    ax.set_ylabel("Glucose (mmol/L)")
    ax.set_xlabel("Time")
    ax.legend()
    st.pyplot(fig)

    # Expandable Notes Table
    if filtered_df["Notes"].notnull().sum() > 0:
        st.subheader("📝 Filtered Notes Table")
        for _, row in filtered_df[filtered_df["Notes"].notnull()].iterrows():
            with st.expander(f"{row['Device Timestamp']} | {row['Glucose (mmol/L)']:.2f} mmol/L"):
                st.write(row['Notes'])

    # Export option
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📤 Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_cgm_data.csv',
        mime='text/csv'
    )

else:
    st.info("Please upload a CGM CSV file to begin.")
