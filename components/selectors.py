from ApiClient import ApiClient
import streamlit as st
import os
import logging


@st.cache_data
def cached_get_extensions():
    return ApiClient.get_extensions()


@st.cache_data
def cached_get_prompts():
    return ApiClient.get_prompts()


skip_args = [
    "command_list",
    "context",
    "COMMANDS",
    "date",
    "conversation_history",
    "agent_name",
    "working_directory",
    "helper_agent_name",
]


def build_args(args: dict = {}, prompt: dict = {}, step_number: int = 0):
    return {
        arg: st.text_input(arg, value=prompt.get(arg, ""), key=f"{arg}_{step_number}")
        for arg in args
        if arg not in skip_args
    }


def prompt_selection(prompt: dict = {}, step_number: int = 0):
    available_prompts = cached_get_prompts()
    prompt_name = st.selectbox(
        "Select Custom Prompt",
        [""] + available_prompts,
        index=available_prompts.index(prompt.get("prompt_name", "")) + 1
        if "prompt_name" in prompt
        else 0,
        key=f"step_{step_number}_prompt_name",
    )
    browse_links = st.checkbox(
        "Enable Browsing Links in the user input",
        value=prompt["browse_links"] if "browse_links" in prompt else True,
        key=f"browse_links_{step_number}",
    )
    websearch = st.checkbox(
        "Enable websearch",
        value=prompt["websearch"] if "websearch" in prompt else False,
        key=f"websearch_{step_number}",
    )
    websearch_depth = (
        3 if websearch else 0
    )  # Default depth is 3 if websearch is enabled

    # Add an input field for websearch depth if websearch is enabled
    if websearch:
        websearch_depth = st.number_input(
            "Websearch depth",
            min_value=1,
            value=int(prompt["websearch_depth"]) if "websearch_depth" in prompt else 3,
            key=f"websearch_depth_{step_number}",
        )
    advanced_options = st.checkbox(
        "Show Advanced Options", value=False, key=f"advanced_options_{step_number}"
    )
    if advanced_options:
        # Add an input field for shots
        shots = st.number_input(
            "Shots (How many times to ask the agent)",
            min_value=1,
            value=int(prompt["shots"]) if "shots" in prompt else 1,
            key=f"shots_{step_number}",
        )
        context_results = st.number_input(
            "How many memories to inject (Default is 5)",
            min_value=1,
            value=int(prompt["context_results"]) if "context_results" in prompt else 5,
            key=f"context_results_{step_number}",
        )
        disable_memory = st.checkbox(
            "Disable Memory",
            value=prompt["disable_memory"] if "disable_memory" in prompt else False,
            key=f"disable_memory_{step_number}",
        )
    else:
        shots = 1
        context_results = 5
        disable_memory = False

    if "user_input" in prompt and "context" in prompt:
        context_results = st.number_input(
            "Context results",
            min_value=1,
            value=int(prompt["context_results"]) if "context_results" in prompt else 5,
        )
    if prompt_name:
        prompt_args = ApiClient.get_prompt_args(prompt_name)
        args = build_args(args=prompt_args, prompt=prompt, step_number=step_number)
        args["websearch"] = websearch
        args["browse_links"] = browse_links
        args["websearch_depth"] = int(websearch_depth)
        args["context_results"] = int(context_results)
        args["disable_memory"] = disable_memory
        args["shots"] = int(shots)
        new_prompt = {
            "prompt_name": prompt_name,
            **args,
        }
        return new_prompt


def command_selection(prompt: dict = {}, step_number: int = 0):
    agent_commands = cached_get_extensions()
    available_commands = []
    for commands in agent_commands:
        for command in commands["commands"]:
            available_commands.append(command["friendly_name"])

    command_name = st.selectbox(
        "Select Command",
        [""] + available_commands,
        key=f"command_name_{step_number}",
        index=available_commands.index(prompt.get("command_name", "")) + 1
        if "command_name" in prompt
        else 0,
    )

    if command_name:
        command_args = ApiClient.get_command_args(command_name=command_name)
        args = build_args(args=command_args, prompt=prompt, step_number=step_number)
        new_prompt = {
            "command_name": command_name,
            **args,
        }
        return new_prompt


def chain_selection(prompt: dict = {}, step_number: int = 0):
    available_chains = ApiClient.get_chains()
    chain_name = st.selectbox(
        "Select Chain",
        [""] + available_chains,
        index=available_chains.index(prompt.get("chain_name", "")) + 1
        if "chain" in prompt
        else 0,
        key=f"step_{step_number}_chain_name",
    )
    user_input = st.text_input(
        "User Input",
        value=prompt.get("input", ""),
        key=f"user_input_{step_number}",
    )

    if chain_name:
        new_prompt = {"chain": chain_name, "input": user_input}
        return new_prompt


def agent_selection(key: str = "select_learning_agent", heading: str = "Agent Name"):
    # Load the previously selected agent name
    try:
        with open(os.path.join("session.txt"), "r") as f:
            previously_selected_agent = f.read().strip()
    except FileNotFoundError:
        previously_selected_agent = None

    # Get the list of agent names
    agent_names = [agent["name"] for agent in ApiClient.get_agents()]

    # If the previously selected agent is in the list, use it as the default
    if previously_selected_agent in agent_names:
        default_index = (
            agent_names.index(previously_selected_agent) + 1
        )  # add 1 for the empty string at index 0
    else:
        default_index = 0

    # Create the selectbox
    selected_agent = st.selectbox(
        heading,
        options=[""] + agent_names,
        index=default_index,
        key=key,
    )
    if key == "select_learning_agent":
        # If the selected agent has changed, save the new selection
        if selected_agent != previously_selected_agent:
            with open(os.path.join("session.txt"), "w") as f:
                f.write(selected_agent)
            try:
                st.experimental_rerun()
            except Exception as e:
                logging.info(e)
    return selected_agent


def helper_agent_selection(
    current_agent: str, key: str = "select_learning_agent", heading: str = "Agent Name"
):
    # Get the list of agent names
    agent_names = [agent["name"] for agent in ApiClient.get_agents()]
    agent_config = ApiClient.get_agentconfig(agent_name=current_agent)
    agent_settings = agent_config.get("settings", {})
    helper_agent = agent_settings.get("helper_agent_name", current_agent)
    # Create the selectbox
    selected_agent = st.selectbox(
        heading,
        options=[""] + agent_names,
        index=agent_names.index(helper_agent) + 1,
        key=key,
    )
    return selected_agent


def conversation_selection(agent_name):
    if not os.path.exists("conversation.txt"):
        with open("conversation.txt", "w") as f:
            f.write("")
    try:
        with open(os.path.join("conversation.txt"), "r") as f:
            conversation = f.read().strip()
    except FileNotFoundError:
        conversation = ""
    conversations = ApiClient.get_conversations(agent_name=agent_name)
    if isinstance(conversations, str):
        conversations = []
    conversation_name = st.selectbox(
        "Choose a conversation",
        [""] + conversations,
        index=conversations.index(conversation) + 1
        if conversation in conversations
        else 0
        if conversations == []
        else 1,
    )
    if conversation != conversation_name:
        with open(os.path.join("conversation.txt"), "w") as f:
            f.write(conversation_name)
        try:
            st.experimental_rerun()
        except Exception as e:
            logging.info(e)
    return conversation_name
