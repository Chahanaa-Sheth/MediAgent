SYMPTOM_WEIGHTS = {

    "chest pain": 10,
    "shortness of breath": 10,
    "difficulty breathing": 10,
    "stroke": 10,
    "unconscious": 10,

    "fever": 5,
    "vomiting": 5,
    "dizziness": 5,
    "migraine": 4,
    "headache": 3,

    "stomach pain": 4,
    "rash": 3,
    "fatigue": 2
}


def compute_severity(symptom_text):

    symptom_text = symptom_text.lower()

    total_score = 0

    detected = []

    for symptom, weight in SYMPTOM_WEIGHTS.items():

        if symptom in symptom_text:

            total_score += weight

            detected.append(symptom)

    # CLASSIFICATION
    if total_score >= 20:

        severity = "CRITICAL"

    elif total_score >= 12:

        severity = "HIGH"

    elif total_score >= 6:

        severity = "MODERATE"

    else:

        severity = "LOW"

    return {

        "severity_score": total_score,

        "severity_level": severity,

        "detected_symptoms": detected
    }