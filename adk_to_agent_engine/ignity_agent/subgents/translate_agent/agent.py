# ignity_agent/subgents/translate_agent.py
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

class TranslationFields(BaseModel):
    src_lang: str = Field(description="Detected source language as ISO-639-1 code (e.g., en, lt, pl)")
    text_en: str = Field(description="The email question/content translated to English")

TRANSLATE_PROMPT = """
You are a translator and language detector.
Input text:
{ingest.body}

Tasks:
1) Detect the language code of the input (ISO-639-1, e.g., en, lt, pl).
2) If the text is already English, keep it; otherwise translate to clear English.
Return JSON with:
- src_lang
- text_en
"""

translate_agent = LlmAgent(
    name="translate_agent",
    model="gemini-2.0-flash",
    instruction=TRANSLATE_PROMPT,
    output_schema=TranslationFields,
    output_key="translation",  # state["translation"] = { src_lang, text_en }
)
