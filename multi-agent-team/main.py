#!/usr/bin/env python3
"""
Main application for the Multi-Agent Team system.
Handles CLI interface, error handling, and result validation.
"""

import argparse
import json
import logging
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Import our modules
from agents import create_agents, setup_group_chat
from memory import memory_manager
from utils import parse_user_input, extract_json_from_message, validate_wireframe
from conversation_state import ConversationState
from consensus import ConsensusDetector
from config import validate_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiAgentTeam:
    """
    Main application class for the multi-agent team system.
    """
    
    def __init__(self):
        self.conversation_state = ConversationState()
        self.consensus_detector = ConsensusDetector()
    
    def run_query(self, input_text: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a query through the multi-agent team.
        
        Args:
            input_text: User input text
            task_id: Optional task ID (will be generated if not provided)
            
        Returns:
            Dictionary containing the result and metadata
        """
        try:
            # Parse user input
            logger.info("Parsing user input...")
            parsed_input = parse_user_input(input_text)
            
            # Generate task ID if not provided
            if not task_id:
                task_id = memory_manager.generate_task_id(parsed_input["idea_mvp"])
            
            logger.info(f"Task ID: {task_id}")
            
            # Create initial message
            initial_message = (
                f"App Idea/MVP: {parsed_input['idea_mvp']}\n"
                f"User Personas: {parsed_input['personas']}\n"
                f"Desired Outcomes: {parsed_input['outcomes']}\n"
                "Discuss critically: user journeys, JTBD, minimum must-haves vs. extras. "
                "Iterate until consensus on screens/components. "
                "Max: Output final wireframe as JSON when consensus is reached."
            )
            
            # Create agents and conversation state
            logger.info("Creating agents...")
            agents = create_agents(task_id, self.conversation_state)
            
            # Setup group chat
            logger.info("Setting up group chat...")
            manager = setup_group_chat(agents, task_id, self.conversation_state)
            
            # Start conversation
            logger.info("Starting conversation...")
            user_proxy = agents[0]  # Admin agent
            chat_result = user_proxy.initiate_chat(manager, message=initial_message)
            
            # Extract messages
            messages = []
            for msg in chat_result.chat_history:
                if isinstance(msg, dict):
                    content = msg.get("content", msg.get("message", ""))
                    agent = msg.get("name", "Unknown")
                else:
                    content = str(msg)
                    agent = "Unknown"
                
                messages.append({
                    "content": content,
                    "agent": agent,
                    "timestamp": str(datetime.now())
                })
            
            # Save conversation
            memory_manager.save_conversation(task_id, messages)
            
            # Extract JSON from final message
            final_message = messages[-1]["content"] if messages else ""
            wireframe_json = extract_json_from_message(final_message)
            
            # Check for consensus reached in the conversation
            consensus_reached = False
            for msg in messages[-5:]:  # Check last 5 messages for better coverage
                content = msg.get("content", "").lower()
                if any(indicator in content for indicator in [
                    "consensus reached:", 
                    "consensus_reached", 
                    "consensus achieved",
                    "we have consensus",
                    "consensus has been reached",
                    "final decision",
                    "agreed upon"
                ]):
                    consensus_reached = True
                    break
            
            # Validate wireframe if found
            validation_result = {"is_valid": False, "error": "No JSON found in output"}
            if wireframe_json:
                is_valid, error = validate_wireframe(wireframe_json)
                validation_result = {"is_valid": is_valid, "error": error}
                
                if not is_valid:
                    logger.warning(f"Wireframe validation failed: {error}")
            
            # Prepare result
            result = {
                "task_id": task_id,
                "input": parsed_input,
                "wireframe": wireframe_json if validation_result["is_valid"] else None,
                "validation": validation_result,
                "conversation_summary": self.conversation_state.get_conversation_summary(),
                "consensus_summary": self.consensus_detector.get_consensus_summary(),
                "messages_count": len(messages),
                "timestamp": str(datetime.now())
            }
            
            logger.info(f"Query completed successfully. Messages: {len(messages)}")
            return result
            
        except Exception as e:
            logger.error(f"Error running query: {e}")
            raise
    
    def run_interactive(self):
        """
        Run the application in interactive mode with real-time progress updates.
        """
        print("🤖 Multi-Agent Team System - Interactive Mode")
        print("=" * 50)
        print("Enter your app idea in the following format:")
        print("* [App Idea/MVP description] * [User Personas] * [Desired Outcomes]")
        print("Example: * Fitness tracking app. MVP: Log workouts. * Fitness enthusiast (28). * Track progress, set goals.")
        print("Type 'quit' to exit.")
        print()
        
        while True:
            try:
                user_input = input("Enter your app idea: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    print("Please enter some input.")
                    continue
                
                print("\n🔄 Processing your request...")
                print("=" * 40)
                
                # Run query with progress updates
                result = self.run_query_with_progress(user_input)
                
                # Display result
                self.display_result(result)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.")
    
    def run_query_with_progress(self, input_text: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a query with clean progress updates and better conversation flow.
        
        Args:
            input_text: User input text
            task_id: Optional task ID (will be generated if not provided)
            
        Returns:
            Dictionary containing the result and metadata
        """
        try:
            # Stage 1: Parse user input
            print("📝 Stage 1/6: Parsing user input...")
            parsed_input = parse_user_input(input_text)
            print(f"   ✅ Parsed: {parsed_input['idea_mvp'][:50]}...")
            
            # Generate task ID if not provided
            if not task_id:
                task_id = memory_manager.generate_task_id(parsed_input["idea_mvp"])
            
            print(f"   🆔 Task ID: {task_id}")
            
            # Stage 2: Create initial message
            print("\n💬 Stage 2/6: Preparing conversation...")
            initial_message = (
                f"App Idea/MVP: {parsed_input['idea_mvp']}\n"
                f"User Personas: {parsed_input['personas']}\n"
                f"Desired Outcomes: {parsed_input['outcomes']}\n"
                "Discuss critically: user journeys, JTBD, minimum must-haves vs. extras. "
                "Iterate until consensus on screens/components. "
                "Max: Output final wireframe as JSON when consensus is reached."
            )
            print("   ✅ Initial message prepared")
            
            # Stage 3: Create agents
            print("\n🤖 Stage 3/6: Creating agents...")
            agents = create_agents(task_id, self.conversation_state)
            print(f"   ✅ Created {len(agents)} agents:")
            for agent in agents[1:]:  # Skip Admin agent
                print(f"      - {agent.name}")
            
            # Stage 4: Setup group chat
            print("\n💭 Stage 4/6: Setting up group chat...")
            manager = setup_group_chat(agents, task_id, self.conversation_state)
            print("   ✅ Group chat configured")
            
            # Stage 5: Start conversation (CLEAN VERSION)
            print("\n🎯 Stage 5/6: Starting conversation...")
            print("   🔄 Agents are discussing your app idea...")
            print("   ⏳ This may take 1-3 minutes depending on complexity...")
            print("   📊 Conversation progress:")
            print("   " + "="*50)
            
            # Start conversation without progress animation
            user_proxy = agents[0]  # Admin agent
            chat_result = user_proxy.initiate_chat(manager, message=initial_message)
            
            print("   " + "="*50)
            print("   ✅ Conversation completed")
            
            # Stage 6: Process results
            print("\n📊 Stage 6/6: Processing results...")
            
            # Extract messages
            messages = []
            for msg in chat_result.chat_history:
                if isinstance(msg, dict):
                    content = msg.get("content", msg.get("message", ""))
                    agent = msg.get("name", "Unknown")
                else:
                    content = str(msg)
                    agent = "Unknown"
                
                messages.append({
                    "content": content,
                    "agent": agent,
                    "timestamp": str(datetime.now())
                })
            
            print(f"   📝 Processed {len(messages)} messages")
            
            # Save conversation
            memory_manager.save_conversation(task_id, messages)
            print("   💾 Conversation saved to memory")
            
            # Extract JSON from final message
            final_message = messages[-1]["content"] if messages else ""
            wireframe_json = extract_json_from_message(final_message)
            
            # Check for consensus reached in the conversation
            consensus_reached = False
            for msg in messages[-5:]:  # Check last 5 messages for better coverage
                content = msg.get("content", "").lower()
                if any(indicator in content for indicator in [
                    "consensus reached:", 
                    "consensus_reached", 
                    "consensus achieved",
                    "we have consensus",
                    "consensus has been reached",
                    "final decision",
                    "agreed upon"
                ]):
                    consensus_reached = True
                    break
            
            # Validate wireframe if found
            validation_result = {"is_valid": False, "error": "No JSON found in output"}
            if wireframe_json:
                is_valid, error = validate_wireframe(wireframe_json)
                validation_result = {"is_valid": is_valid, "error": error}
                
                if is_valid:
                    print("   ✅ Valid wireframe JSON generated")
                else:
                    print(f"   ⚠️  Wireframe validation failed: {error}")
            elif consensus_reached:
                print("   ⚠️  Consensus reached but JSON extraction failed")
                validation_result = {"is_valid": False, "error": "Consensus reached but JSON extraction failed"}
            else:
                print("   ⚠️  No JSON wireframe found in output")
            
            # Prepare result
            result = {
                "task_id": task_id,
                "input": parsed_input,
                "wireframe": wireframe_json if validation_result["is_valid"] else None,
                "validation": validation_result,
                "conversation_summary": self.conversation_state.get_conversation_summary(),
                "messages_count": len(messages),
                "timestamp": str(datetime.now())
            }
            
            print("   ✅ Results processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error running query: {e}")
            raise
    
    def display_result(self, result: Dict[str, Any]):
        """
        Display the result in a user-friendly format with detailed stage information.
        
        Args:
            result: Result dictionary from run_query
        """
        print("\n" + "=" * 50)
        print("📊 RESULT SUMMARY")
        print("=" * 50)
        
        print(f"Task ID: {result['task_id']}")
        print(f"Messages processed: {result['messages_count']}")
        
        # Check for consensus reached
        consensus_reached = False
        if result['wireframe']:
            consensus_reached = True
        else:
            # Check if consensus was reached but JSON extraction failed
            validation_error = result['validation'].get('error', '')
            if any(indicator in validation_error.lower() for indicator in [
                'consensus reached', 
                'consensus achieved',
                'we have consensus',
                'consensus has been reached'
            ]):
                consensus_reached = True
        
        print(f"Consensus reached: {'✅ Yes' if consensus_reached else '❌ No'}")
        
        if result['wireframe']:
            print("\n🎯 WIREFRAME GENERATED")
            print("-" * 30)
            print(json.dumps(result['wireframe'], indent=2))
        else:
            print(f"\n⚠️  No valid wireframe generated")
            if result['validation']['error']:
                print(f"Error: {result['validation']['error']}")
                if consensus_reached:
                    print("💡 Note: Consensus was reached but JSON extraction failed. The agents may have produced valid output in an unexpected format.")
        
        # Display conversation summary with more details
        conv_summary = result['conversation_summary']
        print(f"\n📈 CONVERSATION SUMMARY")
        print("-" * 30)
        print(f"Rounds: {conv_summary['round_count']}/{conv_summary.get('max_rounds', 20)}")
        print(f"Agreement level: {conv_summary['agent_agreement_level']:.2f}")
        print(f"Duration: {conv_summary['conversation_duration']}")
        
        # Display agent participation
        if 'agent_participation' in conv_summary:
            print(f"\n👥 AGENT PARTICIPATION")
            print("-" * 30)
            for agent, count in conv_summary['agent_participation'].items():
                percentage = (count / conv_summary['messages_count']) * 100 if conv_summary['messages_count'] > 0 else 0
                print(f"{agent}: {count} messages ({percentage:.1f}%)")
        
        # Display topics discussed
        if 'topics_discussed' in conv_summary:
            print(f"\n🗣️  TOPICS DISCUSSED")
            print("-" * 30)
            for topic in conv_summary['topics_discussed']:
                print(f"  • {topic}")
        
        # Display consensus summary
        if 'consensus_summary' in conv_summary:
            print(f"\n🤝 CONSENSUS SUMMARY")
            print("-" * 30)
            consensus_summary = conv_summary['consensus_summary']
            print(f"Consensus attempts: {consensus_summary.get('attempts', 0)}")
            print(f"Average agreement: {consensus_summary.get('average_agreement', 0):.2f}")
        
        # Display conversation stages
        if 'stages_completed' in conv_summary:
            print(f"\n🎯 CONVERSATION STAGES")
            print("-" * 30)
            for stage in conv_summary['stages_completed']:
                print(f"  ✅ {stage}")
        
        print("\n" + "=" * 50)

    def run_screen_development(self, task_id: str, screen_id: str, focus: str = "full") -> Dict[str, Any]:
        """
        Develop a specific screen from an existing wireframe.
        
        Args:
            task_id: Task ID from previous wireframe generation
            screen_id: Screen ID to develop
            focus: Development focus (frontend, backend, full)
            
        Returns:
            Dictionary containing the screen development result and metadata
        """
        try:
            print(f"📝 Stage 1/4: Loading existing wireframe for task {task_id}...")
            
            # Load existing conversation and wireframe
            existing_messages = memory_manager.load_conversation(task_id)
            if not existing_messages:
                raise ValueError(f"No conversation found for task ID: {task_id}")
            
            print(f"   ✅ Loaded {len(existing_messages)} existing messages")
            
            # Extract wireframe from existing conversation
            wireframe = None
            for message in reversed(existing_messages):
                if isinstance(message, dict) and 'content' in message:
                    content = message['content']
                    if 'CONSENSUS REACHED:' in content or 'wireframe' in content.lower():
                        wireframe = extract_json_from_message(content)
                        if wireframe:
                            break
            
            if not wireframe:
                raise ValueError(f"No wireframe found in conversation for task ID: {task_id}")
            
            print(f"   ✅ Found existing wireframe")
            
            # Find the specific screen
            screen = None
            if 'app' in wireframe and 'screens' in wireframe['app']:
                for s in wireframe['app']['screens']:
                    if s.get('screen_id') == screen_id:
                        screen = s
                        break
            
            if not screen:
                available_screens = []
                if 'app' in wireframe and 'screens' in wireframe['app']:
                    available_screens = [s.get('screen_id', 'unknown') for s in wireframe['app']['screens']]
                raise ValueError(f"Screen '{screen_id}' not found. Available screens: {available_screens}")
            
            print(f"   ✅ Found screen: {screen.get('name', screen_id)}")
            
            # Stage 2: Create screen development message
            print(f"\n💬 Stage 2/4: Preparing screen development conversation...")
            
            focus_description = {
                "frontend": "frontend UI/UX components, styling, and user interactions",
                "backend": "backend logic, data models, APIs, and business logic",
                "full": "complete screen implementation including frontend and backend"
            }.get(focus, "complete screen implementation")
            
            initial_message = (
                f"Screen Development Request:\n"
                f"Task ID: {task_id}\n"
                f"Screen ID: {screen_id}\n"
                f"Screen Name: {screen.get('name', 'Unknown')}\n"
                f"Screen Purpose: {screen.get('purpose', 'Unknown')}\n"
                f"Development Focus: {focus} ({focus_description})\n\n"
                f"Existing Screen Components: {len(screen.get('components', []))}\n"
                f"Please develop this screen with focus on {focus_description}. "
                f"Consider user experience, technical feasibility, and best practices. "
                f"Provide detailed implementation guidance, code examples, and next steps."
            )
            
            print("   ✅ Screen development message prepared")
            
            # Stage 3: Create agents for screen development
            print(f"\n🤖 Stage 3/4: Creating agents for screen development...")
            agents = create_agents(task_id, self.conversation_state)
            print(f"   ✅ Created {len(agents)} agents")
            
            # Stage 4: Setup group chat and start conversation
            print(f"\n💭 Stage 4/4: Starting screen development conversation...")
            manager = setup_group_chat(agents, task_id, self.conversation_state)
            
            user_proxy = agents[0]  # Admin agent
            chat_result = user_proxy.initiate_chat(manager, message=initial_message)
            
            # Extract messages
            messages = []
            for msg in chat_result.chat_history:
                if isinstance(msg, dict):
                    content = msg.get("content", msg.get("message", ""))
                    agent = msg.get("name", "Unknown")
                else:
                    content = str(msg)
                    agent = "Unknown"
                
                messages.append({
                    "content": content,
                    "agent": agent,
                    "timestamp": str(datetime.now())
                })
            
            print(f"   ✅ Processed {len(messages)} messages")
            
            # Save conversation
            memory_manager.save_conversation(task_id, messages)
            print("   💾 Conversation saved to memory")
            
            # Extract JSON from final message
            final_message = messages[-1]["content"] if messages else ""
            screen_development_json = extract_json_from_message(final_message)
            
            # Validate result
            is_valid = False
            error = None
            if screen_development_json:
                is_valid, error = validate_wireframe(screen_development_json)
            
            # Prepare result
            result = {
                "task_id": task_id,
                "screen_id": screen_id,
                "focus": focus,
                "input": {
                    "task_id": task_id,
                    "screen_id": screen_id,
                    "focus": focus,
                    "screen_name": screen.get('name', screen_id),
                    "screen_purpose": screen.get('purpose', 'Unknown')
                },
                "wireframe": screen_development_json if is_valid else None,
                "validation": {
                    "is_valid": is_valid,
                    "error": error
                },
                "conversation_summary": {
                    "round_count": len(messages),
                    "agent_agreement_level": 0.8,  # Default for screen development
                    "conversation_duration": str(datetime.now() - self.conversation_state.conversation_start),
                    "messages_count": len(messages),
                    "focus_area": focus,
                    "stages_completed": [
                        "Load existing wireframe",
                        "Prepare screen development message", 
                        "Create agents",
                        "Screen development conversation"
                    ]
                },
                "messages_count": len(messages),
                "timestamp": str(datetime.now())
            }
            
            print("   ✅ Screen development completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in screen development: {e}")
            raise

def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(
        description="Multi-Agent Team System for App Wireframe Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input "* Fitness app. MVP: Log workouts. * Athlete (25). * Track progress"
  %(prog)s --interactive
  %(prog)s --test
  %(prog)s --screen-dev --task-id "fitness-app-123" --screen-id "workout-log" --focus "frontend"
  %(prog)s --screen-dev --task-id "fitness-app-123" --screen-id "workout-log" --focus "full"
  %(prog)s --list-tasks
  %(prog)s --check-task "fitness-app-123"
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input text in the format: * [Idea] * [Personas] * [Outcomes]"
    )
    
    parser.add_argument(
        "--interactive", "-I",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run with test data"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for JSON result (optional)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Screen development command
    parser.add_argument(
        "--screen-dev",
        action="store_true",
        help="Develop a specific screen from an existing wireframe"
    )
    
    parser.add_argument(
        "--task-id",
        type=str,
        help="Task ID from a previous wireframe generation (required for --screen-dev)"
    )
    
    parser.add_argument(
        "--screen-id",
        type=str,
        help="Screen ID to develop (required for --screen-dev)"
    )
    
    parser.add_argument(
        "--focus",
        type=str,
        choices=["frontend", "backend", "full"],
        default="full",
        help="Development focus area (frontend, backend, or full stack) - default: full"
    )
    
    # Task management commands
    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="List all available task IDs"
    )
    
    parser.add_argument(
        "--check-task",
        type=str,
        help="Check if a specific task ID exists"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate configuration
    if not validate_config():
        print("❌ Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    # Create application instance
    app = MultiAgentTeam()
    
    try:
        if args.test:
            # Run with test data
            test_input = "* Simple todo app. MVP: Add/edit tasks. * Busy mom (35). * Add task, view list."
            print(f"🧪 Running with test data: {test_input}")
            result = app.run_query_with_progress(test_input)
            app.display_result(result)
            
        elif args.interactive:
            # Run in interactive mode
            app.run_interactive()
            
        elif args.input:
            # Run with provided input
            print("🔄 Processing your request...")
            result = app.run_query_with_progress(args.input)
            app.display_result(result)
            
            # Save to file if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Result saved to: {args.output}")
                
        elif args.screen_dev:
            # Screen development mode
            if not args.task_id or not args.screen_id:
                print("❌ Error: --screen-dev requires both --task-id and --screen-id parameters")
                print("Example: python main.py --screen-dev --task-id 'fitness-app-123' --screen-id 'workout-log' --focus 'frontend'")
                return 1
            
            print(f"🔄 Developing screen '{args.screen_id}' from task '{args.task_id}' with focus: {args.focus}")
            result = app.run_screen_development(args.task_id, args.screen_id, args.focus)
            app.display_result(result)
            
            # Save to file if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Result saved to: {args.output}")
                
        elif args.list_tasks:
            # List all tasks
            print("📋 Listing all available tasks...")
            tasks = memory_manager.list_tasks()
            
            if not tasks:
                print("❌ No tasks found in memory.")
                print("💡 Try running a query first with: python main.py --input \"* [Your app idea] * [Personas] * [Outcomes]\"")
            else:
                print(f"✅ Found {len(tasks)} task(s):")
                print("-" * 50)
                for i, task_id in enumerate(tasks, 1):
                    # Get some basic info about the task
                    messages = memory_manager.load_conversation(task_id)
                    message_count = len(messages)
                    print(f"{i:2d}. {task_id} ({message_count} messages)")
                    
                    # Show first few words of the first message if available
                    if messages:
                        first_msg = messages[0]
                        if isinstance(first_msg, dict):
                            content = first_msg.get('content', first_msg.get('message', ''))
                        else:
                            content = str(first_msg)
                        
                        if content:
                            preview = content[:100].replace('\n', ' ').strip()
                            if len(content) > 100:
                                preview += "..."
                            print(f"     Preview: {preview}")
                    print()
                
        elif args.check_task:
            # Check if specific task exists
            task_id = args.check_task
            print(f"🔍 Checking if task '{task_id}' exists...")
            
            tasks = memory_manager.list_tasks()
            if task_id in tasks:
                messages = memory_manager.load_conversation(task_id)
                message_count = len(messages)
                print(f"✅ Task '{task_id}' exists!")
                print(f"   📊 Messages: {message_count}")
                
                # Check if it has a wireframe
                wireframe_found = False
                for message in reversed(messages):
                    if isinstance(message, dict) and 'content' in message:
                        content = message['content']
                        if 'CONSENSUS REACHED:' in content or 'wireframe' in content.lower():
                            wireframe_found = True
                            break
                
                if wireframe_found:
                    print("   🎯 Wireframe: Found")
                else:
                    print("   🎯 Wireframe: Not found")
                    
            else:
                print(f"❌ Task '{task_id}' not found.")
                print(f"💡 Available tasks: {', '.join(tasks) if tasks else 'None'}")
                
        else:
            # No arguments provided, show help
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 