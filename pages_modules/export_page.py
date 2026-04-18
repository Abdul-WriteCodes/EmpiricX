import streamlit as st
from core.exporter import papers_to_csv, papers_to_excel, synthesis_to_docx


def render():
    papers    = st.session_state.get("extracted_papers", [])
    synthesis = st.session_state.get("synthesis_result")

    st.markdown("""
    <div class="ph-wrap anim-up">
        <div class="ph-eye">Step 03 · Export</div>
        <h1 class="ph-title">Export <span>Results</span></h1>
        <p class="ph-sub">Download your extracted data and synthesis report.</p>
    </div>
    """, unsafe_allow_html=True)

    if not papers:
        st.markdown("""
        <div class="empty-st">
            <div class="empty-st-icon">📥</div>
            <div class="empty-st-title">Nothing to export yet</div>
            <div class="empty-st-desc">Extract papers first to enable downloads.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Paper data exports ─────────────────────────────────────
    st.markdown(f'<div class="detail-lbl" style="margin-bottom:1rem">Paper Extraction Data · {len(papers)} paper(s)</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="exp-card">
            <span class="exp-icon">📋</span>
            <div class="exp-name">CSV Spreadsheet</div>
            <div class="exp-desc">Universal format · Opens in any tool</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            st.download_button(
                "⬇  Download CSV",
                data=papers_to_csv(papers),
                file_name="empiricx_results.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_csv",
            )
        except Exception as e:
            st.error(f"CSV error: {e}")

    with c2:
        st.markdown("""
        <div class="exp-card">
            <span class="exp-icon">📗</span>
            <div class="exp-name">Excel Workbook</div>
            <div class="exp-desc">Styled .xlsx · Freeze panes · Formatted</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            st.download_button(
                "⬇  Download Excel",
                data=papers_to_excel(papers),
                file_name="empiricx_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_excel",
            )
        except Exception as e:
            st.error(f"Excel error: {e}")

    # ── Synthesis report ───────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="detail-lbl" style="margin-bottom:1rem">Synthesis Report</div>', unsafe_allow_html=True)

    if not synthesis:
        st.markdown("""
        <div class="x-card" style="text-align:center;padding:2.5rem">
            <div style="font-size:2rem;margin-bottom:12px;opacity:0.4">📄</div>
            <div style="font-size:0.9rem;color:var(--text-2);margin-bottom:16px">
                Run the Cross-Paper Synthesis first to generate the Word report.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Go to Synthesis", use_container_width=False):
            st.session_state["page"] = "synthesis"
            st.rerun()
        return

    st.markdown("""
    <div class="exp-card" style="text-align:left;max-width:480px">
        <div style="display:flex;align-items:center;gap:14px">
            <span style="font-size:2.2rem">📄</span>
            <div>
                <div class="exp-name">Word Document (.docx)</div>
                <div class="exp-desc" style="margin-top:5px">
                    Full synthesis report — overview, all six sections,
                    underexplored variables, and a paper reference table.
                    Ready for your literature review.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)

    try:
        st.download_button(
            "⬇  Download Synthesis Report (.docx)",
            data=synthesis_to_docx(synthesis, papers),
            file_name="empiricx_synthesis_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_docx",
        )
    except Exception as e:
        st.error(f"DOCX error: {e}")
