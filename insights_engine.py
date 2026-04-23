import os
from groq import Groq

def generate_insights(summary, monthly, active_cp):

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
You are a real estate strategy consultant.

Analyze:

OVERALL:
{summary.to_string(index=False)}

MONTHLY:
{monthly.to_string(index=False)}

Active CPs: {active_cp}

Give:
1. Key insights
2. Risks
3. Top performers (why)
4. Poor performers (why)
5. Actions sourcing head must take
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
