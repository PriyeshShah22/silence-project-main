def build_insights_prompt(summary: dict) -> str:
    return f"""
You are a data analyst for a governance “silence monitoring” tool.

Goal:
Generate meaningful insights, trends, and descriptive analytics from a CSV dataset of civic complaint reporting.

Dataset summary (authoritative):
{summary}

What to produce:
1) Plain-English executive summary (5-8 bullets)
2) Key anomalies / outliers (silent zones, extreme densities, unusual trend gaps)
3) Data quality notes (missingness, suspicious values, skew)
4) Suggested follow-up analyses and what additional columns would improve accuracy
5) Ethical cautions: silence can have multiple causes; avoid over-claiming

Style:
Concise, decision-oriented, no jargon. If you make an inference, state confidence and why. Keep this very very short and readable like a single paragraph. Dont try to make anything bold 
""".strip()
