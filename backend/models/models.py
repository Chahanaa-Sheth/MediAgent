from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class TemporalInfo(BaseModel):
    duration: Optional[str] = None
    onset: Optional[str] = None  # "sudden", "gradual"
    progression: Optional[str] = None  # "worsening", "stable", "improving"
    recurrence_pattern: Optional[str] = None


class MedicalContext(BaseModel):
    symptoms: List[str] = Field(default_factory=list)
    from typing import Union, Dict

    duration: Union[str, Dict, None] = None
    severity_indicators: List[str] = Field(default_factory=list)
    temporal_progression: Optional[str] = None
    medication_history: List[str] = Field(default_factory=list)
    emergency_flags: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1.0)
    medications_detected: bool = False
    additional_context: Dict[str, Any] = Field(default_factory=dict)


class SeverityScore(BaseModel):
    score: float = Field(ge=0, le=100)
    level: SeverityLevel
    reasoning: str
    emergency: bool = False


class ConfidenceScore(BaseModel):
    score: float = Field(ge=0, le=100)
    explanation: str
    factors: Dict[str, float] = Field(default_factory=dict)


class AgentResult(BaseModel):
    agent_name: str
    result: str
    confidence: Optional[float] = None
    reasoning: Optional[str] = None


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Chat(BaseModel):
    chat_id: str
    user_id: str
    title: str = "New Chat"
    messages: List[Message] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class User(BaseModel):
    username: str
    password_hash: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class AnalysisRequest(BaseModel):
    symptom: str
    chat_id: str


class AnalysisResponse(BaseModel):
    chat_id: str
    message_id: str
    content: str
    medical_context: Optional[MedicalContext] = None
    severity: Optional[SeverityScore] = None
    confidence: Optional[ConfidenceScore] = None
    agent_results: List[AgentResult] = Field(default_factory=list)
    rag_sources: List[Dict[str, Any]] = Field(default_factory=list)


class UserSignup(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
