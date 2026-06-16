from typing import Dict, Tuple


class SpecialistMatcher:
    """Match symptoms to appropriate specialists with confidence scoring"""

    SPECIALIST_MAPPINGS = {
        "cardiologist": {
            "keywords": ["chest pain", "heart", "cardiac", "arrhythmia", "palpitations", "heart rate"],
            "severity_required": 6,
            "confidence_base": 0.85
        },
        "neurologist": {
            "keywords": ["migraine", "severe headache", "seizure", "stroke", "vertigo", "neurological"],
            "severity_required": 5,
            "confidence_base": 0.80
        },
        "pulmonologist": {
            "keywords": ["breathing", "shortness of breath", "asthma", "cough", "respiratory", "lung"],
            "severity_required": 4,
            "confidence_base": 0.75
        },
        "gastroenterologist": {
            "keywords": ["stomach", "abdominal", "diarrhea", "vomiting", "digestive", "nausea"],
            "severity_required": 3,
            "confidence_base": 0.70
        },
        "dermatologist": {
            "keywords": ["rash", "skin", "eczema", "psoriasis", "dermatitis"],
            "severity_required": 2,
            "confidence_base": 0.65
        },
        "rheumatologist": {
            "keywords": ["joint pain", "arthritis", "rheumatoid", "autoimmune"],
            "severity_required": 3,
            "confidence_base": 0.70
        },
        "psychiatrist": {
            "keywords": ["depression", "anxiety", "mood", "mental health", "suicidal"],
            "severity_required": 5,
            "confidence_base": 0.80
        }
    }

    @staticmethod
    def match(symptom: str, severity_score: float = 5.0) -> Tuple[str, float]:
        """Match symptom to specialist with confidence score"""
        symptom_lower = symptom.lower()
        best_match = "General Physician"
        best_confidence = 0.0
        best_reasoning = "General presentation, recommend primary care first"

        for specialist, config in SpecialistMatcher.SPECIALIST_MAPPINGS.items():
            # Check if keywords match
            keyword_matches = sum(1 for kw in config["keywords"] if kw in symptom_lower)

            if keyword_matches == 0:
                continue

            # Confidence calculation
            keyword_coverage = min(keyword_matches / len(config["keywords"]), 1.0)
            severity_bonus = 1.0 if severity_score >= config["severity_required"] else 0.6
            confidence = config["confidence_base"] * keyword_coverage * severity_bonus

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = specialist.title().replace("_", " ")

        return best_match, min(best_confidence, 1.0)


def specialist_agent(symptom, severity_score: float = 5.0) -> str:
    """Recommend specialist based on symptoms with confidence scoring"""
    specialist, confidence = SpecialistMatcher.match(symptom, severity_score)

    confidence_pct = int(confidence * 100)
    confidence_label = (
        "High" if confidence > 0.75 else
        "Moderate" if confidence > 0.5 else
        "Low"
    )

    return f"""Recommended Specialist: {specialist}
Confidence: {confidence_pct}% ({confidence_label})

Note: This is a preliminary suggestion. Your primary care physician can provide a proper referral."""