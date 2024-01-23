import os
import base64
import streamlit as st
from components.selectors import agent_selection
from ApiClient import ApiClient
from components.docs import agixt_docs, predefined_memory_collections

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
        ["Website", "File", "Text", "GitHub Repository", "arXiv"],
    )
    advanced_options = st.checkbox("Show advanced options")
    if advanced_options:
        predefined_memory_collections()
        collection_number = st.number_input(
            "Add memories to collection number (Default is 0)",
            min_value=0,
            value=0,
        )
    else:
        collection_number = 0

    if mode == "Website":
        st.markdown("### Train from Websites")
        st.markdown(
            "The agent will scrape data from the websites you provide into its long term memory."
        )
        learn_url = st.text_area(
            "Enter Website links for the agent to learn from.. (One URL per line)"
        )
        if st.button("Train from Websites"):
            if learn_url:
                with st.spinner("Training, please wait..."):
                    if "\n" in learn_url:
                        learn_url = learn_url.split("\n")
                        for url in learn_url:
                            learn = ApiClient.learn_url(
                                agent_name=agent_name,
                                url=url,
                                collection_number=collection_number,
                            )
                        st.success(
                            f"Agent '{agent_name}' has learned from the following websites: {', '.join(learn_url)}."
                        )
                    else:
                        learn = ApiClient.learn_url(
                            agent_name=agent_name,
                            url=learn_url,
                            collection_number=collection_number,
                        )
                        st.success(
                            f"Agent '{agent_name}' has learned from the website: {learn_url}."
                        )
    elif mode == "File":
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
                        collection_number=collection_number,
                    )
                st.success(
                    "Agent '"
                    + agent_name
                    + "' has learned from file: "
                    + learn_file_upload.name
                )
    elif mode == "Text":
        st.markdown("### Train from Text")
        st.markdown(
            "The agent will read the text you provide into its long term memory."
        )
        user_input = st.text_input(
            "Enter some short text, description, or question to associate the learned text with."
        )
        learn_text = st.text_area("Enter some text for the agent to learn from.")
        if st.button("Train from Text"):
            if learn_text:
                with st.spinner("Training, please wait..."):
                    learn = ApiClient.learn_text(
                        agent_name=agent_name,
                        user_input=user_input,
                        text=learn_text,
                        collection_number=collection_number,
                    )
                st.success(f"Agent '{agent_name}' has learned from the text provided.")

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
            use_agent_settings = st.checkbox(
                "Use agent settings for GitHub credentials", value=True
            )
            if not use_agent_settings:
                github_user = st.text_input(
                    "Enter the GitHub user or organization name."
                )
                github_token = st.text_input("Enter a GitHub personal access token.")
        else:
            github_user = None
            github_token = None
            use_agent_settings = False
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
                        use_agent_settings=use_agent_settings,
                        collection_number=collection_number,
                    )
                st.success(
                    f"Agent '{agent_name}' has learned from the GitHub repository {github_repo}."
                )

    elif mode == "arXiv":
        st.markdown("### Train from arXiv")
        st.markdown(
            "The agent will download PDFs from arXiv based on the query you provide into its long term memory."
        )
        use_arxiv_ids = st.checkbox("Use arXiv IDs instead of a query", value=False)
        if use_arxiv_ids:
            arxiv_ids = st.text_area(
                "Enter arXiv IDs for the agent to learn from.. (Comma separated IDs)"
            )
            if st.button("Train from arXiv IDs"):
                if arxiv_ids:
                    with st.spinner(
                        f"Training {agent_name}, please wait... This can take some time depending on the size of the repository."
                    ):
                        arxiv_ids = arxiv_ids.replace("\n", ",")
                        arxiv_ids = arxiv_ids.replace(" ", "")
                        learn = ApiClient.learn_arxiv(
                            agent_name=agent_name,
                            arxiv_id=arxiv_ids,
                            collection_number=collection_number,
                        )
                        st.success(
                            f"Agent '{agent_name}' has learned from the arXiv ID: {arxiv_ids}."
                        )
        else:
            query = st.text_input(
                "Enter a query for the agent to learn from.. For example, 'machine learning'"
            )
            max_results = st.number_input(
                "Enter the maximum number of results to return (Default is 5)",
                min_value=1,
                value=5,
            )
            if st.button("Train from arXiv"):
                with st.spinner(
                    f"Training {agent_name}, please wait... This can take some time.."
                ):
                    learn = ApiClient.learn_arxiv(
                        agent_name=agent_name,
                        query=query,
                        max_results=max_results,
                        collection_number=collection_number,
                    )
