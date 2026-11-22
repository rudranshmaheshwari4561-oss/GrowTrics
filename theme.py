import random
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
import plotly.io as pio
import streamlit as st

PURPLES = ["#8B5CF6", "#A78BFA", "#6D28D9", "#C4B5FD", "#7C3AED", "#DDD6FE"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --purple: #8B5CF6;
  --glass: rgba(255,255,255,0.05);
  --glass-border: rgba(255,255,255,0.12);
}

html, body, .stApp, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4, .hero-title { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.02em; }

/* animated liquid background */
.stApp { background: #07050F; }
.stApp::before {
  content: ""; position: fixed; inset: -10%; z-index: 0; pointer-events: none;
  background:
    radial-gradient(40vmax 40vmax at 20% 25%, rgba(139,92,246,.45), transparent 60%),
    radial-gradient(35vmax 35vmax at 80% 30%, rgba(109,40,217,.40), transparent 60%),
    radial-gradient(45vmax 45vmax at 50% 95%, rgba(168,85,247,.30), transparent 60%);
  filter: blur(40px);
  animation: drift 22s ease-in-out infinite alternate;
}
@keyframes drift {
  0%   { transform: translate3d(0,0,0) scale(1); }
  50%  { transform: translate3d(-4%,3%,0) scale(1.1); }
  100% { transform: translate3d(3%,-3%,0) scale(1.2); }
}

[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: transparent; }
[data-testid="stAppViewContainer"], section[data-testid="stSidebar"] { position: relative; z-index: 1; }

/* animated arrows */
.arrow {
  position: fixed; bottom: -60px; z-index: 0; pointer-events: none;
  color: rgba(167,139,250,.35); font-family: 'Space Grotesk', sans-serif;
  animation: rise linear infinite;
}
@keyframes rise {
  0%   { transform: translateY(0); opacity: 0; }
  10%  { opacity: 1; }
  90%  { opacity: 1; }
  100% { transform: translateY(-115vh); opacity: 0; }
}

/* liquid glass surfaces */
section[data-testid="stSidebar"] {
  background: rgba(15,10,30,.55);
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stMetric"], [data-testid="stAlert"], [data-testid="stDataFrame"],
[data-testid="stPlotlyChart"], .hero {
  background: var(--glass);
  backdrop-filter: blur(18px) saturate(160%);
  -webkit-backdrop-filter: blur(18px) saturate(160%);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.18), 0 10px 40px rgba(0,0,0,.35);
}
[data-testid="stMetric"] { padding: 18px 22px; transition: transform .25s ease, border-color .25s ease; }
[data-testid="stMetric"]:hover { transform: translateY(-4px); border-color: rgba(167,139,250,.6); }
[data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
[data-testid="stPlotlyChart"] { padding: 10px; }
[data-testid="stAlert"] { border-left: 3px solid var(--purple); }

/* hero */
.hero { padding: 34px 38px; margin-bottom: 20px; position: relative; }
.hero-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 9999px;
  background: rgba(139, 92, 246, 0.16);
  border: 1px solid rgba(167, 139, 250, 0.35);
  color: #DDD6FE; font-size: 0.78rem; font-weight: 600;
  letter-spacing: 0.06em; text-transform: uppercase;
  margin-bottom: 12px;
}
.hero-title {
  font-size: 2.6rem; font-weight: 700; margin: 0; line-height: 1.15;
  background: linear-gradient(90deg, #FFFFFF 0%, #E9D5FF 45%, #A855F7 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-tagline {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.15rem; font-weight: 600;
  color: #C4B5FD; margin-top: 6px; margin-bottom: 2px;
  letter-spacing: -0.01em;
}
.hero-sub { color: rgba(237,233,254,.7); margin-top: 6px; font-size: 0.98rem; line-height: 1.5; }

/* tabs bar container */
div[data-baseweb="tab-list"] {
  background: rgba(255, 255, 255, 0.03) !important;
  backdrop-filter: blur(20px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 16px !important;
  padding: 6px 8px !important;
  gap: 6px !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 8px 32px rgba(0, 0, 0, 0.35) !important;
  margin-bottom: 22px !important;
  overflow-x: auto !important;
  scrollbar-width: none !important;
}
div[data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }

/* hide default flat bottom underline */
div[data-baseweb="tab-border"] { display: none !important; }
div[data-baseweb="tab-highlight"] { display: none !important; }

/* tab button base */
button[data-baseweb="tab"] {
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 0.92rem !important;
  font-weight: 500 !important;
  color: rgba(237, 233, 254, 0.65) !important;
  padding: 10px 18px !important;
  border-radius: 12px !important;
  border: 1px solid transparent !important;
  background: transparent !important;
  transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
  position: relative !important;
  overflow: hidden !important;
  white-space: nowrap !important;
}

/* tab hover animation */
button[data-baseweb="tab"]:hover {
  color: #FFFFFF !important;
  background: rgba(139, 92, 246, 0.16) !important;
  border-color: rgba(167, 139, 250, 0.3) !important;
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.25) !important;
}

/* active tab style & glow */
button[data-baseweb="tab"][aria-selected="true"] {
  color: #FFFFFF !important;
  font-weight: 600 !important;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.38) 0%, rgba(109, 40, 217, 0.52) 100%) !important;
  border: 1px solid rgba(196, 181, 253, 0.45) !important;
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
  transform: translateY(-1px) !important;
}

/* tab light shimmer */
button[data-baseweb="tab"]::after {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent);
  transition: left 0.5s ease;
  pointer-events: none;
}
button[data-baseweb="tab"]:hover::after {
  left: 100%;
}

/* smooth tab content transition */
div[data-baseweb="tab-panel"], [data-testid="stTabContent"] {
  animation: tabFadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
@keyframes tabFadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* button hover animations */
.stButton > button,
.stDownloadButton > button,
button[data-testid*="stBaseButton"],
button[kind="primary"],
button[kind="secondary"] {
  position: relative !important;
  overflow: hidden !important;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.22) 0%, rgba(109, 40, 217, 0.32) 100%) !important;
  color: #EDE9FE !important;
  border: 1px solid rgba(167, 139, 250, 0.32) !important;
  border-radius: 12px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
  padding: 10px 22px !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
}

.stButton > button::before,
.stDownloadButton > button::before,
button[data-testid*="stBaseButton"]::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.18), transparent);
  transition: left 0.6s ease;
  pointer-events: none;
}

.stButton > button:hover::before,
.stDownloadButton > button:hover::before,
button[data-testid*="stBaseButton"]:hover::before {
  left: 100%;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
button[data-testid*="stBaseButton"]:hover,
button[kind="primary"]:hover,
button[kind="secondary"]:hover {
  transform: translateY(-3px) scale(1.02) !important;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.42) 0%, rgba(124, 58, 237, 0.52) 100%) !important;
  border-color: rgba(196, 181, 253, 0.75) !important;
  color: #FFFFFF !important;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.45), 0 0 18px rgba(167, 139, 250, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
}

.stButton > button:active,
.stDownloadButton > button:active,
button[data-testid*="stBaseButton"]:active {
  transform: translateY(0px) scale(0.98) !important;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3) !important;
}

/* file uploader dropzone button hover */
[data-testid="stFileUploaderDropzone"] button,
section[data-testid="stFileUploadDropzone"] button {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
  border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
section[data-testid="stFileUploadDropzone"] button:hover {
  transform: translateY(-2px) scale(1.03) !important;
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4) !important;
  border-color: #A78BFA !important;
}

#MainMenu, footer { visibility: hidden; }
</style>
"""


def _arrows(n=14):
    """Generate n arrows with random position, size and speed (same every run)."""
    random.seed(7)
    out = []
    for _ in range(n):
        left = random.randint(2, 96)
        size = random.randint(18, 44)
        dur = random.randint(14, 30)
        delay = -random.randint(0, 25)  # negative = already mid-flight on load
        out.append(
            f'<span class="arrow" style="left:{left}%;font-size:{size}px;'
            f'animation-duration:{dur}s;animation-delay:{delay}s">↗</span>')
    return "".join(out)


def _plotly_template():
    """Make all charts transparent with purple colours and matching fonts."""
    pio.templates["glass"] = go.layout.Template(layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#EDE9FE"),
        colorway=PURPLES,
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zeroline=False),
        title=dict(font=dict(family="Space Grotesk, sans-serif", size=18)),
    ))
    pio.templates.default = "glass"


def apply():
    """Call once, right after st.set_page_config."""
    st.markdown(CSS + _arrows(), unsafe_allow_html=True)
    _plotly_template()


def hero(title, subtitle, tagline=None, badge=None):
    """Glass header card at the top of the page."""
    badge_html = f'<div class="hero-badge">{badge}</div>' if badge else ""
    tagline_html = f'<div class="hero-tagline">{tagline}</div>' if tagline else ""
    st.markdown(
        f'<div class="hero">{badge_html}<div class="hero-title">{title}</div>'
        f'{tagline_html}<div class="hero-sub">{subtitle}</div></div>',
        unsafe_allow_html=True)