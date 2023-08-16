import os
import streamlit as st
from components.selectors import agent_selection
from ApiClient import ApiClient
from components.docs import agixt_docs
from datetime import datetime

st.set_page_config(
    page_title="Memory Management",
    page_icon=":hammer_and_wrench:",
    layout="wide",
)

agixt_docs()
try:
    with open(os.path.join("session.txt"), "r") as f:
        agent_name = f.read().strip()
except:
    agent_name = "OpenAI"
st.header("Memory Management")
st.markdown(
    "The `Search Query` is essentially what you would type to the AI when you're talking to it, this will show you what results would be injected in context for anything you say to the AI based on its memory collection. This will find similar results to anything you type with relevance score from memory. You can choose to delete memories from the memory collection here."
)
agent_name = agent_selection()
if agent_name:
    if "advanced_options" not in st.session_state:
        st.session_state["advanced_options"] = False

    st.session_state["advanced_options"] = st.checkbox(
        "Advanced Options", value=st.session_state["advanced_options"]
    )
    if st.session_state["advanced_options"]:
        collection_number = st.number_input(
            "Inject memories from collection number (Default is 0)",
            min_value=0,
            value=0,
        )

        limit = st.number_input(
            "Limit (Default is 10)", min_value=1, max_value=100, value=10
        )
        min_relevance_score = st.number_input(
            "Minimum relevance score (Default is 0.0)",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
        )
    else:
        collection_number = 0
        limit = 10
        min_relevance_score = 0.0

    with st.form(key="query_memory_form"):
        st.session_state["memory_query"] = st.text_input(
            "Search Query",
            value=""
            if "memory_query" not in st.session_state
            else st.session_state["memory_query"],
        )
        if (
            st.form_submit_button("Query Memory")
            and st.session_state["memory_query"] != ""
        ):
            response = ApiClient.get_agent_memories(
                agent_name=agent_name,
                user_input=st.session_state["memory_query"],
                limit=limit,
                min_relevance_score=min_relevance_score,
                collection_number=collection_number,
            )
            st.session_state["response"] = response
        elif "response" in st.session_state:
            response = st.session_state["response"]
        else:
            response = []
    if response:
        st.markdown(f"**Total Memories:** `{len(response)}`")
    for memory in response:
        if "id" in memory:
            with st.form(key=memory["id"]):
                if "timestamp" in memory:
                    try:
                        memory["timestamp"] = datetime.strptime(
                            memory["timestamp"], "%Y-%m-%dT%H:%M:%S.%f"
                        ).strftime("%B %d, %Y, %I:%M:%S %p")
                    except:
                        memory["timestamp"] = memory["timestamp"]
                    st.markdown(f"**Created on** {memory['timestamp']}")
                st.markdown(f"**Relevance Score:** {memory['relevance_score']}")
                st.markdown(f"**Memory ID:** `{memory['id']}`")
                st.markdown(f"**Memory:**")
                st.markdown(f"```{memory['additional_metadata']}```")
                if st.form_submit_button("Delete Memory"):
                    res = ApiClient.delete_agent_memory(
                        agent_name=agent_name,
                        memory_id=memory["id"],
                        collection_number=collection_number,
                    )
                    st.session_state["response"] = ApiClient.get_agent_memories(
                        agent_name=agent_name,
                        user_input=st.session_state["memory_query"],
                        limit=limit,
                        min_relevance_score=min_relevance_score,
                        collection_number=collection_number,
                    )
                    st.experimental_rerun()
