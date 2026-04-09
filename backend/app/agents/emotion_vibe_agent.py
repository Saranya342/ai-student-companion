from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class EmotionVibeAgent:
    """
    Detects user mood + adapts tone.
    Handles stress/motivation detection and casual language.
    """
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Emotion keywords
        self.emotion_keywords = {
            "stressed": ["stressed", "overwhelmed", "pressure", "too much", "burning out", "can't handle"],
            "tired": ["tired", "exhausted", "drained", "sleepy", "no energy", "fatigue"],
            "sad": ["sad", "depressed", "unhappy", "down", "hopeless", "demotivated"],
            "happy": ["happy", "excited", "great", "amazing", "awesome", "aced", "nailed it"],
            "frustrated": ["frustrated", "stuck", "annoyed", "can't understand", "confused"],
            "anxious": ["anxious", "worried", "nervous", "scared", "panic", "freaking out"]
        }
        
        # Vibe keywords (casual Gen-Z language)
        self.vibe_keywords = {
            "casual": ["macha", "bro", "dude", "yaar", "mate", "buddy", "fam", "bestie"],
            "formal": ["sir", "ma'am", "please", "could you", "would you"],
            "urgent": ["asap", "urgent", "emergency", "right now", "immediately"]
        }
        
        # Response tones for LLM
        self.response_tones = {
            "stressed": "Be calm and reassuring. Acknowledge stress, offer to break tasks down. Use supportive tone.",
            "tired": "Be gentle and caring. Suggest a break, validate their exhaustion. Be comforting.",
            "sad": "Be warm and empathetic. Validate their feelings, offer support. Don't be dismissive.",
            "happy": "Be energetic and celebrate! Match their excitement. Use positive reinforcement.",
            "frustrated": "Be patient. Acknowledge frustration, offer step-by-step help. Don't lecture.",
            "anxious": "Be grounding and calm. Focus on what they CAN control. Reassure them.",
            "neutral": "Be friendly, helpful, and supportive as usual."
        }
    
    def detect_emotion(self, message: str) -> Dict:
        """Analyze message emotion"""
        
        scores = self.analyzer.polarity_scores(message)
        compound = scores["compound"]
        
        message_lower = message.lower()
        detected_emotion = "neutral"
        max_matches = 0
        
        for emotion, keywords in self.emotion_keywords.items():
            matches = sum(1 for kw in keywords if kw in message_lower)
            if matches > max_matches:
                max_matches = matches
                detected_emotion = emotion
        
        if max_matches == 0:
            if compound >= 0.5:
                detected_emotion = "happy"
            elif compound <= -0.5:
                detected_emotion = "sad"
        
        confidence = min(1.0, abs(compound) + (max_matches * 0.2))
        is_negative = compound < -0.3
        
        return {
            "emotion": detected_emotion,
            "confidence": round(confidence, 2),
            "sentiment_score": round(compound, 2),
            "response_tone": self.response_tones[detected_emotion],
            "is_negative": is_negative
        }
    
    def detect_vibe(self, message: str) -> Dict:
        """Detect casual vs formal vibe"""
        
        message_lower = message.lower()
        detected_vibe = "neutral"
        matched_words = []
        
        for vibe, keywords in self.vibe_keywords.items():
            for kw in keywords:
                if kw in message_lower:
                    detected_vibe = vibe
                    matched_words.append(kw)
        
        return {
            "vibe": detected_vibe,
            "matched_words": matched_words,
            "is_casual": detected_vibe == "casual",
            "is_urgent": detected_vibe == "urgent"
        }
    
    def analyze(self, message: str) -> Dict:
        """
        Complete analysis: emotion + vibe
        
        Returns:
        {
            "emotion": "stressed",
            "vibe": "casual",
            "response_tone": "Be calm and...",
            "should_match_casual": True,
            "is_negative": True
        }
        """
        emotion_data = self.detect_emotion(message)
        vibe_data = self.detect_vibe(message)
        
        result = {
            "emotion": emotion_data["emotion"],
            "confidence": emotion_data["confidence"],
            "sentiment_score": emotion_data["sentiment_score"],
            "vibe": vibe_data["vibe"],
            "vibe_words": vibe_data["matched_words"],
            "response_tone": emotion_data["response_tone"],
            "should_match_casual": vibe_data["is_casual"],
            "is_negative": emotion_data["is_negative"],
            "is_urgent": vibe_data["is_urgent"]
        }
        
        logger.info(f"🎭 Emotion: {result['emotion']}, Vibe: {result['vibe']}")
        return result


# Global instance
emotion_vibe_agent = EmotionVibeAgent()