from pptx import Presentation
from datetime import datetime

def create_ppt(insights, summary, cp_funnel):

    prs = Presentation()

    # ---------------- TITLE ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Channel Partner Strategy Report"
    slide.placeholders[1].text = str(datetime.now().date())

    # ---------------- INSIGHTS ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Insights"
    slide.placeholders[1].text = insights

    # ---------------- TOP CP ----------------
    top = summary.sort_values(by="Conversion %", ascending=False).head(5)

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Top Performing CPs"
    slide.placeholders[1].text = top.to_string(index=False)

    # ---------------- RISK CP ----------------
    risk = summary[
        (summary["Fresh_Walkins"] > 20) &
        (summary["Conversion %"] < 5)
    ]

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Underperforming CPs"
    slide.placeholders[1].text = risk.to_string(index=False)

    # ---------------- FUNNEL VIEW ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Lead Quality (Hot/Warm/Cold)"
    slide.placeholders[1].text = cp_funnel.to_string(index=False)

    file = "Strategy_Report.pptx"
    prs.save(file)

    return file
