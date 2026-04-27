import logging
from datetime import datetime
from typing import Dict, List, Optional

from pymongo import MongoClient
from pymongo.errors import ConfigurationError, PyMongoError

from app.config import get_settings
from app.models import Message

logger = logging.getLogger(__name__)


class MongoRepository:
    """
    MongoDB access with lazy client creation so the API can start even when
    Atlas SRV/DNS is unreachable (corporate firewall, VPN, etc.).
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: Optional[MongoClient] = None
        self._db = None
        self._chats = None
        self._emotions = None
        self._sessions = None
        self._users = None
        self._messages = None

    def _connect(self) -> None:
        if self._client is not None:
            return
        self._client = MongoClient(
            self._settings.mongodb_uri,
            serverSelectionTimeoutMS=10_000,
        )
        self._db = self._client[self._settings.mongodb_db_name]
        self._chats = self._db["chats"]
        self._emotions = self._db["emotions"]
        self._sessions = self._db["sessions"]
        self._users = self._db["users"]
        self._messages = self._db["messages"]

    def ping(self) -> tuple[bool, str | None]:
        """
        Returns (ok, error_message). error_message is safe to show in dev when DATABASE_DEBUG=true.
        """
        try:
            self._connect()
            self._client.admin.command("ping")  # type: ignore[union-attr]
            return True, None
        except (ConfigurationError, PyMongoError, OSError, TimeoutError) as exc:
            msg = f"{type(exc).__name__}: {exc}"
            logger.warning("MongoDB ping failed: %s", msg)
            return False, msg[:400]
        except Exception as exc:
            msg = f"{type(exc).__name__}: {exc}"
            logger.warning("MongoDB ping failed: %s", msg)
            return False, msg[:400]

    def save_chat(self, user_id: str, user_message: str, bot_message: str) -> None:
        self._connect()
        self._chats.insert_one(
            {
                "user_id": user_id,
                "user_message": user_message,
                "bot_message": bot_message,
                "timestamp": datetime.utcnow(),
            }
        )

    def save_emotion(self, user_id: str, text: str, emotion: str, score: float, intensity: str) -> None:
        self._connect()
        self._emotions.insert_one(
            {
                "user_id": user_id,
                "text": text,
                "emotion": emotion,
                "score": score,
                "intensity": intensity,
                "timestamp": datetime.utcnow(),
            }
        )

    def get_recent_session(self, user_id: str, limit: int = 10) -> Dict[str, List]:
        self._connect()
        session = self._sessions.find_one({"user_id": user_id}) or {}
        return {
            "messages": session.get("recent_messages", [])[-limit:],
            "emotions": session.get("recent_emotions", [])[-limit:],
        }

    def update_session(self, user_id: str, new_user_message: str, bot_reply: str, emotion: str, limit: int) -> None:
        self._connect()
        existing = self.get_recent_session(user_id, limit=limit)
        messages = existing["messages"] + [
            Message(role="user", content=new_user_message).model_dump(mode="json"),
            Message(role="assistant", content=bot_reply).model_dump(mode="json"),
        ]
        emotions = existing["emotions"] + [emotion]

        self._sessions.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "recent_messages": messages[-limit:],
                    "recent_emotions": emotions[-limit:],
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )

    def get_emotion_trends(self, user_id: str, limit: int = 20) -> List[dict]:
        self._connect()
        cursor = self._emotions.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        return list(cursor)

    # New methods for users and auth
    def create_user(self, user_data: dict) -> str:
        self._connect()
        result = self._users.insert_one(user_data)
        return str(result.inserted_id)

    def get_user_by_username(self, username: str) -> Optional[dict]:
        self._connect()
        return self._users.find_one({"username": username})

    def update_user_last_login(self, username: str) -> None:
        self._connect()
        self._users.update_one(
            {"username": username},
            {"$set": {"last_login": datetime.utcnow()}}
        )

    def get_user_profile(self, user_id: str) -> Optional[dict]:
        self._connect()
        return self._users.find_one({"_id": user_id})

    def save_message(self, user_id: str, role: str, content: str, emotion: Optional[str] = None) -> None:
        self._connect()
        self._messages.insert_one({
            "user_id": user_id,
            "role": role,
            "content": content,
            "emotion": emotion,
            "timestamp": datetime.utcnow(),
        })

    def get_user_messages(self, user_id: str, limit: int = 50) -> List[dict]:
        self._connect()
        cursor = self._messages.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        return list(cursor)
