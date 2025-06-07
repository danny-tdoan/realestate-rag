import os
import re
import json
from chromadb import Collection
from realestate_rag import config
from openai import OpenAI
from realestate_rag.rag.functions import functions
from realestate_rag.rag.search import (
    search_using_text,
    search_within_suburb,
    search_within_suburb_code
)

API_KEY = os.getenv("API_KEY")
OPENAI_CLIENT = OpenAI(api_key=API_KEY)




def rag(openai_client: OpenAI, context: str, query: str) -> str:
    prompt = f"""You are a helpful real estate agent who answers questions from buyers and sellers about property details.

    You need to pick the most relevant property from the provided context and answer the user's question based on that property.

    If the user does not ask any specific question, you should assume they are searching for properties to buy or to sell and return relevant properties from the context.

    Here are some relevant excerpts about the property:
    {context}

    Please answer the following question using only the information above:
    {query}
    """

    # send to openai
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful real estate agent who reads property descriptions."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    if answer is None or len(answer) == 0:
        return "No answer found."
    return answer


def pick_search_function(query: str, functions: list) -> dict:
    function_names = [f["name"] for f in functions]
    function_descriptions = "\n".join(
        [f"{f['name']}: {f['description']}" for f in functions]
    )
    function_arguments = "\n".join(
        [f"{f['name']}: {json.dumps(f['parameters']['required'])}" for f in functions]
    )
    prompt = f"""
            You are an expert function router for a real estate search system.

            Available functions:
            {function_descriptions}

            Given the user query below, pick the most appropriate function and extract the arguments.
            Return your answer as a JSON object with keys 'name' and 'arguments'.

            Map the extracted arguments to the function's parameters.
            Available functions and their required parameters:
            {function_arguments}

            User query: "{query}"
            """

    response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    # Extract JSON from the LLM's response
    content = response.choices[0].message.content
    return json.loads(content)

def answer(collection: Collection, query: str) -> str:
    fn = pick_search_function(query, functions)
    function_name = fn["name"]
    arguments = fn["arguments"]

    if function_name == "search_within_suburb":
        context = search_within_suburb(collection, arguments["suburb"], arguments["query"])
    elif function_name == "search_within_suburb_code":
        context = search_within_suburb_code(collection, arguments["suburb_code"], arguments["query"])
    elif function_name == "search_using_text":
        context = search_using_text(collection, arguments["query"])
    else:
        return "No valid search function found."

    if context is None:
        return "No relevant information found."
    return rag(OPENAI_CLIENT, context, query)