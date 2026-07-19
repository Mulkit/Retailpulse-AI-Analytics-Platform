"""Shared style constants — one place to tweak the dashboard's look."""

PRIMARY_COLOR = "#1F4E79"
ACCENT_COLOR = "#F26B21"
SUCCESS_COLOR = "#2E8B57"
WARNING_COLOR = "#D62828"
NEUTRAL_COLOR = "#6C757D"

PLOTLY_TEMPLATE = "plotly_white"

RISK_COLOR_MAP = {
    "Healthy": SUCCESS_COLOR,
    "Understock Risk": WARNING_COLOR,
    "Overstock Risk": ACCENT_COLOR,
}

CHURN_TIER_COLOR_MAP = {
    "Low": SUCCESS_COLOR,
    "Medium": ACCENT_COLOR,
    "High": WARNING_COLOR,
}
