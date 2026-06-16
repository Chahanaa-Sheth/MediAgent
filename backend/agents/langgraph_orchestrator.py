from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END, conditional_edge
from agents.research_agent import research_agent
from agents.specialist_agent import specialist_agent
from agents.emergency_agent import emergency_agent
from agents.drug_agent import drug_interaction_agent
from utils.exceptions import Logger

logger = Logger("LangGraphOrchestrator")


# STATE
class MediState(TypedDict):
    symptom: str
    history: Optional[List[dict]]
    agents_to_run: List[str]
    emergency_output: str
    specialist_output: str
    research_output: str
    drug_output: str


# AGENT NODES
def emergency_node(state):
    """Run emergency detection"""
    symptom = state["symptom"]
    result = emergency_agent(symptom)
    logger.info("Emergency agent executed", symptom_length=len(symptom))
    return {"emergency_output": result}


def specialist_node(state):
    """Run specialist recommendation"""
    symptom = state["symptom"]
    result = specialist_agent(symptom)
    logger.info("Specialist agent executed")
    return {"specialist_output": result}


def research_node(state):
    """Run research agent"""
    symptom = state["symptom"]
    result = research_agent(symptom)
    logger.info("Research agent executed")
    return {"research_output": result}


def drug_node(state):
    """Run drug interaction agent"""
    symptom = state["symptom"]
    drugs = [
        "ibuprofen", "paracetamol", "aspirin",
        "crocin", "dolo", "aspirin", "amoxicillin",
        "penicillin", "metformin", "lisinopril",
        "atorvastatin", "omeprazole", "sertraline", "fluoxetine"
    ]

    output = ""
    for drug in drugs:
        if drug in symptom.lower():
            output += drug_interaction_agent(drug)

    logger.info("Drug agent executed", drugs_detected=len([d for d in drugs if d in symptom.lower()]))
    return {"drug_output": output}


# CONDITIONAL ROUTING
def should_run_research(state):
    """Determine if research agent should run"""
    agents_to_run = state.get("agents_to_run", [])
    return "research_agent" in agents_to_run


def should_run_drug(state):
    """Determine if drug agent should run"""
    agents_to_run = state.get("agents_to_run", [])
    return "drug_agent" in agents_to_run


# BUILD GRAPH
graph = StateGraph(MediState)

graph.add_node("emergency_agent", emergency_node)
graph.add_node("specialist_agent", specialist_node)
graph.add_node("research_agent", research_node)
graph.add_node("drug_agent", drug_node)

# FLOW WITH INTELLIGENT ROUTING
graph.set_entry_point("emergency_agent")

# Emergency always leads to specialist
graph.add_edge("emergency_agent", "specialist_agent")

# Specialist routes based on agents_to_run
graph.add_conditional_edges(
    "specialist_agent",
    lambda state: "research_agent" if "research_agent" in state.get("agents_to_run", []) else ("drug_agent" if "drug_agent" in state.get("agents_to_run", []) else END),
    {
        "research_agent": "research_agent",
        "drug_agent": "drug_agent",
        END: END
    }
)

# Research can lead to drug or end
graph.add_conditional_edges(
    "research_agent",
    lambda state: "drug_agent" if "drug_agent" in state.get("agents_to_run", []) else END,
    {
        "drug_agent": "drug_agent",
        END: END
    }
)

# Drug always ends
graph.add_edge("drug_agent", END)

# COMPILE
app_graph = graph.compile()


# RUN FUNCTION
def run_langgraph(symptom: str, agents_to_run: List[str] = None, history: Optional[List[dict]] = None):
    """Run the LangGraph orchestrator with intelligent agent routing"""
    if agents_to_run is None:
        agents_to_run = ["emergency_agent", "specialist_agent"]
    if history is None:
        history = []

    result = app_graph.invoke({
        "symptom": symptom,
        "history": history,
        "agents_to_run": agents_to_run,
        "emergency_output": "",
        "specialist_output": "",
        "research_output": "",
        "drug_output": ""
    })

    # Build final report with only executed agents
    final_report = "━━━━━━━━━━━━━━━━━━━\nMEDICAL ANALYSIS\n━━━━━━━━━━━━━━━━━━━\n"

    if "emergency_agent" in agents_to_run and result.get("emergency_output"):
        final_report += f"\n🚨 EMERGENCY ANALYSIS\n{result['emergency_output']}\n"

    if "specialist_agent" in agents_to_run and result.get("specialist_output"):
        final_report += f"\n🏥 SPECIALIST RECOMMENDATION\n{result['specialist_output']}\n"

    if "research_agent" in agents_to_run and result.get("research_output"):
        final_report += f"\n📚 RESEARCH\n{result['research_output']}\n"

    if "drug_agent" in agents_to_run and result.get("drug_output"):
        final_report += f"\n💊 DRUG ANALYSIS\n{result['drug_output']}\n"

    logger.info("LangGraph execution completed", agents_run=agents_to_run)
    return final_report
