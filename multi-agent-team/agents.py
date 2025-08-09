# agents.py
import json
import logging
from typing import List, Dict, Any, Optional
from autogen import AssistantAgent, GroupChatManager, GroupChat
from config import OPENROUTER_API_KEY, get_max_rounds
from memory import memory_manager
from utils import load_schema, extract_consensus_indicator
from conversation_state import ConversationState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_agents(task_id: str, conversation_state: ConversationState) -> List[AssistantAgent]:
    """
    Create enhanced agents with simplified, clear prompts and better communication.
    
    Args:
        task_id: Unique identifier for the task
        conversation_state: Conversation state tracker
        
    Returns:
        List of configured agents
    """
    # Load conversation context (limit to recent messages)
    context = memory_manager.load_conversation(task_id)
    context_summary = memory_manager.get_conversation_summary(task_id, max_messages=3)
    
    # Enhanced base prompt with clear wireframe requirements
    base_prompt = (
        f"Focus on user value and lean MVP development. "
        f"Previous context: {context_summary[:500] if context_summary else 'None'}. "
        f"Build on others' inputs. Use @AgentName to mention others. "
        f"Reach consensus on screens/components. Max leads consensus. "
        f"CRITICAL: When consensus is reached, Max MUST output 'CONSENSUS REACHED:' followed by a complete wireframe JSON with actual data (not schema definitions)."
    )
    
    # Clear termination rules with specific JSON structure requirements
    termination_prompt = (
        "TERMINATION: Max outputs 'CONSENSUS REACHED:' + COMPLETE WIREFRAME JSON when agreed. "
        "The JSON MUST include: app object with name, description, screens array, and version_history. "
        "Each screen must have screen_id, name, purpose, layout, components, navigation, and state. "
        "Each component must have component_id, type, purpose, properties (size, position, style, content, interactions), and children. "
        "After 3 rounds without consensus, Max forces decision. Maximum 15 rounds. Focus on user value."
    )
    
    # Create LLM configs with proper model names
    primary_config = {
        "config_list": [{
            "model": "openai/gpt-4o-mini",
            "api_key": OPENROUTER_API_KEY,
            "base_url": "https://openrouter.ai/api/v1",
            "api_type": "openai"
        }],
        "temperature": 0.7
    }
    
    secondary_config = {
        "config_list": [{
            "model": "anthropic/claude-3.5-sonnet",
            "api_key": OPENROUTER_API_KEY,
            "base_url": "https://openrouter.ai/api/v1",
            "api_type": "openai"
        }],
        "temperature": 0.7
    }
    
    # Enhanced example output format for Max agent with clear structure
    example_output = {
        "app": {
            "name": "AI Agent Platform",
            "description": "Platform for marketing teams to onboard AI agents and manage content creation tasks",
            "screens": [
                {
                    "screen_id": "onboarding",
                    "name": "Onboarding Screen",
                    "purpose": "User setup and business context configuration",
                    "layout": {
                        "type": "stack",
                        "orientation": "vertical",
                        "constraints": {
                            "width": "100%",
                            "height": "100%"
                        }
                    },
                    "components": [
                        {
                            "component_id": "business_context_form",
                            "type": "form",
                            "purpose": "Capture business context and tone of voice",
                            "properties": {
                                "size": {"width": "100%", "height": "auto"},
                                "position": {"x": "0", "y": "0"},
                                "style": {"background": "white"},
                                "content": "Business Context Form",
                                "interactions": [
                                    {
                                        "trigger": "onSubmit",
                                        "action": "navigate",
                                        "target": "agent_creation"
                                    }
                                ]
                            },
                            "children": []
                        }
                    ],
                    "navigation": {
                        "entry_points": [],
                        "exit_points": [
                            {
                                "to_screen_id": "agent_creation",
                                "trigger": "form_submit",
                                "conditions": "none"
                            }
                        ]
                    },
                    "state": {
                        "dynamic_elements": []
                    }
                }
            ],
            "version_history": [
                {
                    "version": "1.0",
                    "date": "2024-01-01",
                    "changes": [
                        {
                            "screen_id": "onboarding",
                            "component_id": "business_context_form",
                            "change_description": "Initial creation",
                            "author": "LLM"
                        }
                    ]
                }
            ]
        }
    }
    
    # Convert example to JSON string for the prompt
    example_json_str = json.dumps(example_output, indent=2)
    
    max_agent = AssistantAgent(
        name="Max",
        system_message=(
            f"You are Max, Product Manager. Lead consensus on MVP screens/components. "
            f"{base_prompt} {termination_prompt} "
            f"CRITICAL: When consensus is reached, output 'CONSENSUS REACHED:' followed by COMPLETE wireframe JSON data (not schema). "
            f"The JSON must include: app object with name, description, screens array, and version_history. "
            f"Each screen must have screen_id, name, purpose, layout, components, navigation, and state. "
            f"Each component must have component_id, type, purpose, properties (size, position, style, content, interactions), and children array. "
            f"EXAMPLE OUTPUT FORMAT:\n"
            f"CONSENSUS REACHED:\n"
            f"{example_json_str}\n"
            f"DO NOT output schema definitions - output actual wireframe data. "
            f"Ensure the JSON is properly formatted and complete."
        ),
        llm_config=primary_config,
    )
    
    alex_agent = AssistantAgent(
        name="Alex",
        system_message=(
            f"You are Alex, Product Designer. Focus on UX, accessibility, user journeys. "
            f"{base_prompt} Challenge designs that don't prioritize user experience. "
            f"Use @Max, @Sam, @Jamie to mention others. "
            f"Ensure wireframe components are user-friendly and accessible."
        ),
        llm_config=primary_config,
    )
    
    sam_agent = AssistantAgent(
        name="Sam",
        system_message=(
            f"You are Sam, Engineer. Focus on technical feasibility, performance, scalability. "
            f"{base_prompt} Suggest minimal tech stacks. Challenge complex features. "
            f"Use @Max, @Alex, @Jamie to mention others. "
            f"Ensure wireframe components are technically feasible."
        ),
        llm_config=primary_config,
    )
    
    jamie_agent = AssistantAgent(
        name="Jamie",
        system_message=(
            f"You are Jamie, QA Engineer. Focus on quality, testing, edge cases. "
            f"{base_prompt} Challenge assumptions. Advocate for robust solutions. "
            f"Use @Max, @Alex, @Sam to mention others. "
            f"Ensure wireframe components are testable and handle edge cases."
        ),
        llm_config=primary_config,
    )
    
    customer_advocate = AssistantAgent(
        name="CustomerAdvocate",
        system_message=(
            f"You are Customer Advocate. Focus on user needs, pain points, business value. "
            f"{base_prompt} Challenge features that don't solve real problems. "
            f"Use @Max, @Alex, @Sam, @Jamie to mention others. "
            f"Ensure wireframe components solve real user problems."
        ),
        llm_config=secondary_config,
    )
    
    # Admin agent
    user_proxy = AssistantAgent(
        name="Admin",
        human_input_mode="NEVER",
        system_message="Coordinate discussion and monitor consensus. Keep conversation focused on creating a complete wireframe JSON with actual data, not schema definitions.",
        llm_config=False,
    )
    
    return [user_proxy, max_agent, alex_agent, sam_agent, jamie_agent, customer_advocate]

def setup_group_chat(agents: List[AssistantAgent], task_id: str, conversation_state: ConversationState) -> GroupChatManager:
    """
    Setup enhanced group chat with better message handling and conversation state tracking.
    
    Args:
        agents: List of agents
        task_id: Unique identifier for the task
        conversation_state: Conversation state tracker
        
    Returns:
        Group chat manager
    """
    # Load previous messages (limit to recent)
    previous_messages = memory_manager.load_conversation(task_id)
    recent_messages = previous_messages[-10:] if len(previous_messages) > 10 else previous_messages
    
    # Determine max rounds based on conversation complexity
    base_rounds = get_max_rounds()
    context_length = len(recent_messages)
    
    # Only reduce rounds for very complex discussions (more than 10 previous messages)
    if context_length > 10:
        base_rounds = max(8, base_rounds - 5)
    elif context_length > 5:
        base_rounds = max(10, base_rounds - 3)
    
    # Create group chat with clean message format
    group_chat = GroupChat(
        agents=agents,
        messages=[msg.get("content", msg.get("message", "")) for msg in recent_messages],
        max_round=base_rounds,
    )
    
    # Create manager with proper configuration
    manager_config = {
        "config_list": [{
            "model": "openai/gpt-4o-mini",
            "api_key": OPENROUTER_API_KEY,
            "base_url": "https://openrouter.ai/api/v1",
            "api_type": "openai"
        }],
        "temperature": 0.7
    }
    
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=manager_config,
    )
    
    logger.info(f"Setup group chat with {len(agents)} agents, max rounds: {base_rounds}")
    return manager

if __name__ == "__main__":
    # Test agent creation
    test_task_id = "test-task-123"
    test_conversation_state = ConversationState(max_rounds=10)
    
    try:
        agents = create_agents(test_task_id, test_conversation_state)
        print(f"✅ Created {len(agents)} agents successfully")
        
        manager = setup_group_chat(agents, test_task_id, test_conversation_state)
        print(f"✅ Created group chat manager successfully")
        
    except Exception as e:
        print(f"❌ Error creating agents: {e}") 