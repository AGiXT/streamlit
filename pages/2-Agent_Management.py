import os
import json
import streamlit as st
from ApiClient import ApiClient
from components.selectors import agent_selection, helper_agent_selection
from components.docs import agixt_docs

st.set_page_config(
    page_title="Agent Management",
    page_icon=":hammer_and_wrench:",
    layout="wide",
)
agixt_docs()


@st.cache_data
def get_providers():
    return ApiClient.get_providers()


@st.cache_data
def get_embed_providers():
    return ApiClient.get_embed_providers()


@st.cache_data
def provider_settings(provider_name: str):
    return ApiClient.get_provider_settings(provider_name=provider_name)


@st.cache_data
def get_extension_settings():
    return ApiClient.get_extension_settings()


@st.cache_data
def get_extensions():
    extensions = ApiClient.get_extensions()
    return [
        command["friendly_name"]
        for extension in extensions
        for command in extension["commands"]
    ]


providers = get_providers()
embedders = get_embed_providers()
extension_setting_keys = get_extension_settings()


def render_provider_settings(agent_settings, provider_name: str):
    try:
        required_settings = provider_settings(provider_name=provider_name)
        # remove "provider" from required settings
        required_settings.pop("provider")
    except (TypeError, ValueError):
        st.error(
            f"Error loading provider settings: expected a list or a dictionary, but got {required_settings}"
        )
        return {}
    rendered_settings = {}

    if not isinstance(required_settings, (list, dict)):
        st.error(
            f"Error loading provider settings: expected a list or a dictionary, but got {required_settings}"
        )
        return rendered_settings

    if isinstance(required_settings, dict):
        required_settings = list(required_settings.keys())

    for key in required_settings:
        if key in agent_settings:
            default_value = agent_settings[key]
        else:
            default_value = ""

        user_val = st.text_input(key, value=default_value)
        rendered_settings[key] = user_val
    return rendered_settings


def render_extension_settings(extension_settings, agent_settings):
    rendered_settings = {}

    for extension, settings in extension_settings.items():
        title_extension = extension.replace("_", " ").title()
        st.subheader(f"{title_extension} Settings")
        for key, val in settings.items():
            if key in agent_settings:
                default_value = agent_settings[key]
            else:
                default_value = val if val else ""
            if key.startswith("USE_") or key == "WORKING_DIRECTORY_RESTRICTED":
                user_val = st.checkbox(key, value=bool(default_value), key=key)
            else:
                user_val = st.text_input(
                    key, value=default_value, key=f"{extension}_{key}"
                )

            # Check if the user value exists before saving the setting
            if user_val:
                rendered_settings[key] = user_val
    return rendered_settings


st.header("Agent Management")
agent_name = agent_selection()

if "new_agent_name" not in st.session_state:
    st.session_state["new_agent_name"] = ""

# Add an input field for the new agent's name
new_agent = False

# Check if a new agent has been added and reset the session state variable
if (
    st.session_state["new_agent_name"]
    and st.session_state["new_agent_name"] != agent_name
):
    st.session_state["new_agent_name"] = ""

if not agent_name:
    agent_file = st.file_uploader("Import Agent", type=["json"])
    if agent_file:
        agent_name = agent_file.name.split(".json")[0]
        agent_settings = agent_file.read().decode("utf-8")
        agent_config = json.loads(agent_settings)
        ApiClient.import_agent(
            agent_name=agent_name,
            settings=agent_config["settings"],
            commands=agent_config["commands"],
        )
        st.success(f"Agent '{agent_name}' imported.")
    new_agent_name = st.text_input("New Agent Name")

    # Add an "Add Agent" button
    add_agent_button = st.button("Add Agent")

    # If the "Add Agent" button is clicked, create a new agent config file
    if add_agent_button:
        if new_agent_name:
            try:
                ApiClient.add_agent(new_agent_name, {})
                st.success(f"Agent '{new_agent_name}' added.")
                agent_name = new_agent_name
                with open(os.path.join("session.txt"), "w") as f:
                    f.write(agent_name)
                st.session_state["new_agent_name"] = agent_name
                st.experimental_rerun()  # Rerun the app to update the agent list
            except Exception as e:
                st.error(f"Error adding agent: {str(e)}")
        else:
            st.error("New agent name is required.")
    new_agent = True

if agent_name and not new_agent:
    try:
        agent_config = ApiClient.get_agentconfig(agent_name=agent_name)
        export_button = st.download_button(
            "Export Agent Config",
            data=json.dumps(agent_config, indent=4),
            file_name=f"{agent_name}.json",
            mime="application/json",
        )
        agent_settings = agent_config.get("settings", {})
        provider_name = agent_settings.get("provider", "")
        provider_name = st.selectbox(
            "Select Provider",
            providers,
            index=providers.index(provider_name) if provider_name in providers else 0,
        )

        agent_settings[
            "provider"
        ] = provider_name  # Update the agent_settings with the selected provider
        with st.form(key="update_agent_settings_form"):
            st.subheader("Agent Settings")
            if "AUTONOMOUS_EXECUTION" not in agent_settings:
                agent_settings["AUTONOMOUS_EXECUTION"] = False
            autonomous_execution = st.checkbox(
                "Autonomous Execution (If checked, agent will run any enabled commands automatically, if not, it will create a chain of commands it would have executed.)",
                value=bool(agent_settings["AUTONOMOUS_EXECUTION"]),
                key="AUTONOMOUS_EXECUTION",
            )
            agent_settings["AUTONOMOUS_EXECUTION"] = autonomous_execution
            if "agent_helper_name" in agent_settings:
                agent_helper_name = agent_settings["helper_agent_name"]
            else:
                agent_helper_name = agent_name
            agent_settings["helper_agent_name"] = helper_agent_selection(
                current_agent=agent_name,
                key="select_helper_agent",
                heading="Select Helper Agent (Your agent will ask this one for help when it needs something.)",
            )

            embedder_name = agent_settings.get("embedder", "default")
            embedder_name = st.selectbox(
                "Select Embedder",
                embedders,
                index=embedders.index(embedder_name)
                if embedder_name in embedders
                else 0,
            )
            agent_settings[
                "embedder"
            ] = embedder_name  # Update the agent_settings with the selected embedder
            if "WEBSEARCH_TIMEOUT" not in agent_settings:
                agent_settings["WEBSEARCH_TIMEOUT"] = 0
            websearch_timeout = st.number_input(
                "Websearch Timeout in seconds.  Set to 0 to disable the timeout and allow the AI to search until it feels it is done.",
                value=int(agent_settings["WEBSEARCH_TIMEOUT"]),
                key="WEBSEARCH_TIMEOUT",
            )
            st.subheader("Provider Settings")
            if provider_name:
                settings = render_provider_settings(
                    agent_settings=agent_settings, provider_name=provider_name
                )
                agent_settings.update(settings)

            extension_settings = render_extension_settings(
                extension_settings=extension_setting_keys, agent_settings=agent_settings
            )

            # Update the extension settings in the agent_settings directly
            agent_settings.update(extension_settings)

            st.subheader("Agent Commands")
            # Fetch the available commands using the `Commands` class
            commands = get_extensions()
            available_commands = ApiClient.get_commands(agent_name=agent_name)
            for command in commands:
                if command not in available_commands:
                    available_commands[command] = False

            # Save the existing command state to prevent duplication
            existing_command_states = {
                command_name: command_status
                for command_name, command_status in available_commands.items()
            }

            all_commands_selected = st.checkbox("Select All Commands")

            for command_name, command_status in available_commands.items():
                if all_commands_selected:
                    available_commands[command_name] = True
                else:
                    toggle_status = st.checkbox(
                        command_name,
                        value=command_status,
                        key=command_name,
                    )
                    available_commands[command_name] = toggle_status

            if st.form_submit_button("Update Agent Settings"):
                try:
                    ApiClient.update_agent_commands(
                        agent_name=agent_name, commands=available_commands
                    )
                    ApiClient.update_agent_settings(
                        agent_name=agent_name, settings=agent_settings
                    )
                    st.success(f"Agent '{agent_name}' updated.")
                except Exception as e:
                    st.error(f"Error updating agent: {str(e)}")
            if st.form_submit_button("Wipe Agent Memories"):
                try:
                    ApiClient.wipe_agent_memories(agent_name=agent_name)
                    st.success(f"Memories of agent '{agent_name}' wiped.")
                except Exception as e:
                    st.error(f"Error wiping agent's memories: {str(e)}")

            if st.form_submit_button("Delete Agent"):
                try:
                    ApiClient.delete_agent(agent_name=agent_name)
                    st.success(f"Agent '{agent_name}' deleted.")
                    st.session_state["new_agent_name"] = ""  # Reset the selected agent
                    st.experimental_rerun()  # Rerun the app to update the agent list
                except Exception as e:
                    st.error(f"Error deleting agent: {str(e)}")
    except Exception as e:
        st.error(f"Error loading agent configuration: {str(e)}")

    # Trigger actions on form submit

else:
    st.error("Agent name is required.")
