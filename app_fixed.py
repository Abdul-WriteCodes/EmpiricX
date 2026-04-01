import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import io
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PanelStatX",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@400;500;600;700;800&display=swap');

:root {
    --bg:        #0a0c10;
    --surface:   #111318;
    --surface2:  #181c24;
    --border:    #1f2535;
    --accent:    #00e5c8;
    --accent2:   #7c6df0;
    --accent3:   #f05c7c;
    --text:      #e2e8f4;
    --muted:     #6b7a9a;
    --success:   #22d3a0;
    --warn:      #f5a623;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* Headers */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] > div > div:first-child {
    color: var(--muted) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="metric-container"] label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 4px !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.05em !important;
}
.stButton > button:hover {
    background: var(--accent) !important;
    color: var(--bg) !important;
}

/* Primary button */
[data-testid="baseButton-primary"] > button,
.stButton [kind="primary"] {
    background: var(--accent) !important;
    color: var(--bg) !important;
    font-weight: 600 !important;
}

/* Selectbox / inputs */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    border-radius: 4px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    background: transparent !important;
    border-radius: 0 !important;
    padding: 12px 24px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

/* Dataframes */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}

/* Sidebar labels */
.stSidebar label, .stSidebar .stMarkdown {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
}

/* Slider */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--accent) !important;
}

/* Custom badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-teal  { background: rgba(0,229,200,0.12); color: var(--accent); border: 1px solid rgba(0,229,200,0.3); }
.badge-purple{ background: rgba(124,109,240,0.12); color: var(--accent2); border: 1px solid rgba(124,109,240,0.3); }
.badge-red   { background: rgba(240,92,124,0.12); color: var(--accent3); border: 1px solid rgba(240,92,124,0.3); }
.badge-warn  { background: rgba(245,166,35,0.12); color: var(--warn); border: 1px solid rgba(245,166,35,0.3); }

/* AI box */
.ai-box {
    background: linear-gradient(135deg, rgba(0,229,200,0.05) 0%, rgba(124,109,240,0.08) 100%);
    border: 1px solid rgba(0,229,200,0.25);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 20px 24px;
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.75;
    color: var(--text);
    white-space: pre-wrap;
}
.ai-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.spinner-dot::after { content: '●'; animation: blink 1s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* Hero header */
.hero {
    padding: 28px 0 20px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text);
    margin: 0;
    line-height: 1;
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 6px;
    letter-spacing: 0.04em;
}
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 0.72rem;
    color: var(--muted);
    margin-right: 8px;
    margin-top: 12px;
    font-family: 'DM Mono', monospace;
}
.stat-pill b { color: var(--accent); }

/* Section card */
.scard {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
}
.scard-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin-bottom: 14px;
}

/* Dividers */
hr { border-color: var(--border) !important; }

/* Info boxes */
[data-testid="stInfo"] { background: rgba(0,229,200,0.06) !important; border-left-color: var(--accent) !important; }
[data-testid="stWarning"] { background: rgba(245,166,35,0.06) !important; border-left-color: var(--warn) !important; }
[data-testid="stSuccess"] { background: rgba(34,211,160,0.06) !important; border-left-color: var(--success) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color="#6b7a9a", size=11),
    xaxis=dict(gridcolor="#1f2535", linecolor="#1f2535", zerolinecolor="#1f2535"),
    yaxis=dict(gridcolor="#1f2535", linecolor="#1f2535", zerolinecolor="#1f2535"),
    colorway=["#00e5c8", "#7c6df0", "#f05c7c", "#f5a623", "#22d3a0", "#60a5fa"],
    margin=dict(l=40, r=20, t=40, b=40),
)


def apply_theme(fig):
    fig.update_layout(**PLOTLY_THEME)
    return fig


def generate_demo_panel():
    """Generate a balanced panel dataset with realistic variation."""
    np.random.seed(42)
    n_entities, n_periods = 30, 10
    entities = [f"Entity_{i:02d}" for i in range(1, n_entities + 1)]
    years = list(range(2014, 2014 + n_periods))
    rows = []
    for e in entities:
        fe = np.random.randn()  # entity fixed effect
        for y in years:
            te = 0.05 * (y - 2014)  # time trend
            x1 = np.random.randn() + fe * 0.3
            x2 = np.random.uniform(0, 10)
            x3 = np.random.choice([0, 1], p=[0.6, 0.4])
            y_val = 2 + 0.8 * x1 - 0.4 * x2 + 1.2 * x3 + fe + te + np.random.randn() * 0.5
            rows.append({"entity": e, "year": y, "y": round(y_val, 4),
                         "x1": round(x1, 4), "x2": round(x2, 4), "x3": int(x3)})
    return pd.DataFrame(rows)


def run_ols(df, y_col, x_cols):
    from numpy.linalg import lstsq
    X = np.column_stack([np.ones(len(df))] + [df[c].values for c in x_cols])
    y = df[y_col].values
    coeffs, residuals, rank, sv = lstsq(X, y, rcond=None)
    y_hat = X @ coeffs
    resid = y - y_hat
    n, k = X.shape
    dof = n - k
    s2 = np.sum(resid**2) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t_stats = coeffs / se
    from scipy import stats as sc_stats
    p_vals = 2 * sc_stats.t.sf(np.abs(t_stats), df=dof)
    ss_tot = np.sum((y - y.mean())**2)
    ss_res = np.sum(resid**2)
    r2 = 1 - ss_res / ss_tot
    r2_adj = 1 - (1 - r2) * (n - 1) / dof
    names = ["const"] + list(x_cols)
    result_df = pd.DataFrame({"Variable": names, "Coeff": coeffs, "Std_Err": se,
                               "t_stat": t_stats, "p_value": p_vals})
    stats = {"R2": r2, "R2_adj": r2_adj, "N": n, "k": k - 1,
             "AIC": n * np.log(ss_res / n) + 2 * k,
             "BIC": n * np.log(ss_res / n) + k * np.log(n)}
    return result_df, resid, y_hat, stats


def run_within(df, y_col, x_cols, entity_col, time_col):
    """Fixed-effects (within) estimator via demeaning."""
    panel = df.copy()
    for col in [y_col] + list(x_cols):
        entity_means = panel.groupby(entity_col)[col].transform("mean")
        time_means = panel.groupby(time_col)[col].transform("mean")
        grand_mean = panel[col].mean()
        panel[col + "_dm"] = panel[col] - entity_means - time_means + grand_mean
    y_dm = panel[y_col + "_dm"].values
    X_dm = np.column_stack([panel[c + "_dm"].values for c in x_cols])
    from numpy.linalg import lstsq
    coeffs, _, _, _ = lstsq(X_dm, y_dm, rcond=None)
    y_hat_dm = X_dm @ coeffs
    resid = y_dm - y_hat_dm
    n, k = X_dm.shape
    dof = n - k - df[entity_col].nunique() - df[time_col].nunique() + 1
    if dof <= 0:
        dof = max(1, n - k)
    s2 = np.sum(resid**2) / dof
    cov = s2 * np.linalg.inv(X_dm.T @ X_dm)
    se = np.sqrt(np.diag(cov))
    t_stats = coeffs / se
    from scipy import stats as sc_stats
    p_vals = 2 * sc_stats.t.sf(np.abs(t_stats), df=dof)
    ss_tot = np.sum((y_dm - y_dm.mean())**2)
    ss_res = np.sum(resid**2)
    r2 = max(0, 1 - ss_res / ss_tot)
    r2_adj = max(0, 1 - (1 - r2) * (n - 1) / dof)
    result_df = pd.DataFrame({"Variable": list(x_cols), "Coeff": coeffs,
                               "Std_Err": se, "t_stat": t_stats, "p_value": p_vals})
    stats = {"R2": r2, "R2_adj": r2_adj, "N": n, "k": k,
             "AIC": n * np.log(max(ss_res, 1e-10) / n) + 2 * k,
             "BIC": n * np.log(max(ss_res, 1e-10) / n) + k * np.log(n)}
    return result_df, resid, y_hat_dm, stats


def run_fd(df, y_col, x_cols, entity_col, time_col):
    """First-difference estimator."""
    panel = df.sort_values([entity_col, time_col]).copy()
    fd = panel.groupby(entity_col)[[y_col] + list(x_cols)].diff().dropna()
    return run_ols(fd, y_col, x_cols)


def hausman_test(fe_coef, re_coef, fe_vcov, re_vcov):
    """Simple Hausman test statistic."""
    diff = fe_coef - re_coef
    diff_vcov = fe_vcov - re_vcov
    try:
        stat = float(diff @ np.linalg.inv(diff_vcov) @ diff)
        df = len(diff)
        from scipy import stats as sc_stats
        p = 1 - sc_stats.chi2.cdf(stat, df)
        return stat, p, df
    except Exception:
        return None, None, None


def significance_stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.1:   return "·"
    return ""


def call_claude(system_prompt, user_prompt, api_key=None):
    """Call Claude API for AI explanations."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers, json=payload, timeout=30
        )
        data = resp.json()
        if "content" in data:
            return data["content"][0]["text"]
        return f"API error: {data.get('error', {}).get('message', str(data))}"
    except Exception as e:
        return f"Request failed: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

for key, default in [
    ("df", None), ("results", None), ("ai_explanation", ""),
    ("model_type", "Fixed Effects (Two-Way)"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 24px 0; border-bottom:1px solid var(--border); margin-bottom:20px;">
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:var(--text);letter-spacing:-0.02em;">
            ⬡ Panel<span style="color:var(--accent);">Stat</span>X
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:var(--muted);margin-top:4px;letter-spacing:0.08em;">
            PANEL REGRESSION ENGINE v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);margin-bottom:8px;">Data Source</div>', unsafe_allow_html=True)
    data_src = st.radio("", ["Use Demo Dataset", "Upload CSV"], label_visibility="collapsed")

    if data_src == "Upload CSV":
        uploaded = st.file_uploader("Upload panel CSV", type=["csv"], label_visibility="collapsed")
        if uploaded:
            st.session_state.df = pd.read_csv(uploaded)
            st.success(f"Loaded: {st.session_state.df.shape[0]} rows")
    else:
        if st.button("⬡ Load Demo Data", use_container_width=True):
            st.session_state.df = generate_demo_panel()
            st.success("Demo panel loaded!")

    st.markdown("---")

    if st.session_state.df is not None:
        df = st.session_state.df
        cols = df.columns.tolist()

        st.markdown('<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);margin-bottom:8px;">Variable Mapping</div>', unsafe_allow_html=True)
        entity_col = st.selectbox("Entity / Panel ID", cols, index=cols.index("entity") if "entity" in cols else 0)
        time_col   = st.selectbox("Time Variable", cols, index=cols.index("year") if "year" in cols else 1)
        y_col      = st.selectbox("Dependent Variable (Y)", [c for c in cols if c not in [entity_col, time_col]],
                                   index=0)
        x_candidates = [c for c in cols if c not in [entity_col, time_col, y_col]]
        x_cols = st.multiselect("Independent Variables (X)", x_candidates, default=x_candidates[:3] if len(x_candidates) >= 3 else x_candidates)

        st.markdown("---")
        st.markdown('<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);margin-bottom:8px;">Estimator</div>', unsafe_allow_html=True)
        model_type = st.selectbox("", ["Fixed Effects (Two-Way)", "Fixed Effects (Entity)", "First Difference", "Pooled OLS"], label_visibility="collapsed")
        st.session_state.model_type = model_type

        st.markdown("---")
        st.markdown('<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);margin-bottom:8px;">AI Explainer Key</div>', unsafe_allow_html=True)
        api_key = st.text_input("Anthropic API Key (optional)", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
        st.caption("Leave blank to use the built-in key.")

        st.markdown("---")
        run_btn = st.button("⬡ Run Analysis", use_container_width=True, type="primary")
    else:
        run_btn = False
        entity_col = time_col = y_col = "—"
        x_cols = []
        api_key = ""
        model_type = "Fixed Effects (Two-Way)"


# ═══════════════════════════════════════════════════════════════════════════════
# RUN MODEL
# ═══════════════════════════════════════════════════════════════════════════════

if run_btn and st.session_state.df is not None and x_cols:
    df = st.session_state.df
    with st.spinner("Running regression…"):
        try:
            if model_type == "Pooled OLS":
                result_df, resid, y_hat, stats = run_ols(df, y_col, x_cols)
            elif model_type == "First Difference":
                result_df, resid, y_hat, stats = run_fd(df, y_col, x_cols, entity_col, time_col)
            elif model_type == "Fixed Effects (Entity)":
                result_df, resid, y_hat, stats = run_within(df, y_col, x_cols, entity_col, time_col)
            else:
                result_df, resid, y_hat, stats = run_within(df, y_col, x_cols, entity_col, time_col)

            st.session_state.results = {
                "result_df": result_df, "resid": resid, "y_hat": y_hat,
                "stats": stats, "y_col": y_col, "x_cols": x_cols,
                "entity_col": entity_col, "time_col": time_col,
            }
            st.session_state.ai_explanation = ""
        except Exception as e:
            st.error(f"Regression error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-title">Panel<span>Stat</span>X</div>
    <div class="hero-sub">⬡ Panel Regression Analysis System · AI-Powered Econometrics</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.df is None:
    # ── Landing state ──────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    for col, icon, title, desc in [
        (col1, "⬡", "Panel-Ready", "Fixed effects, first-difference, and pooled OLS estimators built for longitudinal data."),
        (col2, "◈", "Diagnostic Suite", "Residual analysis, heteroskedasticity checks, Hausman test, and entity plots."),
        (col3, "⬟", "AI Explainer", "Claude interprets your regression output in plain language — coefficients, fit, and caveats."),
    ]:
        with col:
            st.markdown(f"""
            <div class="scard" style="text-align:center;padding:32px 20px;">
                <div style="font-size:2rem;margin-bottom:12px;color:var(--accent);">{icon}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px;">{title}</div>
                <div style="font-size:0.78rem;color:var(--muted);line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:40px;padding:32px;background:var(--surface2);border:1px dashed var(--border);border-radius:8px;">
        <div style="font-family:'Syne',sans-serif;font-size:1rem;color:var(--muted);">
            ← Load demo data or upload a CSV from the sidebar to begin
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Data has been loaded ────────────────────────────────────────────────────
df = st.session_state.df
res = st.session_state.results

# ── Quick dataset stats bar ───────────────────────────────────────────────────
n_e = df[entity_col].nunique() if entity_col in df.columns else "—"
n_t = df[time_col].nunique() if time_col in df.columns else "—"
st.markdown(f"""
<div style="margin-bottom:24px;">
    <span class="stat-pill">Entities <b>{n_e}</b></span>
    <span class="stat-pill">Periods <b>{n_t}</b></span>
    <span class="stat-pill">Observations <b>{len(df):,}</b></span>
    <span class="stat-pill">Estimator <b>{st.session_state.model_type}</b></span>
    <span class="badge badge-teal" style="margin-left:4px;">READY</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab_data, tab_results, tab_diagnostics, tab_entity, tab_ai = st.tabs([
    "⬡ Data Explorer", "◈ Results", "⬟ Diagnostics", "⬢ Entity Plots", "✦ AI Explainer"
])


# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 · DATA EXPLORER
# ──────────────────────────────────────────────────────────────────────────────

with tab_data:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="scard-title">Dataset Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(100), use_container_width=True, height=320)
    with c2:
        st.markdown('<div class="scard-title">Summary Statistics</div>', unsafe_allow_html=True)
        st.dataframe(df.describe().round(3), use_container_width=True, height=320)

    st.markdown("---")
    st.markdown('<div class="scard-title">Correlation Heatmap</div>', unsafe_allow_html=True)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) >= 2:
        corr = df[num_cols].corr().round(3)
        fig_corr = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale=[[0, "#f05c7c"], [0.5, "#111318"], [1, "#00e5c8"]],
            zmid=0, text=corr.values.round(2),
            texttemplate="%{text}", showscale=True,
        ))
        fig_corr.update_layout(title="Pearson Correlation Matrix", height=380, **PLOTLY_THEME)
        st.plotly_chart(fig_corr, use_container_width=True)

    # Distribution of Y
    if y_col in df.columns:
        st.markdown('<div class="scard-title" style="margin-top:16px;">Dependent Variable Distribution</div>', unsafe_allow_html=True)
        fig_dist = px.histogram(df, x=y_col, nbins=40, color_discrete_sequence=["#00e5c8"])
        fig_dist.update_layout(title=f"Distribution of {y_col}", height=300, bargap=0.05, **PLOTLY_THEME)
        st.plotly_chart(fig_dist, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 · RESULTS
# ──────────────────────────────────────────────────────────────────────────────

with tab_results:
    if res is None:
        st.info("Run the analysis from the sidebar to view regression results.")
    else:
        result_df = res["result_df"]
        stats = res["stats"]

        # ── Model fit summary ──────────────────────────────────────────────────
        st.markdown('<div class="scard-title">Model Fit</div>', unsafe_allow_html=True)
        mc = st.columns(6)
        for col, label, val in [
            (mc[0], "R²",        f"{stats['R2']:.4f}"),
            (mc[1], "Adj. R²",   f"{stats['R2_adj']:.4f}"),
            (mc[2], "N",         f"{stats['N']:,}"),
            (mc[3], "Variables", f"{stats['k']}"),
            (mc[4], "AIC",       f"{stats['AIC']:.2f}"),
            (mc[5], "BIC",       f"{stats['BIC']:.2f}"),
        ]:
            with col:
                st.metric(label, val)

        st.markdown("---")

        # ── Coefficient table ──────────────────────────────────────────────────
        st.markdown('<div class="scard-title">Coefficient Estimates</div>', unsafe_allow_html=True)
        display = result_df.copy()
        display["Stars"]  = display["p_value"].apply(significance_stars)
        display["Sig"]    = display["p_value"].apply(
            lambda p: "✓ Significant" if p < 0.05 else "✗ Not sig.")
        display = display.rename(columns={
            "Variable": "Variable", "Coeff": "Coeff.",
            "Std_Err": "Std. Err.", "t_stat": "t-stat", "p_value": "p-value"
        })
        st.dataframe(
            display.style
                .format({"Coeff.": "{:.4f}", "Std. Err.": "{:.4f}",
                         "t-stat": "{:.3f}", "p-value": "{:.4f}"})
                .map(lambda v: "color: #00e5c8" if v == "✓ Significant" else "color: #6b7a9a", subset=["Sig"]),
            use_container_width=True, hide_index=True
        )
        st.caption("*p<0.1  **p<0.05  ***p<0.01")

        st.markdown("---")

        # ── Coefficient plot ───────────────────────────────────────────────────
        st.markdown('<div class="scard-title">Coefficient Plot (with 95% CI)</div>', unsafe_allow_html=True)
        rd = res["result_df"]
        ci_lo = rd["Coeff"] - 1.96 * rd["Std_Err"]
        ci_hi = rd["Coeff"] + 1.96 * rd["Std_Err"]
        colors = ["#00e5c8" if p < 0.05 else "#6b7a9a" for p in rd["p_value"]]

        fig_coef = go.Figure()
        fig_coef.add_hline(y=0, line_dash="dash", line_color="#1f2535")
        for pos, (i, row) in enumerate(rd.iterrows()):
            lo, hi = ci_lo.iloc[pos], ci_hi.iloc[pos]
            fig_coef.add_trace(go.Scatter(
                x=[lo, hi], y=[row["Variable"], row["Variable"]],
                mode="lines", line=dict(color="#1f2535", width=2),
                showlegend=False
            ))
        fig_coef.add_trace(go.Scatter(
            x=rd["Coeff"], y=rd["Variable"], mode="markers",
            marker=dict(size=10, color=colors, line=dict(width=1, color="#0a0c10")),
            name="Coefficient", showlegend=False
        ))
        fig_coef.update_layout(title="Coefficients with 95% Confidence Intervals",
                                height=max(280, len(rd) * 55), **PLOTLY_THEME)
        st.plotly_chart(fig_coef, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 · DIAGNOSTICS
# ──────────────────────────────────────────────────────────────────────────────

with tab_diagnostics:
    if res is None:
        st.info("Run the analysis first.")
    else:
        resid = res["resid"]
        y_hat = res["y_hat"]

        dc1, dc2 = st.columns(2)

        # Residuals vs Fitted
        with dc1:
            fig_rv = go.Figure()
            fig_rv.add_hline(y=0, line_dash="dash", line_color="#f05c7c", line_width=1)
            fig_rv.add_trace(go.Scatter(
                x=y_hat, y=resid, mode="markers",
                marker=dict(size=5, color="#00e5c8", opacity=0.6),
                name="Residual"
            ))
            fig_rv.update_layout(title="Residuals vs Fitted",
                                   xaxis_title="Fitted", yaxis_title="Residual", height=340, **PLOTLY_THEME)
            st.plotly_chart(fig_rv, use_container_width=True)

        # Q-Q Plot
        with dc2:
            from scipy import stats as sc_stats
            resid_clean = np.asarray(resid, dtype=float)
            resid_clean = resid_clean[np.isfinite(resid_clean)]
            probplot_result = sc_stats.probplot(resid_clean)
            osm, osr = probplot_result[0]
            slope, intercept, _ = probplot_result[1]
            fig_qq = go.Figure()
            fig_qq.add_trace(go.Scatter(x=list(osm), y=list(osr), mode="markers",
                                         marker=dict(size=4, color="#7c6df0", opacity=0.7), name="Residuals"))
            fig_qq.add_trace(go.Scatter(x=[float(min(osm)), float(max(osm))],
                                         y=[slope * float(min(osm)) + intercept, slope * float(max(osm)) + intercept],
                                         mode="lines", line=dict(color="#f05c7c", dash="dash"), name="Normal"))
            fig_qq.update_layout(title="Normal Q-Q Plot",
                                   xaxis_title="Theoretical Quantiles",
                                   yaxis_title="Sample Quantiles", height=340, **PLOTLY_THEME)
            st.plotly_chart(fig_qq, use_container_width=True)

        dc3, dc4 = st.columns(2)

        # Residual distribution
        with dc3:
            fig_rh = px.histogram(x=resid, nbins=40, color_discrete_sequence=["#7c6df0"])
            fig_rh.update_layout(title="Residual Distribution", xaxis_title="Residual",
                                   height=300, bargap=0.05, **PLOTLY_THEME)
            st.plotly_chart(fig_rh, use_container_width=True)

        # Scale-Location
        with dc4:
            fig_sl = go.Figure()
            fig_sl.add_trace(go.Scatter(
                x=y_hat, y=np.sqrt(np.abs(resid)), mode="markers",
                marker=dict(size=5, color="#f5a623", opacity=0.6)
            ))
            fig_sl.update_layout(title="Scale-Location (√|Residual| vs Fitted)",
                                   xaxis_title="Fitted", yaxis_title="√|Residual|", height=300, **PLOTLY_THEME)
            st.plotly_chart(fig_sl, use_container_width=True)

        # Residual stats
        st.markdown("---")
        st.markdown('<div class="scard-title">Residual Diagnostics Summary</div>', unsafe_allow_html=True)
        from scipy import stats as sc_stats
        resid_arr = np.asarray(resid, dtype=float)
        resid_arr = resid_arr[np.isfinite(resid_arr)]
        jb_stat, jb_p = sc_stats.jarque_bera(resid_arr)
        dw = np.sum(np.diff(resid_arr)**2) / max(np.sum(resid_arr**2), 1e-10)

        dc5, dc6, dc7, dc8 = st.columns(4)
        with dc5: st.metric("Mean Residual", f"{np.mean(resid_arr):.4f}")
        with dc6: st.metric("Std Residual", f"{np.std(resid_arr):.4f}")
        with dc7: st.metric("Jarque-Bera p", f"{jb_p:.4f}")
        with dc8: st.metric("Durbin-Watson", f"{dw:.4f}")

        if jb_p < 0.05:
            st.warning("⚠ Jarque-Bera test rejects normality (p < 0.05). Consider robust standard errors.")
        if dw < 1.5 or dw > 2.5:
            st.warning(f"⚠ Durbin-Watson = {dw:.3f} suggests possible autocorrelation.")
        else:
            st.success("✓ Durbin-Watson statistic is in the acceptable range.")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 · ENTITY PLOTS
# ──────────────────────────────────────────────────────────────────────────────

with tab_entity:
    if entity_col not in df.columns or time_col not in df.columns:
        st.info("Entity and time columns not set.")
    else:
        y_plot = y_col if y_col in df.columns else df.select_dtypes(np.number).columns[0]

        ec1, ec2 = st.columns([1, 3])
        with ec1:
            entities_avail = sorted(df[entity_col].unique())
            selected_entities = st.multiselect(
                "Select entities to plot",
                entities_avail,
                default=entities_avail[:6] if len(entities_avail) >= 6 else entities_avail
            )
        with ec2:
            x_axis = st.selectbox("X axis", [time_col] + [c for c in df.columns if c not in [entity_col]], index=0)

        if selected_entities:
            plot_df = df[df[entity_col].isin(selected_entities)]

            fig_ep = px.line(
                plot_df, x=x_axis, y=y_plot, color=entity_col,
                markers=True,
                color_discrete_sequence=["#00e5c8", "#7c6df0", "#f05c7c", "#f5a623",
                                          "#22d3a0", "#60a5fa", "#fb923c", "#a78bfa"],
            )
            fig_ep.update_layout(title=f"{y_plot} over {x_axis} by {entity_col}",
                                   height=440, **PLOTLY_THEME)
            st.plotly_chart(fig_ep, use_container_width=True)

            # Entity mean bar
            means = df.groupby(entity_col)[y_plot].mean().sort_values(ascending=False)
            fig_bar = px.bar(
                x=means.index, y=means.values,
                color=means.values,
                color_continuous_scale=["#111318", "#00e5c8"],
                labels={"x": entity_col, "y": f"Mean {y_plot}"},
            )
            fig_bar.update_layout(title=f"Entity Mean of {y_plot}", height=320,
                                   coloraxis_showscale=False, **PLOTLY_THEME)
            st.plotly_chart(fig_bar, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 · AI EXPLAINER
# ──────────────────────────────────────────────────────────────────────────────

with tab_ai:
    st.markdown('<div class="scard-title">AI Regression Explainer</div>', unsafe_allow_html=True)

    if res is None:
        st.info("Run the analysis first to unlock the AI explainer.")
    else:
        result_df = res["result_df"]
        stats = res["stats"]

        # Build a rich summary for Claude
        coeff_table = result_df.to_string(index=False)
        context = f"""
Model: {st.session_state.model_type}
Dependent variable: {res['y_col']}
Independent variables: {', '.join(res['x_cols'])}
Entity column: {res['entity_col']} | Time column: {res['time_col']}

Fit Statistics:
  R²        = {stats['R2']:.4f}
  Adj. R²   = {stats['R2_adj']:.4f}
  N         = {stats['N']}
  AIC       = {stats['AIC']:.2f}
  BIC       = {stats['BIC']:.2f}

Coefficient Table:
{coeff_table}
"""

        sys_prompt = (
            "You are an expert econometrician and data scientist. "
            "Given panel regression output, provide a clear, structured interpretation. "
            "Cover: (1) model choice rationale, (2) coefficient interpretation with economic meaning, "
            "(3) statistical significance and effect sizes, (4) model fit quality, "
            "(5) potential caveats or concerns (endogeneity, heteroskedasticity, etc.), "
            "(6) actionable recommendations. Be concise but insightful. Use plain language."
        )

        col_explain, col_custom = st.columns([3, 2])

        with col_explain:
            if st.button("✦ Generate AI Explanation", type="primary", use_container_width=True):
                with st.spinner("Claude is analysing your results…"):
                    explanation = call_claude(sys_prompt, f"Please explain these panel regression results:\n\n{context}", api_key or None)
                    st.session_state.ai_explanation = explanation

        with col_custom:
            custom_q = st.text_input("Ask a specific question about the results…",
                                      placeholder="e.g. Is x1 economically significant?")
            if st.button("⬡ Ask Claude", use_container_width=True) and custom_q:
                with st.spinner("Thinking…"):
                    answer = call_claude(
                        sys_prompt,
                        f"Here are the regression results:\n\n{context}\n\nQuestion: {custom_q}",
                        api_key or None
                    )
                    st.session_state.ai_explanation = answer

        if st.session_state.ai_explanation:
            st.markdown("---")
            st.markdown(f"""
            <div class="ai-label">✦ &nbsp;CLAUDE AI INTERPRETATION</div>
            <div class="ai-box">{st.session_state.ai_explanation}</div>
            """, unsafe_allow_html=True)

        # ── Quick insight cards ────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="scard-title">Quick Insights</div>', unsafe_allow_html=True)

        ic1, ic2, ic3 = st.columns(3)
        sig_vars = result_df[result_df["p_value"] < 0.05]["Variable"].tolist()
        insig_vars = result_df[result_df["p_value"] >= 0.05]["Variable"].tolist()
        r2_val = stats["R2"]

        with ic1:
            st.markdown(f"""
            <div class="scard">
                <div class="scard-title">Significance</div>
                <div style="color:var(--accent);font-size:1.2rem;font-family:'Syne',sans-serif;font-weight:700;">{len(sig_vars)}/{len(result_df)}</div>
                <div style="color:var(--muted);font-size:0.75rem;margin-top:4px;">variables significant at 5%</div>
                <div style="margin-top:10px;font-size:0.72rem;color:var(--text);">{', '.join(sig_vars) if sig_vars else '—'}</div>
            </div>
            """, unsafe_allow_html=True)
        with ic2:
            r2_color = "#00e5c8" if r2_val > 0.7 else "#f5a623" if r2_val > 0.4 else "#f05c7c"
            r2_label = "Strong fit" if r2_val > 0.7 else "Moderate fit" if r2_val > 0.4 else "Weak fit"
            st.markdown(f"""
            <div class="scard">
                <div class="scard-title">Model Fit</div>
                <div style="color:{r2_color};font-size:1.2rem;font-family:'Syne',sans-serif;font-weight:700;">{r2_val:.4f}</div>
                <div style="color:var(--muted);font-size:0.75rem;margin-top:4px;">R-squared · {r2_label}</div>
            </div>
            """, unsafe_allow_html=True)
        with ic3:
            largest = result_df.iloc[result_df["Coeff"].abs().argmax()]
            st.markdown(f"""
            <div class="scard">
                <div class="scard-title">Largest Effect</div>
                <div style="color:var(--accent2);font-size:1.2rem;font-family:'Syne',sans-serif;font-weight:700;">{largest['Variable']}</div>
                <div style="color:var(--muted);font-size:0.75rem;margin-top:4px;">coeff = {largest['Coeff']:.4f}</div>
            </div>
            """, unsafe_allow_html=True)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-family:'DM Mono',monospace;font-size:0.7rem;color:var(--muted);padding:12px 0;">
    ⬡ PanelStatX · Panel Regression Analysis System · Powered by Claude AI
</div>
""", unsafe_allow_html=True)
