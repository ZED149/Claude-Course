

from dotenv import load_dotenv
from anthropic import Anthropic
import os
import json
from statistics import mean

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
        "max_tokens": 1000,
        "temperature": temperature,
        "messages": messages
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    reponse = client.messages.create(**params)
    
    return reponse.content[0].text


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


# grade by model
def grade_by_model(test_case, output):
    """Asks the model to evaluae the response for the test case provided.
    """
    eval_prompt = f"""
You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

Original Task:
<task>
{test_case["task"]}
</task>

Solution to Evaluate:
<solution>
{output}
</solution>

Output Format
Provide your evaluation as a structured JSON object with the following fields, in this specific order:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

...
IMPORTANT: Respond with raw JSON only. No markdown, no backticks, 
no explanation — just the JSON object.
Do NOT include code, regex patterns, or any backslashes in string values.
Describe issues in plain English only — never quote code inline.
...
Example response shape:
{{
    "strengths": string[],
    "weaknesses": string[],
    "reasoning": string,
    "score": number
}}
    """

    # now that we have our prompt ready, we need to ask the model for the grade
    messages = []
    add_user_message(messages, eval_prompt)
    answer = chat(messages)
    # post clean up of answer, as stop squences (assitant prefilling) is no longer supoorted by new models
    answer = answer.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(answer)


def run_test_case(test_case):
    """Calls the prompt, then grades the result

    Args:
        test_case (_type_): _description_
    """
    response = run_prompt(test_case)

    model_grade = grade_by_model(test_case, response)
    score = model_grade["score"]
    reasoning = model_grade["reasoning"]

    return {
        "response":  response,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning
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

    # averaging the score
    average = mean([result["score"] for result in results])
    print(f"Average Score By Model is: {average}")
    return average

## MAIN

# evaluating the dataset
results = evaluate_dataset("C:/Users/salma/OneDrive/Desktop/Claude Course/prompt_evaluation/dataset.json")
# print(json.dumps(results, indent=2))