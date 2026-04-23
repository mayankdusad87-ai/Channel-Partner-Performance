from pptx import Presentation
from datetime import datetime

def create_ppt(insights, summary, monthly):

    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Channel Partner Performance Report"
    slide.placeholders[1].text = str(datetime.now().date())

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Insights"
    slide.placeholders[1].text = insights

    file = "report.pptx"
    prs.save(file)

    return file
