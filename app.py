import streamlit as st
import pandas as pd
from data_processor import process_data
from insights_engine import generate_insights
from report_generator import create_ppt

st.set_page_config(layout="wide")
st.title("🏢 Channel Partner Strategy Engine")

file = st.file_uploader("Upload Excel File", type=["xlsx"])

if file:
    try:
        excel = pd.ExcelFile(file)

        if "CIF" not in excel.sheet_names:
            st.error("❌ CIF sheet missing")
            st.stop()

        df = pd.read_excel(excel, sheet_name="CIF", header=3)

        summary, monthly = process_data(df)

        tabs = st.tabs([
            "🏆 Top CPs",
            "📊 Diagnostics",
            "📅 Monthly",
            "⚠️ Risk CPs",
            "📊 Network",
            "🎯 Strategy",
            "🧠 Insights"
        ])

        # TOP
        with tabs[0]:
            top = summary.sort_values("Bookings", ascending=False).head(10)
            st.dataframe(top)

        # DIAGNOSTICS
        with tabs[1]:
            st.dataframe(summary)

        # MONTHLY
        with tabs[2]:
            st.dataframe(monthly)

            if len(monthly) > 1:
                latest = monthly.iloc[-1]
                prev = monthly.iloc[-2]

                st.write(f"Booking change: {latest['Bookings'] - prev['Bookings']}")

        # RISK
        with tabs[3]:
            risk = summary[summary["Strategy"].isin(["FIX","DROP"])]
            st.dataframe(risk)

        # NETWORK
        with tabs[4]:
            total = summary["Bookings"].sum()
            top5 = summary.sort_values("Bookings", ascending=False).head(5)

            contribution = (top5["Bookings"].sum()/total)*100 if total else 0

            st.metric("Top 5 Contribution %", round(contribution,2))

            if contribution > 60:
                st.error("High dependency risk")

            st.bar_chart(summary["Strategy"].value_counts())

        # STRATEGY
        with tabs[5]:
            st.dataframe(summary[["Channel Partner","Strategy","Action"]])

        # INSIGHTS
        with tabs[6]:
            if st.button("Generate Insights"):
                insights = generate_insights(summary, monthly)
                st.write(insights)

                ppt = create_ppt(insights, summary)

                with open(ppt, "rb") as f:
                    st.download_button("Download PPT", f)

    except Exception as e:
        st.error(str(e))
