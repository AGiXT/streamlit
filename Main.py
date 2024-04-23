import requests, os, json
import streamlit as st
from components.docs import agixt_docs

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
)

def check_server_conf():
    if os.path.isfile("server_conf.json"):
      f = open("server_conf.json")
      data = json.load(f)
      server_response = requests.get(f""+data['SERVER_URI']+"/api/providers", headers={"Authorization": data['API_KEY']})
    else:
      server_response = requests.get(f"{base_uri}/api/providers", headers={"Authorization": api_key})
    return server_response.status_code
  
if check_server_conf != 200:
    # Show API config
    st.warning("The API Config Is Invalid - Please Re-Enter Server URL & API Key")
    s_URI = st.input("Server URL:", key="server_URI")
    s_KEY = st.input("Server API Key:", key="server_KEY")
    if st.button("Submit"):
        output_json = {"SERVER_URI" : s_URI,"API_KEY" : s_KEY}
        with open("server_conf.json", "w") as outfile:
            json.dump(dictionary, outfile)
        st.reload()
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
        from ApiClient import ApiClient

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
