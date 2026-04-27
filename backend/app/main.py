import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.auth import create_access_token, get_password_hash, verify_password, verify_token
from app.config import get_settings
from app.database import MongoRepository
from app.emotion import EmotionDetector
from app.models import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
    TrendResponse,
    UserCreate,
    UserLogin,
    UserProfile,
    Token,
)
from app.response import ResponseGenerator
from app.safety import SafetyAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")

_backend_dir = Path(__file__).resolve().parent.parent
_env_backend = _backend_dir / ".env"
_env_root = _backend_dir.parent / ".env"
logger.info(
    "Config: backend .env exists=%s | root .env exists=%s | hf_token_set=%s",
    _env_backend.is_file(),
    _env_root.is_file(),
    bool((settings.hf_api_token or "").strip()),
)
logger.info("Frontend origin: %s", settings.frontend_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


security = HTTPBearer()
emotion_detector = EmotionDetector()
safety_analyzer = SafetyAnalyzer()
repository = MongoRepository()
response_generator = ResponseGenerator(repository)

DISCLAIMER = (
    "This chatbot offers emotional support but is not a therapist and does not provide medical advice, "
    "diagnosis, or prescriptions."
)


@app.post("/register", response_model=Token)
def register(user: UserCreate):
    try:
        db_user = repository.get_user_by_username(user.username)

        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = get_password_hash(user.password)

        user_data = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "name": user.name,
            "preferred_tone": "neutral",
            "created_at": datetime.utcnow(),
        }

        repository.create_user(user_data)

        access_token = create_access_token(data={"sub": user.username})
        return Token(access_token=access_token)

    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=Token)
def login(user: UserLogin):
    db_user = repository.get_user_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    repository.update_user_last_login(user.username)
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)


@app.get("/profile", response_model=UserProfile)
def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token_data = verify_token(credentials.credentials, HTTPException(status_code=401, detail="Invalid token"))
    user = repository.get_user_by_username(token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(
        user_id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        name=user.get("name"),
        preferred_tone=user.get("preferred_tone", "neutral"),
        created_at=user["created_at"],
        last_login=user.get("last_login"),
    )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token_data = verify_token(credentials.credentials, HTTPException(status_code=401, detail="Invalid token"))
    return token_data.username


@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={500: {"model": ErrorResponse}},
)
def chat(payload: ChatRequest, current_user: str = Depends(get_current_user)) -> ChatResponse:
    print("Incoming request:", payload.dict())  # Temporary debug
    try:
        risk_detected, _ = safety_analyzer.detect_risk(payload.message)
        emotion, score, intensity, _ = emotion_detector.detect(payload.message)

        recent = repository.get_recent_session(current_user, settings.context_window_size)
        recent_emotions = recent.get("emotions", [])

        user_profile = repository.get_user_by_username(current_user)
        preferred_tone = user_profile.get("preferred_tone", "neutral") if user_profile else "neutral"

        if risk_detected:
            bot_response = safety_analyzer.crisis_response()
        else:
            bot_response = response_generator.generate(
                user_message=payload.message,
                emotion=emotion,
                intensity=intensity,
                recent_emotions=recent_emotions,
                user_id=current_user,
                preferred_tone=preferred_tone,
            )

        repository.save_chat(current_user, payload.message, bot_response)
        repository.save_emotion(current_user, payload.message, emotion, score, intensity)
        repository.save_message(current_user, "user", payload.message, emotion)
        repository.save_message(current_user, "assistant", bot_response)

        repository.update_session(
            user_id=current_user,
            new_user_message=payload.message,
            bot_reply=bot_response,
            emotion=emotion,
            limit=settings.context_window_size,
        )

        return ChatResponse(
            response=str(bot_response),  # Ensure always string
            emotion=emotion,
            emotion_intensity=intensity,
            risk_detected=risk_detected,
            disclaimer=DISCLAIMER,
            timestamp=datetime.utcnow(),
        )
    except Exception as exc:
        logger.exception("Failed to process chat request")
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc


@app.get(
    "/trends",
    response_model=TrendResponse,
    responses={500: {"model": ErrorResponse}},
)
def trends(current_user: str = Depends(get_current_user)) -> TrendResponse:
    try:
        logs = repository.get_emotion_trends(current_user)
        emotions = [row.get("emotion", "neutral") for row in logs]
        counts = emotion_detector.count_emotions(emotions)
        latest = [
            {
                "emotion": row.get("emotion", "neutral"),
                "score": row.get("score", 0.0),
                "intensity": row.get("intensity", "low"),
                "timestamp": row.get("timestamp"),
            }
            for row in reversed(logs)
        ]

        return TrendResponse(
            user_id=current_user,
            emotion_counts=counts,
            latest_emotions=latest,
            total_messages=len(logs),
        )
    except Exception as exc:
        logger.exception("Failed to fetch trend data")
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc
