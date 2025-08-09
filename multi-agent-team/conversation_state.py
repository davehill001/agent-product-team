# conversation_state.py
import logging
from typing import List, Dict, Any, Optional, Tuple
from config import get_max_rounds
from datetime import datetime, timedelta
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationState:
    """
    Enhanced conversation state tracking for infinite loop prevention and consensus detection.
    """
    
    def __init__(self, max_rounds: int = None, stalemate_threshold: float = 0.3):
        self.round_count = 0
        self.max_rounds = max_rounds if max_rounds is not None else get_max_rounds()
        self.stalemate_threshold = stalemate_threshold
        self.last_consensus_attempt = 0
        self.repeated_topics = set()
        self.agent_agreement_level = 0.0
        self.conversation_start = datetime.now()
        self.last_message_time = datetime.now()
        self.message_history = []
        self.agent_participation = {}
        self.topic_history = []
        self.consensus_attempts = 0
        self.stalemate_detected = False
        
        # Consensus detection parameters
        self.consensus_indicators = [
            "consensus reached", "consensus achieved", "agreed upon",
            "final decision", "we have consensus", "consensus has been reached",
            "let's finalize", "ready to move forward", "we should proceed",
            "consensus reached:", "consensus_reached"
        ]
        
        # Stalemate detection parameters
        self.stalemate_phrases = [
            "agree to disagree", "no consensus", "deadlock", "cannot agree",
            "stuck", "impasse", "no progress", "going in circles"
        ]
        
        # Repetition detection parameters
        self.repetition_threshold = 0.7  # 70% similarity threshold
        self.max_recent_messages = 5
    
    def increment_round(self):
        """Increment the round counter."""
        self.round_count += 1
    
    def add_message(self, message: Dict[str, Any], agent_name: str = None) -> None:
        """
        Add a message to the conversation state.
        
        Args:
            message: Message dictionary or string
            agent_name: Name of the agent who sent the message
        """
        self.increment_round()
        self.last_message_time = datetime.now()
        
        # Extract message content
        if isinstance(message, dict):
            content = message.get("content", message.get("message", str(message)))
        else:
            content = str(message)
        
        # Store message
        message_record = {
            "content": content,
            "agent": agent_name,
            "timestamp": datetime.now(),
            "round": self.round_count
        }
        self.message_history.append(message_record)
        
        # Track agent participation
        if agent_name:
            self.agent_participation[agent_name] = self.agent_participation.get(agent_name, 0) + 1
        
        # Extract topics
        topics = self.extract_topics(content)
        self.topic_history.extend(topics)
        
        # Update agreement level
        self.update_agreement_level(content)
        
        logger.debug(f"Added message from {agent_name} (round {self.round_count})")
    
    def extract_topics(self, content: str) -> List[str]:
        """
        Extract topics from message content.
        
        Args:
            content: Message content
            
        Returns:
            List of extracted topics
        """
        # Simple topic extraction based on keywords
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
    
    def update_agreement_level(self, content: str) -> None:
        """
        Update the agreement level based on message content.
        
        Args:
            content: Message content
        """
        content_lower = content.lower()
        
        # Check for agreement indicators
        agreement_phrases = [
            "agree", "consensus", "yes", "correct", "good point",
            "that makes sense", "i agree", "we agree"
        ]
        
        disagreement_phrases = [
            "disagree", "no", "wrong", "bad", "problem",
            "issue", "concern", "dispute"
        ]
        
        agreement_count = sum(1 for phrase in agreement_phrases if phrase in content_lower)
        disagreement_count = sum(1 for phrase in disagreement_phrases if phrase in content_lower)
        
        if agreement_count > disagreement_count:
            self.agent_agreement_level = min(1.0, self.agent_agreement_level + 0.1)
        elif disagreement_count > agreement_count:
            self.agent_agreement_level = max(0.0, self.agent_agreement_level - 0.1)
    
    def detect_repetition(self) -> bool:
        """
        Detect if the conversation is going in circles.
        
        Returns:
            True if repetition is detected
        """
        if len(self.message_history) < 3:
            return False
        
        # Check recent messages for similar content
        recent_messages = self.message_history[-3:]
        content_similarity = 0
        
        for i in range(len(recent_messages) - 1):
            for j in range(i + 1, len(recent_messages)):
                content1 = recent_messages[i]["content"].lower()
                content2 = recent_messages[j]["content"].lower()
                
                # Simple similarity check
                words1 = set(content1.split())
                words2 = set(content2.split())
                
                if words1 and words2:
                    similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                    content_similarity = max(content_similarity, similarity)
        
        return content_similarity > self.repetition_threshold
    
    def detect_stalemate(self) -> bool:
        """
        Detect if the conversation is at a stalemate.
        
        Returns:
            True if stalemate is detected
        """
        if len(self.message_history) < 5:
            return False
        
        # Check for stalemate indicators in recent messages
        recent_content = " ".join([msg["content"].lower() for msg in self.message_history[-5:]])
        
        stalemate_count = sum(1 for phrase in self.stalemate_phrases if phrase in recent_content)
        
        if stalemate_count >= 2:
            self.stalemate_detected = True
            return True
        
        return False
    
    def detect_consensus_attempt(self) -> bool:
        """
        Detect if a consensus attempt is being made.
        
        Returns:
            True if consensus attempt is detected
        """
        if not self.message_history:
            return False
        
        latest_content = self.message_history[-1]["content"].lower()
        
        # Check for consensus indicators
        consensus_found = any(indicator in latest_content for indicator in self.consensus_indicators)
        
        if consensus_found:
            self.consensus_attempts += 1
            self.last_consensus_attempt = self.round_count
        
        return consensus_found
    
    def should_terminate(self, messages: List[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Determine if the conversation should terminate.
        
        Args:
            messages: Optional list of messages to check
            
        Returns:
            Tuple of (should_terminate, reason)
        """
        # Check round limit
        if self.round_count >= self.max_rounds:
            return True, f"Maximum rounds ({self.max_rounds}) reached"
        
        # Check for consensus reached
        if messages:
            for message in messages[-3:]:
                content = message.get("content", "").lower()
                if "consensus reached:" in content or "consensus_reached" in content:
                    return True, "Consensus reached"
        
        # Check for stalemate
        if self.detect_stalemate():
            return True, "Stalemate detected"
        
        # Check for repetition
        if self.detect_repetition():
            return True, "Repetition detected"
        
        # Check consensus attempts
        if self.consensus_attempts >= 3:
            return True, "Multiple consensus attempts without resolution"
        
        return False, ""
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the conversation state.
        
        Returns:
            Dictionary containing conversation summary
        """
        # Calculate actual round count from message history
        actual_rounds = len(self.message_history) if self.message_history else 0
        
        return {
            "round_count": actual_rounds,
            "max_rounds": self.max_rounds,
            "consensus_attempts": self.consensus_attempts,
            "stalemate_detected": self.stalemate_detected,
            "agent_agreement_level": self.agent_agreement_level,
            "agent_participation": self.agent_participation,
            "conversation_duration": str(datetime.now() - self.conversation_start),
            "topics_discussed": list(set(self.topic_history))
        }
    
    def reset(self) -> None:
        """Reset the conversation state."""
        self.round_count = 0
        self.consensus_attempts = 0
        self.stalemate_detected = False
        self.agent_agreement_level = 0.0
        self.conversation_start = datetime.now()
        self.last_message_time = datetime.now()
        self.message_history = []
        self.agent_participation = {}
        self.topic_history = []

# Global conversation state instance
conversation_state = ConversationState()

if __name__ == "__main__":
    # Test conversation state
    state = ConversationState(max_rounds=10)
    
    # Simulate some messages
    test_messages = [
        {"content": "I think we should focus on user experience", "agent": "Alex"},
        {"content": "I agree with Alex on UX", "agent": "Max"},
        {"content": "But we need to consider technical feasibility", "agent": "Sam"},
        {"content": "I agree with Sam", "agent": "Jamie"},
        {"content": "Let's reach consensus on this", "agent": "Max"}
    ]
    
    for msg in test_messages:
        state.add_message(msg, msg["agent"])
    
    should_terminate, reason = state.should_terminate()
    print(f"Should terminate: {should_terminate}, Reason: {reason}")
    
    summary = state.get_conversation_summary()
    print(f"Conversation summary: {summary}") 