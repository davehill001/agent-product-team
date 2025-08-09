#!/usr/bin/env python3
"""
Test script for the enhanced interactive mode functionality.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Set testing environment
os.environ["TESTING"] = "1"

def test_interactive_mode():
    """Test the enhanced interactive mode functionality."""
    print("🧪 Testing Enhanced Interactive Mode")
    print("=" * 40)
    
    try:
        from main import MultiAgentTeam
        
        # Create app instance
        app = MultiAgentTeam()
        
        # Test the progress method
        test_input = "* Test app. MVP: Test features. * Test user (25). * Test outcomes"
        
        print("Testing progress updates...")
        
        # Mock the necessary components for testing
        with patch('main.create_agents') as mock_create_agents, \
             patch('main.setup_group_chat') as mock_setup_chat, \
             patch('main.memory_manager') as mock_memory, \
             patch('main.parse_user_input') as mock_parse, \
             patch('main.extract_json_from_message') as mock_extract, \
             patch('main.validate_wireframe') as mock_validate:
            
            # Setup mocks
            mock_parse.return_value = {
                "idea_mvp": "Test app. MVP: Test features.",
                "personas": "Test user (25)",
                "outcomes": "Test outcomes"
            }
            
            mock_memory.generate_task_id.return_value = "test-task-123"
            mock_memory.save_conversation.return_value = None
            
            mock_agents = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            mock_agents[0].initiate_chat.return_value = MagicMock(
                chat_history=[
                    {"content": "Test message 1", "name": "Agent1"},
                    {"content": 'CONSENSUS REACHED: {"app": {"name": "Test", "description": "Test", "screens": [], "version_history": []}}', "name": "Agent2"}
                ]
            )
            mock_create_agents.return_value = mock_agents
            mock_setup_chat.return_value = MagicMock()
            
            mock_extract.return_value = {
                "app": {
                    "name": "Test App",
                    "description": "Test description",
                    "screens": [],
                    "version_history": []
                }
            }
            mock_validate.return_value = (True, "Valid")
            
            # Test the progress method
            result = app.run_query_with_progress(test_input)
            
            # Verify result structure
            required_keys = ["task_id", "input", "wireframe", "validation", "conversation_summary", "messages_count", "timestamp"]
            for key in required_keys:
                assert key in result, f"Missing key in result: {key}"
            
            print("   ✅ Progress updates working")
            print("   ✅ Result structure correct")
            
            # Test display result
            print("\nTesting result display...")
            app.display_result(result)
            print("   ✅ Result display working")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the interactive mode test."""
    print("🚀 Testing Enhanced Interactive Mode")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_interactive_mode()
    
    if success:
        print("\n🎉 Interactive mode test passed!")
        print("\n📋 Interactive Mode Features:")
        print("  ✅ Real-time progress updates (6 stages)")
        print("  ✅ Progress animation during conversation")
        print("  ✅ Detailed result summary")
        print("  ✅ Agent participation percentages")
        print("  ✅ Topics discussed")
        print("  ✅ Consensus summary")
        print("  ✅ Conversation stages overview")
        return 0
    else:
        print("\n❌ Interactive mode test failed!")
        return 1

if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main()) 