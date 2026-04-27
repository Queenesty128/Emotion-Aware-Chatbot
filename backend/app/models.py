from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    emotion: str
    emotion_intensity: str  # low, medium, high
    risk_detected: bool
    disclaimer: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EmotionLog(BaseModel):
    user_id: str
    text: str
    emotion: str
    score: float
    intensity: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionState(BaseModel):
    user_id: str
    recent_messages: List[Message] = Field(default_factory=list)
    recent_emotions: List[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TrendResponse(BaseModel):
    user_id: str
    emotion_counts: Dict[str, int]
    latest_emotions: List[Dict[str, Any]]
    total_messages: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    status: str
    app: str
    model_loaded: bool
    database_connected: bool
    emotion_backend: str = Field(
        default="huggingface_inference_api",
        description="Remote HF Inference API (no local PyTorch).",
    )
    hf_token_configured: bool = False
    database_error: Optional[str] = Field(
        default=None,
        description="Only set when DATABASE_DEBUG=true and MongoDB ping failed.",
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# New models for authentication and personalization
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    password: str = Field(..., min_length=8)
    name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    user_id: str
    username: str
    email: str
    name: Optional[str] = None
    preferred_tone: str = "neutral"  # gentle, motivational, neutral
    created_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
