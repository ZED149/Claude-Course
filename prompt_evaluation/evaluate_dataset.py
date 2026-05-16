

from dotenv import load_dotenv
from anthropic import Anthropic
import os
import json

load_dotenv(dotenv_path="C:/Users/salma/OneDrive/Desktop/Claude Course/.env")
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


def run_prompt(test_case):
    """Runs the prompt for test case and returns the output

    Args:
        prompt (_type_): _description_
        test_case (_type_): _description_
    """
    prompt = f"""
Please solve the following task:

{test_case}
"""
    messages = []
    add_user_message(messages, prompt)
    reponse = chat(messages)
    return reponse


def run_test_case(test_case):
    """Calls the prompt, then grades the result

    Args:
        test_case (_type_): _description_
    """
    response = run_prompt(test_case)

    # TODO - Grading
    score = 10

    return {
        "response":  response,
        "test_case": test_case,
        "score": score
    }


# evaluate dataset
def evaluate_dataset(dataset):
    # iterate on each task in the dataset
    # and store their response
    
    results = []
    # reading the dataset file
    with open(dataset, "r") as file:
        data = json.load(file)

    for test_case in data:
        response = run_test_case(test_case)
        results.append(response)
    return results

## MAIN

# evaluating the dataset
results = evaluate_dataset("C:/Users/salma/OneDrive/Desktop/Claude Course/prompt_evaluation/dataset.json")
print(json.dumps(results, indent=2))