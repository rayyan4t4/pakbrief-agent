import streamlit as st
from agent import answer

st.set_page_config(page_title="PakBrief Agent", page_icon="🇵🇰")
st.title("🇵🇰 PakBrief Agent")
st.caption("A tool-using research agent for current Pakistan questions — with cited sources.")

q = st.text_input("Ask a current-affairs question:", 
                  placeholder="e.g. What is the petrol price in Pakistan today?")
if st.button("Research") and q:
    with st.spinner("Searching the web..."):
        r = answer(q)
    st.subheader("Answer")
    st.write(r["answer"])
    if r["citations"]:
        st.subheader("Sources")
        for i, u in enumerate(r["citations"], 1):
            st.markdown(f"[{i}] {u}")
    with st.expander("Tool trace"):
        st.write(r["trace"])

st.divider()
st.caption("Built by Rayyan Khan · rayyankhan.online")
