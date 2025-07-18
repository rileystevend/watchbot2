import logging
from langchain_community.llms import OpenAI
import openai

logger = logging.getLogger("evaluator")
llm = OpenAI(openai_api_key=openai.api_key, model="gpt-4o")

def evaluate_listing(title: str) -> float:
    prompt = f"Score this listing (0–100): {title}"
    try:
        response = llm(prompt)
        return float(response)  # adjust parsing as needed
    except Exception as e:
        msg = str(e)
        if "429" in msg or "quota" in msg.lower():
            logger.warning(f"Rate-limit/quota hit for '{title}': {e!r}")
        else:
            logger.error(f"Unexpected error evaluating '{title}': {e!r}")
        return 0.0
