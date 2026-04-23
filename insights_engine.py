from openai import OpenAI

client = OpenAI()

def generate_insights(summary, monthly, active_cp):
    prompt = f"""
    Analyze broker performance.

    Overall:
    {summary.to_string(index=False)}

    Monthly:
    {monthly.to_string(index=False)}

    Active CPs (last 30 days): {active_cp}

    Give:
    - Key insights
    - Risks
    - Recommendations
    """

    response = client.chat.completions.create(
        model="gpt-5.3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
