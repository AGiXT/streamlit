import streamlit as st
import os
import uuid
import logging
import html
import re
import base64
import json
from components.docs import predefined_memory_collections
from agixtsdk import AGiXTSDK
from Globals import getenv


class AGiXTSelectors:
    def __init__(self, ApiClient: AGiXTSDK):
        self.sdk = ApiClient
        self.skip_args = [
            "command_list",
            "context",
            "COMMANDS",
            "date",
            "conversation_history",
            "agent_name",
            "working_directory",
            "helper_agent_name",
        ]
        self.theme = {
            "primaryColor": getenv("PRIMARY_COLOR"),
            "backgroundColor": getenv("BACKGROUND_COLOR"),
            "secondaryBackgroundColor": getenv("SECONDARY_BACKGROUND_COLOR"),
            "textColor": getenv("TEXT_COLOR"),
            "font": getenv("FONT")
        }

    def cached_get_extensions(self):
        return self.sdk.get_extensions()

    def get_history(self, agent_name, conversation_name):
        message_container_css = """
            <style>
            .message-container {
                min-height: 200px;
                height: calc(100vh - 900px);
                overflow: auto;
                overflow-y: scroll;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
            }
            .message {
                margin-bottom: 10px;
            }
            .user-message {
                background-color: #0f0f0f;
                padding: 5px;
                border-radius: 5px;
            }
            .agent-message {
                background-color: #3a3b3c;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            </style>
        """
        st.write(message_container_css, unsafe_allow_html=True)
        with st.container():
            message_container = "<div class='message-container'>"
            try:
                history = self.sdk.get_conversation(
                    agent_name=agent_name,
                    conversation_name=conversation_name,
                    limit=100,
                    page=1,
                )
                if isinstance(history, str):
                    st.write(history)
                else:
                    history.reverse()
                    for item in history:
                        item["message"] = html.escape(item["message"])
                        item["message"] = item["message"].replace(r"\n", "<br>")
                        code_block_match = re.search(
                            r"```(.*)```", item["message"], re.DOTALL
                        )
                        if code_block_match:
                            code_message = code_block_match.group(1)
                            item["message"] = re.sub(
                                r"```.*```",
                                f"<pre><code>{code_message}</code></pre>",
                                item["message"],
                                flags=re.DOTALL,
                            )
                        message = f"{item['timestamp']}<br><b>{item['role']}:</b><br>{item['message']}"
                        if "#GENERATED_IMAGE:" in item["message"]:
                            image_content = re.search(
                                r"#(.*?)(?=\n|$)", item["message"]
                            )
                            image_content = image_content.replace(
                                "GENERATED_IMAGE:", ""
                            )
                            image_content = base64.b64encode(image_content).decode(
                                "utf-8"
                            )
                            message = f"{item['timestamp']}<br><b>{item['role']}:</b><br><img src='data:image/png;base64,{image_content}'>"
                        if agent_name in item["role"]:
                            message_container += (
                                f"<div class='message agent-message'>{message}</div>"
                            )
                        else:
                            message_container += (
                                f"<div class='message user-message'>{message}</div>"
                            )
            except Exception as e:
                print(e)
            message_container += "</div>"
            st.write(message_container, unsafe_allow_html=True)

    def build_args(
        self,
        args: dict = {},
        prompt: dict = {},
        step_number: int = 0,
        show_user_input: bool = True,
    ):
        if not show_user_input:
            self.skip_args.append("user_input")
            self.skip_args.append("input")
        return {
            arg: st.text_area(
                arg, value=prompt.get(arg, ""), key=f"{arg}_{step_number}_{uuid.uuid4()}"
            )
            for arg in args
            if arg not in self.skip_args
        }

    def prompt_options(self, prompt: dict = {}, step_number: int = 0):
        if prompt == {}:
            ops = False
        else:
            for opt in [
                "shots",
                "context_results",
                "browse_links",
                "websearch",
                "websearch_depth",
                "disable_memory",
                "inject_memories_from_collection_number",
                "conversation_results",
            ]:
                if opt not in prompt:
                    ops = False
                    break
                else:
                    ops = True
        advanced_options = st.checkbox(
            "Show Advanced Options", value=ops, key=f"advanced_options_{step_number}"
        )
        if advanced_options:
            conversation_results = st.number_input(
                "How many conversation results to inject (Default is 5)",
                min_value=1,
                value=(
                    5
                    if "conversation_results" not in prompt
                    else int(prompt["conversation_results"])
                ),
                key=f"conversation_results_{step_number}",
            )
            shots = st.number_input(
                "Shots (How many times to ask the agent)",
                min_value=1,
                value=1 if "shots" not in prompt else int(prompt["shots"]),
                key=f"shots_{step_number}",
            )
            predefined_memory_collections()
            inject_memories_from_collection_number = st.text_input(
                "Inject memories from collection (Default is 0)",
                value=(
                    "0"
                    if "inject_memories_from_collection_number" not in prompt
                    else str(prompt["inject_memories_from_collection_number"])
                ),
                key=f"inject_memories_from_collection_number_{step_number}",
            )
            context_results = st.number_input(
                "How many long term memories to inject (Default is 5)",
                min_value=1,
                value=(
                    5
                    if "context_results" not in prompt
                    else int(prompt["context_results"])
                ),
                key=f"context_results_{step_number}",
            )
            browse_links = st.checkbox(
                "Enable Browsing Links in the user input",
                value=False if "browse_links" not in prompt else prompt["browse_links"],
                key=f"browse_links_{step_number}",
            )
            websearch = st.checkbox(
                "Enable websearch",
                value=False if "websearch" not in prompt else prompt["websearch"],
                key=f"websearch_{step_number}",
            )
            if websearch:
                try:
                    default_depth = int(prompt["websearch_depth"])
                except:
                    default_depth = 2
                websearch_depth = st.number_input(
                    "Websearch depth",
                    min_value=0,
                    value=int(default_depth),
                    key=f"websearch_depth_{step_number}",
                )
            else:
                websearch_depth = 0
            if "disable_memory" not in prompt:
                enable_memory = st.checkbox(
                    "Enable Memory Training (Any messages sent to and from the agent will be added to memory if enabled.)",
                    value=False,
                    key=f"enable_memory_{step_number}",
                )
            else:
                enable_memory = st.checkbox(
                    "Enable Memory Training (Any messages sent to and from the agent will be added to memory if enabled.)",
                    value=True if prompt["disable_memory"] == False else False,
                    key=f"enable_memory_{step_number}",
                )
        else:
            shots = 1
            context_results = 5
            browse_links = False
            websearch = False
            websearch_depth = 0
            enable_memory = False
            inject_memories_from_collection_number = "0"
            conversation_results = 5
        return {
            "shots": shots,
            "context_results": context_results,
            "browse_links": browse_links,
            "websearch": websearch,
            "websearch_depth": websearch_depth,
            "disable_memory": (True if enable_memory == False else False),
            "inject_memories_from_collection_number": inject_memories_from_collection_number,
            "conversation_results": conversation_results,
        }

    def prompt_selection(
        self, prompt: dict = {}, step_number: int = 0, show_user_input: bool = True
    ):
        prompt_categories = self.sdk.get_prompt_categories()
        prompt_category = st.selectbox(
            "Select Prompt Category",
            prompt_categories,
            index=prompt_categories.index("Default"),
            key=f"step_{step_number}_prompt_category",
        )
        available_prompts = self.sdk.get_prompts(prompt_category=prompt_category)
        try:
            custom_input_index = available_prompts.index("Custom Input")
        except:
            custom_input_index = 0
        prompt_name = st.selectbox(
            "Select Custom Prompt",
            available_prompts,
            index=(
                available_prompts.index(prompt.get("prompt_name", ""))
                if "prompt_name" in prompt
                else custom_input_index
            ),
            key=f"step_{step_number}_prompt_name",
        )
        prompt_content = self.sdk.get_prompt(
            prompt_name=prompt_name, prompt_category=prompt_category
        )
        prompt_content = prompt_content.replace("```", "` ` `")
        st.markdown(
            f"""
    **Prompt Content**
    ```
    {prompt_content}
    ```
            """
        )
        prompt_args_values = self.prompt_options(prompt=prompt, step_number=step_number)
        if prompt_name:
            prompt_args = self.sdk.get_prompt_args(
                prompt_name=prompt_name, prompt_category=prompt_category
            )
            args = self.build_args(
                args=prompt_args,
                prompt=prompt,
                step_number=step_number,
                show_user_input=show_user_input,
            )
            new_prompt = {
                "prompt_name": prompt_name,
                "prompt_category": prompt_category,
                **args,
                **prompt_args_values,
            }
            return new_prompt

    def command_selection(
        self, prompt: dict = {}, step_number: int = 0, show_user_input: bool = True
    ):
        agent_commands = self.cached_get_extensions()
        available_commands = []
        for commands in agent_commands:
            for command in commands["commands"]:
                available_commands.append(command["friendly_name"])

        command_name = st.selectbox(
            "Select Command",
            [""] + available_commands,
            key=f"command_name_{step_number}",
            index=(
                available_commands.index(prompt.get("command_name", "")) + 1
                if "command_name" in prompt
                else 0
            ),
        )

        if command_name:
            command_args = self.sdk.get_command_args(command_name=command_name)
            args = self.build_args(
                args=command_args,
                prompt=prompt,
                step_number=step_number,
                show_user_input=show_user_input,
            )
            new_prompt = {
                "command_name": command_name,
                "command_args": args,
            }
            return new_prompt

    def chain_selection(
        self, prompt: dict = {}, step_number: int = 0, show_user_input: bool = True
    ):
        available_chains = self.sdk.get_chains()
        chain_name = st.selectbox(
            "Select Chain",
            available_chains,
            index=available_chains.index(prompt["chain"]) if "chain" in prompt else 0,
            key=f"step_{step_number}_chain_name",
        )
        if show_user_input:
            user_input = st.text_area(
                "User Input",
                value=prompt.get("input", ""),
                key=f"user_input_{step_number}",
            )
        args = {}
        if chain_name:
            chain_args = self.sdk.get_chain_args(chain_name=chain_name)
            for arg in chain_args:
                if arg not in self.skip_args and arg != "user_input":
                    override_arg = st.checkbox(f"Override `{arg}` argument.")
                    if override_arg:
                        args[arg] = st.text_area(arg)
            args["chain"] = chain_name
            if show_user_input:
                args["input"] = user_input
        if args != {}:
            args_copy = args.copy()
            for arg in args_copy:
                if args[arg] == "":
                    del args[arg]
        return args

    def agent_selection(
        self, key: str = "select_learning_agent", heading: str = "Agent Name"
    ):
        # Load the previously selected agent name
        try:
            with open(os.path.join("session.txt"), "r") as f:
                previously_selected_agent = f.read().strip()
        except FileNotFoundError:
            previously_selected_agent = None

        # Get the list of agent names
        agent_names = [agent["name"] for agent in self.sdk.get_agents()]

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
                    st.rerun()
                except Exception as e:
                    logging.info(e)
        return selected_agent

    def helper_agent_selection(
        self,
        current_agent: str,
        key: str = "select_learning_agent",
        heading: str = "Agent Name",
        agent_config={},
    ):
        agent_names = [agent["name"] for agent in self.sdk.get_agents()]
        agent_settings = agent_config.get("settings", {})
        helper_agent = agent_settings.get("helper_agent_name", current_agent)
        # Create the selectbox
        try:
            agent_index = agent_names.index(helper_agent) + 1
        except:
            agent_index = 0
        selected_agent = st.selectbox(
            heading,
            options=[""] + agent_names,
            index=agent_index,
            key=key,
        )
        return selected_agent

    def conversation_selection(self, agent_name):
        if not os.path.exists("conversation.txt"):
            with open("conversation.txt", "w") as f:
                f.write("")
        try:
            with open(os.path.join("conversation.txt"), "r") as f:
                conversation = f.read().strip()
        except FileNotFoundError:
            conversation = ""
        conversations = self.sdk.get_conversations(
            agent_name=agent_name if agent_name else "OpenAI"
        )
        # New conversation checkbox
        with st.container():
            new_convo = st.checkbox("New Conversation", value=False)
            if len(conversations) == 0 or new_convo:
                conversation_name = st.text_input("Conversation Name", value="")
                if st.button("Create New Conversation"):
                    self.sdk.new_conversation(
                        agent_name=agent_name if agent_name else "OpenAI",
                        conversation_name=conversation_name,
                        conversation_content=[],
                    )
                    with open(os.path.join("conversation.txt"), "w") as f:
                        f.write(conversation_name)
                    st.success(
                        "Conversation created successfully. Please uncheck 'New Conversation' to interact."
                    )
                    return conversation_name
            else:
                conversation_name = st.selectbox(
                    "Choose a conversation",
                    conversations,
                    index=(
                        conversations.index(conversation)
                        if conversation in conversations
                        else 0
                    ),
                )
                if st.button("Delete Conversation"):
                    self.sdk.delete_conversation(
                        agent_name=agent_name,
                        conversation_name=st.session_state["conversation"],
                    )
                    with open(os.path.join("conversation.txt"), "w") as f:
                        f.write("")
                    st.success("Conversation history deleted successfully.")
                    st.rerun()
                chat_history = self.get_history(
                    agent_name=agent_name, conversation_name=conversation_name
                )
        if conversation != conversation_name:
            with open(os.path.join("conversation.txt"), "w") as f:
                f.write(conversation_name)
            st.rerun()
        return conversation_name

    def add_new_step(self, chain_name, step_number, agents):
        st.markdown(f"## Add Chain Step {step_number}")
        agent_name = st.selectbox(
            "Select Agent",
            options=[""] + [agent["name"] for agent in agents],
            index=0,
            key="add_step_agent_name",
        )
        prompt_type = st.selectbox(
            "Select Step Type",
            [""] + ["Command", "Prompt", "Chain"],
            key="add_step_prompt_type",
        )

        if prompt_type == "Command":
            prompt = self.command_selection(step_number=step_number)
        elif prompt_type == "Prompt":
            prompt = self.prompt_selection(step_number=step_number)
        elif prompt_type == "Chain":
            prompt = self.chain_selection(step_number=step_number)
        else:
            prompt = {}
        if st.button("Add New Step", key=f"add_step_{step_number}"):
            if chain_name and step_number and agent_name and prompt_type and prompt:
                self.sdk.add_step(
                    chain_name=chain_name,
                    step_number=step_number,
                    agent_name=agent_name,
                    prompt_type=prompt_type,
                    prompt=prompt,
                )
                st.success(f"Step added to chain '{chain_name}'.")
                st.rerun()
            else:
                st.error("All fields are required.")

    def modify_step(self, chain_name, step, agents):
        step_number = step["step"]
        agent_name = step["agent_name"]
        prompt_type = step["prompt_type"]
        step_prompt = step["prompt"]
        modify_step_number = st.number_input(
            "Step Number",
            min_value=1,
            step=1,
            value=step_number,
            key=f"step_num_{step_number}",
        )
        modify_agent_name = st.selectbox(
            "Select Agent",
            options=[""] + [agent["name"] for agent in agents],
            index=(
                ([agent["name"] for agent in agents].index(agent_name) + 1)
                if agent_name in [agent["name"] for agent in agents]
                else 0
            ),
            key=f"agent_name_{step_number}",
        )
        modify_prompt_type = st.selectbox(
            "Select Step Type",
            options=["", "Command", "Prompt", "Chain"],
            index=["", "Command", "Prompt", "Chain"].index(prompt_type),
            key=f"prompt_type_{step_number}",
        )
        if prompt_type == "Command":
            prompt = self.command_selection(prompt=step_prompt, step_number=step_number)
        elif prompt_type == "Prompt":
            prompt = self.prompt_selection(prompt=step_prompt, step_number=step_number)
        elif prompt_type == "Chain":
            prompt = self.chain_selection(prompt=step_prompt, step_number=step_number)
        else:
            prompt = {}
        if st.button("Modify Step", key=f"modify_step_{step_number}"):
            if chain_name and step_number and agent_name and prompt_type and prompt:
                self.sdk.update_step(
                    chain_name=chain_name,
                    step_number=modify_step_number,
                    agent_name=modify_agent_name,
                    prompt_type=modify_prompt_type,
                    prompt=prompt,
                )
                st.success(f"Step modified in chain '{chain_name}'.")
                st.rerun()
            else:
                st.error("All fields are required.")

    def modify_chain(self, chain_name, agents):
        if chain_name:
            chain = self.sdk.get_chain(chain_name=chain_name)
            export_button = st.download_button(
                "Export Chain",
                data=json.dumps(chain, indent=4),
                file_name=f"{chain_name}.json",
                mime="application/json",
            )
            st.markdown(f"## Modifying Chain: {chain_name}")
            if chain:
                for step in chain["steps"]:
                    if step is not None:
                        new_step = self.modify_step(
                            chain_name=chain_name,
                            step=step,
                            agents=agents,
                        )

            if len(chain["steps"]) > 0:
                step_number = (
                    max([s["step"] for s in chain["steps"]]) + 1 if chain else 1
                )
            else:
                step_number = 1

            add_step = self.add_new_step(
                chain_name=chain_name,
                step_number=step_number,
                agents=agents,
            )
        else:
            st.warning("Please select a chain to manage steps.")
