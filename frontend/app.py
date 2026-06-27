import streamlit as st
import pandas as pd
import requests
import os
import time
import io
import plotly.express as px
import plotly.graph_objects as go

# ── Must be FIRST Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="DataPilot Analytics",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
APP_VERSION = "2.0.0"

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM  —  aggressive Streamlit override
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ─── Hide Streamlit chrome ───────────────────────────────────────────── */
#MainMenu, header, footer { display: none !important; }
[data-testid="stToolbar"]  { display: none !important; }
[data-testid="stDecoration"]{ display: none !important; }
[data-testid="stStatusWidget"]{ display: none !important; }

/* ─── Tokens ──────────────────────────────────────────────────────────── */
:root {
  --bg0:     #0f172a;
  --bg1:     #0b0f19;
  --bg2:     #1e293b;
  --bg3:     #1e293b;
  --border:  rgba(255,255,255,0.06);
  --border2: rgba(255,255,255,0.1);
  --purple:  #6366f1;
  --purple-h:#4f46e5;
  --purple-g:#6366f1;
  --blue:    #3b82f6;
  --green:   #10b981;
  --amber:   #f59e0b;
  --red:     #ef4444;
  --t1:      #f8fafc;
  --t2:      #94a3b8;
  --t3:      #475569;
  --r:       6px;
  --r-sm:    4px;
  --shadow:  none;
  --glow:    none;
}

/* ─── Base ────────────────────────────────────────────────────────────── */
html,body,[class*="css"],[class*="st-"] {
  font-family: 'Inter', system-ui, sans-serif !important;
  -webkit-font-smoothing: antialiased !important;
}
.stApp { background: var(--bg0) !important; }

/* ─── Sidebar ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 220px !important;
  max-width: 220px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] .block-container { padding: 0 !important; }
section[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ─── Main content ────────────────────────────────────────────────────── */
.main .block-container {
  padding: 1.75rem 2.25rem !important;
  max-width: 1380px !important;
  background: var(--bg0) !important;
}

/* ─── Metric cards ────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 1.25rem 1.5rem !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="metric-container"] > div { gap: 0.25rem !important; }
[data-testid="metric-container"] label {
  font-size: 0.7rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.09em !important;
  text-transform: uppercase !important;
  color: var(--t3) !important;
}
[data-testid="stMetricValue"] > div {
  font-size: 1.9rem !important;
  font-weight: 800 !important;
  color: var(--t1) !important;
  line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.76rem !important; }

/* ─── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
  padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--t3) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  padding: 0.6rem 1.1rem !important;
  border-radius: 0 !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -1px !important;
}
.stTabs [aria-selected="true"] {
  color: var(--purple) !important;
  border-bottom: 2px solid var(--purple) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem !important; }

/* ─── Buttons ─────────────────────────────────────────────────────────── */
.stButton > button {
  border-radius: var(--r-sm) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  transition: all 0.18s ease !important;
  border: 1px solid var(--border2) !important;
  background: var(--bg3) !important;
  color: var(--t2) !important;
}
.stButton > button:hover {
  border-color: var(--purple) !important;
  color: var(--t1) !important;
  background: rgba(124,58,237,.1) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
  background: var(--purple-g) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em !important;
}
.stButton > button[kind="primary"]:hover {
  filter: brightness(1.12) !important;
  box-shadow: var(--glow) !important;
  transform: translateY(-1px) !important;
}

/* ─── Inputs ──────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r) !important;
  color: var(--t1) !important;
  font-size: 0.95rem !important;
  caret-color: var(--purple) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
  border-color: var(--purple) !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,.18) !important;
  outline: none !important;
}
.stTextInput label, .stTextArea label { display: none !important; }

/* ─── Expander ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  background: var(--bg2) !important;
  box-shadow: none !important;
  margin-bottom: 0.5rem !important;
}
[data-testid="stExpander"] summary {
  color: var(--t2) !important;
  font-size: 0.88rem !important;
  font-weight: 500 !important;
  padding: 0.75rem 1rem !important;
}

/* ─── Dataframe ───────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] iframe { border-radius: var(--r) !important; }

/* ─── Alerts ──────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--r-sm) !important;
  border: 1px solid var(--border) !important;
}

/* ─── File uploader ───────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
  background: var(--bg2) !important;
  border: 2px dashed var(--border2) !important;
  border-radius: var(--r) !important;
  transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--purple) !important; }

/* ─── Selectbox ───────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r-sm) !important;
  color: var(--t1) !important;
}

/* ─── Dividers ────────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }

/* ─── Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bg3); border-radius: 99px; }

/* ═══════════════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
═══════════════════════════════════════════════════════════════════════ */

/* Sidebar nav item */
.nav-item {
  display: flex; align-items: center; gap: 0.7rem;
  padding: 0.62rem 1.1rem;
  border-radius: var(--r-sm);
  margin: 0.12rem 0.5rem;
  cursor: pointer; font-size: 0.86rem; font-weight: 500;
  color: var(--t2);
  transition: all 0.15s;
  border: 1px solid transparent;
  text-decoration: none;
}
.nav-item:hover { background: var(--bg2); color: var(--t1); border-color: var(--border); }
.nav-item.active {
  background: rgba(99,102,241,.08) !important;
  color: var(--t1) !important;
  border-left: 3px solid var(--purple) !important;
  border-radius: 0 var(--r-sm) var(--r-sm) 0 !important;
}
.nav-icon { display: none; }

/* KPI Card */
.kpi {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 1.35rem 1.5rem 1.2rem;
  transition: border-color .2s, box-shadow .2s;
}
.kpi:hover { border-color: var(--border2); box-shadow: var(--shadow); }
.kpi-label {
  font-size: 0.68rem; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: var(--t3); margin-bottom: .6rem;
}
.kpi-value {
  font-size: 2.1rem; font-weight: 800; color: var(--t1);
  line-height: 1; letter-spacing: -.02em;
}
.kpi-sub { font-size: 0.75rem; color: var(--t3); margin-top: .4rem; }
.kpi-accent { width:3px; height:2rem; border-radius:99px; display:inline-block; margin-right:.75rem; vertical-align:middle; }

/* Status pill */
.pill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 99px;
  font-size: 0.69rem; font-weight: 600; letter-spacing: .04em;
}
.pill-green { background:rgba(16,185,129,.12); color:#10b981; border:1px solid rgba(16,185,129,.25); }
.pill-yellow{ background:rgba(245,158,11,.12); color:#f59e0b; border:1px solid rgba(245,158,11,.25); }
.pill-red   { background:rgba(239,68,68,.12);  color:#ef4444; border:1px solid rgba(239,68,68,.25); }
.pill-blue  { background:rgba(59,130,246,.12); color:#60a5fa; border:1px solid rgba(59,130,246,.25); }
.pill-purple{ background:rgba(124,58,237,.12); color:#a78bfa; border:1px solid rgba(124,58,237,.25); }

/* Hero search box */
.hero-wrap {
  text-align: center;
  padding: 2.5rem 1rem 1.75rem;
}
.hero-logo { font-size: 2.5rem; margin-bottom: .5rem; }
.hero-title {
  font-size: 2rem; font-weight: 800; color: var(--t1);
  letter-spacing: -.03em; margin-bottom: .4rem;
}
.hero-sub { font-size: 0.95rem; color: var(--t2); margin-bottom: 1.5rem; }

/* Suggestion chips */
.chips { display:flex; flex-wrap:wrap; gap:.5rem; justify-content:center; margin-bottom:1.5rem; }
.chip {
  background: var(--bg2); border: 1px solid var(--border2);
  border-radius: 99px; padding: .38rem 1rem;
  font-size: 0.8rem; color: var(--t2); cursor: pointer;
  transition: all .18s;
}
.chip:hover { border-color: var(--purple); color: var(--t1); background: rgba(124,58,237,.08); }

/* Dataset row */
.ds-row {
  display: flex; align-items: center;
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--r); padding: 1rem 1.25rem;
  margin-bottom: .5rem; transition: border-color .18s;
  gap: 1rem;
}
.ds-row:hover { border-color: var(--border2); }
.ds-icon { font-size: 1.4rem; flex-shrink: 0; }
.ds-info { flex: 1; min-width: 0; }
.ds-name { font-size: .92rem; font-weight: 600; color: var(--t1); }
.ds-meta { font-size: .75rem; color: var(--t3); margin-top: .15rem; }

/* History item */
.h-item {
  border-left: 2px solid var(--purple);
  padding: .8rem 1.1rem;
  background: var(--bg2);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  margin-bottom: .5rem;
  transition: background .15s;
}
.h-item:hover { background: var(--bg3); }
.h-q { font-size: .88rem; font-weight: 500; color: var(--t1); }
.h-meta { font-size: .72rem; color: var(--t3); margin-top: .2rem; }

/* Section headings */
.pg-title {
  font-size: 1.35rem; font-weight: 800; color: var(--t1);
  letter-spacing: -.02em; margin-bottom: .2rem;
}
.pg-sub { font-size: .83rem; color: var(--t2); margin-bottom: 1.25rem; }

/* Result summary bar */
.result-bar {
  display: flex; gap: 1.5rem; align-items: center;
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--r-sm); padding: .65rem 1.1rem;
  margin-bottom: .85rem; flex-wrap: wrap;
}
.rb-item { font-size: .78rem; color: var(--t2); }
.rb-item strong { color: var(--t1); font-weight: 600; }

/* Schema tree */
.stree-table {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--r-sm); margin-bottom: .35rem; overflow: hidden;
}
.stree-header {
  font-size: .85rem; font-weight: 600; color: var(--t1);
  padding: .65rem 1rem; cursor: pointer;
  display: flex; align-items: center; gap: .5rem;
}
.stree-col {
  font-size: .78rem; color: var(--t2);
  padding: .35rem 1rem .35rem 2.25rem;
  border-top: 1px solid var(--border);
  display: flex; justify-content: space-between;
}
.stree-type { font-size: .72rem; color: var(--purple); font-family: monospace; }

/* Settings row */
.srow {
  display: flex; justify-content: space-between; align-items: center;
  padding: .8rem 1rem; border-bottom: 1px solid var(--border);
  font-size: .84rem;
}
.srow:last-child { border-bottom: none; }
.srow-label { color: var(--t2); }
.srow-value { color: var(--t1); font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: .82rem; }

/* Insight card */
.ins-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--r); padding: 1.1rem 1.3rem; margin-bottom: .75rem;
}
.ins-label {
  font-size: .65rem; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; color: var(--purple); margin-bottom: .35rem;
}
.ins-text { font-size: .88rem; color: var(--t1); line-height: 1.6; }

/* Empty state */
.empty {
  text-align: center; padding: 3rem 1rem;
  background: var(--bg2); border: 1px dashed var(--border2);
  border-radius: var(--r);
}
.empty-icon { font-size: 2.25rem; margin-bottom: .65rem; }
.empty-title { font-size: .95rem; font-weight: 600; color: var(--t1); margin-bottom: .25rem; }
.empty-sub { font-size: .8rem; color: var(--t3); }

/* How it works steps */
.step-card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--r); padding: 1.1rem 1rem; text-align: center;
  transition: border-color .2s, box-shadow .2s;
}
.step-card:hover { border-color: var(--purple); box-shadow: var(--glow); }
.step-icon { font-size: 1.5rem; margin-bottom: .45rem; }
.step-title { font-size: .85rem; font-weight: 600; color: var(--t1); margin-bottom: .2rem; }
.step-desc { font-size: .75rem; color: var(--t3); line-height: 1.5; }

/* Query context header */
.q-context {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--r); padding: .85rem 1.1rem;
  margin-bottom: 1rem; font-size: .88rem;
}
.q-context-label { color: var(--t3); font-size: .72rem; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; }
.q-context-text { color: var(--t1); font-weight: 600; margin-top: .2rem; }

/* Conversation Item */
.conv-item {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.45rem 0.75rem;
  border-radius: var(--r-sm);
  margin: 0.15rem 0.5rem;
  cursor: pointer; font-size: 0.8rem; font-weight: 500;
  color: var(--t2);
  transition: all 0.12s;
  border: 1px solid transparent;
  text-align: left;
}
.conv-item:hover { background: var(--bg2); color: var(--t1); }
.conv-item.active {
  background: rgba(99,102,241,.1) !important;
  color: var(--purple) !important;
  border-left: 3px solid var(--purple) !important;
  border-radius: 0 var(--r-sm) var(--r-sm) 0 !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
_D = {
    "page": "AI Analyst",
    "history": [],
    "active_query": None,
    "active_preview": None,
    "pending_q": "",
    "preview_data": None,
    "preview_filename": None,
    "import_ok": False,
    "conversations": {},
    "current_conversation_id": None,
}
for k, v in _D.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Ensure a default conversation thread is always active
if not st.session_state["conversations"] or not st.session_state["current_conversation_id"] or st.session_state["current_conversation_id"] not in st.session_state["conversations"]:
    import time
    default_id = str(time.time())
    st.session_state["conversations"][default_id] = {
        "title": "New Analysis",
        "messages": []
    }
    st.session_state["current_conversation_id"] = default_id

# Ensure st.session_state["messages"] points to the active conversation's messages
st.session_state["messages"] = st.session_state["conversations"][st.session_state["current_conversation_id"]]["messages"]



# ══════════════════════════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=8)
def api_health():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if r.ok:
            d = requests.get(f"{BACKEND_URL}/health/db", timeout=3)
            return "online" if d.ok else "db_offline"
        return "degraded"
    except Exception:
        return "offline"


@st.cache_data(ttl=12)
def api_datasets():
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/datasets", timeout=5)
        return r.json() if r.ok else []
    except Exception:
        return []


@st.cache_data(ttl=15)
def api_schema():
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/schema", timeout=5)
        return r.json() if r.ok else {}
    except Exception:
        return {}


def clear_caches():
    api_datasets.clear()
    api_schema.clear()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
PAGES = [
    ("⬡", "", "Dashboard"),
    ("⬡", "", "AI Analyst"),
    ("⬡", "", "Datasets"),
    ("⬡", "", "Schema Explorer"),
    ("⬡", "", "History"),
    ("⬡", "", "Settings"),
]

health   = api_health()
datasets = api_datasets()
schema   = api_schema()

with st.sidebar:
    # Brand
    st.markdown("""
    <div style="padding:1.25rem 1.1rem .85rem; border-bottom:1px solid var(--border);">
      <div style="font-size:1.15rem;font-weight:800;color:var(--t1);letter-spacing:-.03em;">
        ⬡ DataPilot
      </div>
      <div style="font-size:.68rem;color:var(--t3);margin-top:1px;">AI Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    # ChatGPT-style "+ New Analysis" button
    if st.button("+ New Analysis", key="btn_new_analysis", use_container_width=True, type="secondary"):
        new_id = str(time.time())
        st.session_state["conversations"][new_id] = {
            "title": "New Analysis",
            "messages": []
        }
        st.session_state["current_conversation_id"] = new_id
        st.session_state["page"] = "AI Analyst"
        st.rerun()

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    # Conversation list
    st.markdown("<div style='font-size:.65rem;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-left:.75rem;margin-bottom:.4rem'>Recent Chats</div>", unsafe_allow_html=True)
    
    # Render conversation list
    for conv_id, info in list(st.session_state["conversations"].items()):
        active = st.session_state["current_conversation_id"] == conv_id and st.session_state["page"] == "AI Analyst"
        cls = "conv-item active" if active else "conv-item"
        title = info["title"]
        # Limit title text size
        disp_title = title if len(title) <= 22 else title[:20] + "..."
        if active:
            st.markdown(f'<div class="{cls}">💬 {disp_title}</div>', unsafe_allow_html=True)
        else:
            if st.button(f"💬 {disp_title}", key=f"sel_conv_{conv_id}", use_container_width=True):
                st.session_state["current_conversation_id"] = conv_id
                st.session_state["page"] = "AI Analyst"
                st.rerun()

    st.markdown("<hr style='margin:.5rem 0 !important'>", unsafe_allow_html=True)

    # Nav
    st.markdown("<div style='font-size:.65rem;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-left:.75rem;margin-bottom:.4rem'>Workspace Pages</div>", unsafe_allow_html=True)
    for p_name in ["Dashboard", "AI Analyst", "Datasets", "Schema Explorer", "Settings"]:
        active = st.session_state["page"] == p_name
        cls = "nav-item active" if active else "nav-item"
        if active:
            st.markdown(f'<div class="{cls}">{p_name}</div>', unsafe_allow_html=True)
        else:
            if st.button(p_name, key=f"nb_{p_name}", use_container_width=True):
                st.session_state["page"] = p_name
                st.rerun()

    # Bottom status
    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;width:220px;
                background:var(--bg1);border-top:1px solid var(--border);
                padding:.85rem 1.1rem;z-index:100;">
    """, unsafe_allow_html=True)

    h_map = {
        "online": ('Online', 'pill-green'),
        "db_offline": ('DB Offline', 'pill-yellow'),
        "degraded": ('Degraded', 'pill-yellow'),
        "offline": ('Offline', 'pill-red'),
    }
    hlabel, hcls = h_map.get(health, ('Unknown', 'pill-blue'))

    st.markdown(f"""
    <div style="font-size:.68rem;color:var(--t3);font-weight:600;
                text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem">Status</div>
    <span class="pill {hcls}">{hlabel}</span>
    <div style="margin-top:.55rem;font-size:.72rem;color:var(--t3);line-height:1.7">
      <span style="color:var(--t2)">{len(datasets)}</span> datasets &nbsp;·&nbsp;
      <span style="color:var(--t2)">{len(schema)}</span> tables &nbsp;·&nbsp;
      <span style="color:var(--t2)">{len(st.session_state['history'])}</span> queries
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PLOTLY THEME
# ══════════════════════════════════════════════════════════════════════════════
PLOT_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(30,41,59,1)",
    plot_bgcolor="rgba(30,41,59,1)",
    font=dict(family="Inter, sans-serif", color="#cbd5e1", size=11),
    margin=dict(l=12, r=12, t=44, b=12),
    colorway=["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#14b8a6", "#f97316"],
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)


def make_chart(df: pd.DataFrame, title: str = "") -> go.Figure | None:
    df = df.copy()
    numeric, date_c, cat_c = [], [], []
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col], errors='raise')
            except (ValueError, TypeError):
                pass
        cl = col.lower()
        if any(k in cl for k in ("date", "time", "month", "year", "week")) or pd.api.types.is_datetime64_any_dtype(df[col]):
            date_c.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            if cl.endswith("_id") or cl == "id":
                cat_c.append(col)
            else:
                numeric.append(col)
        else:
            cat_c.append(col)

    if not numeric:
        return None

    y = numeric[0]

    if date_c:
        x = date_c[0]
        fig = px.area(df, x=x, y=y, title=title or f"{y} over {x}")
        fig.update_traces(fill="tozeroy",
                          line=dict(color="#6366f1", width=2),
                          fillcolor="rgba(124,58,237,.15)")
    elif cat_c:
        x = cat_c[0]
        n = df[x].nunique()
        if 1 < n <= 5:
            fig = px.pie(df, names=x, values=y, hole=0.45, title=title or f"{y} by {x}")
        elif n > 10:
            top = df.nlargest(15, y)
            fig = px.bar(top, x=y, y=x, orientation="h", title=title or f"Top {x} by {y}")
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
        else:
            fig = px.bar(df, x=x, y=y, color=x, title=title or f"{y} by {x}")
    else:
        if len(numeric) >= 2:
            fig = px.bar(df, y=numeric, barmode="group", title=title or "Metric Comparison")
        else:
            fig = px.histogram(df, x=y, title=title or f"Distribution of {y}")
            fig.update_traces(marker_color="#6366f1")

    fig.update_layout(**PLOT_BASE)
    fig.update_layout(
        xaxis=dict(gridcolor="rgba(255,255,255,.05)", zeroline=False, linecolor="rgba(255,255,255,.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,.05)", zeroline=False, linecolor="rgba(255,255,255,.06)"),
        title=dict(font=dict(size=13, color="#f8fafc"), x=0, pad=dict(l=0)),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# QUERY RUNNER
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# DATASET UPLOAD HELPER
# ══════════════════════════════════════════════════════════════════════════════
def render_dataset_uploader(key_suffix: str = ""):
    st.markdown('<div style="font-size:.82rem;color:var(--t2);margin-bottom:.75rem">Supports <strong>CSV</strong> and <strong>XLSX</strong> · Maximum file size: <strong>50 MB</strong></div>', unsafe_allow_html=True)
    up = st.file_uploader("file", type=["csv", "xlsx"], label_visibility="collapsed", key=f"uploader_{key_suffix}")

    if up:
        fb = up.getvalue()
        fn = up.name
        if len(fb) > 50 * 1024 * 1024:
            st.error("File exceeds 50 MB limit.")
        else:
            if st.session_state.get(f"preview_filename_{key_suffix}") != fn:
                with st.spinner("Validating structure…"):
                    try:
                        pr = requests.post(
                            f"{BACKEND_URL}/api/v1/upload/preview",
                            files={"file": (fn, fb, up.type)}, timeout=12)
                        if pr.ok:
                            st.session_state[f"preview_data_{key_suffix}"] = pr.json()
                            st.session_state[f"preview_filename_{key_suffix}"] = fn
                            st.session_state[f"import_ok_{key_suffix}"] = False
                        else:
                            st.error(pr.json().get("detail", "Validation failed"))
                    except Exception as e:
                        st.error(str(e))

            p = st.session_state.get(f"preview_data_{key_suffix}")
            if p and st.session_state.get(f"preview_filename_{key_suffix}") == fn and not st.session_state.get(f"import_ok_{key_suffix}"):
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Rows",    f"{p['rows']:,}")
                mc2.metric("Columns", p["columns"])
                mc3.metric("Table",   p["dataset_name"])

                st.markdown('<div style="font-weight:600;margin-top:1.25rem;margin-bottom:0.5rem;color:var(--t2)">Schema & Column Types</div>', unsafe_allow_html=True)
                st.json(p["column_types"])
                
                st.markdown('<div style="font-weight:600;margin-top:1.25rem;margin-bottom:0.5rem;color:var(--t2)">Sample Data (first 10 rows)</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(p["preview"]), use_container_width=True)

                if st.button("Confirm Import", type="primary", use_container_width=True, key=f"confirm_import_{key_suffix}"):
                    with st.spinner("Importing…"):
                        try:
                            ir = requests.post(
                                f"{BACKEND_URL}/api/v1/upload/import",
                                files={"file": (fn, fb, up.type)}, timeout=35)
                            if ir.ok:
                                st.session_state[f"import_ok_{key_suffix}"] = True
                                clear_caches()
                                st.success("Imported successfully!")
                                time.sleep(0.7)
                                st.rerun()
                            else:
                                st.error(ir.json().get("detail", "Import failed"))
                        except Exception as e:
                            st.error(str(e))
    else:
        st.session_state[f"preview_data_{key_suffix}"] = None
        st.session_state[f"preview_filename_{key_suffix}"] = None
        st.session_state[f"import_ok_{key_suffix}"] = False


# ══════════════════════════════════════════════════════════════════════════════
# QUERY RUNNER
# ══════════════════════════════════════════════════════════════════════════════
def run_query(q: str):
    active_id = st.session_state["current_conversation_id"]
    conv = st.session_state["conversations"][active_id]
    
    # Generate conversation title from first user prompt
    if conv["title"] == "New Analysis":
        conv["title"] = q[:28] + ("..." if len(q) > 28 else "")

    # Append user question to message feed
    conv["messages"].append({"role": "user", "content": q})

    with st.status("Generating SQL and executing query…", expanded=True) as s:
        st.write("🔍 Translating natural language to SQL…")
        try:
            resp = requests.post(f"{BACKEND_URL}/api/v1/query",
                                 json={"question": q}, timeout=28)
        except Exception as e:
            s.update(label="Connection failed", state="error")
            st.error(str(e))
            conv["messages"].append({
                "role": "assistant",
                "content": f"Connection failed: {str(e)}",
                "success": False
            })
            st.rerun()
            return

        if not resp.ok:
            s.update(label=f"Error {resp.status_code}", state="error")
            st.error(resp.text[:300])
            conv["messages"].append({
                "role": "assistant",
                "content": f"Query execution failed: {resp.text[:300]}",
                "success": False
            })
            st.rerun()
            return

        res = resp.json()
        if not res.get("success"):
            s.update(label="Query failed", state="error")
            st.error(res.get("error", "Unknown error"))
            sql = res.get("sql", "")
            conv["messages"].append({
                "role": "assistant",
                "content": f"Query execution failed: {res.get('error', 'Unknown error')}",
                "sql": sql,
                "success": False
            })
            st.rerun()
            return

        sql    = res["sql"]
        data   = res["data"]
        ms     = res.get("execution_time_ms", 0)
        ts     = time.strftime("%H:%M:%S")
        ds_ref = "Core Database"
        for d in datasets:
            if d["dataset_name"] in sql:
                ds_ref = d["dataset_name"]; break

        st.write("💡 Generating AI insights…")
        insights = ""
        try:
            ir = requests.post(f"{BACKEND_URL}/api/v1/insights",
                               json={"question": q, "sql": sql, "data": data[:80]},
                               timeout=22)
            if ir.ok:
                insights = ir.json().get("insights", "")
        except Exception:
            insights = ""

        # Log flat query history for Dashboard/History pages consistency
        ctx = dict(question=q, sql=sql, data=data,
                   execution_time_ms=ms, dataset_used=ds_ref,
                   timestamp=ts, insights=insights)
        st.session_state["history"].append(ctx)

        # Build summary response text
        summary = f"I executed the SQL query successfully and retrieved **{len(data):,}** rows."
        if insights:
            lines = [l.strip() for l in insights.strip().splitlines() if l.strip()]
            if lines:
                summary += f" **Primary Finding**: {lines[0]}"

        # Append assistant message to thread
        conv["messages"].append({
            "role": "assistant",
            "content": summary,
            "success": True,
            "sql": sql,
            "data": data,
            "insights": insights,
            "execution_time_ms": ms,
            "dataset_used": ds_ref,
            "timestamp": ts
        })

        s.update(label=f"✓ {len(data):,} rows returned in {ms:.0f} ms", state="complete")

    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown('<div class="pg-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Executive platform overview</div>', unsafe_allow_html=True)

    hist    = st.session_state["history"]
    n_q     = len(hist)
    avg_ms  = sum(q["execution_time_ms"] for q in hist) / n_q if n_q else 0
    n_ds    = len(datasets)
    n_tbls  = len(schema)

    # ─── KPI Row ───
    c1, c2, c3, c4 = st.columns(4)
    status_text = "Online" if health == "online" else "Offline"
    status_color = "var(--green)" if health == "online" else "var(--red)"

    with c1:
        st.markdown(f"""
        <div class="kpi">
          <div class="kpi-label">System Status</div>
          <div class="kpi-value" style="font-size:1.3rem;color:{status_color}">{status_text}</div>
          <div class="kpi-sub">API + Database</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi">
          <div class="kpi-label">Datasets</div>
          <div class="kpi-value">{n_ds}</div>
          <div class="kpi-sub">Uploaded data files</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi">
          <div class="kpi-label">Schema Tables</div>
          <div class="kpi-value">{n_tbls}</div>
          <div class="kpi-sub">Available tables</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi">
          <div class="kpi-label">Avg Query Time</div>
          <div class="kpi-value">{avg_ms:.0f}<span style="font-size:1rem;font-weight:400;color:var(--t3)"> ms</span></div>
          <div class="kpi-sub">{n_q} total queries executed</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ─── Bottom row ───
    col_act, col_ds = st.columns([3, 2])

    with col_act:
        st.markdown('<div style="font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--t3);margin-bottom:.65rem">Recent Activity</div>', unsafe_allow_html=True)
        if hist:
            for hq in list(reversed(hist))[:6]:
                st.markdown(f"""
                <div class="h-item">
                  <div class="h-q">{hq["question"]}</div>
                  <div class="h-meta">
                    <span class="pill pill-green" style="font-size:.62rem;padding:1px 7px">SUCCESS</span>
                    &ensp;Latency: {hq["execution_time_ms"]:.0f} ms
                    &ensp;· {hq["timestamp"]}
                    &ensp;· {len(hq["data"]):,} rows
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty" style="padding:2rem">
              <div class="empty-title">No queries executed yet</div>
              <div class="empty-sub">Navigate to the AI Analyst workspace to begin</div>
            </div>""", unsafe_allow_html=True)

    with col_ds:
        st.markdown('<div style="font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--t3);margin-bottom:.65rem">Active Datasets</div>', unsafe_allow_html=True)
        if datasets:
            for ds in datasets[:5]:
                st.markdown(f"""
                <div class="ds-row" style="padding:.75rem 1rem;margin-bottom:.35rem">
                  <div class="ds-info">
                    <div class="ds-name">{ds["dataset_name"]}</div>
                    <div class="ds-meta">{ds["rows"]:,} rows &nbsp;·&nbsp; {ds["columns"]} columns</div>
                  </div>
                  <span class="pill pill-green">Active</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty" style="padding:2rem">
              <div class="empty-title">No uploaded datasets</div>
              <div class="empty-sub">Add datasets via the Datasets manager</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — AI ANALYST (CONVERSATIONAL WORKSPACE)
# ══════════════════════════════════════════════════════════════════════════════
SUGGESTIONS = [
    "Average salary of each job title",
    "Max salary by job title",
    "Hiring trend by job title",
    "Average experience by industry",
    "Remote work possibility counts",
]


def page_ai_analyst():
    active_id = st.session_state["current_conversation_id"]
    conv = st.session_state["conversations"][active_id]

    st.markdown(f'<div class="pg-title">{conv["title"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Conversational AI Data Analyst</div>', unsafe_allow_html=True)

    # Empty conversation welcome panel
    if not conv["messages"]:
        st.markdown("""
        <div class="hero-wrap">
          <div class="hero-logo">⬡</div>
          <div class="hero-title">Conversational Data Analytics</div>
          <div class="hero-sub">
            Ask questions in plain English. DataPilot writes optimized SQL, queries your database, 
            renders visualizations, and generates business insights.
          </div>
        </div>""", unsafe_allow_html=True)

        # Suggestions list
        st.markdown('<div style="text-align:center;font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.09em;color:var(--t3);margin-bottom:.65rem">Try a suggestion</div>', unsafe_allow_html=True)
        cols = st.columns(len(SUGGESTIONS))
        for i, s in enumerate(SUGGESTIONS):
            with cols[i]:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    run_query(s)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # Inline uploader for empty chat workspace
        st.markdown('<div style="font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--t3);text-align:center;margin-bottom:.65rem">Quick upload dataset</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div style="background:var(--bg2);border:1px dashed var(--border2);border-radius:var(--r);padding:1.5rem;">', unsafe_allow_html=True)
            render_dataset_uploader("empty_chat")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Render conversational message bubbles
        for idx, msg in enumerate(conv["messages"]):
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    st.markdown(f'<div style="font-size:0.95rem;color:var(--t1);line-height:1.5;">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    # Assistant conversational text
                    st.markdown(f'<div style="font-size:0.95rem;color:var(--t1);line-height:1.5;margin-bottom:0.75rem;">{msg["content"]}</div>', unsafe_allow_html=True)

                    if msg.get("success", False):
                        # Metadata execution summary bar
                        st.markdown(f"""
                        <div class="result-bar" style="margin-top:0.5rem;margin-bottom:0.5rem;padding:0.45rem 0.85rem;">
                          <div class="rb-item" style="font-size:0.75rem;">Rows: <strong>{len(msg['data']):,}</strong></div>
                          <div class="rb-item" style="font-size:0.75rem;">Columns: <strong>{len(msg['data'][0]) if msg['data'] else 0}</strong></div>
                          <div class="rb-item" style="font-size:0.75rem;">Latency: <strong>{msg['execution_time_ms']:.1f} ms</strong></div>
                          <div class="rb-item" style="font-size:0.75rem;">Dataset: <strong>{msg['dataset_used']}</strong></div>
                          <div class="rb-item" style="font-size:0.75rem;">Time: <strong>{msg['timestamp']}</strong></div>
                        </div>""", unsafe_allow_html=True)

                        # Parse query response df
                        df_res = pd.DataFrame(msg["data"])
                        # Dynamic cast string-based decimals to numeric float types
                        df_res = df_res.copy()
                        for col in df_res.columns:
                            if df_res[col].dtype == object:
                                try:
                                    df_res[col] = pd.to_numeric(df_res[col], errors='raise')
                                except (ValueError, TypeError):
                                    pass

                        # 1. Results Expander (Expanded by default)
                        with st.expander("Results Table", expanded=True):
                            st.dataframe(df_res, use_container_width=True, height=min(280, 60 + len(df_res) * 35))
                            cc, ce = st.columns(2)
                            with cc:
                                st.download_button("Export CSV", df_res.to_csv(index=False).encode(),
                                                   f"results_{idx}.csv", "text/csv", key=f"dl_csv_{idx}")
                            with ce:
                                buf = io.BytesIO()
                                with pd.ExcelWriter(buf, engine="openpyxl") as w:
                                    df_res.to_excel(w, index=False)
                                st.download_button("Export Excel", buf.getvalue(), f"results_{idx}.xlsx",
                                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                   key=f"dl_xl_{idx}")

                        # 2. SQL Expander (Collapsed)
                        with st.expander("SQL Query", expanded=False):
                            st.code(msg["sql"], language="sql")

                        # 3. Chart Expander (Collapsed)
                        with st.expander("Visualization Chart", expanded=False):
                            fig = make_chart(df_res, conv["messages"][max(0, idx-1)]["content"])
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No numeric columns detected for charting.")

                        # 4. Insights Expander (Collapsed)
                        with st.expander("AI Insights", expanded=False):
                            raw_ins = msg.get("insights", "")
                            if raw_ins:
                                lines = [l.strip() for l in raw_ins.strip().splitlines() if l.strip()]
                                bullets = [l for l in lines if l[:1] in ("*", "•", "-")]
                                if bullets:
                                    for b in bullets:
                                        st.markdown(f"""
                                        <div class="ins-card" style="padding:0.75rem 1rem;margin-bottom:0.4rem;">
                                          <div class="ins-text" style="font-size:0.8rem;">{b.lstrip('*•- ')}</div>
                                        </div>""", unsafe_allow_html=True)
                                else:
                                    for l in lines:
                                        st.markdown(f'<div class="ins-card" style="padding:0.75rem 1rem;margin-bottom:0.4rem;"><div class="ins-text" style="font-size:0.8rem;">{l}</div></div>', unsafe_allow_html=True)
                            else:
                                st.info("No insights generated.")
                    else:
                        if msg.get("sql"):
                            with st.expander("Generated SQL", expanded=True):
                                st.code(msg["sql"], language="sql")

    # Bottom sticky input row
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    c_input, c_pop = st.columns([5, 1.2], gap="small")
    with c_input:
        prompt = st.chat_input("Ask a question about your data…")
        if prompt:
            run_query(prompt.strip())
    with c_pop:
        up_pop = st.popover("Upload Dataset", use_container_width=True)
        with up_pop:
            render_dataset_uploader("chat_popover")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — DATASETS
# ══════════════════════════════════════════════════════════════════════════════
def page_datasets():
    st.markdown('<div class="pg-title">Dataset Manager</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Upload, preview, and manage your data files</div>', unsafe_allow_html=True)

    # Upload panel
    with st.expander("Upload New Dataset", expanded=not bool(datasets)):
        render_dataset_uploader("datasets_page")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # List
    st.markdown(f'<div style="font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:var(--t3);margin-bottom:.65rem">{len(datasets)} Datasets</div>', unsafe_allow_html=True)

    if not datasets:
        st.markdown("""
        <div class="empty">
          <div class="empty-title">No datasets uploaded yet</div>
          <div class="empty-sub">Use the uploader above to import a CSV or XLSX file</div>
        </div>""", unsafe_allow_html=True)
        return

    srch = st.text_input("search", placeholder="Search datasets…", label_visibility="collapsed")
    hits = [d for d in datasets if srch.lower() in d["dataset_name"].lower()] if srch else datasets

    for ds in hits:
        name = ds["dataset_name"]
        c_info, c_prev, c_del = st.columns([4, 1.5, 1.5])
        with c_info:
            st.markdown(f"""
            <div class="ds-row">
              
              <div class="ds-info">
                <div class="ds-name">{name}</div>
                <div class="ds-meta">{ds["rows"]:,} rows &nbsp;·&nbsp; {ds["columns"]} columns</div>
              </div>
              <span class="pill pill-green">Active</span>
            </div>""", unsafe_allow_html=True)
        with c_prev:
            if st.button("Preview", key=f"pv_{name}", use_container_width=True):
                st.session_state["active_preview"] = (
                    None if st.session_state.get("active_preview") == name else name
                )
        with c_del:
            if st.button("Delete", key=f"dl_{name}", use_container_width=True):
                try:
                    dr = requests.delete(f"{BACKEND_URL}/api/v1/datasets/{name}", timeout=6)
                    if dr.ok:
                        clear_caches()
                        if st.session_state.get("active_preview") == name:
                            st.session_state["active_preview"] = None
                        st.success(f"Deleted {name}")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error("Delete failed")
                except Exception as e:
                    st.error(str(e))

        # Inline preview
        if st.session_state.get("active_preview") == name:
            ds_detail = next((d for d in datasets if d["dataset_name"] == name), None)
            if ds_detail:
                with st.container():
                    p1, p2 = st.columns(2)
                    with p1:
                        st.markdown("**Column Types**")
                        st.json(ds_detail.get("column_types", {}))
                    with p2:
                        st.markdown("**Sample Data**")
                        st.dataframe(pd.DataFrame(ds_detail.get("preview", [])), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — SCHEMA EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
def page_schema():
    st.markdown('<div class="pg-title">Schema Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Browse all tables and column definitions</div>', unsafe_allow_html=True)

    if not schema:
        st.warning("Schema unavailable — check backend connection.")
        return

    core = {k: v for k, v in schema.items() if not k.startswith("uploaded_")}
    uploaded = {k: v for k, v in schema.items() if k.startswith("uploaded_")}

    left, right = st.columns([1, 2])

    with left:
        st.markdown(f"""
        <div style="background:var(--bg2);border:1px solid var(--border);
                    border-radius:var(--r);padding:1rem;margin-bottom:.5rem">
          <div style="font-size:.68rem;font-weight:700;text-transform:uppercase;
                      letter-spacing:.09em;color:var(--t3);margin-bottom:.65rem">Overview</div>
          <div style="font-size:.85rem;color:var(--t1);font-weight:600">{len(schema)} total tables</div>
          <div style="font-size:.75rem;color:var(--t2);margin-top:.35rem">
            {len(core)} core &nbsp;·&nbsp; {len(uploaded)} uploaded
          </div>
        </div>""", unsafe_allow_html=True)

        if core:
            st.markdown('<div style="font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:var(--t3);margin:.75rem 0 .4rem">Core Tables</div>', unsafe_allow_html=True)
            for t in core:
                st.markdown(f'<div class="stree-table"><div class="stree-header">{t} <span style="font-size:.7rem;color:var(--t3);font-weight:400">({len(schema[t])} cols)</span></div></div>', unsafe_allow_html=True)

        if uploaded:
            st.markdown('<div style="font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:var(--t3);margin:.75rem 0 .4rem">Uploaded Tables</div>', unsafe_allow_html=True)
            for t in uploaded:
                st.markdown(f'<div class="stree-table"><div class="stree-header">{t} <span style="font-size:.7rem;color:var(--t3);font-weight:400">({len(schema[t])} cols)</span></div></div>', unsafe_allow_html=True)

    with right:
        for section, tables in [("Core Tables", core), ("Uploaded Tables", uploaded)]:
            if not tables:
                continue
            st.markdown(f'<div style="font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:var(--t3);margin-bottom:.5rem">{section}</div>', unsafe_allow_html=True)
            for tbl, cols in tables.items():
                with st.expander(f"**{tbl}** &nbsp; `{len(cols)} columns`"):
                    if cols:
                        df_c = pd.DataFrame(cols)
                        if "name" in df_c.columns and "type" in df_c.columns:
                            df_c = df_c[["name", "type"]].rename(columns={"name": "Column", "type": "Type"})
                        st.dataframe(df_c, hide_index=True, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def page_history():
    st.markdown('<div class="pg-title">Query History</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Browse and re-run queries from this session</div>', unsafe_allow_html=True)

    hist = st.session_state["history"]
    if not hist:
        st.markdown("""
        <div class="empty">
          <div class="empty-title">No history yet</div>
          <div class="empty-sub">Queries you run in AI Analyst will appear here</div>
        </div>""", unsafe_allow_html=True)
        return

    srch = st.text_input("hsrch", placeholder="Filter history…", label_visibility="collapsed")
    items = [q for q in reversed(hist) if srch.lower() in q["question"].lower()] if srch else list(reversed(hist))

    for idx, q in enumerate(items):
        hc, ha, hb = st.columns([5, 1.2, 0.8])
        with hc:
            st.markdown(f"""
            <div class="h-item">
              <div class="h-q">{q['question']}</div>
              <div class="h-meta">
                <span class="pill pill-green" style="font-size:.62rem;padding:1px 7px">SUCCESS</span>
                &ensp;Latency: {q["execution_time_ms"]:.0f} ms
                &ensp;· {q["timestamp"]}
                &ensp;· {len(q["data"]):,} rows
                &ensp;· {q.get("dataset_used","Core DB")}
              </div>
            </div>""", unsafe_allow_html=True)
        with ha:
            if st.button("Re-run", key=f"hr_{idx}", use_container_width=True):
                st.session_state["pending_q"] = q["question"]
                st.session_state["page"] = "AI Analyst"
                st.rerun()
        with hb:
            if st.button("SQL", key=f"hs_{idx}", use_container_width=True):
                st.session_state[f"hsql_{idx}"] = not st.session_state.get(f"hsql_{idx}", False)
                st.rerun()

        if st.session_state.get(f"hsql_{idx}"):
            st.code(q["sql"], language="sql")

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    if st.button("Clear History", use_container_width=True):
        st.session_state["history"] = []
        st.session_state["active_query"] = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown('<div class="pg-title">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Platform configuration and security features — read-only</div>', unsafe_allow_html=True)

    h_label = {"online": "Online", "db_offline": "DB Offline",
                "degraded": "Degraded", "offline": "Offline"}.get(health, "Unknown")

    rows = [
        ("Backend URL",        BACKEND_URL),
        ("System Status",      h_label),
        ("Active Datasets",    str(len(datasets))),
        ("Schema Tables",      str(len(schema))),
        ("Session Queries",    str(len(st.session_state["history"]))),
        ("Max Question Length","2,000 characters"),
        ("Max File Size",      "50 MB"),
        ("Max Rows / Upload",  "100,000"),
        ("Max Columns / Upload","200"),
        ("Query Rate Limit",   "30 req / minute"),
        ("Upload Rate Limit",  "10 uploads / hour"),
        ("Application Version",f"v{APP_VERSION}"),
    ]

    st.markdown("""
    <div style="background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;margin-bottom:1.5rem">
    """, unsafe_allow_html=True)
    for label, val in rows:
        st.markdown(f"""
        <div class="srow">
          <span class="srow-label">{label}</span>
          <span class="srow-value">{val}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:var(--t3);margin-bottom:.65rem">Security Features</div>', unsafe_allow_html=True)
    sec = [
        ("SQL AST Validation",    "All queries parsed and sanitized with SQLGlot before execution"),
        ("SELECT-only Enforcement","Modifying statements (INSERT/UPDATE/DELETE/DROP) are blocked"),
        ("Prompt Injection Guard", "LLM system prompt hardened with SECURITY DIRECTIVE"),
        ("Request Tracing",        "X-Request-ID header attached to every API response"),
        ("Rate Limiting",          "Sliding window limiter per client IP address"),
        ("File Validation",        "Extension, size, structure, duplicate-column, and schema checks"),
    ]
    st.markdown('<div style="background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);overflow:hidden">', unsafe_allow_html=True)
    for feat, desc in sec:
        st.markdown(f"""
        <div class="srow">
          <span class="srow-label">{feat}</span>
          <span style="font-size:.76rem;color:var(--t3)">{desc}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
p = st.session_state["page"]

if p == "Dashboard":
    page_dashboard()
elif p == "AI Analyst":
    page_ai_analyst()
elif p == "Datasets":
    page_datasets()
elif p == "Schema Explorer":
    page_schema()
elif p == "History":
    page_history()
elif p == "Settings":
    page_settings()
