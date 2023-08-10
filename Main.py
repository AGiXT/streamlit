import streamlit as st
from components.docs import agixt_docs

st.set_page_config(
    page_title="AGiXT",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    with open("./.streamlit/config.toml") as f:
        if "dark" in f.read():
            light_theme = False
except:
    light_theme = False


agixt_docs()
if light_theme == True:
    st.markdown(
        """
        <div style="text-align: center;">
        <img src="https://josh-xt.github.io/AGiXT/images/AGiXT-gradient-flat.svg" width="65%">
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div style="text-align: center;">
        <img src="https://josh-xt.github.io/AGiXT/images/AGiXT-gradient-light.svg" width="65%">
        </div>
        """,
        unsafe_allow_html=True,
    )
