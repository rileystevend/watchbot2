import logging
import os
import openai
import time
from langchain_community.llms import OpenAI

logger = logging.getLogger('__name__')

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(openai_api_key=openai.api_key, model="gpt-4o")
except Exception as init_err:
    logger.error(f"Failed to initialize LLM: {init_err}")
    llm = None



 def evaluate_listing(title: str) -> float:
     prompt = f"Score this listing: {title}"
     try:
         response = llm(prompt)
         return float(response)  # or however you parse it
     except Exception as e:
         # detect 429 from the message text if you want:
         if "429" in str(e):
             logger.warning(f"Rate-limit hit evaluating '{title}': {e}")
         else:
             logger.error(f"Unexpected eval error for '{title}': {e}")
         return 0.0

