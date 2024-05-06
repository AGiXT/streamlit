import streamlit as st
from ApiClient import ApiClient
from components.selectors import (
    helper_agent_selection,
    prompt_selection,
    command_selection,
    chain_selection,
)
from components.docs import agixt_docs

st.set_page_config(
    page_title="Agent Management",
    page_icon=":hammer_and_wrench:",
    layout="wide",
)
agixt_docs()

st.title("Agent Management")


def render_provider_settings(provider_name, agent_settings, provider_settings):
    settings = ApiClient.get_provider_settings(provider_name=provider_name)
    for key, value in settings.items():
        if key in provider_settings:
            # Use existing provider settings if available
            settings[key] = provider_settings[key]
        else:
            # Create new provider settings
            settings[key] = st.text_input(
                f"{key}:", value=agent_settings.get(key, value)
            )
    provider_settings.update(settings)
    return provider_settings


agent_action = st.selectbox("Action", ["Create Agent", "Modify Agent", "Delete Agent"])

if agent_action == "Create Agent":
    agent_name = st.text_input("Enter the agent name:")
else:
    agent_names = [agent["name"] for agent in ApiClient.get_agents()]
    agent_name = st.selectbox("Select an agent:", agent_names)


if agent_action == "Modify Agent":
    agent_config = ApiClient.get_agentconfig(agent_name)
    agent_settings = agent_config.get("settings", {})
    agent_commands = agent_config.get("commands", {})
else:
    agent_config = {}
    agent_settings = {}
    agent_commands = {}

provider_settings = {}

st.header("Select Providers")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Language Provider")
    language_providers = ApiClient.get_providers_by_service("llm")
    selected_language_provider = st.selectbox(
        "Select language provider:",
        language_providers,
        index=(
            language_providers.index(agent_settings.get("provider"))
            if "provider" in agent_settings
            else 0
        ),
    )
    provider_settings = render_provider_settings(
        selected_language_provider,
        agent_settings,
        provider_settings,
    )

with col2:
    st.subheader("Vision Provider (Optional)")
    vision_providers = ["None"] + ApiClient.get_providers_by_service("vision")
    vp = agent_settings.get("vision_provider", "None")
    if not vp:
        vp = "None"
    selected_vision_provider = st.selectbox(
        "Select vision provider:",
        vision_providers,
        index=(
            vision_providers.index(vp) if "vision_provider" in agent_settings else 0
        ),
    )
    if selected_vision_provider != "None":
        provider_settings = render_provider_settings(
            selected_vision_provider,
            agent_settings,
            provider_settings,
        )

    st.subheader("Text to Speech Provider")
    tts_providers = ApiClient.get_providers_by_service("tts")
    tts_providers = ["None"] + tts_providers
    selected_tts_provider = st.selectbox(
        "Select text to speech provider:",
        tts_providers,
        index=(
            tts_providers.index(agent_settings.get("tts_provider"))
            if "tts_provider" in agent_settings
            else 0
        ),
    )
    provider_settings = render_provider_settings(
        selected_tts_provider,
        agent_settings,
        provider_settings,
    )

    st.subheader("Speech to Text Provider")
    stt_providers = ApiClient.get_providers_by_service("transcription")
    selected_stt_provider = st.selectbox(
        "Select speech to text provider:",
        stt_providers,
        index=(
            stt_providers.index(agent_settings.get("transcription_provider"))
            if "transcription_provider" in agent_settings
            else 0
        ),
    )
    provider_settings = render_provider_settings(
        selected_stt_provider,
        agent_settings,
        provider_settings,
    )
    st.subheader("Image Generation Provider (Optional)")
    image_providers = ["None"] + ApiClient.get_providers_by_service("image")
    selected_img_provider = (
        agent_settings["image_provider"]
        if "image_provider" in agent_settings
        else "None"
    )
    if selected_img_provider not in image_providers:
        selected_img_provider = "None"
    selected_image_provider = st.selectbox(
        "Select image generation provider:",
        image_providers,
        index=(
            image_providers.index(selected_img_provider)
            if "image_provider" in agent_settings
            else 0
        ),
    )
    if selected_image_provider != "None":
        provider_settings = render_provider_settings(
            selected_image_provider,
            agent_settings,
            provider_settings,
        )
    st.subheader("Embeddings Provider")
    embedding_providers = ApiClient.get_providers_by_service("embeddings")
    selected_embedding_provider = st.selectbox(
        "Select embeddings provider:",
        embedding_providers,
        index=(
            embedding_providers.index(
                agent_settings.get("embeddings_provider", "default")
            )
            if "embeddings_provider" in agent_settings
            else 0
        ),
    )

st.header("Configure Agent Settings")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Extensions")
    extensions = ApiClient.get_extensions()
    extension_options = [extension["extension_name"] for extension in extensions]

    # Automatically select extensions based on enabled commands
    selected_extensions = []
    for extension in extensions:
        for command in extension["commands"]:
            if agent_commands.get(command["friendly_name"], False):
                selected_extensions.append(extension["extension_name"])
                break

    selected_extensions = st.multiselect(
        "Select extensions:",
        extension_options,
        default=list(set(selected_extensions)),
    )

    extension_settings = {}
    selected_commands = []
    for extension in extensions:
        if extension["extension_name"] in selected_extensions:
            st.subheader(extension["extension_name"])
            for setting in extension["settings"]:
                extension_settings[setting] = st.text_input(
                    f"{setting}:", value=agent_settings.get(setting, "")
                )
            st.subheader("Commands")
            for command in extension["commands"]:
                command_enabled = st.checkbox(
                    command["friendly_name"],
                    value=agent_commands.get(command["friendly_name"], False),
                )
                if command_enabled:
                    selected_commands.append(command["friendly_name"])

with col4:
    st.subheader("Helper Agent (Optional)")
    helper_agent = helper_agent_selection(
        current_agent=agent_name,
        key="select_helper_agent",
        heading="Select Helper Agent (Your agent may ask the selected one for help when it needs something.)",
        agent_config=agent_config,
    )
st.header("Configure Chat Completions Mode")
chat_completions_mode = st.selectbox(
    "Select chat completions mode:",
    ["prompt", "chain", "command"],
    index=["prompt", "chain", "command"].index(agent_settings.get("mode", "prompt")),
)

command_variable = ""
if chat_completions_mode == "prompt":
    prompt_settings = prompt_selection(prompt=agent_settings, show_user_input=False)

if chat_completions_mode == "chain":
    chain_settings = chain_selection(prompt=agent_settings, show_user_input=False)

if chat_completions_mode == "command":
    command_settings = command_selection(prompt=agent_settings, show_user_input=False)
    if command_settings and "command_args" in command_settings:
        command_variable = st.selectbox(
            "Select Command Variable",
            [""] + list(command_settings["command_args"].keys()),
            index=(
                list(command_settings["command_args"].keys()).index(
                    agent_settings.get("command_variable", "")
                )
                + 1
                if agent_settings.get("command_variable", "")
                in command_settings["command_args"]
                else 0
            ),
            key="command_variable",
        )
    else:
        command_variable = ""

if st.button("Save Agent Settings"):
    settings = {
        "provider": selected_language_provider,
        **provider_settings,
        "vision_provider": selected_vision_provider,
        "transcription_provider": selected_stt_provider,
        "translation_provider": selected_stt_provider,
        "tts_provider": (
            selected_tts_provider if selected_tts_provider != "None" else "None"
        ),
        "image_provider": (
            selected_image_provider if selected_image_provider != "None" else "None"
        ),
        "embeddings_provider": selected_embedding_provider,
        "helper_agent_name": helper_agent,
        **extension_settings,
        "mode": chat_completions_mode,
    }

    if chat_completions_mode == "prompt":
        settings.update(prompt_settings)

    if chat_completions_mode == "chain":
        settings.update(chain_settings)

    if chat_completions_mode == "command":
        settings.update(command_settings)
        settings["command_variable"] = command_variable

    commands = {command: True for command in selected_commands}

    if agent_action == "Create Agent":
        response = ApiClient.add_agent(
            agent_name=agent_name, settings=settings, commands=commands
        )
        st.success(f"Agent '{agent_name}' created.")
    elif agent_action == "Modify Agent":
        response = ApiClient.update_agent_settings(
            agent_name=agent_name, settings=settings
        )
        response = ApiClient.update_agent_commands(
            agent_name=agent_name, commands=commands
        )
        st.success(f"Agent '{agent_name}' updated.")
    elif agent_action == "Delete Agent":
        response = ApiClient.delete_agent(agent_name)
        st.success(f"Agent '{agent_name}' deleted.")
