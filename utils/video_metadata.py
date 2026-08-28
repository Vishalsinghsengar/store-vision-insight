"""
Real video metadata extraction using OpenCV.
This part is genuine — only the tracking/insight results downstream are simulated.
"""

import os
from datetime import timedelta

import cv2


def get_video_metadata(video_path: str) -> dict:
    """Read real technical metadata from an uploaded video file."""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Unable to read the uploaded video file.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration_sec = (frame_count / fps) if fps else 0

    cap.release()

    file_size_bytes = os.path.getsize(video_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    file_format = os.path.splitext(video_path)[1].replace(".", "").upper()

    # Guard against unreadable frame counts (some codecs under-report)
    if frame_count <= 0 and fps and duration_sec == 0:
        frame_count = 1

    return {
        "file_name": os.path.basename(video_path),
        "format": file_format or "N/A",
        "resolution": f"{width} x {height}" if width and height else "N/A",
        "fps": round(fps, 2),
        "total_frames": max(frame_count, 1),
        "duration": str(timedelta(seconds=int(duration_sec))),
        "duration_seconds": duration_sec,
        "file_size_mb": file_size_mb,
    }
