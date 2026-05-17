

from anthropic import Anthropic
from anthropic.types import ToolParam, Message
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json

load_dotenv("C:/Users/salma/OneDrive/Desktop/Claude Course/.env")

model = "claude-sonnet-4-6"
max_tokens = 1000
API_KEY = os.getenv("API_KEY")

# initializing anthropic client
client = Anthropic(api_key=API_KEY)

# helper functions
# add user message
def add_user_message(chat_history, message):
    user_message = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message
    }
    chat_history.append(user_message)

# add assistant message
def add_assistant_message(chat_history, message):
    assistant_message = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message
    }
    chat_history.append(assistant_message)

# get current datetime
def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)

# add duration to datetime
def add_duration_to_datetime(
    datetime_str, duration=0, unit="days", input_format="%Y-%m-%d"
):
    date = datetime.strptime(datetime_str, input_format)

    if unit == "seconds":
        new_date = date + timedelta(seconds=duration)
    elif unit == "minutes":
        new_date = date + timedelta(minutes=duration)
    elif unit == "hours":
        new_date = date + timedelta(hours=duration)
    elif unit == "days":
        new_date = date + timedelta(days=duration)
    elif unit == "weeks":
        new_date = date + timedelta(weeks=duration)
    elif unit == "months":
        month = date.month + duration
        year = date.year + month // 12
        month = month % 12
        if month == 0:
            month = 12
            year -= 1
        day = min(
            date.day,
            [
                31,
                29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        new_date = date.replace(year=year, month=month, day=day)
    elif unit == "years":
        new_date = date.replace(year=date.year + duration)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return new_date.strftime("%A, %B %d, %Y %I:%M:%S %p")

# chat
def chat(messages, tools=None, temperature=1.0, system=None):
    params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature
    }
    if tools:
        params["tools"] = tools
    if system:
        params['system'] = system
    response = client.messages.create(**params)
    return response

# text from message
def text_from_message(message):
    return "\n".join(
        [block.text for block in message.content if block.type == "text"]
    )

# set reminder
def set_reminder(content, timestamp):
    print(f"----\nSetting the following reminder for {timestamp}:\n{content}\n----")

# run_tool
def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    elif tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)

# run tools
def run_tools(message):
    tool_request = [block for block in message.content if block.type == "tool_use"]
    tool_request_results = []
    for tool_request in tool_request:
        try:
            result = run_tool(tool_request.name, tool_request.input)
            tool_request_results.append(
                {
                    "tool_use_id": tool_request.id,
                    "type": "tool_result",
                    "content": json.dumps(result),
                    "is_error": False
                }
            )
        except Exception as e:
            tool_request_results.append(
                {
                    "tool_use_id": tool_request.id,
                    "type": "tool_result",
                    "content": f"Error: {e}",
                    "is_error": True
                }
            )
                
    return tool_request_results

# run conversation
def run_conversation(message):
    while True:
        response = chat(message, tools=[get_current_datetime_schema, add_duration_to_datetime_schema,],)
        add_assistant_message(message, response)
        print(text_from_message(response))

        # checking the stop reason
        if response.stop_reason != "tool_use":
            # means no more calls are needed for tool use
            break

        tool_request_results = run_tools(response)
        add_user_message(messages, tool_request_results)
    
    return messages


get_current_datetime_schema = {
  "name": "get_current_datetime",
  "description": "Returns the current date and time formatted as a string. Use this tool whenever the user asks about the current date, time, or datetime. The format parameter controls the output string layout using Python strftime directives (e.g., '%Y-%m-%d' for dates, '%H:%M:%S' for times).",
  "input_schema": {
    "type": "object",
    "properties": {
      "date_format": {
        "type": "string",
        "description": "A Python strftime format string that controls the output layout. Must not be empty. Common examples: '%Y-%m-%d' (date only), '%H:%M:%S' (time only), '%Y-%m-%d %H:%M:%S' (full datetime), '%d/%m/%Y %I:%M %p' (UK-style with AM/PM).",
        "default": "%Y-%m-%d %H:%M:%S"
      }
    },
    "required": []
  }
}

add_duration_to_datetime_schema = {
  "name": "add_duration_to_datetime",
  "description": "Adds or subtracts a duration from a given datetime string and returns the result as a human-readable string (e.g., 'Monday, January 15, 2024 02:30:00 PM'). Use this tool when the user asks about a date/time that is N seconds/minutes/hours/days/weeks/months/years before or after a given date. Supports negative durations for going back in time.",
  "input_schema": {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "datetime_str": {
        "type": "string",
        "description": "The starting datetime string to add the duration to. Must match the pattern defined by 'input_format'. Examples: '2024-01-15', '15/01/2024', '2024-01-15 14:30:00'."
      },
      "duration": {
        "type": "number",
        "description": "The amount of time to add. Use a negative value to subtract (go back in time). Fractional values are supported for units like hours (e.g., 1.5 for 90 minutes). Defaults to 0.",
        "default": 0
      },
      "unit": {
        "type": "string",
        "description": "The time unit for the duration. Use 'months' or 'years' for calendar arithmetic (handles variable-length months and leap years). Use 'weeks', 'days', 'hours', 'minutes', or 'seconds' for fixed-length arithmetic.",
        "enum": ["seconds", "minutes", "hours", "days", "weeks", "months", "years"],
        "default": "days"
      },
      "input_format": {
        "type": "string",
        "description": "A Python strftime format string that matches the format of 'datetime_str'. Must not be empty. Examples: '%Y-%m-%d' for '2024-01-15', '%d/%m/%Y' for '15/01/2024', '%Y-%m-%d %H:%M:%S' for '2024-01-15 14:30:00'. Defaults to '%Y-%m-%d'.",
        "default": "%Y-%m-%d"
      }
    },
    "required": ["datetime_str"]
  },
  "strict": True
}


messages = []
add_user_message(messages, "Please give me current time, formatted as H:M and day and also tell me what day comes if add two more days to it?")
run_conversation(messages)
print(messages)
