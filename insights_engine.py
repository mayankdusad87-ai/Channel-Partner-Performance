import os
from groq import Groq

def generate_insights(summary, monthly, active_cp):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "⚠️ Please add GROQ_API_KEY in Streamlit Secrets"

    client = Groq(api_key=api_key)

    prompt = f"""
You are a senior real estate strategist having 20 years work experienc in Lodha, Rustomjee etc..

Analyze the data below:

OVERALL:
{summary.to_string(index=False)}

MONTHLY:
{monthly.to_string(index=False)}

Active CPs (last 30 days): {active_cp}

Give:
1. Key insights
2. Risks
3. Broker behavior patterns
4. Clear actionable recommendations

Use numbers and percentages.
Keep it sharp and business-focused.
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
