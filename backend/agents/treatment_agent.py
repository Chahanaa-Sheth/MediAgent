def treatment_agent(symptom):

    symptom = symptom.lower()

    advice = []

    if "fever" in symptom:
        advice.append(
            "Stay hydrated and rest."
        )

    if "headache" in symptom:
        advice.append(
            "Avoid bright screens and get proper sleep."
        )

    if "stomach" in symptom:
        advice.append(
            "Avoid oily foods and drink fluids."
        )

    if advice:
        return "\n".join(advice)

    return "Monitor symptoms and consult a doctor if worsened."