#!/usr/bin/env python3
"""
Test script for Phase 1 and 2 implementations.
"""

import os
import sys
import json
from datetime import datetime

# Set testing environment
os.environ["TESTING"] = "1"

def test_phase1():
    """Test Phase 1 components."""
    print("🧪 Testing Phase 1: Core Infrastructure & Enhanced Safeguards")
    
    # Test config
    try:
        import config
        print("  ✅ Config module - OK")
    except Exception as e:
        print(f"  ❌ Config module - FAILED: {e}")
        return False
    
    # Test memory
    try:
        import memory
        # Test memory operations
        test_task_id = "test-phase1"
        test_messages = [
            {"message": "Test message 1", "timestamp": str(datetime.now())},
            {"message": "Test message 2", "timestamp": str(datetime.now())}
        ]
        memory.memory_manager.save_conversation(test_task_id, test_messages)
        loaded_messages = memory.memory_manager.load_conversation(test_task_id)
        assert len(loaded_messages) >= 2, "Memory save/load failed"
        print("  ✅ Memory module - OK")
    except Exception as e:
        print(f"  ❌ Memory module - FAILED: {e}")
        return False
    
    # Test utils
    try:
        import utils
        # Test input parsing with proper format
        test_input = "* Simple todo app. MVP: Add tasks. * Busy mom (35). * Add task, view list."
        parsed = utils.parse_user_input(test_input)
        assert "idea_mvp" in parsed, "Input parsing failed"
        print("  ✅ Utils module - OK")
    except Exception as e:
        print(f"  ❌ Utils module - FAILED: {e}")
        return False
    
    # Test conversation state
    try:
        import conversation_state
        state = conversation_state.ConversationState(max_rounds=10)
        state.add_message({"content": "Test message"}, "TestAgent")
        assert state.round_count == 1, "Conversation state failed"
        print("  ✅ Conversation state module - OK")
    except Exception as e:
        print(f"  ❌ Conversation state module - FAILED: {e}")
        return False
    
    print("  🎉 Phase 1 tests passed!")
    return True

def test_phase2():
    """Test Phase 2 components."""
    print("🧪 Testing Phase 2: Agent System & Termination Logic")
    
    # Test consensus detection
    try:
        import consensus
        detector = consensus.ConsensusDetector()
        test_messages = [
            {"content": "I agree with the approach", "agent": "Alex"},
            {"content": "Let's reach consensus", "agent": "Max"},
            {"content": "I support this", "agent": "Sam"}
        ]
        consensus_attempt = detector.detect_consensus_attempt(test_messages)
        agreement_level = detector.calculate_agreement_level(test_messages)
        print("  ✅ Consensus detection - OK")
    except Exception as e:
        print(f"  ❌ Consensus detection - FAILED: {e}")
        return False
    
    # Test agents (without actual LLM calls)
    try:
        import agents
        import conversation_state
        test_task_id = "test-phase2"
        test_conversation_state = conversation_state.ConversationState(max_rounds=10)
        agent_list = agents.create_agents(test_task_id, test_conversation_state)
        assert len(agent_list) >= 5, "Agent creation failed"
        print("  ✅ Agent creation - OK")
    except Exception as e:
        print(f"  ❌ Agent creation - FAILED: {e}")
        return False
    
    # Test group chat setup
    try:
        manager = agents.setup_group_chat(agent_list, test_task_id, test_conversation_state)
        assert manager is not None, "Group chat setup failed"
        print("  ✅ Group chat setup - OK")
    except Exception as e:
        print(f"  ❌ Group chat setup - FAILED: {e}")
        return False
    
    print("  🎉 Phase 2 tests passed!")
    return True

def test_integration():
    """Test integration between components."""
    print("🧪 Testing Integration")
    
    try:
        # Test full workflow without LLM calls
        import memory
        import utils
        import conversation_state
        import consensus
        import agents
        
        # Create test scenario with proper format
        test_input = "* Fitness tracking app. MVP: Log workouts. * Fitness enthusiast (28). * Track progress, set goals."
        task_id = memory.memory_manager.generate_task_id(test_input)
        
        # Parse input
        parsed = utils.parse_user_input(test_input)
        
        # Create conversation state
        conv_state = conversation_state.ConversationState(max_rounds=10)
        
        # Create agents
        agent_list = agents.create_agents(task_id, conv_state)
        
        # Test consensus detection
        detector = consensus.ConsensusDetector()
        
        print("  ✅ Integration test - OK")
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test - FAILED: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Phase 1 & 2 Tests\n")
    
    phase1_success = test_phase1()
    print()
    
    phase2_success = test_phase2()
    print()
    
    integration_success = test_integration()
    print()
    
    # Summary
    print("📊 Test Summary:")
    print(f"  Phase 1: {'✅ PASSED' if phase1_success else '❌ FAILED'}")
    print(f"  Phase 2: {'✅ PASSED' if phase2_success else '❌ FAILED'}")
    print(f"  Integration: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    
    if all([phase1_success, phase2_success, integration_success]):
        print("\n🎉 All tests passed! Phase 1 and 2 are ready for Phase 3.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 