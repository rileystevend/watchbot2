```python
import os
import openai
from langchain_community.llms import OpenAI

openai.api_key = os.getenv("OPENAI_API_KEY")
llm = OpenAI(openai_api_key=openai.api_key, model="gpt-4o")

def evaluate_listing(listing):
    prompt = f"""Analyze this luxury watch listing:\n"""
             f"Title: {listing['title']}\n"""
             f"Price: {listing['price']}\n\n"""
             """Based on current market trends, is this watch undervalued? """
             """Answer with 'Undervalued' or 'Fairly Priced' and brief reasoning."""
    response = llm(prompt)
    return response.strip()
```
