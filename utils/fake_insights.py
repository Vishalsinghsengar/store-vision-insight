"""
Retail-analytics insight content for the demo.

Produces:
  - a short list of structured, human-readable insight pointers
    (icon + text + tone) for the insight cards, and
  - a metric/value table of verified observations.

These are fixed, curated results for the demo build rather than
per-video random simulation - the same for every uploaded file.

tone options: "info" | "success" | "warning" | "neutral"
(used purely for the colored accent on each insight card in the UI)
"""


def generate_insights(video_name: str = "", max_counters: int = 5) -> list:
    """Returns a list of dicts: {"icon": str, "text": str, "tone": str}."""
    return [
        {
            "icon": "\u23F1\uFE0F",
            "text": (
                "Peak counter load lasted <strong>~27 seconds</strong>, with typically "
                "<strong>5\u20137 customers</strong> in the billing area and a maximum of "
                "<strong>8 customers</strong>."
            ),
            "tone": "warning",
        },
        {
            "icon": "\U0001F501",
            "text": (
                "Counter demand stayed continuous throughout the video; there was "
                "<strong>no idle period</strong>, with at least <strong>2 customers</strong> "
                "around the billing zone."
            ),
            "tone": "info",
        },
        {
            "icon": "\U0001F465",
            "text": (
                "During peak traffic, the billing area had around <strong>6\u20137 customers</strong> "
                "with typically <strong>2 associates</strong>, indicating a temporary increase in "
                "counter workload."
            ),
            "tone": "neutral",
        },
    ]


def generate_metrics_table(video_name: str = "") -> list:
    """Returns a list of {"metric": str, "value": str} rows for the verified-observations table."""
    return [
        {"metric": "Video duration", "value": "72.58 sec (~1:12.6)"},
        {"metric": "Avg. customers visible", "value": "~10\u201311"},
        {"metric": "Minimum customers visible", "value": "6"},
        {"metric": "Peak customers visible", "value": "13"},
        {"metric": "Peak observed around", "value": "16s, 22s, 46s, 55s, 60s"},
        {"metric": "Avg. customers in billing zone", "value": "~4\u20135"},
        {"metric": "Peak customers in billing zone", "value": "8"},
        {"metric": "Billing-zone peak observed around", "value": "49s"},
        {"metric": "Lowest billing-zone customers", "value": "2"},
    ]
