def build_user_turn(
    symptom: str,
    rag_results: str,
    formatted_history: str,
    medical_context=None,
    severity=None,
    diagnosis=None,
    followups=None,
    agent_outputs=None
):

    # Conversation History
    history_block = formatted_history.strip()[-3000:] if formatted_history else ""

    history_section = (
        f"""
[CONVERSATION HISTORY]
{history_block}
"""
        if history_block
        else "[CONVERSATION HISTORY]\nNo prior conversation."
    )


    # RAG Results
    research_section = (
        f"""
[RETRIEVED MEDICAL RESEARCH]
{rag_results}
"""
        if rag_results
        else """
[RETRIEVED MEDICAL RESEARCH]
No relevant research retrieved.
"""
    )

    # Medical Extraction
    medical_section = ""

    if medical_context:
        medical_section = f"""
[EXTRACTED MEDICAL CONTEXT]

Symptoms:
{medical_context.symptoms}

Duration:
{medical_context.duration}

Severity Indicators:
{medical_context.severity_indicators}

Temporal Progression:
{medical_context.temporal_progression}

Medications:
{medical_context.medication_history}

Emergency Flags:
{medical_context.emergency_flags}

Confidence:
{medical_context.confidence}
"""

    # Severity
    severity_section = ""

    if severity:
        severity_section = f"""
[SEVERITY ASSESSMENT]

Score:
{severity.score}

Level:
{severity.level}

Reasoning:
{severity.reasoning}

Emergency:
{severity.emergency}
"""
    followup_text = ""

    if followups:
        followup_text = "\n".join(
        [f"- {q}" for q in followups.get("questions", [])]
    )

    # Differential Diagnosis

    diagnosis_section = ""

    if diagnosis:
        conditions = diagnosis.get(
            "conditions",
            []
        )

        specialist = diagnosis.get(
            "recommended_specialist",
            "General Physician"
        )

        formatted_conditions = []

        for condition in conditions:

            formatted_conditions.append(
                f"""
Condition:
{condition.get("name")}

Confidence:
{condition.get("confidence")}%

Reasoning:
{condition.get("reasoning")}
"""
            )

    diagnosis_section = f"""
[DIFFERENTIAL DIAGNOSIS]

Recommended Specialist:
{specialist}

Likely Conditions:

{"".join(formatted_conditions)}
"""

    specialist = diagnosis.get(
        "recommended_specialist",
        "General Physician"
    )

    formatted_conditions = []

    for condition in conditions:

        formatted_conditions.append(
            f"""
Condition:
{condition.get("name")}

Confidence:
{condition.get("confidence")}%

Reasoning:
{condition.get("reasoning")}
"""
        )

    diagnosis_section = f"""
[DIFFERENTIAL DIAGNOSIS]

Recommended Specialist:
{specialist}

FOLLOWUP QUESTIONS:

{followup_text}

Likely Conditions:

{"".join(formatted_conditions)}
"""

    # Agent Findings
    agent_section = ""

    if agent_outputs:
        agent_section = f"""
[AGENT FINDINGS]

{agent_outputs}
"""

    return f"""
{history_section}

{medical_section}

{severity_section}

{diagnosis_section}

{agent_section}

{research_section}

[USER MESSAGE]

{symptom}

Use retrieved research ONLY if it directly relates to the user's symptoms.

Ignore unrelated studies, diseases, biomarkers, cancer reports,
or research that does not directly answer the user's question.

Do not summarize retrieved papers unless they are highly relevant. If relevant, cite them naturally in your response.

Do not repeat the raw extraction data back to the user.

Generate a structured clinical response.

Follow this format:

1. Brief Summary
2. Most Likely Causes
3. Why These Causes Fit
4. Recommended Next Steps
5. When To Seek Urgent Care
6. Follow-up Questions

Always include the follow-up questions provided in the Differential Diagnosis section.

Use the Differential Diagnosis section as your primary reasoning source.

Discuss the most likely conditions and explain why they fit the user's symptoms.

Mention the recommended specialist if relevant.

Do NOT simply say symptoms can be caused by many things.

Be specific.

Do not mention confidence percentages.

Do not mention internal scoring systems.

Do not repeat raw extraction data.
""".strip()