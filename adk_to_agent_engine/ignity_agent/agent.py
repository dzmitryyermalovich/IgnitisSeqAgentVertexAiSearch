# ignity_agent/agent.py
import os
from pydantic import BaseModel, Field
from typing import List, Optional

from google.adk.agents import SequentialAgent, LlmAgent

# subagents
from .subgents.translate_agent import translate_agent
from .subgents.vertex_ai_search_agent import vertex_ai_search_agent
from .subgents.reverse_translate_agent import reverse_translate_agent
from .subgents.agent_validator import agent_validator
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.load_memory_tool import LoadMemoryTool

# --------------------
# Ingest schema
# --------------------
class IngestFields(BaseModel):
    subject: Optional[str] = Field(default=None, description="Email subject as plain text")
    body: str = Field(description="Email body as plain text (no HTML)")
    sender: Optional[str] = Field(default=None, description="Sender email (if known)")
    received_at: Optional[str] = Field(default=None, description="ISO timestamp of reception")

INGEST_PROMPT = """
You are a strict extractor for an incoming email.
Given the user's message (which may contain subject/body or just raw text),
produce a clean JSON with fields:
- subject (string or null)
- body (string, required; remove signatures/footers/trackers where obvious)
- sender (string or null)
- received_at (ISO string or null)

Rules:
- Do not hallucinate content.
- If subject is missing, set null.
- Body must be concise and readable, no HTML tags.
Return ONLY valid JSON per the schema.
"""

ingest_agent = LlmAgent(
    name="ingest_agent",
    model="gemini-2.0-flash",
    instruction=INGEST_PROMPT,
    output_schema=IngestFields,
    output_key="ingest",
)

async def auto_save_session_to_memory_callback(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session)

root_agent = SequentialAgent(
    name="Ignity_Sequential_Email_Agent",
    description="Email → ingest → translate→ search→ reverse-translate → validate → return",
    sub_agents=[
        ingest_agent,
        translate_agent,
        vertex_ai_search_agent,
        reverse_translate_agent,
        agent_validator,
    ],
    after_agent_callback=auto_save_session_to_memory_callback
)
