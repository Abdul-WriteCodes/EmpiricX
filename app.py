import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="EmpiricX — Research Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load CSS ──────────────────────────────────────────────────────
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from utils.session import init_session
init_session()

# ── Read API key from Streamlit secrets (cloud) or env ────────────
def _load_api_key():
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
        if key:
            os.environ["OPENAI_API_KEY"] = key
            return True
    except Exception:
        pass
    if os.environ.get("OPENAI_API_KEY"):
        return True
    return False

_load_api_key()

# ── Password gate ─────────────────────────────────────────────────
def _check_password() -> bool:
    try:
        correct = st.secrets.get("APP_PASSWORD", "empiricx2024")
    except Exception:
        correct = "empiricx2024"

    if st.session_state.get("authenticated"):
        return True

    # ── Landing / gate page ────────────────────────────────────
    # Animated background
    st.markdown('<div class="gate-bg"></div>', unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.6, 1])
    with col_c:
        st.markdown('<div class="gate-card">', unsafe_allow_html=True)

        # Gem + logo
        #st.markdown('<div class="gate-gem"></div>', unsafe_allow_html=True)
        st.markdown('<div class="gate-logo">Empiri<span>X</span></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="gate-sub">Research Intelligence Engine</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="gate-pill">🔬 AI-Powered · Empirical · Synthesis</div>',
            unsafe_allow_html=True,
        )

        # Feature highlights
        st.markdown("""
        <div class="gate-features">
            <div class="gate-feat"><div class="gate-feat-dot"></div>Extract structured empirical data from any research paper</div>
            <div class="gate-feat"><div class="gate-feat-dot"></div>Cross-paper synthesis — gaps, conflicts & patterns</div>
            <div class="gate-feat"><div class="gate-feat-dot"></div>Export-ready: CSV, Excel & Word synthesis report</div>
        </div>
        """, unsafe_allow_html=True)

        # Error placeholder
        err_slot = st.empty()

        # Password input
        pwd = st.text_input(
            "Access Password",
            type="password",
            placeholder="Enter your access password",
            key="pwd_input",
        )

        enter = st.button("Enter Platform →", width='stretch')

        if enter or (pwd and pwd == correct):
            if pwd == correct:
                st.session_state["authenticated"] = True
                st.rerun()
            elif pwd:
                err_slot.markdown(
                    '<div class="gate-error">⚠️  Incorrect password. Please try again.</div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<div class="gate-footer">Access restricted · <strong>EmpiricX</strong> v1.0</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    return False


if not _check_password():
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# AUTHENTICATED APP
# ═══════════════════════════════════════════════════════════════════
from pages_modules import upload_page, results_page, synthesis_page, export_page
from utils.parser import format_file_size

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:

    # Brand
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-gem"></div>
        <span class="sb-name">EmpiricX</span>
    </div>
    <div class="sb-tag">Research Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # ── Upload section ─────────────────────────────────────────
    st.markdown('<span class="sb-label">Upload Papers</span>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader(
    "",                          # ← empty string, not "Drop files"
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    key="sidebar_uploader",
)
    

    # Queue new uploads into session
    if uploaded:
        queued = st.session_state.get("queued_files", [])
        existing_names = {f["name"] for f in queued}
        for f in uploaded:
            if f.name not in existing_names:
                queued.append({"name": f.name, "size": f.size, "obj": f})
                existing_names.add(f.name)
        st.session_state["queued_files"] = queued

    # Show queued / extracted files
    queued = st.session_state.get("queued_files", [])
    extracted = st.session_state.get("extracted_papers", [])
    extracted_names = {p.get("_source_file") for p in extracted}

    if queued:
        st.markdown('<div style="margin-top:10px"></div>', unsafe_allow_html=True)
        for finfo in queued:
            status_cls = "sb-badge-ok" if finfo["name"] in extracted_names else "sb-badge-new"
            status_txt = "Done" if finfo["name"] in extracted_names else "Queued"
            st.markdown(f"""
            <div class="sb-paper">
                <span class="sb-paper-icon">📄</span>
                <div style="min-width:0;flex:1">
                    <div class="sb-paper-name">{finfo["name"]}</div>
                    <div class="sb-paper-meta">{format_file_size(finfo["size"])}</div>
                </div>
                <span class="sb-badge {status_cls}">{status_txt}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top:10px"></div>', unsafe_allow_html=True)

        # Extract button
        pending = [f for f in queued if f["name"] not in extracted_names]
        if pending:
            if st.button(f"⚡  Extract {len(pending)} paper(s)", use_container_width=True):
                st.session_state["trigger_extract"] = True
                st.session_state["page"] = "results"
                st.rerun()

        # Clear button
        if st.button("🗑  Clear all", use_container_width=True):
            st.session_state["queued_files"] = []
            st.session_state["extracted_papers"] = []
            st.session_state["synthesis_result"] = None
            st.rerun()

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # ── Navigation ─────────────────────────────────────────────
    st.markdown('<span class="sb-label">Navigation</span>', unsafe_allow_html=True)

    nav_map = {
        "📊  Results": "results",
        "🔗  Synthesis": "synthesis",
        "📥  Export": "export",
    }

    selected = st.radio(
        "nav",
        list(nav_map.keys()),
        index=list(nav_map.values()).index(
            st.session_state.get("page", "results")
            if st.session_state.get("page") in nav_map.values()
            else "results"
        ),
        label_visibility="collapsed",
        key="main_nav",
    )
    st.session_state["page"] = nav_map[selected]

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # ── Stats ───────────────────────────────────────────────────
    n_papers = len(st.session_state.get("extracted_papers", []))
    syn_done = "✓" if st.session_state.get("synthesis_result") else "—"
    st.markdown(f"""
    <div class="sb-stats">
        <div class="sb-stat">
            <div class="sb-stat-n">{n_papers}</div>
            <div class="sb-stat-l">Papers</div>
        </div>
        <div class="sb-stat">
            <div class="sb-stat-n">{syn_done}</div>
            <div class="sb-stat-l">Synthesis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Logout
    st.markdown('<div style="margin-top:auto; padding-top:1rem"></div>', unsafe_allow_html=True)
    if st.button("⎋  Sign out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

# ── Main content ───────────────────────────────────────────────────
page = st.session_state.get("page", "results")

# Handle extraction trigger from sidebar
if st.session_state.get("trigger_extract"):
    st.session_state["trigger_extract"] = False
    upload_page.run_extraction_from_queue()

if page == "results":
    results_page.render()
elif page == "synthesis":
    synthesis_page.render()
elif page == "export":
    export_page.render()
