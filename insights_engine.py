import os
from groq import Groq

def generate_insights(summary, monthly, active_cp):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "⚠️ Please set GROQ_API_KEY in Streamlit Secrets"

    client = Groq(api_key=api_key)

    prompt = f"""
You are a real estate sourcing performance analyst.

Analyze the data:

OVERALL:
{summary.to_string(index=False)}

MONTHLY:
{monthly.to_string(index=False)}

Active CPs (last 30 days): {active_cp}

Give:
- Key insights
- Risks
- Trends
- Actionable recommendations

Use numbers and keep it business-focused.
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a business analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
