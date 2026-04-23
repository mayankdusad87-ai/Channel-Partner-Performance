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

        # ✅ Correct header row
        df = pd.read_excel(excel, sheet_name="CIF", header=3)

        # 🔥 UPDATED FUNCTION (returns funnel also)
        summary, monthly, cp_funnel, active_cp = process_data(df)

        tabs = st.tabs([
            "🏆 Top Performers",
            "📊 Funnel View",
            "📅 Monthly Summary",
            "⚠️ Underperformers",
            "📊 Network Health",
            "🧠 AI Insights"
        ])

        # ================= TOP PERFORMERS =================
        with tabs[0]:
            top = summary.copy()

            # 🔥 INDUSTRY SCORE (balanced)
            top["Score"] = (
                top["Conversion %"] * 0.4 +
                top["Bookings"] * 0.4 +
                top["Hot"] * 0.2
            )

            top = top.sort_values(by="Score", ascending=False).head(10)
            top = top.reset_index(drop=True)
            top.insert(0, "Rank", top.index + 1)

            st.subheader("Top Channel Partners")
            st.dataframe(top)

        # ================= FUNNEL =================
        with tabs[1]:
            st.subheader("CP Funnel (Lead Quality View)")
            st.dataframe(cp_funnel.reset_index(drop=True))

        # ================= MONTHLY =================
        with tabs[2]:
            latest = monthly.sort_values("Month").iloc[-1:]

            st.subheader("Latest Month Performance")
            st.dataframe(latest)

            st.subheader("Trend")
            st.line_chart(monthly.set_index("Month")[["Fresh", "Bookings"]])

        # ================= UNDERPERFORMERS =================
        with tabs[3]:
            # 🔥 SMART FILTER
            risk = summary[
                ((summary["Fresh_Walkins"] > 20) & (summary["Conversion %"] < 5)) |
                ((summary["Hot"] > 5) & (summary["Bookings"] == 0))
            ]

            st.subheader("Underperforming CPs")
            st.dataframe(risk.reset_index(drop=True))

        # ================= NETWORK HEALTH =================
        with tabs[4]:
            total_bookings = summary["Bookings"].sum()
            top5 = summary.sort_values(by="Bookings", ascending=False).head(5)

            contribution = (top5["Bookings"].sum() / total_bookings) * 100

            st.metric("Top 5 Contribution %", round(contribution, 2))
            st.metric("Active CPs (Last 30 Days)", active_cp)

            # 🔥 Insight hint
            if contribution > 60:
                st.warning("⚠️ High dependency on few CPs")

        # ================= AI INSIGHTS =================
        with tabs[5]:
            if st.button("Generate AI Insights"):
                insights = generate_insights(summary, monthly, cp_funnel)

                st.subheader("Strategic Insights")
                st.write(insights)

                ppt = create_ppt(insights, summary, cp_funnel)

                with open(ppt, "rb") as f:
                    st.download_button(
                        "Download Strategy PPT",
                        f,
                        file_name="Strategy_Report.pptx"
                    )

    except Exception as e:
        st.error(str(e))
