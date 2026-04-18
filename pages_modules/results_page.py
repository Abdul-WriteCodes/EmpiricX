import streamlit as st
import pandas as pd
from collections import Counter


DISPLAY_COLS = [
    ("author_year",            "Author & Year"),
    ("research_context",       "Research Context"),
    ("methodology",            "Methodology"),
    ("independent_variables",  "IVs"),
    ("dependent_variable",     "DV"),
    ("findings",               "Key Findings"),
    ("strengths",              "Strengths"),
    ("limitations",            "Limitations"),
]


def render():
    papers = st.session_state.get("extracted_papers", [])

    # ── Page header ────────────────────────────────────────────
    st.markdown("""
    <div class="ph-wrap anim-up">
        <div class="ph-eye">Step 01 · Analyse</div>
        <h1 class="ph-title">Extraction <span>Results</span></h1>
        <p class="ph-sub">
            Structured empirical data extracted from each paper.
            Inspect the full table or drill into any paper for detail.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Empty state ────────────────────────────────────────────
    if not papers:
        st.markdown("""
        <div class="empty-st">
            <div class="empty-st-icon">📭</div>
            <div class="empty-st-title">No papers extracted yet</div>
            <div class="empty-st-desc">
                Upload papers using the sidebar, then click
                <strong>⚡ Extract</strong> to begin.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Metrics ────────────────────────────────────────────────
    methods     = [p.get("methodology","") for p in papers if p.get("methodology")]
    method_cnt  = Counter(methods)
    top_method  = method_cnt.most_common(1)[0][0][:22] if method_cnt else "—"
    n_unique_m  = len(set(methods))

    st.markdown(f"""
    <div class="m-row anim-up anim-up-d1">
        <div class="m-chip">
            <div class="m-val">{len(papers)}</div>
            <div class="m-lbl">Papers</div>
        </div>
        <div class="m-chip">
            <div class="m-val">{n_unique_m}</div>
            <div class="m-lbl">Methods</div>
        </div>
        <div class="m-chip">
            <div class="m-val" style="font-size:1rem;padding-top:6px">{top_method}</div>
            <div class="m-lbl">Top Method</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["TABLE VIEW", "PAPER DETAIL"])

    with tab1:
        _render_table(papers)

    with tab2:
        _render_detail(papers)

    # ── CTA ─────────────────────────────────────────────────────
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔗  Run Cross-Paper Synthesis →", type="primary", use_container_width=True):
            st.session_state["page"] = "synthesis"
            st.rerun()
    with c2:
        if st.button("📥  Export Data →", use_container_width=True):
            st.session_state["page"] = "export"
            st.rerun()


def _render_table(papers):
    rows = [{label: p.get(key, "—") for key, label in DISPLAY_COLS} for p in papers]
    df   = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        height=min(620, 90 + 65 * len(papers)),
        column_config={
            "Author & Year":  st.column_config.TextColumn(width="small"),
            "Research Context": st.column_config.TextColumn(width="medium"),
            "Methodology":    st.column_config.TextColumn(width="small"),
            "IVs":            st.column_config.TextColumn(width="medium"),
            "DV":             st.column_config.TextColumn(width="small"),
            "Key Findings":   st.column_config.TextColumn(width="large"),
            "Strengths":      st.column_config.TextColumn(width="medium"),
            "Limitations":    st.column_config.TextColumn(width="medium"),
        },
        hide_index=True,
    )


def _render_detail(papers):
    options = [
        f"{i+1}. {p.get('author_year','Unknown')} — {p.get('_source_file','')}"
        for i, p in enumerate(papers)
    ]
    idx = st.selectbox("Select paper", range(len(options)),
                        format_func=lambda i: options[i],
                        label_visibility="collapsed")
    p = papers[idx]

    st.markdown(f"""
    <div class="x-card x-card-gold" style="margin-bottom:1.25rem">
        <div class="ph-eye">{p.get("author_year","")}</div>
        <div style="font-family:var(--font-d);font-size:1.25rem;color:var(--text-1);margin-bottom:6px">
            {p.get("title","Untitled")}
        </div>
        <div style="font-family:var(--font-m);font-size:0.7rem;color:var(--text-3)">
            {p.get("_source_file","")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    left  = ["research_context","methodology","independent_variables","dependent_variable","control_variables"]
    right = ["findings","theoretical_contributions","practical_contributions","strengths","limitations"]
    labels = {
        "research_context": "📍 Research Context",
        "methodology": "⚙️ Methodology",
        "independent_variables": "📌 Independent Variables",
        "dependent_variable": "🎯 Dependent Variable",
        "control_variables": "🔧 Control Variables",
        "findings": "📊 Key Findings",
        "theoretical_contributions": "💡 Theoretical Contributions",
        "practical_contributions": "🏭 Practical Contributions",
        "strengths": "✅ Strengths",
        "limitations": "⚠️ Limitations",
    }

    with c1:
        for k in left:
            _dblock(labels[k], p.get(k, "—"))
    with c2:
        for k in right:
            _dblock(labels[k], p.get(k, "—"))

    with st.expander("📚  Citations"):
        for fmt, key in [("APA 7","citation_apa"),("MLA 9","citation_mla"),("Harvard","citation_harvard")]:
            st.markdown(f"**{fmt}**")
            st.code(p.get(key,"Not available"), language=None)


def _dblock(label, content):
    st.markdown(f"""
    <div class="detail-block">
        <div class="detail-lbl">{label}</div>
        <div class="detail-val">{content}</div>
    </div>
    """, unsafe_allow_html=True)
