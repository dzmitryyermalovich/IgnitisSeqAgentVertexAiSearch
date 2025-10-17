import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
from google import genai
from google.genai.types import GenerateContentConfig, VertexAISearch, Retrieval, Tool
from google.adk.tools.function_tool import FunctionTool

PROJECT = "email-eso-agents-pilot"
MODEL_REGION = "europe-west1"
DATASTORE = "projects/email-eso-agents-pilot/locations/eu/collections/default_collection/dataStores/customer-service-faq_1760082381927"

client = genai.Client(vertexai=True, project=PROJECT, location=MODEL_REGION)

vas_tool_for_inner_call = Tool(
    retrieval=Retrieval(vertex_ai_search=VertexAISearch(datastore=DATASTORE))
)

# Slightly clearer LT prompt (keeps your constraint)
contents_lt = (
    "Kur rasti klientui išrašytas sąskaitas? Kaip surasti klientui išrašytas sąskaitas VL sistemoje? "
)

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents_lt,
    config=GenerateContentConfig(tools=[vas_tool_for_inner_call]),
)

md = getattr(resp.candidates[0], "grounding_metadata", None)
print("\nRETRIEVAL QUERIES:", getattr(md, "retrieval_queries", []))
if md and getattr(md, "grounding_chunks", None):
    for i, ch in enumerate(md.grounding_chunks[:3]):
        rc = ch.retrieved_context
        print(f"\nCHUNK {i} TITLE:", getattr(rc, "title", None))
        print("CHUNK URI:", getattr(rc, "uri", None))
        print("CHUNK PREVIEW:", (getattr(rc, "text", "") or "")[:300])
else:
    print("\nNO GROUNDING CHUNKS RETURNED")

def extract_text_parts(response) -> List[str]:
    """Return a list of all text fragments the LLM generated (in order)."""
    parts: List[str] = []
    try:
        if not getattr(response, "candidates", None):
            return parts
        cand = response.candidates[0]
        content = getattr(cand, "content", None)
        for part in getattr(content, "parts", []) or []:
            # Only keep textual parts; ignore other modalities/tool calls
            txt = getattr(part, "text", None)
            if isinstance(txt, str) and txt.strip():
                parts.append(txt.strip())
    except Exception:
        # Keep it silent; return whatever we have
        pass
    return parts

parts_list = extract_text_parts(resp)

final_answer = "\n\n".join(parts_list) if parts_list else "There isn't this info in the DataStore."
print("PARTS LIST:", parts_list)
print("\nFINAL ANSWER COMBINED:\n", final_answer)
