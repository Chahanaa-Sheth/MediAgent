import json

from services.llm_service import LLMService

llm = LLMService()


async def generate_differential_diagnosis(
    symptom: str,
    medical_context
):

    prompt = f"""
Patient Complaint:
{symptom}

Extracted Symptoms:
{medical_context.symptoms}

Duration:
{medical_context.duration}

Progression:
{medical_context.temporal_progression}

Generate:

1. Top 5 most likely conditions
2. Confidence score (0-100)
3. Short reasoning
4. Recommended specialist

Return ONLY JSON:

{{
    "conditions": [
        {{
            "name": "",
            "confidence": 0,
            "reasoning": ""
        }}
    ],
    "recommended_specialist": ""
}}
"""

    response = await llm.get_full_response(
        system_prompt="""
You are an AI medical differential diagnosis system.

Do NOT claim certainty.

Estimate likelihood based only on symptoms.

You are a medical differential diagnosis engine.

Output MUST be valid JSON.

Do not use markdown.

Do not use ```json blocks.

Do not include explanations before or after JSON.

Your entire response must be a single JSON object.
""",
        user_message=prompt
    )

    print("\n" + "=" * 80)
    print("DIAGNOSIS RAW RESPONSE")
    print("=" * 80)
    print(response)
    print("=" * 80 + "\n")

    try:


        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace(
            "```json",
            "",
            1
        )

        if cleaned.startswith("```"):
            cleaned = cleaned.replace(
            "```",
            "",
            1
        )

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        return json.loads(cleaned)
    
    except Exception as e:

        print("\nDIAGNOSIS PARSE ERROR:")
        print(str(e))
        print("\nRAW RESPONSE:")
        print(response)

        return {
            "conditions": [],
            "recommended_specialist": "General Physician"
        }