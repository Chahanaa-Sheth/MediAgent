import json

from services.llm_service import LLMService

llm = LLMService()


async def expand_medical_query(symptom: str):

    prompt = f"""
You are a clinical NLP query expansion engine.

INPUT:
{symptom}

Expand the user's symptom description into medically useful search terms.

Generate:

1. lay_terms
2. clinical_terms
3. related_symptoms
4. possible_conditions
5. urgency_flag

IMPORTANT:

- Include common patient language
- Include clinical terminology
- Include common co-occurring symptoms
- Include ONLY plausible differential diagnoses
- Maximum 5 possible conditions
- Rank conditions by likelihood
- Avoid extremely rare diseases unless strongly suggested

Return ONLY valid JSON.

{{
  "primary_symptom": "",
  "keywords": {{
      "lay_terms": [],
      "clinical_terms": [],
      "related_symptoms": [],
      "possible_conditions": []
  }},
  "urgency_flag": "LOW"
}}
"""

    response = await llm.get_full_response(
        system_prompt="""
Return valid JSON only.
No markdown.
No explanation.
No code fences.
""",
        user_message=prompt
    )

    try:

        data = json.loads(response)

        retrieval_terms = (
            data["keywords"].get("lay_terms", [])
            + data["keywords"].get("clinical_terms", [])
            + data["keywords"].get("related_symptoms", [])
        )

        retrieval_terms = list(
            dict.fromkeys(retrieval_terms)
        )

        return {
            "primary_symptom": data.get(
                "primary_symptom",
                symptom
            ),

            "retrieval_terms": retrieval_terms,

            "possible_conditions": data["keywords"].get(
                "possible_conditions",
                []
            ),

            "urgency_flag": data.get(
                "urgency_flag",
                "LOW"
            )
        }

    except Exception:

        return {
            "primary_symptom": symptom,
            "retrieval_terms": [symptom],
            "possible_conditions": [],
            "urgency_flag": "LOW"
        }