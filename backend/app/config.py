from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve .env next to the backend package (…/backend/.env), not the shell CWD.
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent
# Later files override earlier keys when both define the same variable.
_ENV_FILES = (
    _PROJECT_ROOT / ".env",
    _BACKEND_DIR / ".env",
)


class Settings(BaseSettings):
    app_name: str = "Emotion-Aware Mental Health Chatbot API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:5173"
    mongodb_uri: str | None = None
    # Optional: set these instead of MONGODB_URI so passwords with @ : / # ? are encoded safely.
    mongodb_atlas_user: str | None = None
    mongodb_atlas_password: str | None = None
    mongodb_atlas_host: str | None = None
    mongodb_db_name: str = "emotion_chatbot"
    model_name: str = "j-hartmann/emotion-english-distilroberta-base"
    # Hugging Face Inference Providers via huggingface_hub (no local PyTorch).
    hf_api_token: str | None = None
    # Appended to MODEL_NAME for InferenceClient (e.g. j-hartmann/...:hf-inference). Set empty to disable.
    hf_inference_provider: str = "hf-inference"
    # Unused by emotion.py; kept for documentation / future use.
    hf_inference_url: str = "https://router.huggingface.co/hf-inference"
    context_window_size: int = 10
    # When true, /health may include a short database_error (dev only; turn off in production).
    database_debug: bool = False
    secret_key: str = "your-secret-key-here-change-in-production"

    @field_validator("database_debug", mode="before")
    @classmethod
    def coerce_database_debug_bool(cls, v: object) -> object:
        # .env typos like "true," or " True " should not crash startup.
        if isinstance(v, str):
            s = v.strip().rstrip(",").strip().lower()
            if s in ("true", "1", "yes", "on"):
                return True
            if s in ("false", "0", "no", "off", ""):
                return False
        return v

    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def build_atlas_uri_from_parts(self) -> "Settings":
        user = (self.mongodb_atlas_user or "").strip()
        password = self.mongodb_atlas_password or ""
        host = (self.mongodb_atlas_host or "").strip()
        if user and password and host:
            self.mongodb_uri = (
                f"mongodb+srv://{quote_plus(user)}:{quote_plus(password)}@{host}/"
                "?retryWrites=true&w=majority"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
