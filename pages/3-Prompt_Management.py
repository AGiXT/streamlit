import streamlit as st
from ApiClient import ApiClient
from components.docs import agixt_docs, predefined_injection_variables


st.set_page_config(
    page_title="Prompt Management",
    page_icon=":scroll:",
    layout="wide",
)
agixt_docs()

st.header("Prompt Management")

prompt_categories = ApiClient.get_prompt_categories()
action = st.selectbox("Action", ["Create New Prompt", "Modify Prompt", "Delete Prompt"])
new_prompt_category = st.checkbox("New Prompt Category", value=False)
if new_prompt_category:
    prompt_category = st.text_input("New Prompt Category Name")
    if st.button("Create Prompt Category"):
        prompt_list = ApiClient.get_prompts(prompt_category=prompt_category)
        st.success(
            f"Prompt category '{prompt_category}' created. Uncheck the `New Prompt Category` add new prompts."
        )
else:
    prompt_category = st.selectbox(
        "Select Prompt Category",
        prompt_categories,
        index=prompt_categories.index("Default"),
    )
    if prompt_category != "Default":
        if st.button("Delete Prompt Category"):
            # TODO: Create this endpoint on the back end and in the SDK
            # ApiClient.delete_prompt_category(prompt_category)
            st.success(f"Prompt category deletion functionality not yet implemented.")
    prompt_list = ApiClient.get_prompts(prompt_category=prompt_category)
    if action == "Create New Prompt":
        # Import prompt button
        prompt_file = st.file_uploader("Import Prompt", type=["txt"])
        if prompt_file:
            prompt_name = prompt_file.name.split(".")[0]
            prompt_content = prompt_file.read().decode("utf-8")
            ApiClient.add_prompt(prompt_name=prompt_name, prompt=prompt_content)
            st.success(f"Prompt '{prompt_name}' added.")
        prompt_name = st.text_input("Prompt Name")
        prompt_content = st.text_area("Prompt Content", height=300)

    elif action == "Modify Prompt":
        prompt_name = st.selectbox("Existing Prompts", prompt_list)
        prompt_content = st.text_area(
            "Prompt Content",
            ApiClient.get_prompt(prompt_name=prompt_name) if prompt_name else "",
            height=300,
        )
        export_button = st.download_button(
            "Export Prompt", data=prompt_content, file_name=f"{prompt_name}.txt"
        )
    elif action == "Delete Prompt":
        prompt_name = st.selectbox("Existing Prompts", prompt_list)
        prompt_content = None

    if st.button("Perform Action"):
        if prompt_name and (prompt_content or action == "Delete Prompt"):
            if action == "Create New Prompt":
                ApiClient.add_prompt(prompt_name=prompt_name, prompt=prompt_content)
                st.success(f"Prompt '{prompt_name}' added.")
            elif action == "Modify Prompt":
                ApiClient.update_prompt(prompt_name=prompt_name, prompt=prompt_content)
                st.success(f"Prompt '{prompt_name}' updated.")
            elif action == "Delete Prompt":
                ApiClient.delete_prompt(prompt_name)
                st.success(f"Prompt '{prompt_name}' deleted.")
        else:
            st.error("Prompt name and content are required.")

st.markdown("### Usage Instructions")
st.markdown(
    """
To create dynamic prompts that can have user inputs, you can use curly braces `{}` in your prompt content. 
Anything between the curly braces will be considered as an input field. For example:

```python
"Hello, my name is {name} and I'm {age} years old."
```
In the above prompt, `name` and `age` will be the input arguments. These arguments can be used in chains.
"""
)
show_injection_var_docs = st.checkbox("Show Prompt Injection Variable Documentation")
if show_injection_var_docs:
    predefined_injection_variables()
