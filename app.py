import streamlit as st
import pandas as pd
from data_processor import process_data
from insights_engine import generate_insights
from report_generator import create_ppt

st.set_page_config(layout="wide")
st.title("🏢 Channel Partner Performance Intelligence")

file = st.file_uploader("Upload Excel File", type=["xlsx"])

if file:
    try:
        excel = pd.ExcelFile(file)

        if "CIF" not in excel.sheet_names:
            st.error(f"❌ CIF sheet not found. Available: {excel.sheet_names}")
            st.stop()

        # 🔥 FIX: header row at row 4
        df = pd.read_excel(excel, sheet_name="CIF", header=3)

        summary, monthly, active_cp = process_data(df)

        tabs = st.tabs([
            "🏆 Top Performers",
            "📅 Monthly Summary",
            "⚠️ Underperformers",
            "📊 Network Health",
            "🧠 AI Insights"
        ])

        # ---------------- TOP PERFORMERS ----------------
        with tabs[0]:
            top = summary.copy()
            top["Score"] = (
                top["Conversion %"] * 0.5 +
                top["Bookings"] * 0.3 +
                top["Revisit Rate"] * 0.2
            )
            top = top.sort_values(by="Score", ascending=False).head(10)

            st.subheader("Top Channel Partners")
            st.dataframe(top.reset_index(drop=True))

        # ---------------- MONTHLY ----------------
        with tabs[1]:
            latest = monthly.sort_values("Month").iloc[-1:]
            st.subheader("Latest Month")
            st.dataframe(latest)

            st.line_chart(monthly.set_index("Month")[["Fresh", "Bookings"]])

        # ---------------- UNDERPERFORMERS ----------------
        with tabs[2]:
            risk = summary[
                (summary["Fresh_Walkins"] > 20) &
                (summary["Conversion %"] < 5)
            ]
            st.subheader("Underperforming CPs")
            st.dataframe(risk)

        # ---------------- NETWORK HEALTH ----------------
        with tabs[3]:
            total_bookings = summary["Bookings"].sum()
            top5 = summary.sort_values(by="Bookings", ascending=False).head(5)

            contribution = (top5["Bookings"].sum() / total_bookings) * 100

            st.metric("Top 5 Contribution %", round(contribution, 2))
            st.metric("Active CPs (Last 30 Days)", active_cp)

        # ---------------- AI INSIGHTS ----------------
        with tabs[4]:
            if st.button("Generate AI Insights"):
                insights = generate_insights(summary, monthly, active_cp)
                st.write(insights)

                ppt = create_ppt(insights, summary, monthly)

                with open(ppt, "rb") as f:
                    st.download_button("Download PPT", f, file_name="Strategy_Report.pptx")

    except Exception as e:
        st.error(str(e))
