import os
import base64
import streamlit as st
from components.selectors import agent_selection
from ApiClient import ApiClient
from components.docs import agixt_docs

st.set_page_config(
    page_title="Agent Training",
    page_icon=":hammer_and_wrench:",
    layout="wide",
)

agixt_docs()

st.header("Agent Training")
agent_name = agent_selection()

if agent_name:
    if agent_name:
        st.markdown("### Learn from a file")
        learn_file_upload = st.file_uploader(
            "Upload a file for the agent to learn from.", accept_multiple_files=True
        )
        if learn_file_upload is not None:
            for learn_file_upload in learn_file_upload.copy():
                learn_file_path = os.path.join(
                    "data", "uploaded_files", learn_file_upload.name
                )
                if not os.path.exists(os.path.dirname(learn_file_path)):
                    os.makedirs(os.path.dirname(learn_file_path))
                with open(learn_file_path, "wb") as f:
                    f.write(learn_file_upload.getbuffer())
                with st.spinner("Learning, please wait..."):
                    ApiClient.learn_file(
                        agent_name=agent_name,
                        file_name=learn_file_path,
                        file_content=base64.b64encode(learn_file_upload.read()).decode(
                            "utf-8"
                        ),
                    )
                st.success(
                    "Agent '"
                    + agent_name
                    + "' has learned from file: "
                    + learn_file_upload.name
                )

        st.markdown("### Learn from a URL")
        learn_url = st.text_input("Enter a URL for the agent to learn from..")
        if st.button("Learn from URL"):
            if learn_url:
                with st.spinner("Learning, please wait..."):
                    learn = ApiClient.learn_url(agent_name=agent_name, url=learn_url)
                st.success(
                    f"Agent '{agent_name}' has learned from the URL {learn_url}."
                )

        st.markdown("### Learn from GitHub Repository")
        github_repo = st.text_input(
            "Enter a GitHub repository for the agent to learn from.. For example, 'Josh-XT/AGiXT'"
        )
        github_branch = st.text_input(
            "Enter a GitHub branch. (Default is main)", value="main"
        )
        github_user = st.text_input(
            "Enter the GitHub user or organization name. (Optional, only necessary for private repositories)"
        )
        github_token = st.text_input(
            "Enter a GitHub personal access token. (Optional, only necessary for private repositories)"
        )
        if st.button("Learn from GitHub Repository"):
            if github_repo:
                with st.spinner("Learning, please wait..."):
                    learn = ApiClient.learn_github_repo(
                        agent_name=agent_name,
                        github_repo=github_repo,
                        github_user=github_user,
                        github_token=github_token,
                    )
                st.success(
                    f"Agent '{agent_name}' has learned from the GitHub repository {github_repo}."
                )

        st.markdown("### Wipe Agent Memory")
        st.markdown(
            "The agent can simply learn too much undesired information at times. If you're having an issue with the context being injected from memory with your agent, try wiping the memory."
        )
        if st.button("Wipe agent memory"):
            ApiClient.wipe_agent_memories(agent_name=agent_name)
            st.success(f"Memory for agent '{agent_name}' has been cleared.")
