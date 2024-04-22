import streamlit as st
from ApiClient import ApiClient as sdk
from components.selectors import (
    prompt_selection,
    command_selection,
    chain_selection,
    render_provider_settings,
)
from components.docs import agixt_docs

st.set_page_config(
    page_title="Agent Builder",
    page_icon=":hammer_and_wrench:",
    layout="wide",
)
agixt_docs()

st.title("AGiXT Agent Builder")

agent_name = st.text_input("Enter the agent name:")

if agent_name:
    provider_settings = {}

    st.header("Select Providers")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Language Provider")
        language_providers = sdk.get_providers_by_service("llm")
        selected_language_provider = st.selectbox(
            "Select language provider:", language_providers
        )
        provider_settings.update(
            render_provider_settings(
                selected_language_provider, provider_settings, key_prefix="language"
            )
        )

        st.subheader("Speech to Text Provider")
        stt_providers = sdk.get_providers_by_service("transcription")
        selected_stt_provider = st.selectbox(
            "Select speech to text provider:", stt_providers
        )
        provider_settings.update(
            render_provider_settings(
                selected_stt_provider, provider_settings, key_prefix="stt"
            )
        )

        st.subheader("Image Generation Provider (Optional)")
        image_providers = ["None"] + sdk.get_providers_by_service("image")
        selected_image_provider = st.selectbox(
            "Select image generation provider:", image_providers
        )
        if selected_image_provider != "None":
            provider_settings.update(
                render_provider_settings(
                    selected_image_provider, provider_settings, key_prefix="image"
                )
            )

    with col2:
        st.subheader("Vision Provider (Optional)")
        vision_providers = ["None"] + sdk.get_providers_by_service("vision")
        selected_vision_provider = st.selectbox(
            "Select vision provider:", vision_providers
        )
        if selected_vision_provider != "None":
            provider_settings.update(
                render_provider_settings(
                    selected_vision_provider, provider_settings, key_prefix="vision"
                )
            )

        st.subheader("Text to Speech Provider")
        tts_providers = sdk.get_providers_by_service("tts")
        selected_tts_provider = st.selectbox(
            "Select text to speech provider:", tts_providers
        )
        provider_settings.update(
            render_provider_settings(
                selected_tts_provider, provider_settings, key_prefix="tts"
            )
        )

    st.header("Configure Agent Settings")
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Web Search (Optional)")
        enable_websearch = st.checkbox("Enable web search")
        if enable_websearch:
            websearch_depth = st.number_input(
                "Set web search depth:", min_value=0, value=0, step=1
            )
        else:
            websearch_depth = 0

        st.subheader("Helper Agent (Optional)")
        helper_agent = st.text_input("Enter helper agent name:")

    with col4:
        st.subheader("Extensions")
        extensions = sdk.get_extensions()
        print(extensions)
        extension_options = [extension["extension_name"] for extension in extensions]
        selected_extensions = st.multiselect("Select extensions:", extension_options)

        extension_settings = {}
        selected_commands = []
        for extension in extensions:
            if extension["extension_name"] in selected_extensions:
                st.subheader(extension["extension_name"])
                for setting in extension["settings"]:
                    extension_settings[setting] = st.text_input(f"{setting}:")
                st.subheader("Commands")
                for command in extension["commands"]:
                    command_enabled = st.checkbox(command["friendly_name"])
                    if command_enabled:
                        selected_commands.append(command["friendly_name"])

    st.header("Configure Chat Completions Mode")
    chat_completions_mode = st.selectbox(
        "Select chat completions mode:", ["prompt", "chain", "command"]
    )

    if chat_completions_mode == "prompt":
        prompt_settings = prompt_selection()

    if chat_completions_mode == "chain":
        chain_settings = chain_selection()

    if chat_completions_mode == "command":
        command_settings = command_selection()

    if st.button("Create Agent"):
        settings = {
            "language_provider": selected_language_provider,
            "language_settings": provider_settings,
            "vision_provider": (
                selected_vision_provider if selected_vision_provider != "None" else None
            ),
            "vision_settings": provider_settings,
            "stt_provider": selected_stt_provider,
            "stt_settings": provider_settings,
            "tts_provider": selected_tts_provider,
            "tts_settings": provider_settings,
            "image_provider": (
                selected_image_provider if selected_image_provider != "None" else None
            ),
            "image_settings": provider_settings,
            "enable_websearch": enable_websearch,
            "websearch_depth": websearch_depth,
            "helper_agent": helper_agent,
            "extensions": selected_extensions,
            "extension_settings": extension_settings,
            "commands": selected_commands,
            "chat_completions_mode": chat_completions_mode,
        }

        if chat_completions_mode == "prompt":
            settings.update(prompt_settings)

        if chat_completions_mode == "chain":
            settings.update(chain_settings)

        if chat_completions_mode == "command":
            settings.update(command_settings)

        # response = sdk.add_agent(agent_name, settings)
        st.success(settings)
else:
    st.warning("Please enter an agent name to start building.")
