import streamlit as st
from ApiClient import ApiClient as sdk
from components.selectors import (
    prompt_selection,
    command_selection,
    chain_selection,
)
from components.docs import agixt_docs

st.set_page_config(
    page_title="Agent Builder",
    page_icon=":hammer_and_wrench:",
    layout="wide",
)
agixt_docs()

st.title("AGiXT Agent Builder")


def render_provider_settings(provider_name, agent_settings, provider_settings):
    settings = sdk.get_provider_settings(provider_name=provider_name)
    for key, value in settings.items():
        if key != "provider":
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
    agent_names = [agent["name"] for agent in sdk.get_agents()]
    agent_name = st.selectbox("Select an agent:", agent_names)

if agent_name:
    if agent_action == "Modify Agent":
        agent_config = sdk.get_agentconfig(agent_name)
        agent_settings = agent_config.get("settings", {})
        agent_commands = agent_config.get("commands", {})
    else:
        agent_settings = {}
        agent_commands = {}

    provider_settings = {}

    st.header("Select Providers")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Language Provider")
        language_providers = sdk.get_providers_by_service("llm")
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

        st.subheader("Speech to Text Provider")
        stt_providers = sdk.get_providers_by_service("transcription")
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
        image_providers = ["None"] + sdk.get_providers_by_service("image")
        selected_image_provider = st.selectbox(
            "Select image generation provider:",
            image_providers,
            index=(
                image_providers.index(agent_settings.get("image_provider"))
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

    with col2:
        st.subheader("Vision Provider (Optional)")
        vision_providers = ["None"] + sdk.get_providers_by_service("vision")
        selected_vision_provider = st.selectbox(
            "Select vision provider:",
            vision_providers,
            index=(
                vision_providers.index(agent_settings.get("vision_provider"))
                if "vision_provider" in agent_settings
                else 0
            ),
        )
        if selected_vision_provider != "None":
            provider_settings = render_provider_settings(
                selected_vision_provider,
                agent_settings,
                provider_settings,
            )

        st.subheader("Text to Speech Provider")
        tts_providers = sdk.get_providers_by_service("tts")
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

    st.header("Configure Agent Settings")
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Web Search (Optional)")
        enable_websearch = st.checkbox(
            "Enable web search", value=agent_settings.get("WEBSEARCH_ENABLED", False)
        )
        if enable_websearch:
            websearch_depth = st.number_input(
                "Set web search depth:",
                min_value=0,
                value=int(agent_settings.get("WEBSEARCH_DEPTH", 0)),
                step=1,
            )
        else:
            websearch_depth = 0

        st.subheader("Helper Agent (Optional)")
        helper_agent = st.text_input(
            "Enter helper agent name:",
            value=agent_settings.get("helper_agent_name", ""),
        )

    with col4:
        st.subheader("Extensions")
        extensions = sdk.get_extensions()
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

    st.header("Configure Chat Completions Mode")
    chat_completions_mode = st.selectbox(
        "Select chat completions mode:",
        ["prompt", "chain", "command"],
        index=["prompt", "chain", "command"].index(
            agent_settings.get("mode", "prompt")
        ),
    )

    if chat_completions_mode == "prompt":
        prompt_settings = prompt_selection(prompt=agent_settings.get("prompt_args", {}))

    if chat_completions_mode == "chain":
        chain_settings = chain_selection(prompt=agent_settings.get("chain_args", {}))

    if chat_completions_mode == "command":
        command_settings = command_selection(
            prompt=agent_settings.get("command_args", {})
        )

    if st.button("Perform Action"):
        settings = {
            "provider": selected_language_provider,
            **provider_settings,
            "vision_provider": (
                selected_vision_provider if selected_vision_provider != "None" else None
            ),
            "transcription_provider": selected_stt_provider,
            "tts_provider": selected_tts_provider,
            "image_provider": (
                selected_image_provider if selected_image_provider != "None" else None
            ),
            "WEBSEARCH_ENABLED": enable_websearch,
            "WEBSEARCH_DEPTH": websearch_depth,
            "helper_agent_name": helper_agent,
            "extensions": selected_extensions,
            **extension_settings,
            "mode": chat_completions_mode,
        }

        if chat_completions_mode == "prompt":
            settings.update(prompt_settings)

        if chat_completions_mode == "chain":
            settings.update(chain_settings)

        if chat_completions_mode == "command":
            settings.update(command_settings)

        commands = {command: True for command in selected_commands}

        if agent_action == "Create Agent":
            response = sdk.add_agent(
                agent_name, {"settings": settings, "commands": commands}
            )
            st.success(f"Agent '{agent_name}' created.")
        elif agent_action == "Modify Agent":
            response = sdk.update_agent_settings(agent_name, settings)
            response = sdk.update_agent_commands(agent_name, commands)
            st.success(f"Agent '{agent_name}' updated.")
        elif agent_action == "Delete Agent":
            response = sdk.delete_agent(agent_name)
            st.success(f"Agent '{agent_name}' deleted.")
else:
    st.warning("Please enter an agent name.")
