import json

from services.llm_service import LLMService

llm = LLMService()


async def extract_medical_context_llm(text: str):

    prompt = f"""
You are a clinical symptom extraction engine.

Extract:

1. symptoms
2. duration
3. progression
4. medications
5. emergency_flags

Normalize symptoms into medical terminology.

Examples:

Input:
"I keep feeling like throwing up"

Output:
{{
    "symptoms": ["nausea"],
    "duration": null,
    "progression": null,
    "medications": [],
    "emergency_flags": []
}}

Input:
"My nose is blocked and I have a cold"

Output:
{{
    "symptoms": [
        "nasal_congestion",
        "common_cold"
    ],
    "duration": null,
    "progression": null,
    "medications": [],
    "emergency_flags": []
}}

Input:
"{text}"

Return ONLY valid JSON.
"""

    response = await llm.get_full_response(
        system_prompt="""
You are a medical NLP engine.

Return only valid JSON.

No markdown.
No explanations.
No backticks.
""",
        user_message=prompt
    )

    try:

        return json.loads(response)

    except Exception:

        return {
            "symptoms": [],
            "duration": None,
            "progression": None,
            "medications": [],
            "emergency_flags": []
        }