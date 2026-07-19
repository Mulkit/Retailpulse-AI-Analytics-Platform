"""
RetailPulse — Export Center page.

Generates a consolidated executive PDF report pulling KPIs from every module
(sales, segmentation, forecasting, churn, inventory), plus quick CSV exports
for the full underlying datasets.
"""
import io
from datetime import datetime

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from utils.data_loader import (
    get_sales_cleaned, get_customer_segments, get_churn_scores,
    get_inventory_recommendations, get_hybrid_metrics, get_churn_metrics, get_hybrid_forecast,
)

st.set_page_config(page_title="RetailPulse | Export Center", page_icon="📤", layout="wide")
st.title("📤 Export Center")
st.caption("Download a consolidated executive report, or raw data from any module, in one place")

try:
    sales = get_sales_cleaned()
    segments = get_customer_segments()
    churn = get_churn_scores()
    inventory = get_inventory_recommendations()
    hybrid_metrics = get_hybrid_metrics()
    churn_metrics = get_churn_metrics()
    forecast = get_hybrid_forecast()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e.filename}. Run the pipeline notebooks first.")
    st.stop()


def build_pdf_report() -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=20, spaceAfter=6)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    body_style = styles["BodyText"]

    story = [
        Paragraph("RetailPulse: AI-Powered Sales &amp; Retail Analytics Platform", title_style),
        Paragraph("Executive Report", styles["Heading3"]),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style),
        Spacer(1, 12),
    ]

    # --- Business KPIs ---
    story.append(Paragraph("Business Overview", heading_style))
    total_revenue = sales["TotalPrice"].sum()
    total_orders = sales["InvoiceNo"].nunique()
    total_customers = sales["CustomerID"].nunique()
    kpi_table = Table([
        ["Metric", "Value"],
        ["Total Revenue", f"£{total_revenue:,.0f}"],
        ["Total Orders", f"{total_orders:,}"],
        ["Total Customers", f"{total_customers:,}"],
        ["Avg Order Value", f"£{total_revenue / total_orders:,.2f}"],
    ], colWidths=[8 * cm, 6 * cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    story.append(kpi_table)

    # --- Model performance ---
    story.append(Paragraph("Model Performance", heading_style))
    model_table = Table([
        ["Model", "Metric", "Value", "Target"],
        ["Hybrid Forecast", "MAPE", f"{hybrid_metrics['mape']:.2f}%", "≤ 12%"],
        ["Churn (tuned)", "AUC-ROC", f"{churn_metrics['auc_roc']:.4f}", "≥ 0.88"],
        ["Churn (tuned)", "Precision@Top-20%", f"{churn_metrics['precision_at_top20']:.4f}", "≥ 0.75"],
    ], colWidths=[5 * cm, 4.5 * cm, 3 * cm, 2.5 * cm])
    model_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    story.append(model_table)

    # --- Segmentation summary ---
    story.append(Paragraph("Customer Segmentation", heading_style))
    seg_summary = segments["Segment"].value_counts()
    seg_rows = [["Segment", "Customers"]] + [[k, f"{v:,}"] for k, v in seg_summary.items()]
    seg_table = Table(seg_rows, colWidths=[8 * cm, 6 * cm])
    seg_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    story.append(seg_table)

    # --- Inventory summary ---
    story.append(Paragraph("Inventory Health", heading_style))
    n_reorder = (inventory["RecommendedOrderQty"] > 0).sum()
    inv_table = Table([
        ["Metric", "Value"],
        ["SKUs Tracked", f"{len(inventory):,}"],
        ["SKUs Needing Reorder", f"{n_reorder:,}"],
        ["Understock Risk", f"{(inventory['StockRisk'] == 'Understock Risk').sum():,}"],
        ["Overstock Risk", f"{(inventory['StockRisk'] == 'Overstock Risk').sum():,}"],
    ], colWidths=[8 * cm, 6 * cm])
    inv_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    story.append(inv_table)

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Generated automatically by the RetailPulse dashboard Export Center. "
        "See the project GitHub repository for full methodology and notebooks.",
        ParagraphStyle("Footer", parent=body_style, fontSize=8, textColor=colors.grey),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


st.subheader("Executive PDF Report")
st.caption("A consolidated summary across sales, segmentation, forecasting, churn, and inventory.")
pdf_bytes = build_pdf_report()
st.download_button(
    "⬇ Download Executive Report (PDF)",
    data=pdf_bytes,
    file_name=f"retailpulse_executive_report_{datetime.now().strftime('%Y%m%d')}.pdf",
    mime="application/pdf",
)

st.markdown("---")
st.subheader("Raw Data Exports (CSV)")
export_options = {
    "Cleaned Sales Transactions": sales,
    "Customer Segments (RFM + Clusters)": segments,
    "Churn Scores": churn,
    "Inventory Recommendations": inventory,
    "30-Day Hybrid Forecast": forecast,
}
choice = st.selectbox("Choose a dataset to export", list(export_options.keys()))
chosen_df = export_options[choice]
st.dataframe(chosen_df.head(20), use_container_width=True, hide_index=True)
st.caption(f"Previewing first 20 of {len(chosen_df):,} rows — the download includes all rows.")
st.download_button(
    f"⬇ Download {choice} (CSV)",
    data=chosen_df.to_csv(index=False).encode("utf-8"),
    file_name=f"retailpulse_{choice.lower().replace(' ', '_').replace('(', '').replace(')', '')}.csv",
    mime="text/csv",
)
