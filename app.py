import streamlit as st
from agent import answer

st.set_page_config(page_title="PakBrief Agent", page_icon="🇵🇰", layout="centered")

st.markdown("""
<style>
  .hero { text-align: center; padding: 2rem 0 1rem; }
  .hero h1 { font-size: 2.6rem; margin-bottom: 0.2rem; }
  .hero p { color: #888; font-size: 1.05rem; max-width: 560px; margin: 0 auto; }
  .stButton>button { background: #0d7a3f; color: white; border: none;
    border-radius: 10px; padding: 0.6rem 2rem; font-weight: 600; width: 100%; }
  .stButton>button:hover { background: #0a6234; color: white; }
  .answer-card { background: #0f1a14; border: 1px solid #1d3a2a; border-radius: 14px;
    padding: 1.4rem; margin: 1rem 0; line-height: 1.7; }
  .source-link { display: block; padding: 0.55rem 0.9rem; margin: 0.3rem 0;
    background: #101418; border: 1px solid #222; border-radius: 10px;
    text-decoration: none; color: #ddd; font-size: 0.9rem; }
  .source-link:hover { border-color: #0d7a3f; color: #fff; }
  .chip { display: inline-block; background: #141a16; border: 1px solid #2a3a30;
    border-radius: 20px; padding: 0.35rem 0.9rem; margin: 0.2rem;
    font-size: 0.85rem; cursor: pointer; color: #bbb; }
  .section-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;
    color: #0d7a3f; font-weight: 700; margin: 1.4rem 0 0.5rem; }
  footer { text-align: center; color: #555; font-size: 0.8rem; margin-top: 3rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🇵🇰 PakBrief Agent</h1>
  <p>Ask anything about current Pakistan — petrol prices, deadlines, match schedules.
  The agent searches the live web and answers with cited sources.</p>
</div>
""", unsafe_allow_html=True)

EXAMPLES = [
    "What is the petrol price in Pakistan today?",
    "Pakistan cricket team upcoming matches",
    "Lahore air quality index today",
    "HEC scholarship deadlines 2026",
]

cols = st.columns(2)
for i, ex in enumerate(EXAMPLES):
    if cols[i % 2].button(ex, key=f"ex{i}"):
        st.session_state["q"] = ex

q = st.text_input("Your question", key="q",
                  placeholder="e.g. What is the petrol price in Pakistan today?",
                  label_visibility="collapsed")

if st.button("🔍 Research", type="primary") and q:
    with st.spinner("Searching the web and reading sources..."):
        r = answer(q)

    st.markdown('<div class="section-label">Answer</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="answer-card">{r["answer"]}</div>', unsafe_allow_html=True)

    if r.get("sources"):
        st.markdown('<div class="section-label">Sources</div>', unsafe_allow_html=True)
        for i, s in enumerate(r["sources"], 1):
            st.markdown(
                f'<a class="source-link" href="{s["url"]}" target="_blank">'
                f'<b>[{i}]</b> {s["title"]}</a>', unsafe_allow_html=True)

    with st.expander("🛠 Tool trace — see what the agent did"):
        for t in r["trace"]:
            st.write(f"**Tool:** `{t.get('tool', '?')}`")
            if "query" in t:
                st.write(f"**Query:** {t['query']}")
            if "url" in t:
                st.write(f"**URL:** {t['url']}")
            if "results_found" in t:
                st.write(f"**Results found:** {t['results_found']}")
            if "chars" in t:
                st.write(f"**Chars read:** {t['chars']}")
            if t.get("error"):
                st.write(f"⚠️ {t['error']}")
            st.divider()

st.markdown("<footer>Built by <b>Rayyan Khan</b> · rayyankhan.online</footer>",
            unsafe_allow_html=True)
