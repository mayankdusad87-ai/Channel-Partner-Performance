def generate_insights(summary, monthly):

    total_bookings = summary["Bookings"].sum()
    top5 = summary.sort_values("Bookings", ascending=False).head(5)

    contribution = (top5["Bookings"].sum()/total_bookings)*100 if total_bookings else 0

    scale = summary[summary["Strategy"]=="SCALE"].shape[0]
    fix = summary[summary["Strategy"]=="FIX"].shape[0]
    drop = summary[summary["Strategy"]=="DROP"].shape[0]

    latest = monthly.iloc[-1]
    prev = monthly.iloc[-2] if len(monthly) > 1 else None

    insights = f"""
EXECUTIVE SUMMARY
- Top 5 CPs contribute {round(contribution,1)}% → dependency risk
- {scale} CPs ready to scale
- {fix} CPs need fixing
- {drop} CPs to be removed

MONTHLY TREND
"""

    if prev is not None:
        growth = latest["Bookings"] - prev["Bookings"]
        insights += f"- Booking change last month: {growth}\n"

    insights += """
NETWORK DIAGNOSIS
- Leakage at Fresh → Booking stage
- Lead quality inconsistency observed

STRATEGY
- SCALE: Double down
- FIX: Improve closing
- INCUBATE: Push volume
- DROP: Clean network

MANAGEMENT ACTIONS
- Reallocate inventory to top CPs
- Weekly CP review
- Incentivize conversion
"""

    return insights
