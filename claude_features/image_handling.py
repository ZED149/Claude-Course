

'''
This file contains the basic implementation of the image handling in claude API
'''

from anthropic import Anthropic
from anthropic.types import Message
from dotenv import load_dotenv
import os
import re
import base64

load_dotenv("C:/Users/salma/OneDrive/Desktop/Claude Course/.env")

#KEYS
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# CLIENTS
anthropic_client = Anthropic(api_key=CLAUDE_API_KEY)

MESSAGES = []
model = "claude-sonnet-4-6"


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
        "content": response.content if isinstance(response, Message) else response
    }
    messages.append(assistant_message)

# chat
def chat(messages, system=None, temperature=1.0, stop_sequences=None):
    params = {
        "model": model,
        "max_tokens": 1024,
        "temperature": temperature,
        "messages": messages
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    response = anthropic_client.messages.create(**params)
    return response


# MAIN

# reading the image file
with open("zms_logo.png", "rb") as file:
    image_bytes = base64.standard_b64encode(file.read()).decode('utf-8')

# creating the user message
message = [
    # Image Block
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": image_bytes
        }
    },
    # Text Block
    {
        "type": "text",
        "text": "What do you see in the image?"
    }
]

# adding user message to the list
add_user_message(MESSAGES, message)

# chating to the claude
response = chat(messages=MESSAGES)

print(response)

# adding the response back to the list
add_assitant_message(MESSAGES, response)