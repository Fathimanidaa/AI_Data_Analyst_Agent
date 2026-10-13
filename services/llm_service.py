
from gradio_client import Client

SPACE_ID = "Zacheus10/free-ai-chat"


def ask_llm(prompt: str) -> str:
    """Send a prompt to the publicly hosted Qwen model."""
    if not prompt or not prompt.strip():
        return "Please enter a question."

    try:
        client = Client(SPACE_ID)

        response = client.predict(
            message=prompt.strip(),
            max_new_tokens=512,
            temperature=0.3,
            api_name="/generate",
        )

        if isinstance(response, str):
            return response

        return str(response)

    except Exception as error:
        return (
            "The online AI service is temporarily unavailable. "
            "Please try again later.\n\n"
            f"Technical details: {error}"
        )