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
    mode = st.selectbox(
        "Select Training Source",
        ["File", "Website", "GitHub Repository"],
    )
    if mode == "File":
        st.markdown("### Train from Files")
        st.markdown(
            "The agent will accept zip files, any kind of plain text file, PDF files, CSV, XLSX, and more. The agent will read the files into its long term memory."
        )
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
                with st.spinner(
                    "Training, please wait... This may take awhile depending on the size of the file."
                ):
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
    elif mode == "Website":
        st.markdown("### Train from Website")
        st.markdown(
            "The agent will scrape data from the website you provide into its long term memory."
        )
        learn_url = st.text_input("Enter a URL for the agent to learn from..")
        if st.button("Train from Website"):
            if learn_url:
                with st.spinner("Training, please wait..."):
                    learn = ApiClient.learn_url(agent_name=agent_name, url=learn_url)
                st.success(
                    f"Agent '{agent_name}' has learned from the URL {learn_url}."
                )
    elif mode == "GitHub Repository":
        st.markdown("### Train from GitHub Repository")
        st.markdown(
            "The agent will download all files from the GitHub repository you provide into its long term memory."
        )
        github_repo = st.text_input(
            "Enter a GitHub repository for the agent to learn from.. For example, 'Josh-XT/AGiXT'"
        )
        branch = st.checkbox("Use a branch other than `main`")
        if branch:
            github_branch = st.text_input("Enter a GitHub branch. (Default is main)")
        else:
            github_branch = "main"
        # Private repository checkbox
        private_repo = st.checkbox("Private repository")
        if private_repo:
            github_user = st.text_input("Enter the GitHub user or organization name.")
            github_token = st.text_input("Enter a GitHub personal access token.")
        else:
            github_user = None
            github_token = None
        if st.button("Train from GitHub Repository"):
            if github_repo:
                with st.spinner(
                    f"Training {agent_name}, please wait... This can take some time depending on the size of the repository."
                ):
                    learn = ApiClient.learn_github_repo(
                        agent_name=agent_name,
                        github_repo=github_repo,
                        github_user=github_user,
                        github_token=github_token,
                    )
                st.success(
                    f"Agent '{agent_name}' has learned from the GitHub repository {github_repo}."
                )
