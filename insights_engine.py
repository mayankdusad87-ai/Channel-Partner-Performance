import os
from groq import Groq

def generate_insights(summary, monthly, cp_funnel):

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
You are a senior real estate sourcing strategist working with Lodha group

DATA:

FUNNEL PERFORMANCE:
{cp_funnel.to_string(index=False)}

MONTHLY PERFORMANCE:
{monthly.to_string(index=False)}

Analyze deeply:

1. Which CPs are top performers and WHY
2. Which CPs are underperforming and WHY
3. Role of Hot/Warm/Cold mix in performance
4. Any inefficiencies in conversion funnel
5. Dependency risks in CP network

Give output in this format:

- Key Insights
- Risks
- Recommended Actions (very specific, actionable)
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
