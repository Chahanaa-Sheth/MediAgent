from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

SPECIALISTS = {

    "Cardiologist":
    "chest pain heart dizziness blood pressure cardiac shortness breath",

    "Neurologist":
    "migraine headache seizures dizziness nervous system",

    "Dermatologist":
    "skin rash itching acne redness allergy",

    "Gastroenterologist":
    "stomach pain digestion vomiting nausea gastritis",

    "Pulmonologist":
    "lungs breathing cough asthma oxygen",

    "General Physician":
    "general fever fatigue weakness infection"
}


def find_best_specialist(symptoms):

    symptom_embedding = model.encode([symptoms])

    best_specialist = None

    best_score = -1

    for specialist, description in SPECIALISTS.items():

        specialist_embedding = model.encode([description])

        similarity = cosine_similarity(
            symptom_embedding,
            specialist_embedding
        )[0][0]

        if similarity > best_score:

            best_score = similarity

            best_specialist = specialist

    return {

        "recommended_specialist": best_specialist,

        "confidence": round(float(best_score), 2)
    }