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
# datastore region must match where DS lives, e.g. 'eu'
DATASTORE = "projects/email-eso-agents-pilot/locations/eu/collections/default_collection/dataStores/customer-service-faq_1760082381927"

client = genai.Client(vertexai=True, project=PROJECT, location=MODEL_REGION)

vas_tool_for_inner_call = Tool(
    retrieval=Retrieval(vertex_ai_search=VertexAISearch(datastore=DATASTORE))
)

def fetch_vas_passages(query: str):
    """
    Calls Gemini with Vertex AI Search grounding to retrieve a factual answer
    strictly based on the charging-station documentation.
    """

    # Construct a clear and context-aware prompt for RAG grounding
    prompt = query.strip()

    # Call Gemini model with Vertex AI Search tool attached
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(
            tools=[vas_tool_for_inner_call],
        ),
    )

    return {"answer_en": resp.text}

vas_function_tool = FunctionTool(
    func=fetch_vas_passages,
)

class RagFields(BaseModel):
    answer_en: str = Field(
        description="Concise grounded English answer")

COMBINED_PROMPT = r"""
You are a strict RAG evaluator.

Steps:
1) Call tool `fetch_vas_passages` with the English question:
   {translation.text_en}

2) Use ONLY the tool output. If the datastore lacks relevant info, set:
   answer_en = "There isn't this info in the DataStore."
   Otherwise set answer_en to a short, clear English answer grounded in the retrieved context.

CRITICAL OUTPUT FORMAT:
- Return ONLY one JSON object that matches the RagFields schema.
- Keys: {"answer_en": "<string>"}.
- Do NOT include markdown, code fences, comments, or extra text.
- Example of valid output:
{"answer_en":"There isn't this info in the DataStore."}
"""



vertex_ai_search_agent = LlmAgent(
    name="vertex_ai_search_agent",
    model="gemini-2.5-flash",
    instruction=COMBINED_PROMPT,
    tools=[vas_function_tool],
    output_schema=RagFields,
    output_key="rag",
)
