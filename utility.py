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
