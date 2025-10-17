# ignity_agent/subgents/reverse_translate_agent.py
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

class FinalAnswerFields(BaseModel):
    target_lang: str = Field(description="Language of the final answer (ISO code)")
    final_answer: str = Field(description="Answer in user's original language or English if original was English")

REVERSE_PROMPT = """
You are a translator.
Source language of the user's email: {translation.src_lang}
English answer to send:
{rag.answer_en}

If src_lang == "en", do NOT translate and return the English answer.
Otherwise, translate the answer from English to src_lang preserving meaning and tone.

Return JSON:
- target_lang  (== src_lang if not 'en', else 'en')
- final_answer
"""

reverse_translate_agent = LlmAgent(
    name="reverse_translate_agent",
    model="gemini-2.0-flash",
    instruction=REVERSE_PROMPT,
    output_schema=FinalAnswerFields,
    output_key="final",
)
