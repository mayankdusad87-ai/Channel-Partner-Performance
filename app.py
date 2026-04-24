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

        df = pd.read_excel(excel, sheet_name="CIF", header=3)

        summary, monthly, cp_funnel, active_cp, active_cp_df = process_data(df)

        tabs = st.tabs([
            "🏆 Top Performers",
            "📊 Funnel View",
            "📅 Monthly Summary",
            "⚠️ Underperformers",
            "📊 Network Health",
            "🧠 AI Insights"
        ])

        # TOP PERFORMERS
        with tabs[0]:
            top = summary.copy()
            top["Score"] = (
                top["Conversion %"] * 0.4 +
                top["Bookings"] * 0.4 +
                top["Hot"] * 0.2
            )
            top = top.sort_values(by="Score", ascending=False).head(10)
            top = top.reset_index(drop=True)
            top.insert(0, "Rank", top.index + 1)

            st.dataframe(top)

        # FUNNEL
        with tabs[1]:
            st.dataframe(cp_funnel)

        # MONTHLY
        with tabs[2]:
            latest = monthly.sort_values("Month").iloc[-1:]
            st.dataframe(latest)
            st.line_chart(monthly.set_index("Month")[["Fresh", "Bookings"]])

        # UNDERPERFORMERS
        with tabs[3]:
            risk = summary[
                (summary["Fresh_Walkins"] > 20) &
                (summary["Conversion %"] < 5)
            ]
            st.dataframe(risk)

        # NETWORK HEALTH
        with tabs[4]:

    st.subheader("📊 Network Health")

    # ---- Top 5 Contribution ----
    total_bookings = summary["Bookings"].sum()

    if total_bookings > 0:
        top5 = summary.sort_values(by="Bookings", ascending=False).head(5)
        contribution = (top5["Bookings"].sum() / total_bookings) * 100
    else:
        contribution = 0

    st.metric("Top 5 Contribution %", round(contribution, 2))

    # ---- Active CPs ----
    st.subheader("Active CPs (Last 30 Days - Fresh Walk-ins)")

    st.metric("Total Active CPs", active_cp)

    # ✅ Show ONLY UNIQUE CP names
    cp_column_name = active_cp_df.columns[0]

    unique_cp_names = (
        active_cp_df[[cp_column_name]]
        .dropna()
        .drop_duplicates()
        .sort_values(by=cp_column_name)
    )

    st.dataframe(unique_cp_names.reset_index(drop=True))
        # AI
        with tabs[5]:
            if st.button("Generate AI Insights"):
                insights = generate_insights(summary, monthly, cp_funnel)
                st.write(insights)

                ppt = create_ppt(insights, summary, cp_funnel)

                with open(ppt, "rb") as f:
                    st.download_button("Download PPT", f, file_name="Strategy_Report.pptx")

    except Exception as e:
        st.error(str(e))
