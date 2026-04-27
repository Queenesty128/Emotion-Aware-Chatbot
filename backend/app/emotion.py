from collections import Counter
from typing import Any, Dict, List, Tuple

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from app.config import get_settings


def _inference_model_id(model_name: str, provider: str | None) -> str:
    """Build model id for InferenceClient (e.g. org/model:hf-inference)."""
    p = (provider or "").strip()
    if not p:
        return model_name
    if model_name.endswith(f":{p}"):
        return model_name
    return f"{model_name}:{p}"


class EmotionDetector:

    def __init__(self) -> None:
        settings = get_settings()

        self.model_name = settings.model_name
        self._inference_model = settings.model_name  # ✅ fixed earlier
        self.token = (settings.hf_api_token or "").strip() or None

        self.supported_emotions = {"sadness", "joy", "anger", "fear", "neutral"}

        self._client: InferenceClient | None = None

        if self.token:
            self._client = InferenceClient(
                model=self._inference_model,
                token=self.token
            )
    def detect(self, text: str) -> Tuple[str, float, str, Dict[str, float]]:
        if not self.token or self._client is None:
            raise RuntimeError(
                "HF_API_TOKEN is not set. Create a token at https://huggingface.co/settings/tokens "
                "with permission to use Inference Providers, and add HF_API_TOKEN to backend/.env."
            )

        try:
            raw = self._client.text_classification(text)
        except HfHubHTTPError as exc:
            resp = getattr(exc, "response", None)
            code = getattr(resp, "status_code", None) if resp is not None else None
            if code == 401:
                raise RuntimeError("Hugging Face returned 401: check HF_API_TOKEN is valid.") from exc
            if code == 403:
                body = ""
                try:
                    if resp is not None and resp.text:
                        body = f" Details: {resp.text[:300].strip()}"
                except Exception:
                    pass
                raise RuntimeError(
                    "Hugging Face returned 403 (forbidden). Fix it like this:\n"
                    "1) Open https://huggingface.co/settings/tokens/new — choose Fine-grained.\n"
                    "2) Under 'User permissions', enable 'Make calls to Inference Providers' "
                    "(may appear as inference / serverless access).\n"
                    "3) Generate the token, set HF_API_TOKEN in backend/.env, restart uvicorn.\n"
                    "4) Open https://huggingface.co/settings/inference-providers and ensure "
                    "providers are allowed for your account.\n"
                    f"{body}"
                ) from exc
            raise RuntimeError(f"Hugging Face inference failed: {exc}") from exc

        score_map = self._scores_from_output(raw)
        if not score_map:
            return "neutral", 0.0, "low", {}

        dominant = max(score_map, key=score_map.get)
        if dominant not in self.supported_emotions:
            dominant = "neutral"

        score = score_map.get(dominant, 0.0)
        intensity = self._get_intensity(dominant, score)
        return dominant, score, intensity, score_map

    @staticmethod
    def _get_intensity(emotion: str, score: float) -> str:
        if emotion == "neutral":
            return "low"
        if score > 0.8:
            return "high"
        elif score > 0.5:
            return "medium"
        else:
            return "low"

    @staticmethod
    def _scores_from_output(raw: Any) -> Dict[str, float]:
        if raw is None:
            return {}
        items: List[Any] = raw if isinstance(raw, list) else [raw]
        out: Dict[str, float] = {}
        for item in items:
            label: str | None = None
            score: float | None = None
            if isinstance(item, dict):
                label = item.get("label")
                score = item.get("score")
            else:
                label = getattr(item, "label", None)
                score = getattr(item, "score", None)
            if isinstance(label, str) and isinstance(score, (int, float)):
                out[label.lower()] = float(score)
        return out

    @staticmethod
    def count_emotions(emotions: List[str]) -> Dict[str, int]:
        return dict(Counter(emotions))
