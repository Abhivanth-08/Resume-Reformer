from langchain.prompts import ChatPromptTemplate
from custom_wrapper import OpenRouterChat  # Your wrapper


def rewrite_to_length(original_text: str, desired_length: int) -> str:
    template = """
    You are a smart writing agent.

    TASK:
    - Rewrite the input content to be the same in meaning.
    - Ensure the new version has exactly {length} characters.
    - Maintain correct grammar and natural flow.

    INPUT:
    {text}

    IMPORTANT:
    - Output ONLY the rewritten text.
    - Do NOT add quotation marks or any explanation.
    - Remove the quotes if present
    - Output must be nearer to {length} characters long , the word should be completed.
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = OpenRouterChat(
        api_key="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",
        model="mistralai/mistral-7b-instruct:free",
        temperature=0.4
    )

    chain = prompt | llm

    print(f"🔁 Rewriting to {desired_length} characters...")

    response = chain.invoke({
        "text": original_text,
        "length": desired_length
    })

    output = response.content.strip() if hasattr(response, "content") else str(response).strip()

    # Optional: Truncate in case it overshoots by 1-2 characters
    if len(output) > desired_length:
        output = output[:desired_length].rstrip()

    return output

