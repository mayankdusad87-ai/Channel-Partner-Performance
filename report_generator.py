from pptx import Presentation
from datetime import datetime

def create_ppt(insights, summary, monthly):

    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "CP Performance Strategy"
    slide.placeholders[1].text = str(datetime.now().date())

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Insights"
    slide.placeholders[1].text = insights

    top = summary.sort_values(by="Conversion %", ascending=False).head(5)

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Top CPs"
    slide.placeholders[1].text = top.to_string(index=False)

    risk = summary[summary["Conversion %"] < 5]

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Risk CPs"
    slide.placeholders[1].text = risk.to_string(index=False)

    file = "Strategy_Report.pptx"
    prs.save(file)

    return file
