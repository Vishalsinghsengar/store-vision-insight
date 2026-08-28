"""
ChatGPT-style "thinking" loader for the insight-generation stage.

Renders a spinning gradient orb, shimmering gradient-text status line
that cycles through analysis phases, and blurred/shimmering skeleton
rows standing in for the insight cards about to appear — all animated
client-side (HTML/CSS/JS) so it stays smooth regardless of Streamlit
reruns. Python just keeps the page open for `duration_seconds`.
"""

import time

import streamlit.components.v1 as components

_PHASES = [
    "Analyzing customer behavior patterns",
    "Detecting dwell time & footfall trends",
    "Cross-referencing counter activity",
    "Scoring engagement signals",
    "Compiling insight summary",
]


def run_insight_thinking(duration_seconds: float) -> None:
    phases_js = ", ".join(f'"{p}\u2026"' for p in _PHASES)
    interval_ms = max(int(duration_seconds * 1000 / len(_PHASES)), 550)

    html = f"""
    <div class="svi-think-wrap">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        * {{ box-sizing: border-box; }}

        .svi-think-wrap {{
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.05rem 1.3rem 1.2rem;
            background: linear-gradient(180deg,#ffffff 0%, #f8fafc 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .svi-think-head {{
            display: flex; align-items: center; gap: .6rem; margin-bottom: 1rem;
        }}
        .svi-orb {{
            width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
            background: conic-gradient(from 0deg, #0284c7, #818cf8, #38bdf8, #0284c7);
            animation: svi-spin 1.3s linear infinite;
            box-shadow: 0 0 10px rgba(56,189,248,.45);
        }}
        @keyframes svi-spin {{ to {{ transform: rotate(360deg); }} }}

        .svi-think-text {{
            font-weight: 700; font-size: .96rem;
            background: linear-gradient(90deg, #0f172a 0%, #94a3b8 45%, #0f172a 90%);
            background-size: 220% auto;
            -webkit-background-clip: text; background-clip: text; color: transparent;
            animation: svi-shimmer-text 2.2s linear infinite;
            transition: opacity .18s ease;
        }}
        @keyframes svi-shimmer-text {{ to {{ background-position: -220% center; }} }}

        .svi-skel {{
            position: relative;
            overflow: hidden;
            height: 13px; border-radius: 7px; margin-bottom: .6rem;
            background: #eef2f7;
        }}
        .svi-skel::after {{
            content: "";
            position: absolute; inset: 0;
            background: linear-gradient(90deg, transparent, rgba(148,163,184,.45), transparent);
            transform: translateX(-100%);
            animation: svi-sweep 1.5s ease-in-out infinite;
            filter: blur(2px);
        }}
        @keyframes svi-sweep {{ 100% {{ transform: translateX(100%); }} }}

        .svi-foot {{
            display: flex; align-items: center; gap: .35rem; margin-top: .2rem;
            color: #94a3b8; font-size: .72rem; font-weight: 500;
        }}
        .svi-foot .dot {{ width: 4px; height: 4px; border-radius: 50%; background: #94a3b8; animation: svi-blink 1.2s ease-in-out infinite; }}
        .svi-foot .dot:nth-child(2) {{ animation-delay: .2s; }}
        .svi-foot .dot:nth-child(3) {{ animation-delay: .4s; }}
        @keyframes svi-blink {{ 0%,100% {{ opacity: .25; }} 50% {{ opacity: 1; }} }}
      </style>

      <div class="svi-think-head">
        <div class="svi-orb"></div>
        <div class="svi-think-text" id="sviThinkText">{_PHASES[0]}\u2026</div>
      </div>

      <div class="svi-skel" style="width: 97%;"></div>
      <div class="svi-skel" style="width: 89%;"></div>
      <div class="svi-skel" style="width: 93%;"></div>
      <div class="svi-skel" style="width: 61%; margin-bottom: 0;"></div>

      <div class="svi-foot">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        &nbsp;Generating insights from tracked footage
      </div>

      <script>
        (function () {{
          var phases = [{phases_js}];
          var el = document.getElementById('sviThinkText');
          var i = 0;
          setInterval(function () {{
            i = (i + 1) % phases.length;
            el.style.opacity = 0;
            setTimeout(function () {{
              el.textContent = phases[i];
              el.style.opacity = 1;
            }}, 180);
          }}, {interval_ms});
        }})();
      </script>
    </div>
    """

    components.html(html, height=175)
    # Small extra buffer so the shimmer/phrase cycle doesn't feel cut off
    # right as it lands on a new phrase.
    time.sleep(duration_seconds + 0.4)
