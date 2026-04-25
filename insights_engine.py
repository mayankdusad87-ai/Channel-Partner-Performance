def generate_insights(summary, monthly):

    total_bookings = summary["Bookings"].sum()
    top5 = summary.sort_values("Bookings", ascending=False).head(5)

    contribution = (top5["Bookings"].sum()/total_bookings)*100 if total_bookings else 0

    scale = summary[summary["Strategy"]=="SCALE"].shape[0]
    fix = summary[summary["Strategy"]=="FIX"].shape[0]
    drop = summary[summary["Strategy"]=="DROP"].shape[0]

    insights = f"""
EXECUTIVE SUMMARY
- Top 5 CPs contribute {round(contribution,1)}% of bookings → dependency risk
- {scale} CPs can be scaled immediately
- {fix} CPs need fixing (conversion issues)
- {drop} CPs are underperforming → rationalize network

NETWORK DIAGNOSIS
- Major leakage at Fresh → Booking stage
- Lead quality vs closing mismatch observed

STRATEGY
- SCALE: High conversion + volume → double down
- FIX: High walk-ins but poor conversion → sales issue
- INCUBATE: Good conversion but low volume → push leads
- DROP: Low contribution → reduce bandwidth

MANAGEMENT ACTIONS
- Reallocate inventory to top CPs
- Introduce CP performance review weekly
- Incentivize conversion, not just walk-ins
"""

    return insights
