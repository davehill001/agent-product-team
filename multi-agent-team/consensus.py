# consensus.py
import logging
from typing import List, Dict, Any, Tuple, Optional
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsensusDetector:
    """
    Enhanced consensus detection with confidence scoring and agreement tracking.
    """
    
    def __init__(self):
        self.consensus_threshold = 0.7  # 70% agreement required
        self.confidence_threshold = 0.6  # 60% confidence required
        self.agreement_history = []
        self.consensus_attempts = []
        
        # Consensus indicators
        self.consensus_indicators = [
            "consensus reached", "consensus achieved", "agreed upon",
            "final decision", "we have consensus", "consensus has been reached",
            "let's finalize", "ready to move forward", "we should proceed",
            "we all agree", "unanimous decision", "collective agreement",
            "consensus reached:", "consensus_reached"
        ]
        
        # Agreement indicators
        self.positive_indicators = [
            "agree", "yes", "correct", "right", "good", "excellent",
            "consensus", "aligned", "support", "approve", "like",
            "sounds good", "works for me", "I'm on board"
        ]
        
        self.negative_indicators = [
            "disagree", "no", "wrong", "bad", "problem", "issue",
            "concern", "disapprove", "against", "oppose", "don't like",
            "not sure", "hesitant", "worried"
        ]
        
        # Neutral indicators
        self.neutral_indicators = [
            "maybe", "perhaps", "possibly", "consider", "think about",
            "explore", "investigate", "look into", "examine"
        ]
    
    def detect_consensus_attempt(self, messages: List[Dict[str, Any]]) -> bool:
        """
        Detect if agents are attempting to reach consensus.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            True if consensus attempt detected, False otherwise
        """
        if len(messages) < 3:
            return False
        
        recent_messages = messages[-3:]
        consensus_count = 0
        
        for msg in recent_messages:
            if isinstance(msg, dict):
                content = msg.get("content", msg.get("message", ""))
            else:
                content = str(msg)
            
            content_lower = content.lower()
            
            # Check for consensus indicators
            if any(indicator in content_lower for indicator in self.consensus_indicators):
                consensus_count += 1
            
            # Check for agreement patterns
            if self._has_agreement_pattern(content_lower):
                consensus_count += 0.5
        
        # Record consensus attempt
        if consensus_count >= 2:
            self.consensus_attempts.append({
                "timestamp": datetime.now(),
                "message_count": len(messages),
                "confidence": consensus_count / 3
            })
            logger.info(f"Consensus attempt detected (confidence: {consensus_count/3:.2f})")
            return True
        
        return False
    
    def calculate_agreement_level(self, messages: List[Dict[str, Any]]) -> float:
        """
        Calculate the overall agreement level in the conversation.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Agreement level between 0.0 and 1.0
        """
        if not messages:
            return 0.0
        
        total_agreement = 0.0
        message_count = 0
        
        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content", msg.get("message", ""))
            else:
                content = str(msg)
            
            agreement_score = self._calculate_message_agreement(content)
            total_agreement += agreement_score
            message_count += 1
        
        if message_count == 0:
            return 0.0
        
        overall_agreement = total_agreement / message_count
        self.agreement_history.append(overall_agreement)
        
        return overall_agreement
    
    def _calculate_message_agreement(self, content: str) -> float:
        """
        Calculate agreement score for a single message.
        
        Args:
            content: Message content
            
        Returns:
            Agreement score between 0.0 and 1.0
        """
        content_lower = content.lower()
        
        positive_count = sum(1 for indicator in self.positive_indicators if indicator in content_lower)
        negative_count = sum(1 for indicator in self.negative_indicators if indicator in content_lower)
        neutral_count = sum(1 for indicator in self.neutral_indicators if indicator in content_lower)
        
        total_indicators = positive_count + negative_count + neutral_count
        
        if total_indicators == 0:
            return 0.5  # Neutral if no indicators found
        
        # Calculate weighted agreement score
        agreement_score = (positive_count * 1.0 + neutral_count * 0.5) / total_indicators
        
        return agreement_score
    
    def _has_agreement_pattern(self, content: str) -> bool:
        """
        Check if content has agreement patterns.
        
        Args:
            content: Message content
            
        Returns:
            True if agreement pattern detected
        """
        content_lower = content.lower()
        
        # Check for explicit agreement phrases
        agreement_phrases = [
            "i agree", "we agree", "that's right", "exactly",
            "you're right", "correct", "good point", "makes sense"
        ]
        
        return any(phrase in content_lower for phrase in agreement_phrases)
    
    def detect_stalemate(self, messages: List[Dict[str, Any]], agreement_level: float) -> bool:
        """
        Detect if the conversation is at a stalemate.
        
        Args:
            messages: List of conversation messages
            agreement_level: Current agreement level
            
        Returns:
            True if stalemate detected
        """
        if len(messages) < 5:
            return False
        
        # Check for stalemate indicators
        stalemate_phrases = [
            "agree to disagree", "no consensus", "deadlock", "cannot agree",
            "stuck", "impasse", "no progress", "going in circles"
        ]
        
        recent_content = " ".join([
            msg.get("content", msg.get("message", str(msg))).lower() 
            for msg in messages[-5:]
        ])
        
        stalemate_count = sum(1 for phrase in stalemate_phrases if phrase in recent_content)
        
        # Check for low agreement over multiple rounds
        if agreement_level < 0.3 and len(messages) > 10:
            return True
        
        return stalemate_count >= 2
    
    def _detect_repetition(self, messages: List[Dict[str, Any]]) -> bool:
        """
        Detect if the conversation is repeating itself.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            True if repetition detected
        """
        if len(messages) < 3:
            return False
        
        recent_messages = messages[-3:]
        content_similarity = 0
        
        for i in range(len(recent_messages) - 1):
            for j in range(i + 1, len(recent_messages)):
                content1 = recent_messages[i].get("content", recent_messages[i].get("message", str(recent_messages[i]))).lower()
                content2 = recent_messages[j].get("content", recent_messages[j].get("message", str(recent_messages[j]))).lower()
                
                # Simple similarity check
                words1 = set(content1.split())
                words2 = set(content2.split())
                
                if words1 and words2:
                    similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                    content_similarity = max(content_similarity, similarity)
        
        return content_similarity > 0.7
    
    def _extract_topics(self, content: str) -> List[str]:
        """
        Extract topics from message content.
        
        Args:
            content: Message content
            
        Returns:
            List of extracted topics
        """
        topics = []
        content_lower = content.lower()
        
        # Common app development topics
        topic_keywords = {
            "user experience": ["ux", "user experience", "user interface", "ui"],
            "technical": ["technical", "feasibility", "implementation", "architecture"],
            "business": ["business", "value", "roi", "market"],
            "quality": ["quality", "testing", "qa", "reliability"],
            "design": ["design", "layout", "components", "wireframe"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def get_consensus_confidence(self, messages: List[Dict[str, Any]]) -> float:
        """
        Get confidence level for consensus detection.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Confidence level between 0.0 and 1.0
        """
        if not messages:
            return 0.0
        
        # Calculate agreement level
        agreement_level = self.calculate_agreement_level(messages)
        
        # Check for consensus indicators
        consensus_indicator_count = 0
        for msg in messages[-3:]:
            content = msg.get("content", msg.get("message", str(msg))).lower()
            if any(indicator in content for indicator in self.consensus_indicators):
                consensus_indicator_count += 1
        
        # Calculate confidence based on agreement and consensus indicators
        confidence = (agreement_level * 0.7) + (consensus_indicator_count / 3 * 0.3)
        
        return min(1.0, confidence)
    
    def should_force_consensus(self, messages: List[Dict[str, Any]], round_count: int) -> bool:
        """
        Determine if consensus should be forced.
        
        Args:
            messages: List of conversation messages
            round_count: Current round count
            
        Returns:
            True if consensus should be forced
        """
        # Force consensus after 15 rounds
        if round_count >= 15:
            return True
        
        # Force consensus if stalemate detected
        if self.detect_stalemate(messages, self.calculate_agreement_level(messages)):
            return True
        
        # Force consensus if repetition detected
        if self._detect_repetition(messages):
            return True
        
        # Force consensus if multiple consensus attempts failed
        if len(self.consensus_attempts) >= 3:
            return True
        
        return False
    
    def get_consensus_summary(self) -> Dict[str, Any]:
        """
        Get a summary of consensus detection.
        
        Returns:
            Dictionary containing consensus summary
        """
        return {
            "consensus_attempts": len(self.consensus_attempts),
            "agreement_history": self.agreement_history[-5:] if self.agreement_history else [],
            "average_agreement": sum(self.agreement_history) / len(self.agreement_history) if self.agreement_history else 0.0,
            "last_consensus_attempt": self.consensus_attempts[-1] if self.consensus_attempts else None
        }

# Global consensus detector instance
consensus_detector = ConsensusDetector()

if __name__ == "__main__":
    # Test consensus detection
    detector = ConsensusDetector()
    
    # Test messages
    test_messages = [
        {"content": "I think we should focus on user experience", "agent": "Alex"},
        {"content": "I agree with Alex on UX", "agent": "Max"},
        {"content": "But we need to consider technical feasibility", "agent": "Sam"},
        {"content": "I agree with Sam", "agent": "Jamie"},
        {"content": "Let's reach consensus on this", "agent": "Max"}
    ]
    
    # Test consensus detection
    consensus_attempt = detector.detect_consensus_attempt(test_messages)
    print(f"Consensus attempt detected: {consensus_attempt}")
    
    # Test agreement level
    agreement_level = detector.calculate_agreement_level(test_messages)
    print(f"Agreement level: {agreement_level:.2f}")
    
    # Test consensus confidence
    confidence = detector.get_consensus_confidence(test_messages)
    print(f"Consensus confidence: {confidence:.2f}")
    
    # Test stalemate detection
    stalemate = detector.detect_stalemate(test_messages, agreement_level)
    print(f"Stalemate detected: {stalemate}")
    
    # Test force consensus
    should_force = detector.should_force_consensus(test_messages, 5)
    print(f"Should force consensus: {should_force}") 