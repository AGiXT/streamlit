import json
import streamlit as st
from ApiClient import ApiClient
from components.docs import agixt_docs, predefined_injection_variables
from components.chain import modify_chain

st.set_page_config(
    page_title="Chain Management",
    page_icon=":chains:",
    layout="wide",
)

agixt_docs()
st.session_state = {}
chain_names = ApiClient.get_chains()
agents = ApiClient.get_agents()
st.header("Chain Management")
chain_action = st.selectbox("Action", ["Create Chain", "Modify Chain", "Delete Chain"])

if chain_action == "Create Chain":
    chain_name = st.text_input("Chain Name")
else:
    chain_name = st.selectbox("Chains", options=chain_names)

if chain_action == "Create Chain":
    action_button = st.button("Create New Chain")
    # Import Chain
    chain_file = st.file_uploader("Import Chain", type=["json"])
    if chain_file:
        chain_name = chain_file.name.split(".")[0]
        chain_content = chain_file.read().decode("utf-8")
        steps = json.loads(chain_content)
        ApiClient.import_chain(chain_name=chain_name, steps=steps)
        st.success(f"Chain '{chain_name}' added.")
        chain_file = None
    if action_button:
        if chain_name:
            ApiClient.add_chain(chain_name=chain_name)
            st.success(f"Chain '{chain_name}' created.")
            st.experimental_rerun()
        else:
            st.error("Chain name is required.")

elif chain_action == "Delete Chain":
    action_button = st.button("Delete Chain")
    if action_button:
        if chain_name:
            ApiClient.delete_chain(chain_name=chain_name)
            st.success(f"Chain '{chain_name}' deleted.")
            st.experimental_rerun()
        else:
            st.error("Chain name is required.")

elif chain_action == "Modify Chain":
    if chain_name:
        chain = modify_chain(chain_name=chain_name, agents=agents)
    else:
        st.warning("Please select a chain to manage steps.")

show_injection_var_docs = st.checkbox("Show Prompt Injection Variable Documentation")
if show_injection_var_docs:
    predefined_injection_variables()
