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
            st.error(f"❌ CIF sheet not found. Available: {excel.sheet_names}")
            st.stop()

        df = pd.read_excel(excel, sheet_name="CIF", header=3)

        # 🔥 NEW ENGINE OUTPUT
        summary, monthly = process_data(df)

        tabs = st.tabs([
            "🏆 Top Performers",
            "📊 Funnel & Diagnostics",
            "📅 Monthly Trend",
            "⚠️ Problem CPs",
            "📊 Network Health",
            "🎯 Strategy & Actions",
            "🧠 Management Insights"
        ])

        # ================= TOP PERFORMERS =================
        with tabs[0]:
            st.subheader("Top Channel Partners")

            top = summary.copy()
            top["Score"] = (
                top["Conversion %"] * 0.5 +
                top["Bookings"] * 0.3 +
                top["Hot %"] * 0.2
            )

            top = top.sort_values(by="Score", ascending=False).head(10)
            top = top.reset_index(drop=True)
            top.insert(0, "Rank", top.index + 1)

            st.dataframe(top)

        # ================= FUNNEL & DIAGNOSTICS =================
        with tabs[1]:
            st.subheader("Funnel Diagnostics (Per CP)")

            cols = [
                summary.columns[0],  # CP name
                "Fresh", "Hot", "Warm", "Cold",
                "Bookings", "Conversion %",
                "Hot %", "Hot→Booking %",
                "Problem"
            ]

            st.dataframe(summary[cols])

        # ================= MONTHLY =================
        with tabs[2]:
            st.subheader("Monthly Performance")

            latest = monthly.sort_values("Month").iloc[-1:]
            st.write("Latest Month Snapshot")
            st.dataframe(latest)

            st.write("Trend")
            st.line_chart(monthly.set_index("Month")[["Fresh", "Bookings"]])

        # ================= PROBLEM CP =================
        with tabs[3]:
            st.subheader("CPs Needing Attention")

            risk = summary[
                summary["Strategy"].isin(["FIX", "DROP"])
            ]

            st.dataframe(risk)

        # ================= NETWORK HEALTH =================
        with tabs[4]:
            st.subheader("📊 Network Health")

            total_bookings = summary["Bookings"].sum()

            if total_bookings > 0:
                top5 = summary.sort_values(by="Bookings", ascending=False).head(5)
                contribution = (top5["Bookings"].sum() / total_bookings) * 100
            else:
                contribution = 0

            st.metric("Top 5 Contribution %", round(contribution, 2))

            # Strategy split
            st.subheader("Strategy Split")
            st.bar_chart(summary["Strategy"].value_counts())

            # Lifecycle
            st.metric("Project Lifecycle", summary["Lifecycle"].iloc[0])

        # ================= STRATEGY =================
        with tabs[5]:
            st.subheader("CP Strategy & Actions")

            st.dataframe(
                summary[[
                    summary.columns[0],
                    "Strategy",
                    "Problem",
                    "Action"
                ]]
            )

            # 🔥 Highlight SCALE CPs
            st.subheader("🚀 Scale Immediately")
            st.dataframe(summary[summary["Strategy"] == "SCALE"])

            # 🔥 Highlight FIX CPs
            st.subheader("🛠 Fix Immediately")
            st.dataframe(summary[summary["Strategy"] == "FIX"])

        # ================= MANAGEMENT INSIGHTS =================
        with tabs[6]:
            st.subheader("🧠 Management Insights")

            if st.button("Generate Strategy Insights"):
                insights = generate_insights(summary, monthly)

                st.write(insights)

                ppt = create_ppt(insights, summary)

                with open(ppt, "rb") as f:
                    st.download_button(
                        "📥 Download Strategy PPT",
                        f,
                        file_name="Strategy_Report.pptx"
                    )

    except Exception as e:
        st.error(str(e))
