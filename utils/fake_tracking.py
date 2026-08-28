"""
"Video processing" style loader for the object-tracking stage.

Instead of a plain st.progress bar, this renders a self-contained
HTML/CSS/JS component: a blurred backdrop pulled from the uploaded
video, a scanning-line sweep, a circular progress ring that fills via
requestAnimationFrame, and a rotating shimmer-text status line (the
same cycling/shimmer treatment used on the "Generating insights"
panel, adapted for the dark backdrop here). Because the animation runs
entirely in the browser, it stays perfectly smooth no matter how
Streamlit reruns — Python only needs to keep the page open for
`duration_seconds` so the animation has time to finish before the app
moves to the next state.

Only frame-count progress is ever implied to the user (no literal
countdown/timer) — pacing is controlled internally by
config.FRAME_TRACKING_DURATION.
"""

import time

import streamlit.components.v1 as components

from utils.frame_preview import get_blurred_frame_base64

_RING_RADIUS = 52
_RING_CIRCUMFERENCE = round(2 * 3.14159265 * _RING_RADIUS, 2)  # 326.73

_PHASES = [
    "Detecting objects in frame",
    "Tracking motion across frames",
    "Mapping customer trajectories",
    "Identifying zones of interest",
    "Finalizing detections",
]


def run_tracking_simulation(total_frames: int, duration_seconds: float, video_path: str) -> None:
    total_frames = max(int(total_frames), 1)

    backdrop_b64 = get_blurred_frame_base64(video_path)
    if backdrop_b64:
        backdrop_css = (
            "background-image: linear-gradient(180deg, rgba(6,10,20,.55), rgba(6,10,20,.86)), "
            f"url(data:image/jpeg;base64,{backdrop_b64}); "
            "background-size: cover; background-position: center;"
        )
    else:
        backdrop_css = "background: linear-gradient(135deg,#0b1120,#0f2b4d 55%,#0b1120);"

    phases_js = ", ".join(f'"{p}\u2026"' for p in _PHASES)
    interval_ms = max(int(duration_seconds * 1000 / len(_PHASES)), 700)

    html = f"""
    <div class="svi-track-wrap">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        * {{ box-sizing: border-box; }}

        .svi-track-wrap {{
            position: relative;
            border-radius: 16px;
            overflow: hidden;
            {backdrop_css}
            height: 236px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .svi-track-wrap::after {{
            content: "";
            position: absolute;
            inset: 0;
            box-shadow: inset 0 0 60px rgba(0,0,0,.45);
            pointer-events: none;
        }}
        .svi-scanline {{
            position: absolute;
            left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, #38bdf8 25%, #bae6fd 50%, #38bdf8 75%, transparent);
            box-shadow: 0 0 14px 2px rgba(56,189,248,.75);
            animation: svi-scan 2.3s ease-in-out infinite;
            opacity: .9;
            z-index: 1;
        }}
        @keyframes svi-scan {{
            0%   {{ top: 8%;  opacity: 0; }}
            12%  {{ opacity: .95; }}
            50%  {{ top: 92%; opacity: .95; }}
            88%  {{ opacity: 0; }}
            100% {{ top: 92%; opacity: 0; }}
        }}
        .svi-corner {{
            position: absolute; width: 22px; height: 22px;
            border: 2px solid rgba(186,230,253,.55);
            z-index: 1;
        }}
        .svi-c-tl {{ top: 14px; left: 14px; border-right: 0; border-bottom: 0; border-top-left-radius: 4px; }}
        .svi-c-tr {{ top: 14px; right: 14px; border-left: 0; border-bottom: 0; border-top-right-radius: 4px; }}
        .svi-c-bl {{ bottom: 14px; left: 14px; border-right: 0; border-top: 0; border-bottom-left-radius: 4px; }}
        .svi-c-br {{ bottom: 14px; right: 14px; border-left: 0; border-top: 0; border-bottom-right-radius: 4px; }}

        .svi-badge {{
            position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
            display: flex; align-items: center; gap: .35rem;
            background: rgba(15,23,42,.55);
            border: 1px solid rgba(148,163,184,.3);
            padding: .22rem .65rem;
            border-radius: 999px;
            font-size: .68rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
            color: #bae6fd;
            z-index: 2;
        }}
        .svi-rec-dot {{
            width: 6px; height: 6px; border-radius: 50%; background: #f87171;
            animation: svi-rec 1.1s ease-in-out infinite;
        }}
        @keyframes svi-rec {{ 0%,100% {{ opacity: .3; }} 50% {{ opacity: 1; }} }}

        .svi-ring-box {{
            position: relative; z-index: 2;
            display: flex; flex-direction: column; align-items: center;
        }}
        .svi-ring-box svg {{ transform: rotate(-90deg); filter: drop-shadow(0 0 10px rgba(56,189,248,.5)); }}
        .svi-ring-bg {{ fill: none; stroke: rgba(148,163,184,.28); stroke-width: 7; }}
        .svi-ring-fg {{ fill: none; stroke: url(#sviGrad); stroke-width: 7; stroke-linecap: round; }}
        .svi-pct {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
            font-size: 1.55rem; font-weight: 800; color: #f0f9ff; letter-spacing: -.5px;
        }}

        .svi-foot {{
            position: absolute; bottom: 16px; left: 0; right: 0; text-align: center; z-index: 2;
        }}
        .svi-label {{
            font-size: .84rem; font-weight: 700; letter-spacing: .01em;
            display: flex; align-items: center; justify-content: center; gap: .4rem;
        }}
        .svi-phase {{
            background: linear-gradient(90deg, #e0f2fe 0%, #7dd3fc 25%, #e0f2fe 50%, #7dd3fc 75%, #e0f2fe 100%);
            background-size: 220% auto;
            -webkit-background-clip: text; background-clip: text; color: transparent;
            animation: svi-shimmer-text 2.2s linear infinite;
            transition: opacity .18s ease;
        }}
        @keyframes svi-shimmer-text {{ to {{ background-position: -220% center; }} }}
        .svi-sub {{ color: #93c5fd; font-size: .74rem; font-weight: 500; opacity: .9; margin-top: .15rem; }}
        .svi-pulse-dot {{
            width: 6px; height: 6px; border-radius: 50%; background: #38bdf8;
            box-shadow: 0 0 8px 2px rgba(56,189,248,.85);
            animation: svi-pulse 1.1s ease-in-out infinite;
            flex-shrink: 0;
        }}
        @keyframes svi-pulse {{ 0%,100% {{ opacity: .35; transform: scale(.8); }} 50% {{ opacity: 1; transform: scale(1.2); }} }}
      </style>

      <span class="svi-corner svi-c-tl"></span>
      <span class="svi-corner svi-c-tr"></span>
      <span class="svi-corner svi-c-bl"></span>
      <span class="svi-corner svi-c-br"></span>
      <div class="svi-scanline" id="sviScan"></div>

      <div class="svi-badge"><span class="svi-rec-dot"></span>PROCESSING</div>

      <div class="svi-ring-box">
        <svg width="118" height="118" viewBox="0 0 118 118">
          <defs>
            <linearGradient id="sviGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#38bdf8"/>
              <stop offset="100%" stop-color="#818cf8"/>
            </linearGradient>
          </defs>
          <circle class="svi-ring-bg" cx="59" cy="59" r="{_RING_RADIUS}"></circle>
          <circle id="sviRingFg" class="svi-ring-fg" cx="59" cy="59" r="{_RING_RADIUS}"
                  stroke-dasharray="{_RING_CIRCUMFERENCE}" stroke-dashoffset="{_RING_CIRCUMFERENCE}"></circle>
        </svg>
        <div class="svi-pct" id="sviPct">0%</div>
      </div>

      <div class="svi-foot">
        <div class="svi-label"><span class="svi-pulse-dot"></span><span class="svi-phase" id="sviPhase">{_PHASES[0]}\u2026</span></div>
        <div class="svi-sub" id="sviSub">Frame 0 / {total_frames:,}</div>
      </div>
    </div>

    <script>
      (function () {{
        var duration = {duration_seconds} * 1000;
        var totalFrames = {total_frames};
        var circumference = {_RING_CIRCUMFERENCE};
        var ring = document.getElementById('sviRingFg');
        var pct = document.getElementById('sviPct');
        var sub = document.getElementById('sviSub');
        var phaseEl = document.getElementById('sviPhase');
        var scan = document.getElementById('sviScan');
        var start = performance.now();
        var done = false;

        var phases = [{phases_js}];
        var pIdx = 0;
        var phaseTimer = setInterval(function () {{
          if (done) return;
          pIdx = (pIdx + 1) % phases.length;
          phaseEl.style.opacity = 0;
          setTimeout(function () {{
            phaseEl.textContent = phases[pIdx];
            phaseEl.style.opacity = 1;
          }}, 180);
        }}, {interval_ms});

        function tick(now) {{
          var elapsed = now - start;
          var progress = Math.min(elapsed / duration, 1);
          var eased = 1 - Math.pow(1 - progress, 2);
          ring.setAttribute('stroke-dashoffset', circumference * (1 - eased));
          pct.textContent = Math.round(eased * 100) + '%';
          var frame = Math.min(Math.round(eased * totalFrames), totalFrames);
          sub.textContent = 'Frame ' + frame.toLocaleString() + ' / ' + totalFrames.toLocaleString();

          if (progress < 1) {{
            requestAnimationFrame(tick);
          }} else {{
            done = true;
            clearInterval(phaseTimer);
            phaseEl.style.opacity = 1;
            phaseEl.textContent = 'Tracking complete ✅';
            sub.textContent = totalFrames.toLocaleString() + ' / ' + totalFrames.toLocaleString() + ' frames processed';
            scan.style.animation = 'none';
            scan.style.opacity = '0';
          }}
        }}
        requestAnimationFrame(tick);
      }})();
    </script>
    """

    components.html(html, height=250)
    # Keep the page open long enough for the client-side animation to
    # finish (plus a little breathing room) before Streamlit moves on
    # to the "complete" state.
    time.sleep(duration_seconds + 0.6)
