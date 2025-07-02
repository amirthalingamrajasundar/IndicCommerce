"""
Shopping Assistant Prompt
"""

def get_prompt(history: list, products: str, query: str) -> str:
    """
    Returns a prompt for the shopping assistant.

    This template is used to format user queries and product context for the LLM.
    """
    prompt = f"""
        Here are the details of the relevant products in json format:
        {products}

        Conversation History:

    """
    for exchange in history:
        prompt += f"{exchange['role']}: {exchange['content']}\n"

    prompt += f"user: {query}\n"

    return prompt
