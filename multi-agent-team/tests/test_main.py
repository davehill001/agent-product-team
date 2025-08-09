#!/usr/bin/env python3
"""
Unit tests for the main application and core components.
"""

import unittest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime

# Set testing environment
os.environ["TESTING"] = "1"

# Import our modules
from main import MultiAgentTeam
import config
import memory
import utils
import conversation_state
import consensus
import agents

class TestConfig(unittest.TestCase):
    """Test configuration module."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        self.assertTrue(config.validate_config())
    
    def test_get_config(self):
        """Test getting configuration."""
        config_obj = config.get_config()
        self.assertIn("model", config_obj)
        self.assertIn("base_url", config_obj)
        self.assertIn("api_type", config_obj)
    
    def test_fallback_config(self):
        """Test fallback configuration."""
        fallback = config.get_fallback_config()
        self.assertEqual(fallback["model"], config.MODEL_CONFIGS["fallback"])

class TestMemory(unittest.TestCase):
    """Test memory management module."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.memory_manager = memory.MemoryManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_memory_initialization(self):
        """Test memory initialization."""
        self.memory_manager.initialize_memory()
        self.assertTrue(os.path.exists(self.temp_file.name))
    
    def test_save_and_load_conversation(self):
        """Test saving and loading conversations."""
        task_id = "test-task-123"
        test_messages = [
            {"message": "Test message 1", "timestamp": str(datetime.now())},
            {"message": "Test message 2", "timestamp": str(datetime.now())}
        ]
        
        self.memory_manager.save_conversation(task_id, test_messages)
        loaded_messages = self.memory_manager.load_conversation(task_id)
        
        self.assertEqual(len(loaded_messages), 2)
        self.assertEqual(loaded_messages[0]["message"], "Test message 1")
    
    def test_generate_task_id(self):
        """Test task ID generation."""
        query = "Test query"
        task_id = self.memory_manager.generate_task_id(query)
        self.assertIsInstance(task_id, str)
        self.assertTrue(len(task_id) > 0)
    
    def test_cleanup_old_conversations(self):
        """Test cleanup of old conversations."""
        # This would require more complex setup with actual timestamps
        # For now, just test the method exists and doesn't crash
        result = self.memory_manager.cleanup_old_conversations()
        self.assertIsInstance(result, int)

class TestUtils(unittest.TestCase):
    """Test utilities module."""
    
    def test_parse_user_input_asterisks(self):
        """Test parsing user input with asterisks."""
        input_text = "* Test app. MVP: Test features. * Test user (25). * Test outcomes"
        parsed = utils.parse_user_input(input_text)
        
        self.assertIn("idea_mvp", parsed)
        self.assertIn("personas", parsed)
        self.assertIn("outcomes", parsed)
        self.assertEqual(parsed["idea_mvp"], "Test app. MVP: Test features.")
    
    def test_parse_user_input_newlines(self):
        """Test parsing user input with newlines."""
        input_text = "Test app. MVP: Test features.\n\nTest user (25).\n\nTest outcomes"
        parsed = utils.parse_user_input(input_text)
        
        self.assertIn("idea_mvp", parsed)
        self.assertIn("personas", parsed)
        self.assertIn("outcomes", parsed)
    
    def test_extract_json_from_message(self):
        """Test JSON extraction from messages."""
        message = 'Here is the result: {"app": {"name": "Test", "description": "Test app"}}'
        json_data = utils.extract_json_from_message(message)
        
        self.assertIsNotNone(json_data)
        self.assertEqual(json_data["app"]["name"], "Test")
    
    def test_validate_wireframe(self):
        """Test wireframe validation."""
        valid_wireframe = {
            "app": {
                "name": "Test App",
                "description": "Test description",
                "screens": [],
                "version_history": []
            }
        }
        
        is_valid, error = utils.validate_wireframe(valid_wireframe)
        self.assertTrue(is_valid)
        self.assertEqual(error, "Valid")

class TestConversationState(unittest.TestCase):
    """Test conversation state module."""
    
    def setUp(self):
        """Set up test environment."""
        self.state = conversation_state.ConversationState(max_rounds=10)
    
    def test_add_message(self):
        """Test adding messages to conversation state."""
        self.state.add_message({"content": "Test message"}, "TestAgent")
        
        self.assertEqual(self.state.round_count, 1)
        self.assertEqual(len(self.state.message_history), 1)
        self.assertEqual(self.state.message_history[0]["content"], "Test message")
    
    def test_detect_repetition(self):
        """Test repetition detection."""
        # Add some repeated messages
        for i in range(5):
            self.state.add_message({"content": "Same message"}, "TestAgent")
        
        self.assertTrue(self.state.detect_repetition())
    
    def test_detect_stalemate(self):
        """Test stalemate detection."""
        # Add messages that might indicate stalemate
        self.state.add_message({"content": "We cannot agree on this"}, "TestAgent")
        self.state.add_message({"content": "This is going in circles"}, "TestAgent")
        self.state.add_message({"content": "We're stuck here"}, "TestAgent")
        
        self.assertTrue(self.state.detect_stalemate())
    
    def test_should_terminate(self):
        """Test termination detection."""
        # Test max rounds
        for i in range(11):
            self.state.add_message({"content": f"Message {i}"}, "TestAgent")
        
        should_terminate, reason = self.state.should_terminate()
        self.assertTrue(should_terminate)
        self.assertEqual(reason, "Max rounds reached")

class TestConsensus(unittest.TestCase):
    """Test consensus detection module."""
    
    def setUp(self):
        """Set up test environment."""
        self.detector = consensus.ConsensusDetector()
    
    def test_detect_consensus_attempt(self):
        """Test consensus attempt detection."""
        messages = [
            {"content": "I agree with the approach", "agent": "Alex"},
            {"content": "Let's reach consensus", "agent": "Max"},
            {"content": "I support this", "agent": "Sam"}
        ]
        
        result = self.detector.detect_consensus_attempt(messages)
        self.assertTrue(result)
    
    def test_calculate_agreement_level(self):
        """Test agreement level calculation."""
        messages = [
            {"content": "I agree with this", "agent": "Alex"},
            {"content": "This is good", "agent": "Max"},
            {"content": "I support this approach", "agent": "Sam"}
        ]
        
        agreement_level = self.detector.calculate_agreement_level(messages)
        self.assertGreater(agreement_level, 0.5)
        self.assertLessEqual(agreement_level, 1.0)
    
    def test_detect_stalemate(self):
        """Test stalemate detection."""
        messages = [
            {"content": "We cannot agree", "agent": "Alex"},
            {"content": "This is not working", "agent": "Max"},
            {"content": "We're stuck", "agent": "Sam"}
        ]
        
        agreement_level = 0.2  # Low agreement
        result = self.detector.detect_stalemate(messages, agreement_level)
        self.assertTrue(result)

class TestAgents(unittest.TestCase):
    """Test agents module."""
    
    def setUp(self):
        """Set up test environment."""
        self.task_id = "test-task-123"
        self.conversation_state = conversation_state.ConversationState(max_rounds=10)
    
    @patch('agents.get_config')
    def test_create_agents(self, mock_get_config):
        """Test agent creation."""
        mock_get_config.return_value = {
            "model": "test-model",
            "base_url": "https://test.com",
            "api_type": "openai"
        }
        
        agents_list = agents.create_agents(self.task_id, self.conversation_state)
        
        self.assertGreaterEqual(len(agents_list), 5)
        agent_names = [agent.name for agent in agents_list]
        self.assertIn("Max", agent_names)
        self.assertIn("Alex", agent_names)
        self.assertIn("Sam", agent_names)
        self.assertIn("Jamie", agent_names)
        self.assertIn("CustomerAdvocate", agent_names)
    
    def test_is_termination_msg(self):
        """Test termination message detection."""
        messages = [
            {"content": "Normal message"},
            {"content": "CONSENSUS REACHED: Here is the result"}
        ]
        
        result = agents.is_termination_msg(messages)
        self.assertTrue(result)

class TestMainApplication(unittest.TestCase):
    """Test main application."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = MultiAgentTeam()
    
    def test_app_initialization(self):
        """Test application initialization."""
        self.assertIsNotNone(self.app.conversation_state)
        self.assertIsNotNone(self.app.consensus_detector)
    
    @patch('main.create_agents')
    @patch('main.setup_group_chat')
    @patch('main.memory_manager')
    def test_run_query(self, mock_memory, mock_setup_chat, mock_create_agents):
        """Test running a query."""
        # Mock the dependencies
        mock_agents = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_agents[0].initiate_chat.return_value = MagicMock(
            chat_history=[
                {"content": "Test message 1", "name": "Agent1"},
                {"content": 'CONSENSUS REACHED: {"app": {"name": "Test", "description": "Test", "screens": [], "version_history": []}}', "name": "Agent2"}
            ]
        )
        mock_create_agents.return_value = mock_agents
        mock_setup_chat.return_value = MagicMock()
        mock_memory.generate_task_id.return_value = "test-task-123"
        mock_memory.save_conversation.return_value = None
        
        input_text = "* Test app. MVP: Test features. * Test user (25). * Test outcomes"
        result = self.app.run_query(input_text)
        
        self.assertIn("task_id", result)
        self.assertIn("input", result)
        self.assertIn("wireframe", result)
        self.assertIn("validation", result)
        self.assertIn("conversation_summary", result)
    
    def test_display_result(self):
        """Test result display."""
        result = {
            "task_id": "test-123",
            "input": {"idea_mvp": "Test", "personas": "Test", "outcomes": "Test"},
            "wireframe": {"app": {"name": "Test App"}},
            "validation": {"is_valid": True, "error": None},
            "conversation_summary": {
                "round_count": 5,
                "max_rounds": 20,
                "agent_agreement_level": 0.8,
                "conversation_duration": "0:02:30",
                "agent_participation": {"Max": 2, "Alex": 1}
            },
            "messages_count": 5,
            "timestamp": str(datetime.now())
        }
        
        # This should not raise any exceptions
        self.app.display_result(result)

class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_workflow_without_llm(self):
        """Test the full workflow without making LLM calls."""
        # This test verifies that all components work together
        # without actually calling the LLM APIs
        
        app = MultiAgentTeam()
        
        # Test input parsing
        input_text = "* Test app. MVP: Test features. * Test user (25). * Test outcomes"
        parsed = utils.parse_user_input(input_text)
        
        self.assertIn("idea_mvp", parsed)
        self.assertIn("personas", parsed)
        self.assertIn("outcomes", parsed)
        
        # Test task ID generation
        task_id = memory.memory_manager.generate_task_id(parsed["idea_mvp"])
        self.assertIsInstance(task_id, str)
        
        # Test conversation state
        conv_state = conversation_state.ConversationState(max_rounds=10)
        conv_state.add_message({"content": "Test message"}, "TestAgent")
        self.assertEqual(conv_state.round_count, 1)
        
        # Test consensus detection
        detector = consensus.ConsensusDetector()
        messages = [{"content": "Test message", "agent": "TestAgent"}]
        agreement_level = detector.calculate_agreement_level(messages)
        self.assertIsInstance(agreement_level, float)

if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 