import logging
import os
import openai
import time
from openai.error import RateLimitError, InsufficientQuotaError
from langchain_community.llms import OpenAI

logger = logging.getLogger('__name__')

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(openai_api_key=openai.api_key, model="gpt-4o")
except Exception as init_err:
    logger.error(f"Failed to initialize LLM: {init_err}")
    llm = None


def evaluate_listing(title: str) -> float:
    prompt = f"Rate how attractive a deal this listing is: {title}"
    try:
        # if using ChatCompletion, you'd use openai.ChatCompletion.create(...)
        response = llm(prompt)
        # parse out a numeric score...
        return float(response)  
    except (RateLimitError, InsufficientQuotaError) as e:
        logger.warning(f"Quota/rate-limit hit when evaluating '{title}': {e}.  Skipping evaluation.")
        return 0.0
    except Exception as e:
        logger.error(f"Unexpected error during evaluation of '{title}': {e}")
        return 0.0

