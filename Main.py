import streamlit as st
from components.docs import agixt_docs
from ApiClient import get_agixt

# Check if session.txt exists
try:
    with open("./session.txt") as f:
        agent_name = f.read()
except:
    agent_name = ""

st.set_page_config(
    page_title="AGiXT",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="expanded",
    theme={
        "primaryColor": "#4CAF50",
        "backgroundColor": "#F0F0F0",
        "secondaryBackgroundColor": "#E0E0E0",
        "textColor": "#333333",
        "font": "sans-serif"
    }
)
ApiClient = get_agixt()
if not ApiClient:
    st.stop()
agixt_docs()

if agent_name == "":
    st.markdown("# Getting Started")
    st.markdown(
        "If you do not intend to use the OpenAI agent at this time, go to the [Agent Management](Agent_Management) page and create a new agent for your chosen provider, or modify the default OpenAI agent there."
    )
    st.markdown("## OpenAI Agent Quick Start")
    st.markdown(
        "**If you would like to use an OpenAI agent, please enter your API key below.**"
    )

    openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key")
    if st.button("Update API Key"):
        agent_config = ApiClient.get_agentconfig(agent_name="OpenAI")
        agent_settings = agent_config["settings"]
        agent_settings["OPENAI_API_KEY"] = openai_api_key
        ApiClient.update_agent_settings(
            agent_name="OpenAI",
            settings=agent_settings,
        )
        with open("./session.txt", "w") as f:
            f.write("OpenAI")
        st.rerun()
else:
    try:
        with open("./.streamlit/config.toml") as f:
            if "dark" in f.read():
                logo = "AGiXT-gradient-light.svg"
            else:
                logo = "AGiXT-gradient-flat.svg"
    except:
        logo = "AGiXT-gradient-light.svg"
    st.markdown(
        f"""
        <div style="text-align: center;">
        <img src="https://josh-xt.github.io/AGiXT/images/{logo}" width="65%">
        </div>
        """,
        unsafe_allow_html=True,
    )
