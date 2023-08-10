import streamlit as st
import os
from components.selectors import agent_selection, conversation_selection, skip_args
from ApiClient import ApiClient
from components.docs import agixt_docs

st.set_page_config(
    page_title="Agent Interactions",
    page_icon=":speech_balloon:",
    layout="wide",
)

agixt_docs()

st.header("Agent Interactions")

try:
    with open(os.path.join("session.txt"), "r") as f:
        agent_name = f.read().strip()
except:
    agent_name = "OpenAI"
st.session_state["conversation"] = conversation_selection(agent_name=agent_name)
mode = st.selectbox("Select Mode", ["Chat", "Chains", "Prompt", "Instruct"])
agent_name = agent_selection() if mode != "Chains" else None

if mode != "Chains":
    prompt_name = "Chat" if mode != "Instruct" else "instruct"
    advanced_options = st.checkbox("Show Advanced Options")
    if advanced_options:
        shots = st.number_input(
            "Shots (How many times to ask the agent)", min_value=1, value=1, key="shots"
        )
        context_results = st.number_input(
            "How many long term memories to inject (Default is 5)",
            min_value=1,
            value=5,
            key="context_results",
        )
        browse_links = st.checkbox(
            "Enable Browsing Links in the user input", value=False
        )
        websearch = st.checkbox("Enable websearch")
        websearch_depth = 3 if websearch else 0
        enable_memory = st.checkbox(
            "Enable Memory Training (Any messages sent to and from the agent will be added to memory if enabled.)",
            value=False,
        )
    else:
        shots = 1
        context_results = 5
        browse_links = False
        websearch = False
        websearch_depth = 0
        enable_memory = False

    if websearch:
        websearch_depth = st.number_input(
            "Websearch depth", min_value=1, value=3, key="websearch_depth"
        )
    prompt_args_values = {}
    if mode == "Prompt":
        prompts = ApiClient.get_prompts()
        try:
            custom_input_index = prompts.index("Custom Input")
        except:
            custom_input_index = 0
        prompt_name = st.selectbox("Choose a prompt", prompts, index=custom_input_index)
        prompt_args = ApiClient.get_prompt_args(prompt_name=prompt_name)
        st.markdown("**Prompt Variables**")
        for arg in prompt_args:
            if arg not in skip_args:
                prompt_args_values[arg] = st.text_area(arg)
        if "user_input" in prompt_args and "context" in prompt_args:
            context_results = st.number_input("Context results", min_value=1, value=5)
        user_input = (
            prompt_args_values["user_input"] if "user_input" in prompt_args else ""
        )
    else:
        user_input = st.text_area("User Input")
    if st.button("Send"):
        if prompt_args_values == {}:
            prompt_args_values = {
                "user_input": user_input,
                "websearch": websearch,
                "browse_links": browse_links,
                "websearch_depth": int(websearch_depth),
                "context_results": int(context_results),
                "shots": int(shots),
                "conversation_name": st.session_state["conversation"],
                "disable_memory": True if enable_memory == False else False,
            }
        else:
            prompt_args_values["user_input"] = user_input
            prompt_args_values["websearch"] = websearch
            prompt_args_values["browse_links"] = browse_links
            prompt_args_values["websearch_depth"] = int(websearch_depth)
            prompt_args_values["context_results"] = int(context_results)
            prompt_args_values["shots"] = int(shots)
            prompt_args_values["conversation_name"] = st.session_state["conversation"]
            prompt_args_values["disable_memory"] = (
                True if enable_memory == False else False
            )
        with st.spinner("Thinking, please wait..."):
            agent_prompt_resp = ApiClient.prompt_agent(
                agent_name=agent_name,
                prompt_name=prompt_name,
                prompt_args=prompt_args_values,
            )
            if agent_prompt_resp:
                st.experimental_rerun()
else:
    chain_names = ApiClient.get_chains()
    chain_action = "Run Chain"
    chain_name = st.selectbox("Select a Chain to Run", chain_names)
    agent_override = st.checkbox("Override Agent")
    if agent_override:
        agent_name = agent_selection()
    else:
        agent_name = ""
    user_input = st.text_area("User Input")
    args = {}
    if chain_name:
        chain_args = ApiClient.get_chain_args(chain_name=chain_name)
        for arg in chain_args:
            if arg not in skip_args and arg != "user_input":
                override_arg = st.checkbox(f"Override `{arg}` argument.")
                if override_arg:
                    args[arg] = st.text_area(arg)
    if args != {}:
        args_copy = args.copy()
        for arg in args_copy:
            if args[arg] == "":
                del args[arg]
    args["conversation_name"] = st.session_state["conversation"]
    single_step = st.checkbox("Run a Single Step")
    if single_step:
        from_step = st.number_input("Step Number to Run", min_value=1, value=1)
        all_responses = False
        if st.button("Run Chain Step"):
            if chain_name:
                if chain_action == "Run Chain":
                    responses = ApiClient.run_chain_step(
                        chain_name=chain_name,
                        user_input=user_input,
                        agent_name=agent_name,
                        step_number=from_step,
                        chain_args=args,
                    )
                    st.success(f"Chain '{chain_name}' executed.")
                    st.write(responses)
            else:
                st.error("Chain name is required.")
    else:
        from_step = st.number_input("Start from Step", min_value=1, value=1)
        all_responses = st.checkbox(
            "Show All Responses (If not checked, you will only be shown the last step's response in the chain when done.)"
        )
        if st.button("Run Chain"):
            if chain_name:
                if chain_action == "Run Chain":
                    responses = ApiClient.run_chain(
                        chain_name=chain_name,
                        user_input=user_input,
                        agent_name=agent_name,
                        all_responses=all_responses,
                        from_step=from_step,
                        chain_args=args,
                    )
                    st.success(f"Chain '{chain_name}' executed.")
                    st.write(responses)
            else:
                st.error("Chain name is required.")
