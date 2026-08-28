# 🛒 Store Vision Insight

A Streamlit demo interface for a store computer-vision analytics product.
Real video metadata is read from the uploaded file; the "tracking" and
"insight generation" stages are simulated for demo purposes (no timer is
ever shown — only frame/stage progress).

## Project structure

```
store-vision-insight/
├── app.py                    # Streamlit entry point (UI + flow)
├── config.py                 # All adjustable parameters live here
├── requirements.txt
├── .gitignore
├── uploads/                  # User-uploaded videos are saved here (metadata only)
│   └── .gitkeep
├── tracked_videos/           # BACKEND: pre-rendered "already-tracked" outputs
│   └── .gitkeep
├── assets/
│   └── style.css             # Custom professional theme
└── utils/
    ├── __init__.py
    ├── video_metadata.py     # Real metadata extraction (OpenCV)
    ├── fake_tracking.py      # Simulated frame-tracking progress animation
    └── fake_insights.py      # Simulated, file-seeded text-pointer insights
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## How it works

1. **Upload** — user uploads a video (`mp4`, `avi`, `mov`, `mkv`); it's saved
   into `uploads/` and used only to read real metadata from.
2. **Metadata** — `utils/video_metadata.py` reads real resolution, fps,
   frame count, duration, and file size via OpenCV.
3. **Tracking simulation** — `utils/fake_tracking.py` animates a
   `frame X / total frames` progress bar over
   `config.FRAME_TRACKING_DURATION` seconds. No elapsed/remaining time is
   ever displayed.
4. **Tracked footage** — the app never shows the raw upload. Instead it
   looks for a matching pre-rendered file in `tracked_videos/` (same
   filename as the upload). If none is found, it falls back to
   `config.DEFAULT_TRACKED_VIDEO`.
5. **Insight generation** — clicking **Generate Insights** runs a similar
   staged-progress animation (`config.INSIGHT_GENERATION_DURATION`
   seconds), then renders a short list of plain-text insight pointers,
   e.g. *"5 people were seen standing near Counter 2"*, *"Counter 3 was
   the busiest checkout"*, etc. — no charts, capped at a clean, readable
   set (tied to `config.MAX_COUNTERS`).

Insight text is deterministically seeded from the uploaded file's name,
so re-uploading the same file reproduces the same "results" — useful for
consistent demos.

## Adding backend tracked videos

For each source video you plan to demo with, add its already-tracked
(bounding-boxes-drawn) counterpart to `tracked_videos/` using the exact
same filename as the upload:

```
uploads/shop_1.mp4        <- what the user uploads
tracked_videos/shop_1.mp4 <- what gets shown after "tracking" (pre-made by you)
```

If a match isn't found, `config.DEFAULT_TRACKED_VIDEO` is used as a
fallback (set it to any generic tracked clip), otherwise a friendly
warning is shown.

## Adjusting timings & limits

All simulation timings and limits are defined at the top of `config.py`:

```python
FRAME_TRACKING_DURATION = 4        # seconds
INSIGHT_GENERATION_DURATION = 3    # seconds
MAX_COUNTERS = 5
```

Change these values to speed up, slow down, or extend the demo — no other
file needs to be touched.

## Disclaimer

This is a **UI/UX demo only**. No actual computer-vision model runs
against the uploaded footage — metadata is real, but the tracked video
and insights are pre-made / simulated for presentation purposes.
