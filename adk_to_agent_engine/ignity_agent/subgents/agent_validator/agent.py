# ignity_agent/subgents/agent_validator.py
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

# -----------------------------
# Extended schema for memory logging
# -----------------------------
class ValidationFields(BaseModel):
    ok: bool = Field(description="True if the answer directly and correctly addresses the question")
    issues: str = Field(description="If ok=false, short reason (off-topic, not grounded, unsafe, unclear)")
    score: float = Field(description="0..1 quality score based on helpfulness, correctness, clarity")
    question: str = Field(description="Original question text in English used for validation")
    final_answer: str = Field(description="Final answer text in user language after translation")
    target_lang: str = Field(description="Target language code of the final answer (e.g., 'en', 'lt', 'pl')")

# -----------------------------
# Validator prompt
# -----------------------------
VALIDATOR_PROMPT = """
You are a strict validator.

Question (English):
{translation.text_en}

Answer (final, user's language '{final.target_lang}'):
{final.final_answer}

Validation rules:
- The answer must directly address the question.
- It must be safe, non-sensitive, and grounded in the KB (assume KB grounding came from prior step).
- Penalize vague, generic, or off-topic responses.
- Consider clarity and conciseness.

Return valid JSON with:
- ok: true/false
- issues: short reason (empty if ok)
- score: number 0..1
- question: the exact English question being validated
- final_answer: the final answer text (translated or original)
- target_lang: user’s language code
"""

# -----------------------------
# Agent definition
# -----------------------------
agent_validator = LlmAgent(
    name="agent_validator",
    model="gemini-2.0-flash",
    instruction=VALIDATOR_PROMPT,
    output_schema=ValidationFields,
    output_key="validation",
)
