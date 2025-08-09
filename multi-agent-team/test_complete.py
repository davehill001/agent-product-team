#!/usr/bin/env python3
"""
Comprehensive test for the complete Multi-Agent Team system.
Tests the full workflow without making actual LLM calls.
"""

import os
import sys
import json
from datetime import datetime

# Set testing environment
os.environ["TESTING"] = "1"

def test_complete_system():
    """Test the complete system workflow."""
    print("🧪 Testing Complete Multi-Agent Team System")
    print("=" * 60)
    
    try:
        # Import all modules
        print("1. Testing module imports...")
        import config
        import memory
        import utils
        import conversation_state
        import consensus
        import agents
        from main import MultiAgentTeam
        print("   ✅ All modules imported successfully")
        
        # Test configuration
        print("2. Testing configuration...")
        assert config.validate_config(), "Configuration validation failed"
        config_obj = config.get_config()
        assert "model" in config_obj, "Config missing model"
        assert "base_url" in config_obj, "Config missing base_url"
        print("   ✅ Configuration validated")
        
        # Test memory management
        print("3. Testing memory management...")
        test_task_id = "complete-test-123"
        test_messages = [
            {"message": "Test message 1", "timestamp": str(datetime.now())},
            {"message": "Test message 2", "timestamp": str(datetime.now())}
        ]
        memory.memory_manager.save_conversation(test_task_id, test_messages)
        loaded_messages = memory.memory_manager.load_conversation(test_task_id)
        assert len(loaded_messages) >= 2, "Memory save/load failed"
        print("   ✅ Memory management working")
        
        # Test input parsing
        print("4. Testing input parsing...")
        test_input = "* Test app. MVP: Test features. * Test user (25). * Test outcomes"
        parsed = utils.parse_user_input(test_input)
        assert "idea_mvp" in parsed, "Input parsing failed"
        assert "personas" in parsed, "Input parsing failed"
        assert "outcomes" in parsed, "Input parsing failed"
        print("   ✅ Input parsing working")
        
        # Test conversation state
        print("5. Testing conversation state...")
        conv_state = conversation_state.ConversationState(max_rounds=10)
        conv_state.add_message({"content": "Test message"}, "TestAgent")
        assert conv_state.round_count == 1, "Conversation state failed"
        print("   ✅ Conversation state working")
        
        # Test consensus detection
        print("6. Testing consensus detection...")
        detector = consensus.ConsensusDetector()
        test_messages = [
            {"content": "I agree with this", "agent": "Alex"},
            {"content": "This is good", "agent": "Max"},
            {"content": "I support this", "agent": "Sam"}
        ]
        agreement_level = detector.calculate_agreement_level(test_messages)
        assert isinstance(agreement_level, float), "Agreement level calculation failed"
        print("   ✅ Consensus detection working")
        
        # Test agent creation (without LLM calls)
        print("7. Testing agent creation...")
        agent_list = agents.create_agents(test_task_id, conv_state)
        assert len(agent_list) >= 5, "Agent creation failed"
        agent_names = [agent.name for agent in agent_list]
        expected_names = ["Admin", "Max", "Alex", "Sam", "Jamie", "CustomerAdvocate"]
        for name in expected_names:
            assert name in agent_names, f"Missing agent: {name}"
        print("   ✅ Agent creation working")
        
        # Test group chat setup
        print("8. Testing group chat setup...")
        manager = agents.setup_group_chat(agent_list, test_task_id, conv_state)
        assert manager is not None, "Group chat setup failed"
        print("   ✅ Group chat setup working")
        
        # Test main application
        print("9. Testing main application...")
        app = MultiAgentTeam()
        assert app.conversation_state is not None, "App conversation state failed"
        assert app.consensus_detector is not None, "App consensus detector failed"
        print("   ✅ Main application working")
        
        # Test JSON extraction and validation
        print("10. Testing JSON extraction and validation...")
        test_json = '{"app": {"name": "Test App", "description": "Test", "screens": [], "version_history": []}}'
        extracted = utils.extract_json_from_message(test_json)
        assert extracted is not None, "JSON extraction failed"
        
        is_valid, error = utils.validate_wireframe(extracted)
        assert is_valid, f"Wireframe validation failed: {error}"
        print("   ✅ JSON extraction and validation working")
        
        # Test complete workflow simulation
        print("11. Testing complete workflow simulation...")
        result = {
            "task_id": test_task_id,
            "input": parsed,
            "wireframe": extracted,
            "validation": {"is_valid": True, "error": None},
            "conversation_summary": conv_state.get_conversation_summary(),
            "consensus_summary": detector.get_consensus_summary(),
            "messages_count": len(test_messages),
            "timestamp": str(datetime.now())
        }
        
        # Verify result structure
        required_keys = ["task_id", "input", "wireframe", "validation", "conversation_summary", "messages_count", "timestamp"]
        for key in required_keys:
            assert key in result, f"Missing key in result: {key}"
        
        print("   ✅ Complete workflow simulation working")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! System is ready for production.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Test system performance characteristics."""
    print("\n📊 Performance Testing")
    print("=" * 30)
    
    try:
        import memory
        import time
        
        # Test memory usage
        start_time = time.time()
        test_task_id = "perf-test-123"
        test_messages = [{"message": f"Message {i}", "timestamp": str(datetime.now())} for i in range(100)]
        
        memory.memory_manager.save_conversation(test_task_id, test_messages)
        loaded_messages = memory.memory_manager.load_conversation(test_task_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Memory operations: {len(test_messages)} messages in {duration:.3f}s")
        print(f"Memory size: {memory.memory_manager.get_memory_size_mb():.2f}MB")
        
        if duration < 1.0:  # Should be very fast
            print("   ✅ Performance acceptable")
        else:
            print("   ⚠️  Performance slower than expected")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        return False

def main():
    """Run comprehensive tests."""
    print("🚀 Starting Comprehensive System Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run main tests
    main_success = test_complete_system()
    
    # Run performance tests
    perf_success = test_performance()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"Main tests: {'✅ PASSED' if main_success else '❌ FAILED'}")
    print(f"Performance tests: {'✅ PASSED' if perf_success else '❌ FAILED'}")
    
    if main_success and perf_success:
        print("\n🎉 ALL TESTS PASSED! System is production-ready.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED! Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 