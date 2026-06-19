import json

from services.llm_service import LLMService

llm = LLMService()


async def generate_followup_questions(
    symptom: str,
    medical_context,
    diagnosis
):

    prompt = f"""
Patient Complaint:
{symptom}

Extracted Symptoms:
{medical_context.symptoms}

Possible Diagnoses:
{diagnosis}

Generate 3-5 high value follow-up questions.

Questions should help distinguish
between the possible diagnoses.

Examples:

Stomach Pain:
- Where is the pain located?
- Any vomiting?
- Any fever?
- Pain after eating?

Chest Pain:
- Does pain radiate to arm?
- Shortness of breath?
- Sweating?

Return JSON:

{{
    "questions": [
        "question1",
        "question2",
        "question3"
    ]
}}
"""

    response = await llm.get_full_response(
        system_prompt="""
You are a medical triage assistant.

Return ONLY JSON.

No markdown.
No explanations.
""",
        user_message=prompt
    )

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

    except Exception:

        return {
            "questions": []
        }