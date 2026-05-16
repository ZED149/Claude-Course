

from dotenv import load_dotenv
from anthropic import Anthropic
import os
import json

load_dotenv(dotenv_path=".env")
API_KEY = os.getenv("API_KEY")
model = "claude-haiku-4-5"
client = Anthropic(api_key=API_KEY)
MESSAGES = []


# add user message
def add_user_message(messages, text):
    """Addd the text(prompt) to the list of messages.

    Args:
        messages (_type_): List of messages.
        text (_type_): Prompt to be sent and add to the messages
    """
    user_message = {
        "role": "user",
        "content": text
    }
    messages.append(user_message)


# add assistant message
def add_assitant_message(messages, text):
    """Adds the text sent back by the api to the list of messages.

    Args:
        messages (_type_): List of messages
        text (_type_): response sent back by the api
    """
    assistant_message = {
        "role": "assistant",
        "content": text
    }
    messages.append(assistant_message)

# chat
def chat(messages, system=None, temperature=1.0, stop_sequences=None):
    params = {
        "model": model,
        "max_tokens": 300,
        "temperature": temperature,
        "messages": messages
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    with client.messages.stream(
        **params
    ) as stream:
        for text in stream.text_stream:
            # print(text, end="", flush=True)
            pass
    
    return stream.get_final_message().content[0].text

# generate dataset
def generate_dataset():
    prompt = """
Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
    {
        "task": "Description of task",
    },
    ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
* Focus on tasks that do not require writing much code

Please generate 3 objects.
"""
    add_user_message(MESSAGES, prompt)
    add_assitant_message(MESSAGES, "```json")
    answer = chat(MESSAGES, stop_sequences=["```"])
    return json.loads(answer)



## MAIN

# genrating dataset for evaluation, when using claude for this purpose, it is recommended to use haiku model 
# as it has lower latency and no heavy intelligence is required
dataset = generate_dataset()

# writing that data set to a file
with open("prompt_evaluation/dataset.json", "w+") as file:
    file.write(json.dumps(dataset, indent=2))