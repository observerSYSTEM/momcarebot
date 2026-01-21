from __future__ import annotations

from pathlib import Path
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

from .plan_reader import CarePlan


def build_mom_care_pdf(
    plan: CarePlan,
    out_path: str | Path,
    fx_rate_note: str = "NGN values are plan estimates (rate may change).",
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontSize=20, leading=24, spaceAfter=12))
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontSize=10.5, leading=14))

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []
    story.append(Paragraph("Mom Care Plan 2026", styles["Title2"]))
    story.append(Paragraph(f"Prepared for: Emmanuel Ayoola  |  Date: {date.today().strftime('%d %b %Y')}", styles["Body"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Plan summary", styles["H2"]))
    story.append(Paragraph(
        "This plan supports your mum after retirement in Nigeria with stability, health coverage, and emergency readiness — "
        "without over-stretching your finances.",
        styles["Body"]
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Your income baseline", styles["H2"]))
    income_tbl = Table(
        [
            ["Item", "Amount"],
            ["Weekly income (avg)", f"GBP {plan.weekly_income_gbp:.0f}"],
            ["Monthly income (estimate)", f"GBP {plan.monthly_income_gbp:.0f}"],
            ["Support budget rule", "Target 15–20% of income for sustainability"],
        ],
        colWidths=[7.5 * cm, 7.5 * cm],
    )
    income_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(income_tbl)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Monthly support budget (recommended)", styles["H2"]))
    if plan.total_support_ngn is not None:
        story.append(Paragraph(
            f"Total monthly support: <b>GBP {plan.total_support_gbp:.0f}</b> (approx <b>NGN {plan.total_support_ngn:,.0f}</b>).",
            styles["Body"]
        ))
    else:
        story.append(Paragraph(
            f"Total monthly support: <b>GBP {plan.total_support_gbp:.0f}</b>.",
            styles["Body"]
        ))
    story.append(Spacer(1, 6))

    budget_data = [["Category", "GBP / month", "NGN approx", "Notes"]]
    for item in plan.items:
        ngn = f"NGN {item.amount_ngn:,.0f}" if item.amount_ngn is not None else "-"
        budget_data.append([item.category, f"GBP {item.amount_gbp:.0f}", ngn, item.notes or ""])
    total_ngn = f"NGN {plan.total_support_ngn:,.0f}" if plan.total_support_ngn is not None else "-"
    budget_data.append(["TOTAL", f"GBP {plan.total_support_gbp:.0f}", total_ngn, "Safe & sustainable baseline"])

    budget_tbl = Table(budget_data, colWidths=[7.1 * cm, 3.0 * cm, 3.2 * cm, 4.2 * cm])
    budget_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F9FAFB")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(budget_tbl)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Operational checklist (Nigeria)", styles["H2"]))
    checklist = [
        "Set a fixed transfer date each month and keep it consistent.",
        "Enroll her in a state health insurance scheme / NHIS equivalent (state-dependent).",
        "Name one trusted local contact for check-ins and emergencies.",
        "Build an emergency fund gradually (start with NGN 100k–200k).",
        "Weekly call rhythm: 1–2 calls per week to support emotional wellbeing after retirement.",
    ]
    for item in checklist:
        story.append(Paragraph(f"• {item}", styles["Body"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Notes", styles["H2"]))
    story.append(Paragraph(fx_rate_note, styles["Body"]))

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(2 * cm, 1.3 * cm, "Mom Care Plan 2026 | Prepared by Emmanuel Ayoola")
        canvas.drawRightString(A4[0] - 2 * cm, 1.3 * cm, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out_path
