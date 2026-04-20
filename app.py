# ╔══════════════════════════════════════════════════════════════════════╗
# ║  EmpiricX — Research Intelligence Engine                            ║
# ║  Single-file deployment · v3.0                                      ║
# ║                                                                      ║
# ║  Dependencies (pip install):                                        ║
# ║    streamlit openai pdfplumber python-docx openpyxl pandas          ║
# ╚══════════════════════════════════════════════════════════════════════╝

import io
import os
import re
import json
import textwrap
import traceback
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Optional heavy deps (graceful fallback) ────────────────────────────
try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from docx import Document as DocxOut
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX_OUT = True
except ImportError:
    HAS_DOCX_OUT = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# ══════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EmpiricX — Research Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — CSS
# ══════════════════════════════════════════════════════════════════════
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --gold:        #d4a843;
  --gold-light:  #f0c866;
  --gold-dim:    rgba(212,168,67,.16);
  --gold-glow:   rgba(212,168,67,.07);
  --navy:        #0c0c1e;
  --navy-2:      #11112a;
  --navy-3:      #191932;
  --surface:     #15152d;
  --surface-2:   #1c1c38;
  --border:      rgba(212,168,67,.15);
  --border-soft: rgba(255,255,255,.055);
  --text-1:      #f0ede5;
  --text-2:      #b0aca0;
  --text-3:      #6e6c64;
  --teal:        #4ecdc4;
  --rose:        #e8647a;
  --fh:          'Syne', sans-serif;
  --fb:          'DM Sans', sans-serif;
  --fm:          'JetBrains Mono', monospace;
  --r:           10px;
  --rl:          16px;
  --tr:          .2s cubic-bezier(.4,0,.2,1);
  --sg:          0 0 36px rgba(212,168,67,.1);
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--navy) !important;
  color: var(--text-1) !important;
  font-family: var(--fb) !important;
  font-size: 15px;
  line-height: 1.66;
  -webkit-font-smoothing: antialiased;
}

h1,h2,h3,h4,h5,h6,
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3,
.stMarkdown h4,.stMarkdown h5,.stMarkdown h6 {
  font-family: var(--fh) !important;
  color: var(--text-1) !important;
  letter-spacing: -.025em;
  line-height: 1.22;
}
p, li, .stMarkdown p {
  font-family: var(--fb) !important;
  color: var(--text-2);
  line-height: 1.7;
}
code, pre, [data-testid="stCode"] { font-family: var(--fm) !important; }

/* ── Streamlit chrome ── */
[data-testid="stHeader"]             { background: transparent !important; }
[data-testid="stToolbar"]            { display: none !important; }
[data-testid="stDecoration"]         { display: none !important; }
footer                               { display: none !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1.6rem !important; }
.block-container { padding-left: 2rem !important; padding-right: 2rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--navy-2) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.2rem 1rem 1.4rem !important; }

.sb-brand   { display:flex; align-items:center; gap:.7rem; padding:.2rem 0; }
.sb-name    { font-family:var(--fh); font-size:1.3rem; font-weight:800; color:var(--text-1); letter-spacing:-.035em; }
.sb-name em { color:var(--gold); font-style:normal; }
.sb-tag     { font-family:var(--fb); font-size:.68rem; font-weight:500; color:var(--text-3); letter-spacing:.13em; text-transform:uppercase; margin-top:.1rem; }
.sb-div     { height:1px; background:var(--border); margin:.85rem 0; }
.sb-lbl     { font-family:var(--fb); font-size:.67rem; font-weight:700; color:var(--text-3); letter-spacing:.14em; text-transform:uppercase; display:block; margin-bottom:.5rem; }

.sb-paper   { display:flex; align-items:center; gap:.55rem; background:var(--surface); border:1px solid var(--border-soft); border-radius:var(--r); padding:.5rem .65rem; margin-bottom:.35rem; }
.sb-pname   { font-family:var(--fb); font-size:.78rem; font-weight:500; color:var(--text-1); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; min-width:0; flex:1; }
.sb-pmeta   { font-family:var(--fm); font-size:.65rem; color:var(--text-3); }
.sb-badge   { font-family:var(--fb); font-size:.6rem; font-weight:700; letter-spacing:.07em; text-transform:uppercase; padding:.15rem .45rem; border-radius:99px; flex-shrink:0; }
.ok  { background:rgba(78,205,196,.13); color:var(--teal); border:1px solid rgba(78,205,196,.28); }
.nw  { background:var(--gold-dim); color:var(--gold-light); border:1px solid rgba(212,168,67,.28); }

.sb-stats   { display:flex; gap:.6rem; }
.sb-stat    { flex:1; background:var(--surface); border:1px solid var(--border-soft); border-radius:var(--r); padding:.6rem .4rem; text-align:center; }
.sb-stat-n  { font-family:var(--fh); font-size:1.25rem; font-weight:700; color:var(--gold-light); }
.sb-stat-l  { font-family:var(--fb); font-size:.65rem; color:var(--text-3); text-transform:uppercase; letter-spacing:.09em; }

[data-testid="stSidebar"] .stRadio label {
  padding:.42rem .55rem !important; border-radius:var(--r) !important;
  transition:background var(--tr) !important;
}
[data-testid="stSidebar"] .stRadio label:hover { background:var(--gold-glow) !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
  font-family:var(--fb) !important; font-size:.86rem !important; font-weight:500; color:var(--text-2) !important;
}

/* ── Buttons ── */
.stButton > button {
  font-family:var(--fb) !important; font-weight:600 !important; font-size:.84rem !important;
  background:var(--gold-dim) !important; color:var(--gold-light) !important;
  border:1px solid rgba(212,168,67,.32) !important; border-radius:var(--r) !important;
  padding:.52rem 1.15rem !important; transition:all var(--tr) !important;
  letter-spacing:.02em !important;
}
.stButton > button:hover {
  background:var(--gold) !important; color:var(--navy) !important;
  border-color:var(--gold) !important; transform:translateY(-1px);
  box-shadow:0 4px 18px rgba(212,168,67,.28) !important;
}
.stButton > button:active { transform:translateY(0) !important; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  font-family:var(--fb) !important; background:var(--surface) !important;
  border:1px solid var(--border) !important; border-radius:var(--r) !important;
  color:var(--text-1) !important; font-size:.88rem !important;
  transition:border var(--tr) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color:var(--gold) !important; box-shadow:0 0 0 3px var(--gold-dim) !important;
}
label[data-testid="stWidgetLabel"] p {
  font-family:var(--fb) !important; font-size:.78rem !important; font-weight:600 !important;
  color:var(--text-3) !important; letter-spacing:.08em !important; text-transform:uppercase !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background:var(--surface) !important; border:1.5px dashed var(--border) !important;
  border-radius:var(--r) !important; transition:border-color var(--tr) !important;
}
[data-testid="stFileUploader"]:hover { border-color:var(--gold) !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background:transparent !important; gap:.25rem !important;
  border-bottom:1px solid var(--border) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  font-family:var(--fb) !important; font-size:.84rem !important; font-weight:600 !important;
  color:var(--text-3) !important; background:transparent !important;
  border:none !important; padding:.5rem .95rem !important;
}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
  color:var(--gold-light) !important; border-bottom:2px solid var(--gold) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
  background:var(--surface) !important; border-radius:var(--r) !important;
  font-family:var(--fb) !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] { border-radius:var(--r) !important; overflow:hidden; }

/* ── Expander ── */
[data-testid="stExpander"] {
  background:var(--surface) !important; border:1px solid var(--border-soft) !important;
  border-radius:var(--r) !important;
}
[data-testid="stExpander"] summary {
  font-family:var(--fb) !important; font-weight:600 !important; color:var(--text-2) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p { font-family:var(--fb) !important; color:var(--text-2) !important; }

/* ── Gate page ── */
.gate-bg {
  position:fixed; inset:0; z-index:-1;
  background:
    radial-gradient(ellipse 70% 55% at 50% 28%, rgba(212,168,67,.055) 0%, transparent 68%),
    radial-gradient(ellipse 45% 40% at 80% 82%, rgba(78,205,196,.035) 0%, transparent 55%),
    var(--navy);
}
.gate-card {
  background:var(--navy-2); border:1px solid var(--border);
  border-radius:var(--rl); padding:2.4rem 2.2rem 1.8rem;
  box-shadow:0 24px 80px rgba(0,0,0,.55), var(--sg);
  margin-top:1.5rem;
}
.gate-logo { font-family:var(--fh); font-size:2rem; font-weight:800; color:var(--text-1); letter-spacing:-.04em; }
.gate-logo span { color:var(--gold); }
.gate-sub  { font-family:var(--fb); font-size:.76rem; font-weight:500; color:var(--text-3); letter-spacing:.15em; text-transform:uppercase; margin-top:.2rem; }
.gate-pill {
  display:inline-flex; align-items:center; justify-content:center;
  background:var(--gold-dim); border:1px solid rgba(212,168,67,.26);
  color:var(--gold-light); font-family:var(--fb); font-size:.73rem; font-weight:600;
  letter-spacing:.08em; padding:.28rem .95rem; border-radius:99px; margin:.9rem auto 1.1rem;
}
.gate-feats { display:flex; flex-direction:column; gap:.5rem; margin-bottom:1.3rem; text-align:left; }
.gate-feat  { display:flex; align-items:flex-start; gap:.6rem; font-family:var(--fb); font-size:.82rem; color:var(--text-2); line-height:1.5; }
.gate-dot   { width:5px; height:5px; border-radius:50%; background:var(--gold); margin-top:.48rem; flex-shrink:0; }
.gate-err   { background:rgba(232,100,122,.11); border:1px solid rgba(232,100,122,.28); border-radius:var(--r); color:var(--rose); font-family:var(--fb); font-size:.81rem; padding:.48rem .8rem; margin-bottom:.65rem; }
.gate-foot  { font-family:var(--fb); font-size:.7rem; color:var(--text-3); text-align:center; margin-top:.9rem; }
.gate-links { display:flex; justify-content:center; gap:1.4rem; margin-top:.55rem; flex-wrap:wrap; }
.gate-links a { font-family:var(--fb); font-size:.71rem; color:var(--text-3); text-decoration:none; transition:color var(--tr); }
.gate-links a:hover { color:var(--gold-light); }

/* ── Pricing ── */
.pricing-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:.9rem; margin:1.5rem 0 .4rem; }
.pcrd {
  background:var(--navy-3); border:1px solid var(--border-soft);
  border-radius:var(--rl); padding:1.5rem 1.3rem 1.2rem;
  display:flex; flex-direction:column; gap:.35rem;
  transition:border-color var(--tr), box-shadow var(--tr), transform var(--tr);
  position:relative; overflow:hidden;
}
.pcrd:hover { border-color:var(--gold); box-shadow:var(--sg); transform:translateY(-2px); }
.pcrd.feat {
  background:linear-gradient(140deg,#1c1c3a 0%,#242450 100%);
  border-color:var(--gold); box-shadow:var(--sg);
}
.pcrd.feat::before {
  content:'POPULAR'; position:absolute; top:11px; right:-24px;
  background:var(--gold); color:var(--navy); font-family:var(--fb);
  font-size:.58rem; font-weight:800; letter-spacing:.1em;
  padding:.18rem 2.5rem; transform:rotate(35deg);
}
.pc-plan  { font-family:var(--fb); font-size:.67rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase; color:var(--gold); }
.pc-price { font-family:var(--fh); font-size:1.85rem; font-weight:800; color:var(--text-1); letter-spacing:-.04em; line-height:1; }
.pc-price span { font-family:var(--fb); font-size:.8rem; font-weight:400; color:var(--text-3); letter-spacing:0; }
.pc-desc  { font-family:var(--fb); font-size:.76rem; color:var(--text-3); margin-top:.05rem; margin-bottom:.4rem; flex:1; }
.pc-feats { list-style:none; padding:0; margin:0 0 .9rem; display:flex; flex-direction:column; gap:.28rem; }
.pc-feats li { font-family:var(--fb); font-size:.76rem; color:var(--text-2); display:flex; align-items:flex-start; gap:.4rem; }
.pc-feats li::before { content:'✓'; color:var(--gold); font-weight:800; flex-shrink:0; }
.pc-cta {
  display:block; text-align:center; padding:.55rem .9rem; border-radius:var(--r);
  font-family:var(--fb); font-size:.8rem; font-weight:700; letter-spacing:.04em;
  text-decoration:none !important; transition:all var(--tr); cursor:pointer;
}
.pc-out { background:transparent; border:1px solid rgba(212,168,67,.38); color:var(--gold-light) !important; }
.pc-out:hover { background:var(--gold-dim); border-color:var(--gold); }
.pc-sol { background:var(--gold); border:1px solid var(--gold); color:var(--navy) !important; }
.pc-sol:hover { background:var(--gold-light); box-shadow:0 4px 20px rgba(212,168,67,.3); }

/* ── Content page ── */
.pg-head { font-family:var(--fh); font-size:1.5rem; font-weight:700; color:var(--text-1); letter-spacing:-.028em; margin-bottom:.2rem; }
.pg-sub  { font-family:var(--fb); font-size:.85rem; color:var(--text-3); margin-bottom:1.3rem; }

/* ── Paper card ── */
.pcard {
  background:var(--surface); border:1px solid var(--border-soft);
  border-radius:var(--rl); padding:1.3rem 1.5rem 1.1rem;
  margin-bottom:.9rem;
  transition:border-color var(--tr), box-shadow var(--tr);
}
.pcard:hover { border-color:var(--border); box-shadow:var(--sg); }
.pcard-title { font-family:var(--fh); font-size:1.05rem; font-weight:700; color:var(--text-1); margin-bottom:.3rem; }
.pcard-meta  { font-family:var(--fm); font-size:.7rem; color:var(--text-3); margin-bottom:.7rem; }
.pcard-field { display:flex; gap:.5rem; margin-bottom:.28rem; }
.pf-label    { font-family:var(--fb); font-size:.72rem; font-weight:700; color:var(--gold); letter-spacing:.06em; text-transform:uppercase; min-width:110px; flex-shrink:0; padding-top:.03rem; }
.pf-value    { font-family:var(--fb); font-size:.82rem; color:var(--text-2); line-height:1.55; }

/* ── Synthesis output ── */
.syn-block {
  background:var(--surface); border:1px solid var(--border-soft);
  border-radius:var(--rl); padding:1.8rem 2rem;
  font-family:var(--fb); font-size:.9rem; color:var(--text-2);
  line-height:1.8;
}
.syn-block h3 {
  font-family:var(--fh) !important; font-size:1.1rem !important;
  font-weight:700 !important; color:var(--gold-light) !important;
  margin:1.2rem 0 .5rem; letter-spacing:-.02em !important;
}
.syn-block p  { margin-bottom:.85rem; }
.syn-block blockquote {
  border-left:3px solid var(--gold); padding-left:1rem;
  color:var(--text-3); font-style:italic; margin:1rem 0;
}

/* ── Empty state ── */
.empty-state {
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  padding:3.5rem 1rem; text-align:center;
}
.empty-icon  { font-size:2.8rem; margin-bottom:1rem; opacity:.45; }
.empty-title { font-family:var(--fh); font-size:1.15rem; font-weight:700; color:var(--text-2); margin-bottom:.4rem; }
.empty-desc  { font-family:var(--fb); font-size:.84rem; color:var(--text-3); max-width:340px; line-height:1.6; }

/* ── Status badge inline ── */
.badge { display:inline-flex; align-items:center; gap:.3rem; font-family:var(--fb); font-size:.71rem; font-weight:700; letter-spacing:.07em; text-transform:uppercase; padding:.16rem .5rem; border-radius:99px; }
.b-gold { background:var(--gold-dim); color:var(--gold-light); border:1px solid rgba(212,168,67,.28); }
.b-teal { background:rgba(78,205,196,.12); color:var(--teal); border:1px solid rgba(78,205,196,.26); }
.b-rose { background:rgba(232,100,122,.12); color:var(--rose); border:1px solid rgba(232,100,122,.26); }

/* ── Mobile ── */
@media (max-width:768px) {
  .block-container { padding-left:.8rem !important; padding-right:.8rem !important; }
  .gate-card        { padding:1.5rem 1.1rem 1.4rem !important; margin-top:.4rem; border-radius:var(--r) !important; }
  .gate-logo        { font-size:1.65rem !important; }
  .pricing-grid     { grid-template-columns:1fr !important; gap:.65rem !important; }
  .pcrd.feat::before { display:none; }
  .pg-head          { font-size:1.25rem; }
  [data-testid="stMainBlockContainer"] { padding-top:.9rem !important; }
}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# SVG LOGOS
# ══════════════════════════════════════════════════════════════════════
LOGO_SM = """<svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polygon points="17,1 31,9 31,25 17,33 3,25 3,9" fill="#11112a" stroke="#d4a843" stroke-width="1.3"/>
  <polygon points="17,7 27,12.5 27,21.5 17,27 7,21.5 7,12.5" fill="none" stroke="#d4a843" stroke-width=".55" opacity=".38"/>
  <polygon points="17,11 24,15 24,19 17,23 10,19 10,15" fill="#d4a843" opacity=".2"/>
  <circle cx="17" cy="17" r="3.3" fill="#f0c866"/>
  <circle cx="17" cy="17" r="1.5" fill="#fff" opacity=".88"/>
  <circle cx="17" cy="1"   r="1"   fill="#d4a843" opacity=".7"/>
  <circle cx="31" cy="9"   r="1"   fill="#d4a843" opacity=".7"/>
  <circle cx="31" cy="25"  r="1"   fill="#d4a843" opacity=".7"/>
  <circle cx="17" cy="33"  r="1"   fill="#d4a843" opacity=".7"/>
  <circle cx="3"  cy="25"  r="1"   fill="#d4a843" opacity=".7"/>
  <circle cx="3"  cy="9"   r="1"   fill="#d4a843" opacity=".7"/>
</svg>"""

LOGO_LG = """<svg width="62" height="62" viewBox="0 0 62 62" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="g1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f0c866" stop-opacity=".3"/>
      <stop offset="100%" stop-color="#d4a843" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <polygon points="31,2 58,16.5 58,45.5 31,60 4,45.5 4,16.5" fill="#11112a" stroke="#d4a843" stroke-width="1.5"/>
  <circle cx="31" cy="31" r="24" fill="url(#g1)"/>
  <polygon points="31,11 50,21 50,41 31,51 12,41 12,21" fill="none" stroke="#d4a843" stroke-width=".9" opacity=".3"/>
  <polygon points="31,18 44,25.5 44,36.5 31,44 18,36.5 18,25.5" fill="#d4a843" opacity=".22"/>
  <circle cx="31" cy="31" r="6.2" fill="#f0c866"/>
  <circle cx="31" cy="31" r="3"   fill="#fff" opacity=".88"/>
  <circle cx="31" cy="2"  r="1.7" fill="#d4a843" opacity=".8"/>
  <circle cx="58" cy="16.5" r="1.7" fill="#d4a843" opacity=".8"/>
  <circle cx="58" cy="45.5" r="1.7" fill="#d4a843" opacity=".8"/>
  <circle cx="31" cy="60"  r="1.7" fill="#d4a843" opacity=".8"/>
  <circle cx="4"  cy="45.5" r="1.7" fill="#d4a843" opacity=".8"/>
  <circle cx="4"  cy="16.5" r="1.7" fill="#d4a843" opacity=".8"/>
</svg>"""

# ══════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "authenticated": False,
    "page": "results",
    "queued_files": [],
    "extracted_papers": [],
    "synthesis_result": None,
    "synthesis_topic": "",
    "trigger_extract": False,
    "_routing_lock": False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════
def fmt_size(n: int) -> str:
    if n < 1024:       return f"{n} B"
    if n < 1024**2:    return f"{n/1024:.1f} KB"
    return f"{n/1024**2:.1f} MB"

def navigate(page: str):
    st.session_state["page"] = page
    st.session_state["_routing_lock"] = True
    st.rerun()

def get_openai_client():
    key = ""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        pass
    if not key:
        key = os.environ.get("OPENAI_API_KEY", "")
    if not key or not HAS_OPENAI:
        return None
    return OpenAI(api_key=key)

# ── Text extraction ────────────────────────────────────────────────────
def extract_text_from_file(file_obj) -> str:
    name = file_obj.name.lower()
    raw = file_obj.read()

    if name.endswith(".pdf"):
        if not HAS_PDF:
            return "[pdfplumber not installed — cannot read PDF]"
        try:
            pages = []
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                for pg in pdf.pages[:40]:          # cap at 40 pages
                    t = pg.extract_text()
                    if t:
                        pages.append(t)
            return "\n\n".join(pages)
        except Exception as e:
            return f"[PDF extraction error: {e}]"

    elif name.endswith(".docx"):
        if not HAS_DOCX:
            return "[python-docx not installed — cannot read DOCX]"
        try:
            doc = DocxDocument(io.BytesIO(raw))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            return f"[DOCX extraction error: {e}]"

    else:  # .txt
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                return raw.decode(enc)
            except Exception:
                pass
        return raw.decode("utf-8", errors="replace")

# ── AI extraction ──────────────────────────────────────────────────────
EXTRACT_SYSTEM = """You are a precise academic research analyst.
Extract structured empirical data from the provided research paper text.
Return ONLY valid JSON — no markdown fences, no commentary.
Schema:
{
  "title": "...",
  "authors": "...",
  "year": "...",
  "journal": "...",
  "research_question": "...",
  "methodology": "...",
  "sample": "...",
  "key_findings": ["..."],
  "statistical_results": "...",
  "limitations": "...",
  "conclusion": "...",
  "keywords": ["..."]
}
If a field cannot be determined, use null."""

def ai_extract_paper(text: str, filename: str) -> dict:
    client = get_openai_client()
    if not client:
        return _mock_extract(filename)
    try:
        snippet = text[:12000]
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM},
                {"role": "user",   "content": f"Paper filename: {filename}\n\n---\n\n{snippet}"},
            ],
            temperature=0.1,
            max_tokens=1200,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)
        data["_source_file"] = filename
        return data
    except Exception as e:
        return {"_source_file": filename, "_error": str(e),
                "title": filename, "authors": None, "year": None,
                "journal": None, "research_question": None,
                "methodology": None, "sample": None,
                "key_findings": [], "statistical_results": None,
                "limitations": None, "conclusion": None, "keywords": []}

def _mock_extract(filename: str) -> dict:
    """Fallback when no API key is present — returns a clearly labelled stub."""
    return {
        "_source_file": filename,
        "_mock": True,
        "title": f"[Demo] {filename}",
        "authors": "Demo Author et al.",
        "year": "2024",
        "journal": "Demo Journal",
        "research_question": "Add your OpenAI API key to extract real data.",
        "methodology": "N/A (demo mode)",
        "sample": "N/A",
        "key_findings": ["Connect an OpenAI API key to enable real extraction."],
        "statistical_results": None,
        "limitations": None,
        "conclusion": "Set OPENAI_API_KEY in Streamlit secrets or environment.",
        "keywords": ["demo"],
    }

# ── AI Synthesis ───────────────────────────────────────────────────────
SYNTH_SYSTEM = """You are a senior academic researcher writing a rigorous synthesis.
Given structured data from multiple research papers, write a cohesive, cited, publication-ready synthesis.
Use inline citations in the format (Author, Year).
Structure with clear section headings using ### markdown.
Write in flowing academic prose — no bullet lists.
Minimum 500 words. Be analytical, not merely descriptive."""

def ai_synthesise(papers: list[dict], topic: str) -> str:
    client = get_openai_client()
    if not client:
        return _mock_synthesis(papers, topic)
    try:
        summaries = []
        for i, p in enumerate(papers, 1):
            authors = p.get("authors") or "Unknown"
            year    = p.get("year") or "n.d."
            title   = p.get("title") or p.get("_source_file", f"Paper {i}")
            findings = "; ".join(p.get("key_findings") or [])
            summaries.append(
                f"[{i}] {authors} ({year}). {title}.\n"
                f"RQ: {p.get('research_question','')}\n"
                f"Method: {p.get('methodology','')}\n"
                f"Findings: {findings}\n"
                f"Stats: {p.get('statistical_results','')}\n"
                f"Conclusion: {p.get('conclusion','')}"
            )
        payload = "\n\n---\n\n".join(summaries)
        user_msg = f"Topic: {topic or 'General synthesis of uploaded papers'}\n\n{payload}"
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYNTH_SYSTEM},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0.4,
            max_tokens=2400,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"**Synthesis error:** {e}\n\n{_mock_synthesis(papers, topic)}"

def _mock_synthesis(papers: list[dict], topic: str) -> str:
    titles = [p.get("title") or p.get("_source_file","Untitled") for p in papers]
    titles_str = "; ".join(titles)
    return textwrap.dedent(f"""
    ### Overview
    This is a **demo synthesis** (no OpenAI API key detected). In production, EmpiricX
    generates a full cited academic synthesis from your extracted papers.

    ### Papers Included
    The following {len(papers)} paper(s) were provided for synthesis: {titles_str}.

    ### Topic
    Requested synthesis topic: *{topic or 'General'}*.

    ### Next Steps
    Add your `OPENAI_API_KEY` to `.streamlit/secrets.toml`:
    ```
    OPENAI_API_KEY = "sk-..."
    APP_PASSWORD   = "your-password"
    ```
    Then re-run synthesis to generate publication-ready prose.
    """).strip()

# ── Export helpers ─────────────────────────────────────────────────────
def build_csv(papers: list[dict]) -> bytes:
    rows = []
    for p in papers:
        rows.append({
            "Title":             p.get("title",""),
            "Authors":           p.get("authors",""),
            "Year":              p.get("year",""),
            "Journal":           p.get("journal",""),
            "Research Question": p.get("research_question",""),
            "Methodology":       p.get("methodology",""),
            "Sample":            p.get("sample",""),
            "Key Findings":      " | ".join(p.get("key_findings") or []),
            "Statistics":        p.get("statistical_results",""),
            "Limitations":       p.get("limitations",""),
            "Conclusion":        p.get("conclusion",""),
            "Keywords":          ", ".join(p.get("keywords") or []),
            "Source File":       p.get("_source_file",""),
        })
    return pd.DataFrame(rows).to_csv(index=False).encode()

def build_excel(papers: list[dict]) -> bytes:
    buf = io.BytesIO()
    df = pd.DataFrame([{
        "Title":             p.get("title",""),
        "Authors":           p.get("authors",""),
        "Year":              p.get("year",""),
        "Journal":           p.get("journal",""),
        "Research Question": p.get("research_question",""),
        "Methodology":       p.get("methodology",""),
        "Sample":            p.get("sample",""),
        "Key Findings":      " | ".join(p.get("key_findings") or []),
        "Statistics":        p.get("statistical_results",""),
        "Limitations":       p.get("limitations",""),
        "Conclusion":        p.get("conclusion",""),
        "Keywords":          ", ".join(p.get("keywords") or []),
        "Source File":       p.get("_source_file",""),
    } for p in papers])
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Extracted Papers")
    return buf.getvalue()

def build_word_report(papers: list[dict], synthesis: str | None) -> bytes:
    if not HAS_DOCX_OUT:
        return b""
    buf = io.BytesIO()
    doc = DocxOut()

    # Title
    title_p = doc.add_heading("EmpiricX Research Synthesis Report", 0)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Papers analysed: {len(papers)}")
    doc.add_paragraph("")

    if synthesis:
        doc.add_heading("Cross-Paper Synthesis", level=1)
        for line in synthesis.split("\n"):
            line = line.strip()
            if not line:
                doc.add_paragraph("")
            elif line.startswith("### "):
                doc.add_heading(line[4:], level=2)
            elif line.startswith("## "):
                doc.add_heading(line[3:], level=1)
            else:
                doc.add_paragraph(line)
        doc.add_page_break()

    doc.add_heading("Individual Paper Extractions", level=1)
    for p in papers:
        doc.add_heading(p.get("title") or p.get("_source_file","Untitled"), level=2)
        fields = [
            ("Authors",          p.get("authors")),
            ("Year",             p.get("year")),
            ("Journal",         p.get("journal")),
            ("Research Question",p.get("research_question")),
            ("Methodology",      p.get("methodology")),
            ("Sample",           p.get("sample")),
            ("Key Findings",     " | ".join(p.get("key_findings") or [])),
            ("Statistics",       p.get("statistical_results")),
            ("Limitations",      p.get("limitations")),
            ("Conclusion",       p.get("conclusion")),
        ]
        for label, val in fields:
            if val:
                para = doc.add_paragraph()
                run_l = para.add_run(f"{label}: ")
                run_l.bold = True
                para.add_run(str(val))
        doc.add_paragraph("")

    doc.save(buf)
    return buf.getvalue()

# ══════════════════════════════════════════════════════════════════════
# AUTH GATE
# ══════════════════════════════════════════════════════════════════════
def check_password() -> bool:
    try:
        correct = st.secrets.get("APP_PASSWORD", "empiricx2024")
    except Exception:
        correct = "empiricx2024"

    if st.session_state.get("authenticated"):
        return True

    st.markdown('<div class="gate-bg"></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.75, 1])

    with col:
        st.markdown('<div class="gate-card">', unsafe_allow_html=True)

        # Brand
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:1.3rem;">
          {LOGO_LG}
          <div class="gate-logo" style="margin-top:10px;">Empiri<span>X</span></div>
          <div class="gate-sub">Research Intelligence Engine</div>
        </div>
        <div style="display:flex;justify-content:center;">
          <div class="gate-pill">⬡ AI-Powered &nbsp;·&nbsp; Empirical &nbsp;·&nbsp; Synthesis</div>
        </div>
        """, unsafe_allow_html=True)

        # Features
        st.markdown("""
        <div class="gate-feats" style="margin-top:1rem;">
          <div class="gate-feat"><div class="gate-dot"></div>Extract structured empirical data from any research paper</div>
          <div class="gate-feat"><div class="gate-dot"></div>Deep cross-paper synthesis — cited, flowing, publication-ready prose</div>
          <div class="gate-feat"><div class="gate-dot"></div>Export-ready: CSV, Excel &amp; Word synthesis reports</div>
        </div>
        """, unsafe_allow_html=True)

        # Pricing
        st.markdown("""
        <div style="text-align:center;font-family:'DM Sans',sans-serif;font-size:.67rem;
                    font-weight:800;color:#6e6c64;letter-spacing:.14em;text-transform:uppercase;
                    margin-top:1.5rem;margin-bottom:.7rem;">Choose a Plan</div>
        <div class="pricing-grid">

          <div class="pcrd">
            <div class="pc-plan">Starter</div>
            <div class="pc-price">₦9,500<span>/mo</span></div>
            <div class="pc-desc">Individual researchers &amp; students</div>
            <ul class="pc-feats">
              <li>Up to 10 papers / month</li>
              <li>Structured extraction</li>
              <li>CSV &amp; Excel export</li>
              <li>Email support</li>
            </ul>
            <a href="#FLUTTERWAVE_STARTER_LINK" class="pc-cta pc-out">Get Started →</a>
          </div>

          <div class="pcrd feat">
            <div class="pc-plan">Pro</div>
            <div class="pc-price">₦24,000<span>/mo</span></div>
            <div class="pc-desc">Serious researchers &amp; labs</div>
            <ul class="pc-feats">
              <li>Unlimited papers</li>
              <li>Cross-paper synthesis</li>
              <li>Word synthesis reports</li>
              <li>Priority support</li>
              <li>Early feature access</li>
            </ul>
            <a href="#FLUTTERWAVE_PRO_LINK" class="pc-cta pc-sol">Upgrade to Pro →</a>
          </div>

          <div class="pcrd">
            <div class="pc-plan">Team</div>
            <div class="pc-price">₦60,000<span>/mo</span></div>
            <div class="pc-desc">Departments &amp; institutions</div>
            <ul class="pc-feats">
              <li>Up to 10 seats</li>
              <li>All Pro features</li>
              <li>Shared workspace</li>
              <li>Dedicated account manager</li>
              <li>Custom integrations</li>
            </ul>
            <a href="#FLUTTERWAVE_TEAM_LINK" class="pc-cta pc-out">Contact Sales →</a>
          </div>

        </div>
        """, unsafe_allow_html=True)

        # Login
        st.markdown("""
        <div style="font-family:'DM Sans',sans-serif;font-size:.67rem;font-weight:800;
                    color:#6e6c64;letter-spacing:.14em;text-transform:uppercase;
                    margin-top:1.4rem;margin-bottom:.45rem;">Already a member</div>
        """, unsafe_allow_html=True)

        err_slot = st.empty()
        pwd = st.text_input("Password", type="password",
                            placeholder="Enter your access password", key="pwd_input",
                            label_visibility="collapsed")
        st.button("Enter Platform →", use_container_width=True, key="gate_enter")

        if st.session_state.get("gate_enter") or pwd:
            if pwd == correct:
                st.session_state["authenticated"] = True
                st.rerun()
            elif pwd:
                err_slot.markdown(
                    '<div class="gate-err">⚠ Incorrect password — please try again.</div>',
                    unsafe_allow_html=True)

        # Footer
        st.markdown("""
        <div class="gate-foot">Restricted access &nbsp;·&nbsp; <strong>EmpiricX</strong> v3.0</div>
        <div class="gate-links">
          <a href="mailto:support@empiricx.io">✉ Contact Support</a>
          <a href="https://docs.empiricx.io" target="_blank">📖 User Guide</a>
          <a href="https://empiricx.io/privacy" target="_blank">Privacy Policy</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    return False

if not check_password():
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">{LOGO_SM}<span class="sb-name">Empiri<em>X</em></span></div>
    <div class="sb-tag">Research Intelligence</div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # Upload
    st.markdown('<span class="sb-lbl">📄 Upload Papers</span>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["pdf","docx","txt"],
                                 accept_multiple_files=True,
                                 label_visibility="collapsed",
                                 key="sidebar_uploader")
    if uploaded:
        queued = st.session_state["queued_files"]
        existing = {f["name"] for f in queued}
        for f in uploaded:
            if f.name not in existing:
                queued.append({"name": f.name, "size": f.size, "obj": f})
                existing.add(f.name)
        st.session_state["queued_files"] = queued

    queued        = st.session_state["queued_files"]
    extracted     = st.session_state["extracted_papers"]
    extracted_names = {p.get("_source_file") for p in extracted}

    if queued:
        st.markdown('<div style="margin-top:8px"></div>', unsafe_allow_html=True)
        for fi in queued:
            cls = "ok" if fi["name"] in extracted_names else "nw"
            lbl = "Done" if fi["name"] in extracted_names else "Queued"
            st.markdown(f"""
            <div class="sb-paper">
              <div style="font-size:.9rem;flex-shrink:0;">📄</div>
              <div style="min-width:0;flex:1">
                <div class="sb-pname">{fi["name"]}</div>
                <div class="sb-pmeta">{fmt_size(fi["size"])}</div>
              </div>
              <span class="sb-badge {cls}">{lbl}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div style="margin-top:8px"></div>', unsafe_allow_html=True)
        pending = [f for f in queued if f["name"] not in extracted_names]
        if pending:
            if st.button(f"⚡ Extract {len(pending)} paper{'s' if len(pending)>1 else ''}",
                         use_container_width=True, key="sb_extract"):
                st.session_state["trigger_extract"] = True
                navigate("results")

        if st.button("🗑 Clear all", use_container_width=True, key="sb_clear"):
            st.session_state.update(queued_files=[], extracted_papers=[],
                                    synthesis_result=None, synthesis_topic="")
            st.rerun()

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # Navigation
    st.markdown('<span class="sb-lbl">Navigation</span>', unsafe_allow_html=True)
    nav_map = {"📊  Results":"results","🔗  Synthesis":"synthesis","📥  Export":"export"}
    cur = st.session_state.get("page","results")
    if cur not in nav_map.values(): cur = "results"

    sel = st.radio("nav", list(nav_map.keys()),
                   index=list(nav_map.values()).index(cur),
                   label_visibility="collapsed", key="main_nav")
    if not st.session_state.get("_routing_lock"):
        st.session_state["page"] = nav_map[sel]
    st.session_state["_routing_lock"] = False

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # Stats
    n_p  = len(st.session_state["extracted_papers"])
    s_ok = "✓" if st.session_state.get("synthesis_result") else "—"
    st.markdown(f"""
    <div class="sb-stats">
      <div class="sb-stat"><div class="sb-stat-n">{n_p}</div><div class="sb-stat-l">Papers</div></div>
      <div class="sb-stat"><div class="sb-stat-n">{s_ok}</div><div class="sb-stat-l">Synthesis</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)
    if st.button("⏹ Sign out", use_container_width=True, key="sb_signout"):
        st.session_state["authenticated"] = False
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# EXTRACTION RUNNER
# ══════════════════════════════════════════════════════════════════════
def run_extraction():
    queued    = st.session_state["queued_files"]
    extracted = st.session_state["extracted_papers"]
    done_names = {p.get("_source_file") for p in extracted}
    pending   = [f for f in queued if f["name"] not in done_names]
    if not pending:
        return

    prog = st.progress(0, text="Starting extraction…")
    for i, fi in enumerate(pending):
        prog.progress((i) / len(pending), text=f"Extracting: {fi['name']}")
        fi["obj"].seek(0)
        raw_text = extract_text_from_file(fi["obj"])
        result   = ai_extract_paper(raw_text, fi["name"])
        st.session_state["extracted_papers"].append(result)
    prog.progress(1.0, text="✓ Extraction complete")
    import time; time.sleep(.6)
    prog.empty()

# ══════════════════════════════════════════════════════════════════════
# PAGE — RESULTS
# ══════════════════════════════════════════════════════════════════════
def render_results():
    if st.session_state.get("trigger_extract"):
        st.session_state["trigger_extract"] = False
        run_extraction()

    papers = st.session_state["extracted_papers"]

    st.markdown('<div class="pg-head">Extracted Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Structured empirical data extracted from your uploaded papers</div>',
                unsafe_allow_html=True)

    if not papers:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">📂</div>
          <div class="empty-title">No papers extracted yet</div>
          <div class="empty-desc">Upload PDF, DOCX, or TXT research papers using the sidebar, then click Extract.</div>
        </div>""", unsafe_allow_html=True)
        return

    # Summary row
    years  = [p.get("year") for p in papers if p.get("year")]
    yr_rng = f"{min(years)}–{max(years)}" if years else "—"
    c1,c2,c3 = st.columns(3)
    for col, label, val in [
        (c1,"Papers Extracted",  str(len(papers))),
        (c2,"Year Range",        yr_rng),
        (c3,"Synthesis Ready",   "Yes" if len(papers)>=2 else "Need ≥2"),
    ]:
        col.markdown(f"""
        <div style="background:var(--surface);border:1px solid var(--border-soft);
                    border-radius:var(--r);padding:.9rem 1.1rem;text-align:center;">
          <div style="font-family:var(--fh);font-size:1.5rem;font-weight:700;color:var(--gold-light);">{val}</div>
          <div style="font-family:var(--fb);font-size:.72rem;color:var(--text-3);
                      text-transform:uppercase;letter-spacing:.1em;">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)

    # View toggle
    view = st.radio("View as", ["Cards","Table"], horizontal=True, key="results_view")

    if view == "Table":
        rows = [{
            "Title":       p.get("title",""),
            "Authors":     p.get("authors",""),
            "Year":        p.get("year",""),
            "Journal":     p.get("journal",""),
            "Methodology": p.get("methodology",""),
            "Conclusion":  p.get("conclusion",""),
        } for p in papers]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        for p in papers:
            mock_tag = ' <span class="badge b-rose">Demo</span>' if p.get("_mock") else ""
            err_tag  = f' <span class="badge b-rose">Error</span>' if p.get("_error") else ""
            st.markdown(f"""
            <div class="pcard">
              <div class="pcard-title">{p.get("title") or p.get("_source_file","Untitled")}{mock_tag}{err_tag}</div>
              <div class="pcard-meta">{p.get("authors","") or ""} &nbsp;·&nbsp; {p.get("year","") or ""} &nbsp;·&nbsp; {p.get("journal","") or ""}</div>
            """, unsafe_allow_html=True)
            fields = [
                ("Research Question", p.get("research_question")),
                ("Methodology",       p.get("methodology")),
                ("Sample",            p.get("sample")),
                ("Key Findings",      " · ".join(p.get("key_findings") or []) or None),
                ("Statistics",        p.get("statistical_results")),
                ("Limitations",       p.get("limitations")),
                ("Conclusion",        p.get("conclusion")),
            ]
            for lbl, val in fields:
                if val:
                    st.markdown(f"""
                    <div class="pcard-field">
                      <span class="pf-label">{lbl}</span>
                      <span class="pf-value">{val}</span>
                    </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

    # CTA row — FIXED routing
    ca, cb = st.columns(2)
    with ca:
        if st.button("🔗 Run Cross-Paper Synthesis", use_container_width=True,
                     key="res_to_syn",
                     disabled=len(papers) < 2,
                     help="Need at least 2 extracted papers"):
            navigate("synthesis")
    with cb:
        if st.button("📥 Export Data", use_container_width=True, key="res_to_exp"):
            navigate("export")

# ══════════════════════════════════════════════════════════════════════
# PAGE — SYNTHESIS
# ══════════════════════════════════════════════════════════════════════
def render_synthesis():
    papers = st.session_state["extracted_papers"]

    st.markdown('<div class="pg-head">Cross-Paper Synthesis</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">AI-generated academic synthesis across all extracted papers</div>',
                unsafe_allow_html=True)

    if len(papers) < 2:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🔗</div>
          <div class="empty-title">Need at least 2 papers</div>
          <div class="empty-desc">Extract 2 or more papers first, then return here to generate a cross-paper synthesis.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("← Back to Results", key="syn_back"):
            navigate("results")
        return

    # Topic input
    topic = st.text_input(
        "Synthesis Focus (optional)",
        value=st.session_state.get("synthesis_topic",""),
        placeholder="e.g. 'Impact of social media on adolescent mental health'",
        key="syn_topic_input",
    )
    st.session_state["synthesis_topic"] = topic

    # Paper selector
    all_titles = [p.get("title") or p.get("_source_file","Untitled") for p in papers]
    selected_titles = st.multiselect(
        "Papers to include",
        options=all_titles,
        default=all_titles,
        key="syn_paper_sel",
    )
    selected_papers = [p for p in papers
                       if (p.get("title") or p.get("_source_file","Untitled")) in selected_titles]

    col_run, _ = st.columns([1,3])
    with col_run:
        run_btn = st.button("⚡ Generate Synthesis", use_container_width=True, key="syn_run",
                            disabled=len(selected_papers) < 2)

    if run_btn:
        with st.spinner("Generating synthesis…"):
            result = ai_synthesise(selected_papers, topic)
        st.session_state["synthesis_result"] = result
        st.rerun()

    result = st.session_state.get("synthesis_result")
    if result:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        # Render synthesis with styled block
        lines_html = ""
        for line in result.split("\n"):
            s = line.strip()
            if not s:
                lines_html += "<br>"
            elif s.startswith("### "):
                lines_html += f"<h3>{s[4:]}</h3>"
            elif s.startswith("## "):
                lines_html += f"<h2>{s[3:]}</h2>"
            else:
                lines_html += f"<p>{s}</p>"
        st.markdown(f'<div class="syn-block">{lines_html}</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:.9rem"></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            if st.button("📥 Export Synthesis Report", use_container_width=True, key="syn_to_exp"):
                navigate("export")
        with cb:
            if st.button("🔄 Regenerate", use_container_width=True, key="syn_regen"):
                st.session_state["synthesis_result"] = None
                st.rerun()

# ══════════════════════════════════════════════════════════════════════
# PAGE — EXPORT
# ══════════════════════════════════════════════════════════════════════
def render_export():
    papers    = st.session_state["extracted_papers"]
    synthesis = st.session_state.get("synthesis_result")

    st.markdown('<div class="pg-head">Export</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Download your extracted data and synthesis report</div>',
                unsafe_allow_html=True)

    if not papers:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">📥</div>
          <div class="empty-title">Nothing to export yet</div>
          <div class="empty-desc">Extract papers first, then return here to download your data.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("← Go to Results", key="exp_back"):
            navigate("results")
        return

    st.markdown(f"""
    <div style="background:var(--surface);border:1px solid var(--border-soft);
                border-radius:var(--r);padding:1rem 1.3rem;margin-bottom:1.2rem;
                display:flex;gap:2rem;flex-wrap:wrap;">
      <div>
        <span style="font-family:var(--fh);font-size:1.2rem;font-weight:700;
                     color:var(--gold-light);">{len(papers)}</span>
        <span style="font-family:var(--fb);font-size:.78rem;color:var(--text-3);
                     margin-left:.4rem;text-transform:uppercase;letter-spacing:.09em;">Papers</span>
      </div>
      <div>
        <span style="font-family:var(--fh);font-size:1.2rem;font-weight:700;
                     color:{'var(--teal)' if synthesis else 'var(--text-3)'};">
          {'✓' if synthesis else '—'}
        </span>
        <span style="font-family:var(--fb);font-size:.78rem;color:var(--text-3);
                     margin-left:.4rem;text-transform:uppercase;letter-spacing:.09em;">Synthesis</span>
      </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div style="background:var(--surface);border:1px solid var(--border-soft);
                    border-radius:var(--r);padding:1.1rem 1.2rem;margin-bottom:.6rem;">
          <div style="font-family:var(--fh);font-weight:700;color:var(--text-1);margin-bottom:.3rem;">CSV</div>
          <div style="font-family:var(--fb);font-size:.78rem;color:var(--text-3);">
            Raw extraction data — works with Excel, R, Python
          </div>
        </div>""", unsafe_allow_html=True)
        st.download_button(
            "⬇ Download CSV",
            data=build_csv(papers),
            file_name="empiricx_extraction.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_csv",
        )

    with c2:
        st.markdown("""
        <div style="background:var(--surface);border:1px solid var(--border-soft);
                    border-radius:var(--r);padding:1.1rem 1.2rem;margin-bottom:.6rem;">
          <div style="font-family:var(--fh);font-weight:700;color:var(--text-1);margin-bottom:.3rem;">Excel</div>
          <div style="font-family:var(--fb);font-size:.78rem;color:var(--text-3);">
            Formatted spreadsheet with all extracted fields
          </div>
        </div>""", unsafe_allow_html=True)
        st.download_button(
            "⬇ Download Excel",
            data=build_excel(papers),
            file_name="empiricx_extraction.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_xlsx",
        )

    with c3:
        st.markdown("""
        <div style="background:var(--surface);border:1px solid var(--border-soft);
                    border-radius:var(--r);padding:1.1rem 1.2rem;margin-bottom:.6rem;">
          <div style="font-family:var(--fh);font-weight:700;color:var(--text-1);margin-bottom:.3rem;">Word Report</div>
          <div style="font-family:var(--fb);font-size:.78rem;color:var(--text-3);">
            Full report with synthesis + all extractions
          </div>
        </div>""", unsafe_allow_html=True)
        if HAS_DOCX_OUT:
            word_bytes = build_word_report(papers, synthesis)
            st.download_button(
                "⬇ Download Word",
                data=word_bytes,
                file_name="empiricx_synthesis_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="dl_docx",
            )
        else:
            st.button("⬇ Download Word", disabled=True, use_container_width=True,
                      help="python-docx not installed", key="dl_docx_dis")

    if not synthesis:
        st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
        st.info("💡 Run a cross-paper synthesis first to include it in the Word report.")
        if st.button("🔗 Go to Synthesis", use_container_width=False, key="exp_to_syn"):
            navigate("synthesis")

# ══════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════
page = st.session_state.get("page", "results")

if page == "results":
    render_results()
elif page == "synthesis":
    render_synthesis()
elif page == "export":
    render_export()
