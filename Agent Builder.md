# Agent Builder

Agent builder will allow you to create an AI agent pipeline without code in a simple interface.

[Providers](https://josh-xt.github.io/AGiXT/2-Concepts/02-Providers.html) are the services that run the AI models that we interact with in the pipeline. The agent builder will allow you to select the providers you want to use in your pipeline and configure them.

Components of the pipeline:

- Selection of Language provider, model, and settings
- Selection of Vision provider, model, and settings (Optional)
- Selection of Speech to Text provider and model
- Selection of Text to Speech provider, model, and voice if applicable
- Selection of Image Generation provider, model, and settings if applicable (Optional)
- Enable or disable websearch and set websearch depth if enabled (Optional)
- Set a helper agent to assist the main agent in the pipeline (Optional)
- Selection of extensions that the agent will have access to and configure them with the necessary credentials
- Toggling each command that the agent will have access to autonomously execute from selected extensions if any
- Add training data to the agent if needed from files, GitHub repositories, websites, arXiv papers, or YouTube videos. (Optional)
- Selection of [Chat Completions Mode (prompt, chain, or command)](https://josh-xt.github.io/AGiXT/2-Concepts/04-Chat%20Completions.html)
  - The `prompt` mode requires selection of prompt category and the prompt template to be used. `user_input` in prompt templates will be the user input variable.
  - The `chain` mode requires selection of an existing chain to use that uses a selected workflow of prompts and commands. `user_input` for the chain will be the user input variable.
  - The `command` mode requires selection of an existing command to use, the default arguments for the command, and the variable that will be used for the user input.

Once complete, the agent is essentially a multimodal AI model accessible through an OpenAI chat completions API endpoint using your AGiXT server.

```python
import openai

openai.base_url = "http://localhost:7437/v1/"
openai.api_key = "Your AGiXT API Key"

response = openai.chat.completions.create(
    model="THE AGENTS NAME GOES HERE",
    messages=[
        {
            "role": "user",
            "create_image": "true",  # Generates an image with the agents designated image_provider and sends image with response.
            "context_results": 5,  # Optional, default will be 5 if not set.
            "websearch": False,  # Set to true to enable websearch, false to disable. Default is false if not set.
            "websearch_depth": 0,  # Set to the number of depth you want to websearch to go (3 would go 3 links deep per link it scrapes)
            "browse_links": True,  # Will make the agent scrape any web URLs the user puts in chat.
            "content": [
                {"type": "text", "text": "YOUR USER INPUT TO THE AGENT GOES HERE"},
                {
                    "type": "image_url",
                    "image_url": {  # Will download the image and send it to the vision model
                        "url": f"https://www.visualwatermark.com/images/add-text-to-photos/add-text-to-image-3.webp"
                    },
                },
                {
                    "type": "text_url",  # Or just "url"
                    "text_url": {  # Content of the text or URL for it to be scraped
                        "url": "https://agixt.com"
                    },
                    "collection_number": 0,  # Optional field, defaults to 0.
                },
                {
                    "type": "application_url",
                    "application_url": {  # Will scrape mime type `application` into the agent's memory
                        "url": "data:application/pdf;base64,base64_encoded_pdf_here"
                    },
                    "collection_number": 0,  # Optional field, defaults to 0.
                },
                {
                    "type": "audio_url",
                    "audio_url": {  # Will transcribe the audio and send it to the agent
                        "url": "data:audio/wav;base64,base64_encoded_audio_here"
                    },
                },
            ],
        },
    ],
    max_tokens=4096,
    temperature=0.7,
    top_p=0.9,
    user="THE CONVERSATION NAME", # Set to the conversation name you want to use
)
print(response.choices[0].message.content)
```
