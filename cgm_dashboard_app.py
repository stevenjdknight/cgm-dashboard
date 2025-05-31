
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

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

    # Layout: Summary
    st.header("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Glucose", f"{df['Glucose (mmol/L)'].mean():.2f} mmol/L")
    with col2:
        st.metric("Max Glucose", f"{df['Glucose (mmol/L)'].max():.2f} mmol/L")
    with col3:
        st.metric("Min Glucose", f"{df['Glucose (mmol/L)'].min():.2f} mmol/L")

    # Glucose Over Time
    st.subheader("📈 Glucose Over Time")
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.lineplot(data=df, x="Device Timestamp", y="Glucose (mmol/L)", marker="o", ax=ax)
    ax.axhline(7.8, color='orange', linestyle='--', label='Upper Normal (7.8)')
    ax.axhline(3.9, color='red', linestyle='--', label='Lower Normal (3.9)')
    ax.set_ylabel("Glucose (mmol/L)")
    ax.set_xlabel("Time")
    ax.legend()
    st.pyplot(fig)

    # Optional notes display
    if df["Notes"].notnull().sum() > 0:
        st.subheader("📝 Notes")
        st.dataframe(df[df["Notes"].notnull()][["Device Timestamp", "Glucose (mmol/L)", "Notes"]].reset_index(drop=True))

else:
    st.info("Please upload a CGM CSV file to begin.")
