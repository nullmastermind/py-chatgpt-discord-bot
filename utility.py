def is_message_limit(message: str) -> bool:
    if len(message) < 1500:
        return False
    code_block_tags = message.count("```")
    return code_block_tags % 2 == 0 and not message.strip().endswith("`")
