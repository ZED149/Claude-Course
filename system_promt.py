

from dotenv import load_dotenv
from anthropic import Anthropic
import os

load_dotenv(dotenv_path=".env")
API_KEY = os.getenv("API_KEY")
model = "claude-sonnet-4-6"
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
def chat(messages, system=None):
    """Sends a request to the server

    Args:
        messages (_type_): List of messages to be sent
    """
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages
    }
    if system:
        params["system"] = system

    response = client.messages.create(
        **params
    )
    return response.content[0].text


## MAIN

add_user_message(MESSAGES, "Write a Python function that checks for a string for duplciate characters")
answer = chat(MESSAGES, system="Act a programming teacher and teach student by doing the practical rather than explaining it all at once. Do it in chunks and explain with simple examples and code snippets.")
add_assitant_message(MESSAGES, answer)
print(answer)