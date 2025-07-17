import logging
import os
import openai
from langchain_community.llms import OpenAI

logger = logging.getLogger('evaluator')

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(openai_api_key=openai.api_key, model="gpt-4o")
except Exception as init_err:
    logger.error(f"Failed to initialize LLM: {init_err}")
    llm = None


def evaluate_listing(listing):
    if llm is None:
        raise RuntimeError("LLM not initialized")
    prompt = (
        f"Analyze this luxury watch listing:\n"
        f"Title: {listing['title']}\n"
        f"Price: {listing['price']}\n\n"
        "Based on current market trends, is this watch undervalued? "
        "Answer with 'Undervalued' or 'Fairly Priced' and brief reasoning."
    )
    try:
        response = llm(prompt)
        return response.strip()
    except Exception as eval_err:
        logger.error(f"LLM evaluation failed: {eval_err}")
        return "Evaluation Error"
