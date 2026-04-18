import streamlit as st
from core.extractor import synthesize_papers


def render():
    papers    = st.session_state.get("extracted_papers", [])
    synthesis = st.session_state.get("synthesis_result")

    st.markdown("""
    <div class="ph-wrap anim-up">
        <div class="ph-eye">Step 02 · Synthesize</div>
        <h1 class="ph-title">Cross-Paper <span>Insights</span></h1>
        <p class="ph-sub">
            Patterns, conflicts, and gaps synthesized across your entire paper set —
            turning weeks of manual review into minutes of strategic insight.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not papers:
        st.markdown("""
        <div class="empty-st">
            <div class="empty-st-icon">🔗</div>
            <div class="empty-st-title">No papers loaded</div>
            <div class="empty-st-desc">Upload and extract at least 2 papers to run synthesis.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    if len(papers) < 2:
        st.warning("Add at least 2 papers for meaningful cross-paper synthesis.")
        return

    # ── Run bar ────────────────────────────────────────────────
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(
            f'<p style="color:var(--text-2);font-size:0.88rem;margin:0">'
            f'<strong style="color:var(--gold)">{len(papers)}</strong> papers ready for synthesis.</p>',
            unsafe_allow_html=True,
        )
    with c2:
        label = "🔗  Run" if not synthesis else "🔄  Re-run"
        run   = st.button(label, type="primary", use_container_width=True)

    if run:
        with st.spinner("Synthesizing across papers…"):
            try:
                result = synthesize_papers(papers)
                st.session_state["synthesis_result"] = result
                synthesis = result
            except Exception as e:
                st.error(f"Synthesis failed: {e}")
                return

    if not synthesis:
        st.markdown("---")
        st.markdown(
            '<p style="color:var(--text-3);font-size:0.88rem">Click <strong>Run</strong> above to generate cross-paper intelligence.</p>',
            unsafe_allow_html=True,
        )
        return

    _render(synthesis)


def _render(s):
    st.markdown("---")

    # Overall summary
    summary = s.get("overall_summary", "")
    if summary:
        st.markdown(f"""
        <div class="x-card x-card-gold anim-up" style="margin-bottom:1.5rem">
            <div class="detail-lbl">Overview</div>
            <div style="font-size:0.95rem;color:var(--text-2);line-height:1.7">{summary}</div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        _syn_block("📈 Common Findings",        s.get("common_findings",[]),      "dot-gold")
        _syn_block("⚙️ Methodology Patterns",    s.get("methodology_patterns",[]), "dot-blue")
        _syn_block("⚠️ Common Weaknesses",       s.get("common_weaknesses",[]),    "dot-red")

    with col2:
        _syn_block("⚡ Conflicting Results",      s.get("conflicting_results",[]),  "dot-red")
        _syn_block("🔭 Research Gaps",           s.get("research_gaps",[]),        "dot-gold")
        _syn_block("🚀 Future Directions",        s.get("future_directions",[]),    "dot-green")

    # Underexplored variables
    unexplored = s.get("underexplored_variables", [])
    if unexplored:
        tags = "".join(f'<span class="var-tag">{v}</span>' for v in unexplored)
        st.markdown(f"""
        <div class="syn-section" style="margin-top:0.5rem">
            <div class="syn-head">🔮 Underexplored Variables</div>
            <div style="margin-top:6px">{tags}</div>
        </div>
        """, unsafe_allow_html=True)

    # Dominant methodology
    dom = s.get("dominant_methodology","")
    if dom:
        st.markdown(f"""
        <div class="x-card" style="display:flex;align-items:center;gap:16px;margin-top:0.5rem">
            <div style="font-size:1.8rem">⚙️</div>
            <div>
                <div class="detail-lbl">Dominant Methodology</div>
                <div style="font-family:var(--font-d);font-size:1.1rem;color:var(--gold);margin-top:3px">{dom}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("📥  Export Synthesis Report →", type="primary"):
        st.session_state["page"] = "export"
        st.rerun()


def _syn_block(title, items, dot_cls):
    if not items:
        return
    items_html = "".join(
        f'<div class="syn-item"><div class="syn-dot {dot_cls}"></div><div>{item}</div></div>'
        for item in items
    )
    st.markdown(f"""
    <div class="syn-section">
        <div class="syn-head">{title}</div>
        {items_html}
    </div>
    """, unsafe_allow_html=True)
