from typing import Dict, List, Any, Optional
import re
from datetime import datetime
from models.models import MedicalContext, SeverityScore, SeverityLevel, ConfidenceScore, TemporalInfo
from utils.exceptions import Logger
from services.symptom_extraction_service import (
    extract_medical_context_llm
)

class SymptomExtractor:
    """Extract and normalize symptoms from free text"""

    # Common symptom mappings to standard medical terms
    SYMPTOM_MAPPINGS = {

    "headache": [
        "headache",
        "head pain",
        "migraine"
    ],

    "fever": [
        "fever",
        "high temperature",
        "temperature",
        "temp",
        "feverish"
    ],

    "nausea": [
        "nausea",
        "nauseous",
        "queasy",
        "feeling sick",
        "sick to my stomach"
    ],

    "vomiting": [
        "vomiting",
        "vomit",
        "throwing up",
        "threw up"
    ],

    "cough": [
        "cough",
        "coughing"
    ],

    "nasal_congestion": [
        "blocked nose",
        "nose block",
        "stuffy nose",
        "nasal congestion",
        "congested nose",
        "blocked nostril"
    ],

    "runny_nose": [
        "runny nose",
        "running nose",
        "nasal discharge"
    ],

    "common_cold": [
        "cold",
        "common cold"
    ],

    "sore_throat": [
        "sore throat",
        "throat pain"
    ],

    "difficulty_breathing": [
        "difficulty breathing",
        "shortness of breath",
        "sob",
        "cant breathe",
        "can't breathe"
    ],

    "chest_pain": [
        "chest pain",
        "chest ache",
        "heart pain"
    ],

    "fatigue": [
        "fatigue",
        "tired",
        "exhaustion",
        "weakness"
    ],

    "dizziness": [
        "dizzy",
        "dizziness",
        "lightheaded"
    ],

    "diarrhea": [
        "diarrhea",
        "loose stool",
        "loose stools"
    ],

    "abdominal_pain": [
        "stomach pain",
        "abdominal pain",
        "belly pain",
        "stomach ache"
    ]
}

    MEDICATIONS = [
        "ibuprofen", "aspirin", "paracetamol", "acetaminophen",
        "amoxicillin", "penicillin", "metformin", "lisinopril",
        "atorvastatin", "omeprazole", "sertraline", "fluoxetine",
        "crocin", "dolo", "tylenol", "advil", "motrin"
    ]

    def __init__(self):
        self.logger = Logger("SymptomExtractor")

    async def extract(self, text: str, history: List[Dict[str, Any]] = None) -> MedicalContext:
        """Extract medical context from user input"""
        text_lower = text.lower()

        # Extract symptoms
        llm_result = await extract_medical_context_llm(text)

        symptoms = llm_result.get("symptoms",[])

        if not symptoms:
            symptoms = self._extract_symptoms(
        text_lower
    )

        # Extract duration
        duration = llm_result.get("duration")

        # Extract temporal progression
        temporal_progression = llm_result.get("progression")

        # Extract medications
        medications = llm_result.get("medications",[])
        medications_detected = len(medications) > 0

        # Extract emergency flags
        emergency_flags = llm_result.get("emergency_flags",[])

        # Combine with history if available
        if history:
            for msg in history:
                if msg.get("role") == "user":
                    history_symptoms = self._extract_symptoms(msg.get("content", "").lower())
                    symptoms.extend([s for s in history_symptoms if s not in symptoms])

        # Calculate confidence
        confidence = self._calculate_extraction_confidence(symptoms, duration, temporal_progression)

        return MedicalContext(
            symptoms=list(set(symptoms)),  # Deduplicate
            duration=duration,
            severity_indicators=self._extract_severity_indicators(text_lower),
            temporal_progression=temporal_progression,
            medication_history=medications,
            emergency_flags=emergency_flags,
            confidence=confidence,
            medications_detected=medications_detected
        )

    def _extract_symptoms(self,text: str) -> List[str]:

        symptoms = []

        for standard_symptom, variations in self.SYMPTOM_MAPPINGS.items():
            for variation in variations:
                if re.search(rf"\b{re.escape(variation)}\b",text):
                    symptoms.append(standard_symptom)
                break

        return symptoms

    def _extract_duration(self, text: str) -> Optional[str]:
        """Extract symptom duration"""
        patterns = [
            r'(\d+)\s*(weeks?|w)',
            r'(\d+)\s*(days?|d)',
            r'(\d+)\s*(hours?|h)',
            r'(\d+)\s*(months?|m)',
            r'(a week|a day|a month|a few days)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _extract_progression(self, text: str) -> Optional[str]:
        """Extract temporal progression"""
        if "worsening" in text or "getting worse" in text or "deteriorating" in text:
            return "worsening"
        elif "improving" in text or "getting better" in text:
            return "improving"
        elif "stable" in text or "same" in text:
            return "stable"
        elif "sudden" in text or "sudden onset" in text:
            return "acute"
        elif "gradually" in text or "gradual" in text:
            return "gradual"
        return None

    def _extract_medications(self, text: str) -> List[str]:
        """Extract medications from text"""
        medications = []
        for med in self.MEDICATIONS:
            if med in text:
                medications.append(med)
        return medications

    def _extract_emergency_flags(self, text: str) -> List[str]:
        """Extract emergency indicators"""
        emergency_keywords = [
            "chest pain", "heart attack", "stroke", "severe bleeding",
            "can't breathe", "difficulty breathing", "unconscious",
            "suicidal", "passing out"
        ]
        flags = []
        for keyword in emergency_keywords:
            if keyword in text:
                flags.append(keyword)
        return flags

    def _extract_severity_indicators(self, text: str) -> List[str]:
        """Extract severity indicators"""
        indicators = []
        if "severe" in text:
            indicators.append("severe")
        if "multiple" in text or "both" in text:
            indicators.append("multi-symptom")
        if "recurring" in text or "recurring" in text:
            indicators.append("recurring")
        return indicators

    def _calculate_extraction_confidence(self, symptoms: List[str], duration: Optional[str], progression: Optional[str]) -> float:
        """Calculate confidence score for extraction"""
        confidence = 0.5  # Base confidence
        if symptoms:
            confidence += 0.2
        if duration:
            confidence += 0.15
        if progression:
            confidence += 0.15
        return min(confidence, 1.0)


class SeverityScorer:
    """Score symptom severity"""

    SYMPTOM_WEIGHTS = {
        "chest_pain": 15,
        "difficulty_breathing": 14,
        "stroke_symptoms": 15,
        "severe_bleeding": 16,
        "suicidal_ideation": 16,
        "unconsciousness": 15,
        "migraine": 6,
        "fever": 7,
        "nausea": 4,
        "diarrhea": 3,
        "cough": 3,
        "sore_throat": 2,
        "fatigue": 3,
        "dizziness": 5,
        "skin_rash": 4,
        "joint_pain": 4,
        "muscle_pain": 3,
        "back_pain": 4,
        "vomiting": 5,
    }

    TEMPORAL_MODIFIERS = {
        "acute": 1.5,
        "worsening": 1.3,
        "gradual": 0.8,
        "stable": 0.8,
        "improving": 0.6,
    }

    def __init__(self):
        self.logger = Logger("SeverityScorer")

    async def score(self, medical_context: MedicalContext) -> SeverityScore:
        """Score severity of medical condition"""
        # Emergency check first
        if medical_context.emergency_flags:
            return SeverityScore(
                score=100,
                level=SeverityLevel.CRITICAL,
                reasoning="Emergency symptoms detected",
                emergency=True
            )

        # Calculate base score
        base_score = 0
        for symptom in medical_context.symptoms:
            base_score += self.SYMPTOM_WEIGHTS.get(symptom, 3)

        # Apply temporal modifier
        temporal_modifier = self.TEMPORAL_MODIFIERS.get(medical_context.temporal_progression, 1.0)
        final_score = base_score * temporal_modifier

        # Determine level
        if final_score >= 20:
            level = SeverityLevel.CRITICAL
        elif final_score >= 12:
            level = SeverityLevel.HIGH
        elif final_score >= 6:
            level = SeverityLevel.MODERATE
        else:
            level = SeverityLevel.LOW

        reasoning = self._build_reasoning(medical_context, base_score, temporal_modifier, final_score)

        return SeverityScore(
            score=min(final_score, 100),
            level=level,
            reasoning=reasoning,
            emergency=final_score >= 20
        )

    def _build_reasoning(self, context: MedicalContext, base: float, modifier: float, final: float) -> str:
        """Build reasoning for severity score"""
        parts = []
        if context.symptoms:
            parts.append(f"{len(context.symptoms)} symptom(s)")
        if context.duration:
            parts.append(f"duration: {context.duration}")
        if context.temporal_progression:
            parts.append(f"progression: {context.temporal_progression}")
        return " | ".join(parts)


class AgentRouter:
    """Intelligently route to agents based on context"""

    def __init__(self):
        self.logger = Logger("AgentRouter")

    async def route(self, medical_context: MedicalContext, severity: SeverityScore) -> List[str]:
        """Determine which agents to run"""
        agents = []

        # Always run emergency detection
        agents.append("emergency_agent")

        # Always get specialist recommendation
        agents.append("specialist_agent")

        # Run drug agent if medications detected
        if medical_context.medications_detected:
            agents.append("drug_agent")

        # Run research agent for high severity
        if severity.score >= 12:
            agents.append("research_agent")

        self.logger.info("Agents routed", agents=agents, severity=severity.level)
        return agents
