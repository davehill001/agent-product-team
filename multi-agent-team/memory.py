# memory.py
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MEMORY_FILE = "conversation_history.json"
MAX_MEMORY_SIZE_MB = 50
MAX_CONVERSATION_AGE_DAYS = 30
MAX_CONVERSATION_SIZE_MB = 5

class MemoryManager:
    """Enhanced memory management for conversation history."""
    
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.initialize_memory()
    
    def initialize_memory(self) -> None:
        """Initialize memory file if it doesn't exist."""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump({"tasks": {}, "metadata": {"created": str(datetime.now())}}, f, indent=2)
            logger.info(f"Initialized memory file: {self.memory_file}")
    
    def get_memory_size_mb(self) -> float:
        """Get current memory file size in MB."""
        if os.path.exists(self.memory_file):
            return os.path.getsize(self.memory_file) / (1024 * 1024)
        return 0.0
    
    def cleanup_old_conversations(self, max_age_days: int = MAX_CONVERSATION_AGE_DAYS) -> int:
        """
        Remove conversations older than max_age_days.
        
        Args:
            max_age_days: Maximum age in days for conversations to keep
            
        Returns:
            Number of conversations removed
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        removed_count = 0
        
        try:
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
            
            cleaned_tasks = {}
            for task_id, messages in data.get("tasks", {}).items():
                if messages:
                    # Get the latest timestamp from the conversation
                    latest_timestamp = None
                    for msg in messages:
                        if "timestamp" in msg:
                            try:
                                msg_timestamp = datetime.fromisoformat(msg["timestamp"])
                                if latest_timestamp is None or msg_timestamp > latest_timestamp:
                                    latest_timestamp = msg_timestamp
                            except ValueError:
                                continue
                    
                    # Keep conversation if it's recent enough
                    if latest_timestamp and latest_timestamp > cutoff_date:
                        cleaned_tasks[task_id] = messages
                    else:
                        removed_count += 1
                        logger.info(f"Removed old conversation: {task_id}")
            
            data["tasks"] = cleaned_tasks
            data["metadata"] = data.get("metadata", {})
            data["metadata"]["last_cleanup"] = str(datetime.now())
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Cleaned up {removed_count} old conversations")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    def check_memory_size(self) -> bool:
        """
        Check if memory file is getting too large and trigger cleanup if needed.
        
        Returns:
            True if cleanup was performed, False otherwise
        """
        current_size = self.get_memory_size_mb()
        
        if current_size > MAX_MEMORY_SIZE_MB:
            logger.warning(f"Memory size ({current_size:.2f}MB) exceeds limit ({MAX_MEMORY_SIZE_MB}MB)")
            self.cleanup_old_conversations(max_age_days=7)  # More aggressive cleanup
            return True
        
        return False
    
    def save_conversation(self, task_id: str, messages: List[Dict[str, Any]]) -> None:
        """
        Save conversation messages to memory.
        
        Args:
            task_id: Unique identifier for the task
            messages: List of message dictionaries
        """
        try:
            self.initialize_memory()
            
            # Check memory size before saving
            self.check_memory_size()
            
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
            
            # Add timestamp to each message if not present
            timestamped_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    if "timestamp" not in msg:
                        msg["timestamp"] = str(datetime.now())
                    timestamped_messages.append(msg)
                else:
                    # Handle string messages
                    timestamped_messages.append({
                        "message": str(msg),
                        "timestamp": str(datetime.now())
                    })
            
            # Store messages by task_id
            data["tasks"].setdefault(task_id, []).extend(timestamped_messages)
            
            # Update metadata
            data["metadata"] = data.get("metadata", {})
            data["metadata"]["last_updated"] = str(datetime.now())
            data["metadata"]["total_tasks"] = len(data["tasks"])
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(timestamped_messages)} messages for task: {task_id}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            raise
    
    def load_conversation(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Load conversation messages for a specific task.
        
        Args:
            task_id: Unique identifier for the task
            
        Returns:
            List of message dictionaries
        """
        try:
            self.initialize_memory()
            
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
            
            messages = data.get("tasks", {}).get(task_id, [])
            logger.info(f"Loaded {len(messages)} messages for task: {task_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
            return []
    
    def generate_task_id(self, query: str) -> str:
        """
        Generate a unique task ID based on the query.
        
        Args:
            query: The user query to generate ID for
            
        Returns:
            Unique task ID string
        """
        # Create a deterministic ID based on query content
        query_key = query[:50].lower().strip()
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, query_key))
    
    def get_conversation_summary(self, task_id: str, max_messages: int = 5) -> str:
        """
        Get a summary of recent conversation messages.
        
        Args:
            task_id: Unique identifier for the task
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Summary string of recent conversation
        """
        messages = self.load_conversation(task_id)
        if not messages:
            return ""
        
        # Get the most recent messages
        recent_messages = messages[-max_messages:]
        summary_parts = []
        
        for msg in recent_messages:
            if isinstance(msg, dict):
                content = msg.get("message", msg.get("content", ""))
            else:
                content = str(msg)
            
            if content:
                summary_parts.append(content[:200] + "..." if len(content) > 200 else content)
        
        return "\n".join(summary_parts)
    
    def list_tasks(self) -> List[str]:
        """
        List all task IDs in memory.
        
        Returns:
            List of task IDs
        """
        try:
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
            
            return list(data.get("tasks", {}).keys())
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return []

# Global memory manager instance
memory_manager = MemoryManager()

# Convenience functions for backward compatibility
def initialize_memory():
    """Initialize memory (deprecated - use MemoryManager directly)."""
    memory_manager.initialize_memory()

def save_conversation(task_id: str, messages: List[Dict[str, Any]]) -> None:
    """Save conversation (deprecated - use MemoryManager directly)."""
    memory_manager.save_conversation(task_id, messages)

def load_conversation(task_id: str) -> List[Dict[str, Any]]:
    """Load conversation (deprecated - use MemoryManager directly)."""
    return memory_manager.load_conversation(task_id)

def generate_task_id(query: str) -> str:
    """Generate task ID (deprecated - use MemoryManager directly)."""
    return memory_manager.generate_task_id(query)

if __name__ == "__main__":
    # Test memory management
    test_task_id = "test-task-123"
    test_messages = [
        {"message": "Hello", "timestamp": str(datetime.now())},
        {"message": "World", "timestamp": str(datetime.now())}
    ]
    
    # Test save and load
    memory_manager.save_conversation(test_task_id, test_messages)
    loaded_messages = memory_manager.load_conversation(test_task_id)
    
    print(f"✅ Memory management test passed")
    print(f"Saved {len(test_messages)} messages")
    print(f"Loaded {len(loaded_messages)} messages")
    print(f"Memory size: {memory_manager.get_memory_size_mb():.2f}MB") 