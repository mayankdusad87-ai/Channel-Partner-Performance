import streamlit as st
import pandas as pd
from data_processor import process_data
from insights_engine import generate_insights
from report_generator import create_ppt

st.title("🏢 Broker Performance AI (Clean Version)")

file = st.file_uploader("Upload Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    summary, monthly, active_cp = process_data(df)

    st.subheader("📊 Overall Summary")
    st.dataframe(summary)

    st.subheader("📅 Monthly Summary")
    st.dataframe(monthly)

    st.metric("Active CPs (Last 30 Days)", active_cp)

    if st.button("Generate AI Insights"):
        insights = generate_insights(summary, monthly, active_cp)
        st.write(insights)

        ppt = create_ppt(insights, summary, monthly)
        with open(ppt, "rb") as f:
            st.download_button("Download PPT", f, file_name="report.pptx")
