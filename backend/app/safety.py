from typing import List, Tuple


class SafetyAnalyzer:
    def __init__(self) -> None:
        self.crisis_keywords: List[str] = [
            "kill myself",
            "end my life",
            "suicide",
            "self harm",
            "hurt myself",
            "i want to die",
            "no reason to live",
            "hopeless",
            "can't go on",
            "worthless",
            "not worth living",
            "give up",
            "end it all",
        ]
        self.distress_keywords: List[str] = [
            "panic attack",
            "can't breathe",
            "heart racing",
            "terrified",
            "overwhelmed",
            "breaking down",
        ]

    def detect_risk(self, text: str) -> Tuple[bool, List[str]]:
        lowered = text.lower()
        crisis_matches = [kw for kw in self.crisis_keywords if kw in lowered]
        distress_matches = [kw for kw in self.distress_keywords if kw in lowered]
        all_matches = crisis_matches + distress_matches
        is_crisis = len(crisis_matches) > 0
        is_distress = len(distress_matches) > 0
        return is_crisis or is_distress, all_matches

    @staticmethod
    def crisis_response() -> str:
        return (
            "Thank you for sharing this with me. I am really glad you reached out. "
            "You deserve support right now. I am not a therapist, but I strongly encourage you "
            "to contact a trusted person or a local crisis helpline immediately. "
            "If you are in immediate danger, please call emergency services now. "
            "You are not alone, and there are people who care about you."
        )

    @staticmethod
    def distress_response() -> str:
        return (
            "I can hear how distressed you are right now. This sounds really overwhelming. "
            "Please try to take slow, deep breaths if you can. Reach out to someone you trust "
            "or a helpline for immediate support. You're important, and this feeling will pass."
        )
