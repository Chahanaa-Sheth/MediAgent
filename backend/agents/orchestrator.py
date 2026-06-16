from agents.research_agent import research_agent
from agents.specialist_agent import specialist_agent
from agents.emergency_agent import emergency_agent
from agents.drug_agent import drug_interaction_agent
from agents.severity_engine import compute_severity
from agents.specialist_matcher import find_best_specialist

def orchestrator_agent(symptom):

    outputs = []

    # EMERGENCY CHECK
    emergency_output = emergency_agent(symptom)

    # SPECIALIST
    specialist_output = specialist_agent(symptom)

    # RESEARCH
    research_output = research_agent(symptom)

    # DRUG CHECK
    drug_output = ""

    drug_keywords = [
        "ibuprofen",
        "paracetamol",
        "aspirin",
        "crocin",
        "dolo",
        "acetaminophen"
    ]

    symptom_lower = symptom.lower()

    for drug in drug_keywords:

        if drug in symptom_lower:

            drug_output += drug_interaction_agent(drug)

    # FINAL STRUCTURED BRIEF
    final_report = f"""

━━━━━━━━━━━━━━━━━━━
EMERGENCY ANALYSIS
━━━━━━━━━━━━━━━━━━━

{emergency_output}

━━━━━━━━━━━━━━━━━━━
RECOMMENDED SPECIALIST
━━━━━━━━━━━━━━━━━━━

{specialist_output}

━━━━━━━━━━━━━━━━━━━
DRUG SAFETY ANALYSIS
━━━━━━━━━━━━━━━━━━━

{drug_output if drug_output else "No medication risks detected."}

━━━━━━━━━━━━━━━━━━━
RESEARCH FINDINGS
━━━━━━━━━━━━━━━━━━━

{research_output}

"""

    return final_report