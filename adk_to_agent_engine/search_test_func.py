import os
from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
import os, json
from typing import List, Dict, Any
from google import genai
from google.genai.types import GenerateContentConfig, VertexAISearch, Retrieval, Tool
from google.adk.tools.function_tool import FunctionTool  # ADK FunctionTool
import json, re
from typing import List, Dict, Any

PROJECT = "email-eso-agents-pilot"
MODEL_REGION = "europe-west1"
DATASTORE = "projects/email-eso-agents-pilot/locations/eu/collections/default_collection/dataStores/customer-service-faq_1760082381927"

client = genai.Client(vertexai=True, project=PROJECT, location=MODEL_REGION)

vas_tool_for_inner_call = Tool(
    retrieval=Retrieval(
        vertex_ai_search=VertexAISearch(
            datastore=DATASTORE
        )
    )
)
# prompt = (
#     f"What does the blue light on the charging station mean? It's on constantly, even when the car is not connected?\n\n"
#     "Answer only if you find verified information in the charging station documentation. "
#     "If there is no relevant information in the DataStore, reply exactly with: "
#     "'There isn't this info in the DataStore.'"
# )
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Kur rasti klientui išrašytas sąskaitas? Kaip surasti klientui išrašytas sąskaitas VL sistemoje?",
    config=GenerateContentConfig(tools=[vas_tool_for_inner_call])
)
print(resp)
# resp = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="Ką reiškia mėlyna lemputė ant elektromobilių įkrovimo stotelės? Atsakykite tik tuo atveju, jei ją rasite dokumentuose.",
#     # contents=prompt,
#     # contents = "Sveiki,\nką reiškia mėlyna lemputė ant pakrovimo stotelės? Ji dega nuolat, net kai automobilis neprijungtas.\nAčiū!",
#     # contents="What is the maximum height the mower can cut grass?Answer only if you find it in the charging station documentation",
#     # contents="What does the blue light on the charging station mean? It's on constantly, even when the car is not connected.Answer only if you find it in documentation",
#     # contents="Koks yra maksimalus žolės aukštis, kurį gali nupjauti vejapjovė? Atsakykite tik tuo atveju, jei tai nurodyta dokumentuose.",
#     config=GenerateContentConfig(tools=[vas_tool_for_inner_call])
# )
# print(resp.text)
# print(resp)