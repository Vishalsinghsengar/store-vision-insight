"""
Store Vision Insight — Configuration
--------------------------------------
Central place to control every "knob" of the demo: simulation timings,
branding, upload rules, and insight limits. Edit the values below —
nothing else in the app needs to change.
"""

# ------------------------------------------------------------------
# Simulation timings (in seconds)
# These control how long the FAKE processing animations run.
# No countdown/timer is ever shown to the end user — only frame /
# stage progress — but internally these values decide the pacing.
# ------------------------------------------------------------------
FRAME_TRACKING_DURATION = 8        # duration of the "tracking objects" animation
INSIGHT_GENERATION_DURATION = 6    # duration of the "generating insights" animation

# ------------------------------------------------------------------
# Insight generation
# ------------------------------------------------------------------
MAX_COUNTERS = 5                   # maximum number of billing counters simulated

# ------------------------------------------------------------------
# Branding
# ------------------------------------------------------------------
APP_TITLE = "Store Vision Insight"
APP_ICON = "🛒"
APP_TAGLINE = "AI-Powered Retail Analytics & Customer Behavior Intelligence"

# ------------------------------------------------------------------
# Upload settings
# ------------------------------------------------------------------
UPLOAD_DIR = "uploads"
ALLOWED_VIDEO_TYPES = ["mp4", "avi", "mov", "mkv"]

# ------------------------------------------------------------------
# Tracked (backend) video settings
# ------------------------------------------------------------------
# After "tracking" finishes, the app shows a pre-rendered, already-tracked
# video instead of the raw upload. Drop the tracked output file into
# TRACKED_VIDEO_DIR using the SAME filename as the source video the user
# will upload (e.g. uploads/shop_1.mp4 -> tracked_videos/shop_1.mp4).
# If no matching file is found, DEFAULT_TRACKED_VIDEO is used as a fallback.
TRACKED_VIDEO_DIR = "tracked_videos"
DEFAULT_TRACKED_VIDEO = "tracked_videos/default_tracked.mp4"
