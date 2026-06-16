def build_user_turn(symptom: str, rag_results: str, formatted_history: str):

    history_block = (
        formatted_history.strip()[-3000:]
        if formatted_history.strip()
        else None
    )

    rag_block = (
        rag_results.strip()
        if rag_results.strip()
        else None
    )

    history_section = (
        f"[CONVERSATION HISTORY — use only if directly relevant to the current message]\n{history_block}"
        if history_block
        else "[CONVERSATION HISTORY — none yet]"
    )

    research_section = (
        f"[RETRIEVED MEDICAL RESEARCH — cite naturally if relevant; ignore if off-topic]\n{rag_block}"
        if rag_block
        else (
            "[RETRIEVED MEDICAL RESEARCH — no relevant papers found for this query. "
            "Answer from established medical knowledge and label it as such.]"
        )
    )

    return f"""
{history_section}

{research_section}

[USER MESSAGE]
{symptom.strip()}

Respond now. Apply your reasoning protocol silently — do not narrate your thinking steps. \
Do not start your response with "I" or repeat the user's question back to them. \
Do not append a generic disclaimer paragraph to every response — include safety guidance only when \
the clinical content genuinely warrants it.
""".strip()