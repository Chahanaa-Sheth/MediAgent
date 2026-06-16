def emergency_agent(symptom):

    emergency_keywords = [
        "chest pain",
        "heart attack",
        "can't breathe",
        "difficulty breathing",
        "stroke",
        "severe bleeding",
        "suicidal",
        "passed out",
        "unconscious"
    ]

    symptom_lower = symptom.lower()

    for keyword in emergency_keywords:

        if keyword in symptom_lower:

            return f"""
🚨 EMERGENCY WARNING

Possible serious condition detected:
{keyword}

Seek immediate medical attention or call emergency services.
"""

    return "No emergency symptoms detected."