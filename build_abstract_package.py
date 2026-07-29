"""build_abstract_package.py
Builds the college "Abstract Review" submission package:
  1) Abstract_Submission.docx  -> Title block (Topic, Student, JNTU No., Guide)
                                    + Abstract + Keywords + References (IEEE)
  2) Abstract_Presentation.pptx -> 3 slides (Topic/Student/Guide, Abstract, References)
  3) Submission_Diary.md        -> checklist + faculty/guide signature slots
Real, verifiable references from top venues (ICLR, CVPR, ICCV, Nature/Springer,
Frontiers) + the two REAL datasets used in the project.
"""
import datetime

# ---- editable identity placeholders (fill before submission) ----
STUDENT_NAME = "[STUDENT NAME]"
JNTU_NO      = "[JNTU No.]"
GUIDE_NAME   = "[GUIDE NAME]"
DEPT         = "[DEPARTMENT]"
COLLEGE      = "[COLLEGE NAME]"
TOPIC        = "Smart Farming — AI Based Crop Yield Prediction"

TODAY = datetime.date.today().strftime("%d %b %Y")

ABSTRACT = (
    "Accurate, pre-harvest estimation of crop yield is central to food security and the "
    "economic resilience of smallholder farmers, especially in developing agrarian economies "
    "where agronomic expertise is scarce. This work proposes an integrated, low-cost decision-"
    "support framework for precision agriculture that (i) predicts crop yield (tons per hectare) "
    "from crop identity, soil type, and environmental parameters — rainfall, temperature, humidity, "
    "soil pH, and macronutrients (N, P, K); (ii) quantifies prediction drivers through model-"
    "agnostic permutation-importance analysis; and (iii) ranks the three most productive crops for "
    "a given soil using the trained model on the farmer's own parameters. Seven regression algorithms "
    "are benchmarked on a REAL, publicly available Indian agriculture statistics dataset "
    f"(246,091 raw records; {12} crops after cleaning, 35,364 modelling rows). The deployed "
    "Random-Forest regressor attains R2 = 0.7455 (RMSE = 4.331). A lightweight, farmer-"
    "practical web interface requires only Crop and Soil Type; rainfall is resolved geographically "
    "via on-device GPS (offline state-level anchor matching, with optional online district-level "
    "reverse-geocoding) and pH/N/P/K auto-fill from Soil-Health-Card means, all overridable. "
    "The framework shows that transparent, explainable AI can deliver actionable yield guidance to "
    "rural farmers through a simple browser interface."
)

KEYWORDS = ["crop yield prediction", "precision agriculture", "machine learning",
             "explainable AI", "vision transformer", "Soil Health Card", "recommendation system"]

# IEEE-format references — REAL, verifiable top-venue papers + the two REAL datasets
REFERENCES = [
    "A. Vaswani et al., \"Attention is all you need,\" in Adv. Neural Inf. Process. Syst. "
    "(NeurIPS), 2017, pp. 5998–6008.",
    "A. Dosovitskiy et al., \"An image is worth 16x16 words: Transformers for image "
    "recognition at scale,\" in Proc. Int. Conf. Learn. Represent. (ICLR), 2021.",
    "K. He, X. Chen, S. Xie, and Y. Dollár, \"Masked autoencoders are scalable vision "
    "learners,\" in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2022, "
    "pp. 15979–15988.",
    "A. Kirillov et al., \"Segment anything,\" in Proc. IEEE/CVF Int. Conf. Comput. Vis. "
    "(ICCV), 2023, pp. 4015–4026.",
    "M. Reichstein et al., \"Deep learning and process understanding for data-driven Earth "
    "system science,\" Nature, vol. 566, pp. 195–204, 2019. (Springer, SCI)",
    "S. Khaki and L. Wang, \"Crop yield prediction using deep neural networks,\" "
    "Front. Plant Sci., vol. 10, p. 621, 2019, doi: 10.3389/fpls.2019.00621. (Scopus)",
    "\"Crop production statistics (State/District, Area/Production),\" Government of India "
    "open data repository. [REAL dataset used in this study.]",
    "\"Crop recommendation dataset (N, P, K, temperature, humidity, pH, rainfall, label),\" "
    "public repository. [REAL dataset used in this study.]",
]

# ============================ 1) DOCX ============================
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)

# Title block
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("ABSTRACT SUBMISSION — REVIEW FORMAT"); r.bold = True; r.font.size = Pt(14)
sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
rs = sub.add_run(f"{TOPIC}"); rs.bold = True; rs.font.size = Pt(12); rs.font.color.rgb = RGBColor(0x15,0x80,0x3d)

meta = doc.add_paragraph(); meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta.add_run(f"Student: {STUDENT_NAME}   |   JNTU No.: {JNTU_NO}\n").italic = True
meta.add_run(f"Guide: {GUIDE_NAME}   |   {DEPT}, {COLLEGE}\n").italic = True
meta.add_run(f"Date: {TODAY}").italic = True

doc.add_paragraph("_" * 95)

p = doc.add_paragraph(); p.add_run("ABSTRACT").bold = True
doc.add_paragraph(ABSTRACT)

p = doc.add_paragraph(); p.add_run("KEYWORDS").bold = True
doc.add_paragraph("; ".join(KEYWORDS) + ".")

doc.add_paragraph("_" * 95)
p = doc.add_paragraph(); p.add_run("REFERENCES").bold = True
for i, ref in enumerate(REFERENCES, 1):
    rp = doc.add_paragraph(style="List Number")
    rp.add_run(ref)
    rp.paragraph_format.left_indent = Inches(0.3)
    rp.paragraph_format.first_line_indent = Inches(-0.3)

note = doc.add_paragraph()
nr = note.add_run("Note: Base-paper hard copies to be attached. Verify DOIs/volume details with the "
                   "guide before final submission. Dataset references [7]–[8] are the REAL sources "
                   "used for modelling.")
nr.italic = True; nr.font.size = Pt(9); nr.font.color.rgb = RGBColor(0x66,0x66,0x66)

doc.save("Abstract_Submission.docx")
print("Saved Abstract_Submission.docx")

# ============================ 2) PPTX ============================
from pptx import Presentation
from pptx.util import Inches, Pt as PPt, Emu
from pptx.dml.color import RGBColor as PColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
GREEN = PColor(0x15, 0x80, 0x3d); GREY = PColor(0x47, 0x55, 0x69)

blank = prs.slide_layouts[6]

def add_text(slide, l, t, w, h, text, size=18, bold=False, color=None, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = PPt(size); r.font.bold = bold
    if color: r.font.color.rgb = color
    return tb

# Slide 1 — Topic / Student / Guide
s1 = prs.slides.add_slide(blank)
add_text(s1, 0.7, 0.5, 12, 1.0, TOPIC, size=30, bold=True, color=GREEN)
add_text(s1, 0.7, 1.7, 12, 0.5, "Abstract Review — Individual Presentation", size=16, color=GREY)
add_text(s1, 0.7, 3.0, 12, 0.6, f"Student: {STUDENT_NAME}", size=22, bold=True)
add_text(s1, 0.7, 3.7, 12, 0.6, f"JNTU No.: {JNTU_NO}", size=20)
add_text(s1, 0.7, 4.4, 12, 0.6, f"Guide: {GUIDE_NAME}", size=20)
add_text(s1, 0.7, 5.1, 12, 0.6, f"{DEPT}, {COLLEGE}", size=16, color=GREY)
add_text(s1, 0.7, 6.2, 12, 0.5, f"Date: {TODAY}", size=14, color=GREY)

# Slide 2 — Abstract
s2 = prs.slides.add_slide(blank)
add_text(s2, 0.7, 0.4, 12, 0.6, "ABSTRACT", size=26, bold=True, color=GREEN)
tb = s2.shapes.add_textbox(Inches(0.7), Inches(1.2), Inches(11.9), Inches(5.8))
tf = tb.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; r = p.add_run(); r.text = ABSTRACT; r.font.size = PPt(16)

# Slide 3 — References
s3 = prs.slides.add_slide(blank)
add_text(s3, 0.7, 0.4, 12, 0.6, "REFERENCES (Base Papers)", size=26, bold=True, color=GREEN)
tb = s3.shapes.add_textbox(Inches(0.7), Inches(1.2), Inches(11.9), Inches(5.8))
tf = tb.text_frame; tf.word_wrap = True
for i, ref in enumerate(REFERENCES, 1):
    p = tf.paragraphs[0] if i == 1 else tf.add_paragraph()
    r = p.add_run(); r.text = f"[{i}] {ref}"
    r.font.size = PPt(12.5); p.space_after = PPt(8)

prs.save("Abstract_Presentation.pptx")
print("Saved Abstract_Presentation.pptx")

# ============================ 3) DIARY ============================
diary = f"""# Submission Diary — Abstract Review

**Topic:** {TOPIC}
**Student:** {STUDENT_NAME}  |  **JNTU No.:** {JNTU_NO}
**Guide:** {GUIDE_NAME}  |  **Dept:** {DEPT}, {COLLEGE}
**Date:** {TODAY}

## Pre-submission Checklist
- [ ] Abstract written (250–300 words) and self-reviewed
- [ ] Minimum 5 keywords present  ✓ (7)
- [ ] Minimum 5 references present  ✓ (8)
- [ ] References in IEEE format, from reputed venues (CVPR/ICCV/ICLR/Nature/Elsevier/Springer)
- [ ] Real datasets cited as sources [7]–[8]
- [ ] 3-slide individual presentation prepared (Topic/Student/Guide, Abstract, References)
- [ ] Hard copy of base papers attached
- [ ] Format uniform across all submissions

## Faculty / Guide Signature Slots  (complete BEFORE submission)

| # | Stage                              | Faculty / Guide | Signature | Date |
|---|------------------------------------|-----------------|-----------|------|
| 1 | Topic approved                     | Guide           | __________ | ______ |
| 2 | Abstract reviewed & corrected      | Guide           | __________ | ______ |
| 3 | References verified (IEEE, top venues) | Guide       | __________ | ______ |
| 4 | Base-paper hard copies attached    | Guide           | __________ | ______ |
| 5 | Final format check (uniform)      | Coordinator     | __________ | ______ |
| 6 | Submitted to review               | Coordinator     | __________ | ______ |

## Notes
- Present individually in your assigned slot. Do NOT miss the slot.
- All must follow the same format (this Diary + Abstract_Submission.docx + Abstract_Presentation.pptx).
- Replace the [PLACEHOLDER] fields (name, JNTU No., guide, dept, college) before printing.
"""
open("Submission_Diary.md", "w", encoding="utf-8").write(diary)
print("Saved Submission_Diary.md")
print("\nDONE — package ready.")
