from typing import Dict, List, Optional
from app.database import MongoRepository


class ResponseGenerator:
    def __init__(self, repository: MongoRepository) -> None:
        self.repository = repository
        self.templates = {
            "sadness": {
                "low": ["I hear that. It's okay to feel this way sometimes.", "Take your time. I'm here."],
                "medium": ["That sounds tough. Want to talk about what's making you feel this way?", "I can sense this is weighing on you. How can I support you?"],
                "high": ["I'm really sorry you're going through this. You don't have to carry this alone.", "This sounds incredibly heavy. Please know that your feelings are valid."]
            },
            "anger": {
                "low": ["I understand feeling frustrated. Let's work through this.", "It's normal to feel angry sometimes."],
                "medium": ["That anger makes sense. What triggered it?", "I can feel the intensity. Want to explore what's behind it?"],
                "high": ["This sounds really upsetting. I'm here to listen without judgment.", "Strong emotions like this are valid. How can I help you process this?"]
            },
            "fear": {
                "low": ["Anxiety can be tough. You're not alone.", "It's okay to feel worried."],
                "medium": ["That fear sounds overwhelming. What specifically worries you?", "I hear the anxiety in your words. Let's take this one step at a time."],
                "high": ["I'm here with you during this scary time. Your safety matters.", "This sounds terrifying. Please reach out to someone you trust if you need immediate support."]
            },
            "joy": {
                "low": ["That's nice to hear. Tell me more?", "Glad to hear some positivity."],
                "medium": ["That sounds wonderful! What's bringing you joy?", "I'm happy for you. Let's celebrate this moment."],
                "high": ["This is amazing! You deserve to feel this happiness.", "What a beautiful feeling! Share more if you'd like."]
            },
            "neutral": {
                "low": ["How are you feeling today?", "I'm here to listen."],
                "medium": ["Tell me more about what's on your mind.", "I'm listening."],
                "high": ["I'm here for whatever you need.", "Take your time."]
            }
        }

    def generate(
        self,
        user_message: str,
        emotion: str,
        intensity: str,
        recent_emotions: List[str],
        user_id: str,
        preferred_tone: str = "neutral"
    ) -> str:
        # Get user history for personalization
        user_profile = self.repository.get_user_by_username(user_id)  # Assuming user_id is username for now
        name = user_profile.get("name", "") if user_profile else ""

        # Analyze patterns
        pattern = self._analyze_patterns(recent_emotions, emotion)

        # Build prompt-like response
        base_responses = self.templates.get(emotion, self.templates["neutral"]).get(intensity, ["I'm here to listen."])
        response = base_responses[len(user_message) % len(base_responses)]

        # Personalize
        if name:
            response = f"{name}, {response.lower()}"
        if pattern:
            response += f" {pattern}"

        # Adapt to tone
        if preferred_tone == "gentle":
            response = response.replace("!", ".").replace("?", "? Take your time.")
        elif preferred_tone == "motivational":
            response += " Remember, you're stronger than you know."

        return response.strip()

    def _analyze_patterns(self, recent_emotions: List[str], current_emotion: str) -> str:
        if not recent_emotions:
            return ""

        negative = {"sadness", "anger", "fear"}
        recent_negative = sum(1 for e in recent_emotions[-5:] if e in negative)

        if recent_negative >= 4 and current_emotion in negative:
            return "You've been feeling this way a lot lately. Would you like to talk about what's been going on?"
        elif current_emotion == "joy" and recent_negative > 2:
            return "It's great to hear some positivity after what's been tough."

        return ""
