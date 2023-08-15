import os
import base64
import streamlit as st
from components.selectors import agent_selection
from ApiClient import ApiClient
from components.docs import agixt_docs

st.set_page_config(
    page_title="Memory Management",
    page_icon=":hammer_and_wrench:",
    layout="wide",
)

agixt_docs()

st.header("Memory Management")
agent_name = agent_selection()
if agent_name:
    advanced_options = st.checkbox("Advanced Options")
    if advanced_options:
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
            max_value=100.0,
            value=0.0,
        )
    else:
        collection_number = 0
        limit = 10
        min_relevance_score = 0.0
    user_input = st.text_input(
        "Search string (This will find similar results to anything you type with relevance score from memory.)"
    )
    if st.button("Query Memory"):
        response = ApiClient.get_agent_memories(
            agent_name=agent_name,
            user_input=user_input,
            limit=limit,
            min_relevance_score=min_relevance_score,
            collection_number=collection_number,
        )
        if response:
            for memory in response:
                if "id" in memory:
                    st.markdown(f"**Memory ID:** `{memory['id']}`")
                    st.markdown(f"**Relevance Score:** `{memory['relevance_score']}`")
                    st.markdown(f"**Memory Data:**")
                    st.markdown(f"```{memory['memory_data']}```")
                    if st.button("Delete Memory"):
                        ApiClient.delete_agent_memory(
                            agent_name=agent_name,
                            memory_id=memory["id"],
                            collection_number=collection_number,
                        )
                        st.success("Memory deleted.")
