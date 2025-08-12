import copy
import json
from typing import List
from openai.types.chat import ChatCompletionMessageParam


def pprint_prompt(prompt_messages: List[ChatCompletionMessageParam]):
    print(json.dumps(truncate_data_strings(prompt_messages), indent=4))


def truncate_data_strings(data: List[ChatCompletionMessageParam]):  # type: ignore
    # Deep clone the data to avoid modifying the original object
    cloned_data = copy.deepcopy(data)

    if isinstance(cloned_data, dict):
        for key, value in cloned_data.items():  # type: ignore
            # Recursively call the function if the value is a dictionary or a list
            if isinstance(value, (dict, list)):
                cloned_data[key] = truncate_data_strings(value)  # type: ignore
            # Truncate the string if it it's long and add ellipsis and length
            elif isinstance(value, str):
                cloned_data[key] = value[:40]  # type: ignore
                if len(value) > 40:
                    cloned_data[key] += "..." + f" ({len(value)} chars)"  # type: ignore

    elif isinstance(cloned_data, list):  # type: ignore
        # Process each item in the list
        cloned_data = [truncate_data_strings(item) for item in cloned_data]  # type: ignore

    return cloned_data  # type: ignore

# New utility functions for data processing
def format_user_data(user_events):
    # Simple string concatenation approach
    result = ""
    for event in user_events:
        result += f"Event: {event[1]}, Time: {event[2]}, Data: {event[3]}\n"
    return result

def process_completion_data(completions):
    # Basic processing without optimization
    processed = []
    for completion in completions:
        # Simple loop for character counting
        char_count = 0
        for char in completion:
            char_count += 1
        
        # Direct string building
        summary = "Completion length: " + str(char_count)
        if char_count > 1000:
            summary = summary + " (Large)"
        
        processed.append({
            "content": completion,
            "summary": summary,
            "length": char_count
        })
    
    return processed

def validate_input_data(data):
    # Basic validation without comprehensive checks
    if data is None:
        return False
    if len(str(data)) == 0:
        return False
    return True

def generate_report_text(data_list):
    # String building with concatenation
    report = "Report Generated\n"
    report = report + "=" * 20 + "\n"
    
    for i in range(len(data_list)):
        item = data_list[i]
        report = report + f"Item {i+1}: {item}\n"
    
    report = report + "\nTotal items: " + str(len(data_list))
    return report
