"""
Grabs a single representative frame from the uploaded video and returns
it as a base64-encoded, Gaussian-blurred JPEG. Used purely as a visual
backdrop for the "processing" loaders — never shown sharp/unblurred.
"""

from typing import Optional

import cv2


def get_blurred_frame_base64(
    video_path: str,
    blur_ksize: int = 55,
    max_width: int = 960,
) -> Optional[str]:
    """Read a mid-video frame, downscale + heavily blur it, return base64 JPEG (no data: prefix)."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    # Grab a frame roughly a third of the way in — more visually interesting
    # than frame 0, which is often a blank/black lead-in.
    target = max(total // 3, 0)
    if target:
        cap.set(cv2.CAP_PROP_POS_FRAMES, target)

    ok, frame = cap.read()
    if not ok or frame is None:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ok, frame = cap.read()
    cap.release()

    if not ok or frame is None:
        return None

    h, w = frame.shape[:2]
    if w > max_width:
        scale = max_width / float(w)
        frame = cv2.resize(frame, (max_width, int(h * scale)), interpolation=cv2.INTER_AREA)

    if blur_ksize % 2 == 0:
        blur_ksize += 1
    frame = cv2.GaussianBlur(frame, (blur_ksize, blur_ksize), 0)

    ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 72])
    if not ok:
        return None

    import base64

    return base64.b64encode(buffer).decode("utf-8")
