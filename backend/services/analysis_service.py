from typing import Dict, List, Any, AsyncGenerator
from services.chat_service import ChatService
from services.rag_service import RAGService
from services.llm_service import LLMService
from services.medical_reasoning import SymptomExtractor, SeverityScorer, AgentRouter
from agents.langgraph_orchestrator import run_langgraph
from prompts.system_prompt import SYSTEM_PROMPT
from prompts.prompt_builder import build_user_turn
from models.models import MedicalContext, AgentResult
from utils.exceptions import Logger
import json
from agents.followup_agent import (
    generate_followup_questions
)

class AnalysisService:
    """Orchestrate medical analysis pipeline"""

    def __init__(self, chat_service: ChatService, rag_service: RAGService, llm_service: LLMService):
        self.chat_service = chat_service
        self.rag_service = rag_service
        self.llm_service = llm_service
        self.logger = Logger("AnalysisService")

        # Medical reasoning components
        self.extractor = SymptomExtractor()
        self.scorer = SeverityScorer()
        self.router = AgentRouter()

    async def analyze_symptom_stream(self, symptom: str, chat_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream medical analysis with real-time updates"""
        try:
            # Get chat history
            chat = await self.chat_service.get_chat_history(chat_id, limit=50)
            history = [msg for msg in chat.get("messages", [])]
            self.logger.info("Starting analysis", chat_id=chat_id, symptom_length=len(symptom))

            # Extract medical context
            yield self._format_event("status", {"message": "Extracting medical context..."})
            medical_context = await self.extractor.extract(symptom, history)

            from agents.diagnosis_agent import (generate_differential_diagnosis)
            yield self._format_event(
    "status",
    {
        "message":
        "Generating differential diagnosis..."
    }
)
            
            diagnosis = await generate_differential_diagnosis(symptom,medical_context)
            yield self._format_event("diagnosis",diagnosis)
            followups = await generate_followup_questions(symptom,medical_context,diagnosis)
            yield self._format_event("followup",followups)

            
            yield self._format_event("extraction", {
                "symptoms": medical_context.symptoms,
                "duration": medical_context.duration,
                "confidence": medical_context.confidence
            })

            # Score severity
            yield self._format_event("status", {"message": "Scoring severity..."})
            severity_score = await self.scorer.score(medical_context)
            yield self._format_event("severity", {
                "score": severity_score.score,
                "level": severity_score.level,
                "reasoning": severity_score.reasoning,
                "emergency": severity_score.emergency
            })

            # Route agents
            yield self._format_event("status", {"message": "Routing agents..."})
            agents_to_run = await self.router.route(medical_context, severity_score)
            yield self._format_event("routing", {"agents": agents_to_run})

            # Run LangGraph orchestrator
            yield self._format_event("status", {"message": "Running medical agents..."})
            agent_outputs = run_langgraph(symptom, agents_to_run, history=history)
            yield self._format_event("agents", agent_outputs)

            # RAG search
            yield self._format_event("status", {"message": "Searching medical knowledge..."})
            rag_results = await self.rag_service.search_all_sources(symptom)
            # keep only top relevant results
            rag_results["pubmed_papers"] = rag_results["pubmed_papers"][:2]
            rag_results["local_documents"] = rag_results["local_documents"][:3]
            yield self._format_event("rag", rag_results)

            # Build prompt with all context
            formatted_history = "\n".join(
                [f"{msg.get('role', '')}: {msg.get('content', '')}" for msg in history[-4:]]
            )

            # Format RAG results as a concatenated string
                        # Format RAG results as a concatenated string
            rag_text_parts = []

            if rag_results.get("local_documents"):

                local_docs = []

                for doc in rag_results["local_documents"]:

                    if isinstance(doc, dict):

                        local_docs.append(
                            f"""
SOURCE: {doc.get("source", "unknown")}
RELEVANCE: {doc.get("score", 0)}

{doc.get("content", "")}
"""
                        )

                    else:

                        local_docs.append(str(doc))

                rag_text_parts.append(
                    "LOCAL DOCUMENTS:\n\n"
                    + "\n\n".join(local_docs)
                )

            if rag_results.get("pubmed_papers"):

                summaries = []

                for paper in rag_results["pubmed_papers"][:3]:

                    summaries.append(str(paper)[:1000])

                rag_text_parts.append(
                    "PUBMED RESEARCH SUMMARIES:\n"
                    + "\n\n".join(summaries)
                )

            if rag_results.get("pinecone_results"):

                pinecone_docs = []

                for doc in rag_results["pinecone_results"]:

                    if isinstance(doc, dict):

                        pinecone_docs.append(
                            doc.get("content", str(doc))
                        )

                    else:

                        pinecone_docs.append(str(doc))

                rag_text_parts.append(
                    "PINECONE RESULTS:\n"
                    + "\n\n".join(pinecone_docs)
                )

            rag_text = (
                "\n\n".join(rag_text_parts)
                if rag_text_parts
                else ""
            )
       

            user_prompt = build_user_turn(           
    symptom=symptom,
    rag_results=rag_text,
    formatted_history=formatted_history,
    medical_context=medical_context,
    severity=severity_score,
    diagnosis=diagnosis,
    followups=followups,
    agent_outputs=agent_outputs
)

            # Stream LLM response
            yield self._format_event("status", {"message": "Generating response..."})
            full_response = ""
            async for chunk in self.llm_service.stream_response(SYSTEM_PROMPT, user_prompt):
                full_response += chunk
                yield self._format_event("chunk", {"content": chunk})

            # Save to database
            yield self._format_event("status", {"message": "Saving to database..."})
            await self.chat_service.add_message(chat_id, "user", symptom)
            await self.chat_service.add_message(
                chat_id,
                "assistant",
                full_response,
                metadata={
                    "medical_context": medical_context.dict(),
                    "severity": severity_score.dict(),
                    "agents_run": agents_to_run
                }
            )

            # Auto-title if needed
            if chat.get("title") == "New Chat":
                await self.chat_service.auto_title_chat(chat_id, symptom)

            yield self._format_event("done", {"success": True})
            self.logger.info("Analysis completed", chat_id=chat_id)

        except Exception as e:
            self.logger.error("Analysis failed", error=str(e), chat_id=chat_id)
            yield self._format_event("error", {"message": str(e)})

    def _format_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """Format event as SSE"""
        return f"data: {json.dumps({'type': event_type, 'data': data})}\n\n"

    async def extract_medical_context(self, symptom: str, history: List[Dict[str, Any]]) -> MedicalContext:
        """Extract medical context from input"""
        return await self.extractor.extract(symptom, history)

    async def route_agents(self, medical_context: MedicalContext, severity: Dict[str, Any]) -> List[str]:
        """Route to appropriate agents"""
        # Convert severity dict back to SeverityScore if needed
        from models.models import SeverityScore, SeverityLevel
        if isinstance(severity, dict):
            severity = SeverityScore(
                score=severity.get("score", 0),
                level=SeverityLevel(severity.get("level", "LOW")),
                reasoning=severity.get("reasoning", ""),
                emergency=severity.get("emergency", False)
            )
        return await self.router.route(medical_context, severity)
