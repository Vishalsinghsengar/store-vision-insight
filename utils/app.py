"""
Store Vision Insight
---------------------
A demo Streamlit interface for a store computer-vision analytics product.

Flow:
  1. Upload store footage (saved to /uploads)
  2. Real technical metadata is extracted from the file
  3. A simulated "object tracking" pass runs (frame-count progress only)
  4. A pre-rendered, already-tracked video (added to /tracked_videos by
     the backend/dev) is shown - never the raw upload
  5. "Generate Insights" triggers a simulated analytics pass and displays
     a short list of plain-text insight pointers (file-seeded), e.g.
     "5 people were seen standing near Counter 2".

Every timing knob lives in config.py - nothing here needs editing.
"""

import os

import streamlit as st

import config
from utils.fake_insights import generate_insights, generate_metrics_table
from utils.fake_tracking import run_tracking_simulation
from utils.thinking_panel import run_insight_thinking
from utils.video_metadata import get_video_metadata

# ------------------------------------------------------------------
# Page setup
# ------------------------------------------------------------------
st.set_page_config(page_title=config.APP_TITLE, page_icon=config.APP_ICON, layout="wide")


def load_css(path: str) -> None:
    if os.path.exists(path):
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css(os.path.join(os.path.dirname(__file__), "assets", "style.css"))


def section_heading(step: str, icon: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-heading">
            <span class="step-tag">{step}</span>{icon} {title}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(f'<p class="section-sub">{subtitle}</p>', unsafe_allow_html=True)


TONE_COLORS = {
    "info": "#0284C7",
    "success": "#059669",
    "warning": "#D97706",
    "neutral": "#64748B",
}


def insight_card(icon: str, text: str, tone: str = "neutral") -> None:
    color = TONE_COLORS.get(tone, TONE_COLORS["neutral"])
    st.markdown(
        f"""
        <div class="insight-card" style="--tone-color: {color};">
            <div class="icon">{icon}</div>
            <div class="text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metrics_table(rows: list) -> None:
    row_html = "".join(
        f'<tr><td class="metrics-metric">{row["metric"]}</td>'
        f'<td class="metrics-value">{row["value"]}</td></tr>'
        for row in rows
    )
    table_html = (
        '<table class="metrics-table"><thead><tr>'
        "<th>Metric</th><th>Verified observation</th>"
        f"</tr></thead><tbody>{row_html}</tbody></table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


# ------------------------------------------------------------------
# Session state
# ------------------------------------------------------------------
defaults = {
    "video_path": None,
    "metadata": None,
    "tracking_done": False,
    "insights": None,
    "metrics": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown(
    f"""
    <div class="app-header">
        <span class="badge">● Live Demo &nbsp;·&nbsp; AI Vision Pipeline</span>
        <h1>{config.APP_ICON} {config.APP_TITLE}</h1>
        <p>{config.APP_TAGLINE}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Upload
# ------------------------------------------------------------------
os.makedirs(config.UPLOAD_DIR, exist_ok=True)

with st.container(border=True):
    section_heading("STEP 1", "📤", "Upload Footage", "Upload store surveillance footage to begin analysis.")
    uploaded_file = st.file_uploader(
        "Upload store surveillance footage",
        type=config.ALLOWED_VIDEO_TYPES,
        help=f"Supported formats: {', '.join(t.upper() for t in config.ALLOWED_VIDEO_TYPES)}",
        label_visibility="collapsed",
    )

if uploaded_file is not None:
    save_path = os.path.join(config.UPLOAD_DIR, uploaded_file.name)
    if st.session_state.video_path != save_path:
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.video_path = save_path
        st.session_state.metadata = get_video_metadata(save_path)
        st.session_state.tracking_done = False
        st.session_state.insights = None
        st.session_state.metrics = None

# ------------------------------------------------------------------
# Main flow (only once a video is uploaded)
# ------------------------------------------------------------------
if st.session_state.video_path and st.session_state.metadata:
    meta = st.session_state.metadata

    st.write("")
    with st.container(border=True):
        section_heading("STEP 2", "📄", "Video Metadata", "Technical details extracted directly from the uploaded file.")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Resolution", meta["resolution"])
        c2.metric("Frame Rate", f'{meta["fps"]} fps')
        c3.metric("Total Frames", f'{meta["total_frames"]:,}')
        c4.metric("Duration", meta["duration"])
        c5.metric("File Size", f'{meta["file_size_mb"]} MB')

    st.write("")
    with st.container(border=True):
        section_heading("STEP 3", "🎯", "Object Tracking", "Running detection & tracking across every frame.")
        if not st.session_state.tracking_done:
            run_tracking_simulation(
                meta["total_frames"],
                config.FRAME_TRACKING_DURATION,
                st.session_state.video_path,
            )
            st.session_state.tracking_done = True
            st.rerun()
        else:
            st.markdown(
                f'<span class="status-pill">✅ Tracking complete · '
                f'{meta["total_frames"]:,} / {meta["total_frames"]:,} frames processed</span>',
                unsafe_allow_html=True,
            )

    st.write("")
    # with st.container(border=True):
    #     section_heading("STEP 4", "🎬", "Tracked Footage", "Output from the tracking model, with detections overlaid.")
    #     tracked_path = os.path.join(config.TRACKED_VIDEO_DIR, meta["file_name"])
    #     if os.path.exists(tracked_path):
    #         st.video(tracked_path)
    #     elif os.path.exists(config.DEFAULT_TRACKED_VIDEO):
    #         st.video(config.DEFAULT_TRACKED_VIDEO)
    #     else:
    #         st.warning(
    #             f"No tracked output found for **{meta['file_name']}**. "
    #             f"Add it to `{config.TRACKED_VIDEO_DIR}/{meta['file_name']}` "
    #             f"(or set a fallback at `{config.DEFAULT_TRACKED_VIDEO}`)."
    #         )


    with st.container(border=True):
        section_heading(
            "STEP 4",
            "🎬",
            "Tracked Footage",
            "Output from the tracking model, with detections overlaid."
        )

        tracked_path = os.path.join(
            config.TRACKED_VIDEO_DIR,
            "extracted_video.mp4"
        )

        if os.path.exists(tracked_path):
            st.video(tracked_path)

        elif os.path.exists(config.DEFAULT_TRACKED_VIDEO):
            st.video(config.DEFAULT_TRACKED_VIDEO)

        else:
            st.warning(
                f"No tracked output found for **extracted_video.mp4**. "
                f"Expected location: `{tracked_path}`"
            )

    st.write("")
    with st.container(border=True):
        section_heading("STEP 5", "📊", "Insight Generation", "AI-generated observations from the tracked footage.")

        if st.button("✨ Generate Insights", type="primary"):
            think_ph = st.empty()
            with think_ph:
                run_insight_thinking(config.INSIGHT_GENERATION_DURATION)
            think_ph.empty()
            st.session_state.insights = generate_insights(meta["file_name"], config.MAX_COUNTERS)
            st.session_state.metrics = generate_metrics_table(meta["file_name"])

        if st.session_state.insights:
            st.markdown(
                '<span class="status-pill">✅ Insights generated successfully</span>',
                unsafe_allow_html=True,
            )
            st.write("")
            for item in st.session_state.insights:
                insight_card(item["icon"], item["text"], item["tone"])

        if st.session_state.metrics:
            st.write("")
            metrics_table(st.session_state.metrics)

    st.markdown(
        '<div class="app-footer">Store Vision Insight · Simulated CV pipeline demo build</div>',
        unsafe_allow_html=True,
    )

else:
    st.info("👆 Upload a video file above to begin analysis.")
