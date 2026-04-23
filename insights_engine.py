import os
from groq import Groq

def generate_insights(summary, monthly, active_cp):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "⚠️ Add GROQ_API_KEY in Streamlit Secrets"

    client = Groq(api_key=api_key)

    prompt = f"""
Analyze this broker performance data:

OVERALL:
{summary.to_string(index=False)}

MONTHLY:
{monthly.to_string(index=False)}

Active CPs: {active_cp}

Give:
- Insights
- Risks
- Trends
- Recommendations
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
