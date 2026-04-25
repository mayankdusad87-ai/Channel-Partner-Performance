from pptx import Presentation
from datetime import datetime

def create_ppt(insights, summary):

    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Channel Partner Strategy"
    slide.placeholders[1].text = str(datetime.now().date())

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Executive Summary"
    slide.placeholders[1].text = insights

    # Strategy split
    strat = summary["Strategy"].value_counts()

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Strategy Split"
    slide.placeholders[1].text = strat.to_string()

    # Top CP
    top = summary.sort_values("Bookings", ascending=False).head(5)

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Top Performers"
    slide.placeholders[1].text = top.to_string(index=False)

    # Actions
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Action Plan"
    slide.placeholders[1].text = summary[["Channel Partner","Strategy","Action"]].to_string(index=False)

    file = "Strategy_Report.pptx"
    prs.save(file)

    return file
