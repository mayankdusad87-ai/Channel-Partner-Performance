from pptx import Presentation
from datetime import datetime

def create_ppt(insights, summary, monthly):
    prs = Presentation()

    # Slide 1: Title
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Channel Partner Performance Report"
    slide.placeholders[1].text = str(datetime.now().date())

    # Slide 2: Insights
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Insights"
    slide.placeholders[1].text = insights

    file = "report.pptx"
    prs.save(file)

    return file
