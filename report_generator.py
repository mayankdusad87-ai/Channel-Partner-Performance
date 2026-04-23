from pptx import Presentation
from datetime import datetime


def create_ppt(insights, summary, monthly):
    prs = Presentation()

    # Title Slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Broker Performance Report"
    slide.placeholders[1].text = str(datetime.now().date())

    # Insights Slide
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Insights"
    slide.placeholders[1].text = insights

    file = "broker_report.pptx"
    prs.save(file)

    return file
