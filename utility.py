import json


def is_message_limit(message: str) -> bool:
    if len(message) < 1000:
        return False
    message = message.strip()
    code_block_tags = message.count("```")
    return (
        code_block_tags % 2 == 0
        and not message.endswith("`")
        and message.count("\n") > 0
    )


def break_answer(answer: str) -> (str, str):
    answers = answer.split("\n")
    next_answer = answers.pop(-1).strip()
    if len(next_answer) == 0:
        next_answer = "..."
    return "\n".join(answers).strip(), next_answer


def preprocess_prompt(prompt: str):
    return prompt.replace("\\n", "\n")


def cut_string_to_json(string: str):
    string = string.replace("\n", " ").replace("`", "")
    if len(string) > 50:
        string = string[:50] + "..."
    return string


def replace_with_characters_map(input_str):
    characters_map = {
        "1": "₁",
        "2": "₂",
        "3": "₃",
        "4": "₄",
        "5": "₅",
        "6": "₆",
        "7": "₇",
        "8": "₈",
        "9": "₉",
        "0": "₀",
        "s": "ₛ",
        ",": ",",
        ".": ".",
    }
    output_str = ""
    for char in input_str:
        if char in characters_map:
            output_str += characters_map[char]
        else:
            output_str += char
    return output_str
