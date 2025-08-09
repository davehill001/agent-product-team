## Overview
This document provides the **complete, final implementation plan** for a multi-agent system using Microsoft AutoGen and OpenRouter. The system simulates a product development team to process user input (app idea/MVP, user personas, desired outcomes) and collaboratively generate a lean MVP wireframe. Agents discuss critically—focusing on user journeys, JTBD (Jobs To Be Done), minimum must-haves vs. extras—iterating until consensus. The output is a validated JSON wireframe matching the provided schema.

Features Incorporated:
- **Agents and Roles**: Product Manager (Max), Product Designer (Alex), Full Stack Developer (Sam), QA Engineer (Jamie), Customer Advocate (formerly Claude).
- **Collaboration**: Group chat with mentions, consensus termination (via "CONSENSUS REACHED").
- **Memory**: Persistent conversation history across queries for task continuity (JSON-based, optional SQLite).
- **Input Handling**: Parses combined text input into idea/MVP, personas, outcomes.
- **Output**: Strict JSON wireframe with schema validation.
- **OpenRouter Integration**: Uses `openai/gpt-4o-mini` and `anthropic/claude-3.5-sonnet`.
- **Cursor Integration**: Query via CLI or API for vibe coding support; extendable for N8N if needed.
- **Consensus and Critical Thinking**: Agents challenge each other on UX, value, feasibility, edge cases.

This plan is designed to be imported into Cursor as a `.md` file. Use Composer mode to generate code files (e.g., prompt: "Generate [file] based on the final plan.").

## Requirements
- **Python**: 3.10+.
- **Libraries**:
  - `autogen` (pip install autogen)
  - `openai` (pip install openai)
  - `jsonschema` (pip install jsonschema)
  - `dotenv` (pip install python-dotenv)
  - Optional: `fastapi`, `uvicorn` (for API; pip install fastapi uvicorn)
- **OpenRouter**: API key in `.env` as `OPENROUTER_API_KEY`.
- **Cursor**: Open this file; use Composer for code generation/debugging.

## Project Structure
```
multi-agent-team/
├── main.py          # Entry point: Parses input, runs chat, extracts/validates JSON
├── agents.py        # Defines agents, group chat, termination
├── config.py        # OpenRouter LLM configs
├── memory.py        # Conversation history storage/retrieval
├── utils.py         # Input parsing, JSON extraction/validation
├── schema.json      # Wireframe JSON schema
├── requirements.txt # List of pip installs
└── .env             # API keys (git ignore)
```

In Cursor: "Create project structure with these files."

## 1. Config File (config.py)
Handles OpenRouter API configuration.

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_config(model_name):
    return {
        "model": model_name,
        "api_key": OPENROUTER_API_KEY,
        "base_url": "https://openrouter.ai/api/v1",
        "api_type": "openai",
    }
```

In Cursor: "Generate config.py with OpenRouter setup."

## 2. Memory Management (memory.py)
Stores conversation history by task ID for context continuity.

```python
# memory.py
import json
import os
import uuid
from datetime import datetime

MEMORY_FILE = "conversation_history.json"

def initialize_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w') as f:
            json.dump({"tasks": {}}, f)

def save_conversation(task_id, messages):
    initialize_memory()
    with open(MEMORY_FILE, 'r') as f:
        data = json.load(f)
    data["tasks"].setdefault(task_id, []).extend(
        [{"message": msg, "timestamp": str(datetime.now())} for msg in messages]
    )
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_conversation(task_id):
    initialize_memory()
    with open(MEMORY_FILE, 'r') as f:
        data = json.load(f)
    return data["tasks"].get(task_id, [])

def generate_task_id(query):
    query_key = query[:50].lower().strip()
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, query_key))

# Optional SQLite Alternative (uncomment to use)
# import sqlite3
# def initialize_db():
#     conn = sqlite3.connect("conversation_history.db")
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS conversations (task_id TEXT, message TEXT, timestamp TEXT)''')
#     conn.commit()
#     conn.close()
# 
# def save_conversation(task_id, messages):
#     initialize_db()
#     conn = sqlite3.connect("conversation_history.db")
#     c = conn.cursor()
#     for msg in messages:
#         c.execute("INSERT INTO conversations VALUES (?, ?, ?)", (task_id, msg, str(datetime.now())))
#     conn.commit()
#     conn.close()
# 
# def load_conversation(task_id):
#     initialize_db()
#     conn = sqlite3.connect("conversation_history.db")
#     c = conn.cursor()
#     c.execute("SELECT message FROM conversations WHERE task_id = ? ORDER BY timestamp", (task_id,))
#     messages = [{"message": row[0], "timestamp": ""} for row in c.fetchall()]
#     conn.close()
#     return messages
```

In Cursor: "Generate memory.py with JSON storage and optional SQLite."

## 3. Utilities (utils.py)
Parses input, extracts/validates JSON.

```python
# utils.py
import json
import re
from jsonschema import validate, ValidationError

# Load schema (assume schema.json is in the same directory)
with open("schema.json", "r") as f:
    WIREFRAME_SCHEMA = json.load(f)

def parse_user_input(input_text):
    parts = re.split(r'\*\s*|\n\n', input_text.strip())
    if len(parts) < 3:
        raise ValueError("Input must contain idea/MVP, personas, and outcomes.")
    return {
        "idea_mvp": parts[0].strip(),
        "personas": parts[1].strip(),
        "outcomes": parts[2].strip()
    }

def extract_json_from_message(message):
    json_match = re.search(r'\{.*\}', message, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return None
    return None

def validate_wireframe(wireframe_json):
    try:
        validate(instance=wireframe_json, schema=WIREFRAME_SCHEMA)
        return True, "Valid"
    except ValidationError as e:
        return False, str(e)
```

In Cursor: "Generate utils.py with parsing, extraction, and validation."

## 4. Agents Definition (agents.py)
Defines agents with task-specific prompts, consensus logic.

```python
# agents.py
import json
from autogen import AssistantAgent, GroupChatManager, GroupChat
from config import get_config
from memory import load_conversation
from utils import WIREFRAME_SCHEMA

def is_termination_msg(messages):
    if messages and "CONSENSUS REACHED" in messages[-1].get("content", ""):
        return True
    return False

def create_agents(task_id):
    context = load_conversation(task_id)
    context_summary = "\n".join([msg["message"] for msg in context[-5:]])

    base_prompt = (
        f"Discuss app MVP: critically evaluate user journeys, JTBD for screens/components, challenge minimum vs. must-have. "
        f"Iterate until consensus. When agreed, Max outputs final wireframe as JSON matching schema, prefixed with 'CONSENSUS REACHED:'. "
        f"Schema: {json.dumps(WIREFRAME_SCHEMA, indent=2)[:2000]}... (use full structure). "
        f"Previous context: {context_summary}. Build on inputs, mention others (e.g., @Alex)."
    )

    max_agent = AssistantAgent(
        name="Max",
        system_message=f"You are Max, Product Manager obsessed with user value/lean MVPs. Lead consensus. Output JSON when agreed. {base_prompt}",
        llm_config=get_config("openai/gpt-4o-mini"),
    )

    alex_agent = AssistantAgent(
        name="Alex",
        system_message=f"You are Alex, Product Designer focused on UX/journeys/JTBD. Challenge designs. {base_prompt}",
        llm_config=get_config("openai/gpt-4o-mini"),
    )

    sam_agent = AssistantAgent(
        name="Sam",
        system_message=f"You are Sam, Engineer focused on tech feasibility/efficiency. Suggest minimal stacks. {base_prompt}",
        llm_config=get_config("openai/gpt-4o-mini"),
    )

    jamie_agent = AssistantAgent(
        name="Jamie",
        system_message=f"You are Jamie, QA Engineer focused on edge cases/reliability. Test implications. {base_prompt}",
        llm_config=get_config("openai/gpt-4o-mini"),
    )

    customer_advocate = AssistantAgent(
        name="CustomerAdvocate",
        system_message=f"You are Customer Advocate, representing user needs/pain points/value. Challenge non-essentials. {base_prompt}",
        llm_config=get_config("anthropic/claude-3.5-sonnet"),
    )

    user_proxy = AssistantAgent(
        name="Admin",
        human_input_mode="NEVER",
        system_message="Initiate/oversee discussion.",
        llm_config=False,
    )

    return [user_proxy, max_agent, alex_agent, sam_agent, jamie_agent, customer_advocate]

def setup_group_chat(agents, task_id):
    group_chat = GroupChat(
        agents=agents,
        messages=[msg["message"] for msg in load_conversation(task_id)],
        max_round=20,
    )
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=get_config("openai/gpt-4o-mini"),
        is_termination_msg=is_termination_msg,
    )
    return manager
```

In Cursor: "Generate agents.py with updated personas and consensus."

## 5. Main Application (main.py)
Runs the system, handles CLI/API.

```python
# main.py
from agents import create_agents, setup_group_chat
from autogen import UserProxyAgent
from memory import generate_task_id, save_conversation
from utils import parse_user_input, extract_json_from_message, validate_wireframe
import argparse
import json

def run_query(input_text):
    parsed = parse_user_input(input_text)
    task_id = generate_task_id(parsed["idea_mvp"])
    
    initial_message = (
        f"App Idea/MVP: {parsed['idea_mvp']}\n"
        f"User Personas: {parsed['personas']}\n"
        f"Desired Outcomes: {parsed['outcomes']}\n"
        "Discuss critically: journeys, JTBD, minimums. Iterate to consensus on screens/components. Max: Output JSON wireframe."
    )
    
    agents = create_agents(task_id)
    manager = setup_group_chat(agents, task_id)
    
    user_proxy = agents[0]
    chat_result = user_proxy.initiate_chat(manager, message=initial_message)
    
    messages = [msg.get("content", "") for msg in chat_result.chat_history]
    save_conversation(task_id, messages)
    
    final_message = messages[-1]
    wireframe_json = extract_json_from_message(final_message)
    
    if wireframe_json:
        is_valid, error = validate_wireframe(wireframe_json)
        if is_valid:
            return wireframe_json
        else:
            raise ValueError(f"Invalid JSON: {error}")
    raise ValueError("No JSON in output.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_text", type=str, help="User input text")
    args = parser.parse_args()
    
    if args.input_text:
        result = run_query(args.input_text)
        print(json.dumps(result, indent=2))
    else:
        test_input = "* Simple todo app for parents. MVP: Add/edit tasks. * Busy mom (35). * Add task, view list."
        result = run_query(test_input)
        print(json.dumps(result, indent=2))

# Optional API (add for Cursor integration)
# from fastapi import FastAPI
# app = FastAPI()
# @app.post("/query")
# def query_agents(body: dict):
#     input_text = body.get("input_text")
#     result = run_query(input_text)
#     return {"wireframe": result}
# # Run: uvicorn main:app --reload
```

In Cursor: "Generate main.py with full query handling."

## 6. Schema File (schema.json)

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/wireframe-schema.json",
  "title": "App Wireframe Schema",
  "description": "A schema for defining app wireframes, including screens, components, navigation, state, and version history. Used to instruct AIs to output JSON in this format for MVP designs.",
  "type": "object",
  "properties": {
    "app": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "The name of the app"
        },
        "description": {
          "type": "string",
          "description": "A brief overview of the app's purpose"
        },
        "screens": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/screen"
          },
          "description": "Array of screens in the app"
        },
        "version_history": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/version_entry"
          },
          "description": "Changelog tracking modifications to the wireframe"
        }
      },
      "required": ["name", "description", "screens", "version_history"]
    }
  },
  "required": ["app"],
  "$defs": {
    "screen": {
      "type": "object",
      "properties": {
        "screen_id": {
          "type": "string",
          "description": "Unique identifier for the screen"
        },
        "name": {
          "type": "string",
          "description": "Human-readable name of the screen"
        },
        "purpose": {
          "type": "string",
          "description": "High-level purpose of the screen"
        },
        "layout": {
          "$ref": "#/$defs/layout"
        },
        "components": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/component"
          },
          "description": "Array of components on the screen"
        },
        "navigation": {
          "$ref": "#/$defs/navigation"
        },
        "state": {
          "$ref": "#/$defs/state"
        }
      },
      "required": ["screen_id", "name", "purpose", "layout", "components", "navigation", "state"]
    },
    "layout": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "description": "Layout type (e.g., stack, grid, absolute)"
        },
        "orientation": {
          "type": "string",
          "enum": ["vertical", "horizontal"],
          "description": "Orientation of the layout"
        },
        "constraints": {
          "type": "object",
          "properties": {
            "width": {
              "type": "string",
              "description": "Width constraint (e.g., 100%, 200px)"
            },
            "height": {
              "type": "string",
              "description": "Height constraint (e.g., 100%, 200px)"
            },
            "padding": {
              "type": "string",
              "description": "Padding value (e.g., 16px)"
            },
            "margin": {
              "type": "string",
              "description": "Margin value (e.g., 0)"
            }
          },
          "additionalProperties": true,
          "description": "Additional layout constraints"
        }
      },
      "required": ["type", "orientation", "constraints"]
    },
    "component": {
      "type": "object",
      "properties": {
        "component_id": {
          "type": "string",
          "description": "Unique identifier for the component"
        },
        "type": {
          "type": "string",
          "description": "Type of component (e.g., button, text, list)"
        },
        "purpose": {
          "type": "string",
          "description": "Specific role of the component"
        },
        "properties": {
          "type": "object",
          "properties": {
            "size": {
              "type": "object",
              "properties": {
                "width": {
                  "type": "string"
                },
                "height": {
                  "type": "string"
                }
              },
              "required": ["width", "height"]
            },
            "position": {
              "type": "object",
              "properties": {
                "x": {
                  "type": "string"
                },
                "y": {
                  "type": "string"
                }
              },
              "required": ["x", "y"]
            },
            "style": {
              "type": "object",
              "additionalProperties": {
                "type": "string"
              },
              "description": "Style properties (e.g., background, color, font)"
            },
            "content": {
              "type": "string",
              "description": "Content of the component (text, placeholder, etc.)"
            },
            "interactions": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/interaction"
              }
            }
          },
          "required": ["size", "position", "style", "content", "interactions"],
          "additionalProperties": true
        },
        "children": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/component"
          },
          "description": "Nested child components (recursive)"
        }
      },
      "required": ["component_id", "type", "purpose", "properties", "children"]
    },
    "interaction": {
      "type": "object",
      "properties": {
        "trigger": {
          "type": "string",
          "description": "Event trigger (e.g., onClick, onChange)"
        },
        "action": {
          "type": "string",
          "description": "Action to perform (e.g., navigate, update_state)"
        },
        "target": {
          "type": "string",
          "description": "Target component or screen ID"
        }
      },
      "required": ["trigger", "action", "target"]
    },
    "navigation": {
      "type": "object",
      "properties": {
        "entry_points": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/nav_point"
          }
        },
        "exit_points": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/nav_point"
          }
        }
      },
      "required": ["entry_points", "exit_points"]
    },
    "nav_point": {
      "type": "object",
      "properties": {
        "from_screen_id": {
          "type": "string",
          "description": "Source screen ID (for entry_points)"
        },
        "to_screen_id": {
          "type": "string",
          "description": "Destination screen ID (for exit_points)"
        },
        "trigger": {
          "type": "string",
          "description": "Trigger event (e.g., button_click)"
        },
        "conditions": {
          "type": "string",
          "description": "Optional conditions (e.g., none, field_not_empty)"
        }
      },
      "additionalProperties": false
    },
    "state": {
      "type": "object",
      "properties": {
        "dynamic_elements": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/dynamic_element"
          }
        }
      },
      "required": ["dynamic_elements"]
    },
    "dynamic_element": {
      "type": "object",
      "properties": {
        "component_id": {
          "type": "string",
          "description": "ID of the dynamic component"
        },
        "data_source": {
          "type": "string",
          "description": "Data source (e.g., local_storage, API)"
        },
        "update_trigger": {
          "type": "string",
          "description": "Trigger for updates (e.g., on_load, on_change)"
        }
      },
      "required": ["component_id", "data_source", "update_trigger"]
    },
    "version_entry": {
      "type": "object",
      "properties": {
        "version": {
          "type": "string",
          "description": "Version number (e.g., 1.0)"
        },
        "date": {
          "type": "string",
          "description": "Date of the change (e.g., YYYY-MM-DD)"
        },
        "changes": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/change"
          }
        }
      },
      "required": ["version", "date", "changes"]
    },
    "change": {
      "type": "object",
      "properties": {
        "screen_id": {
          "type": "string",
          "description": "ID of the affected screen"
        },
        "component_id": {
          "type": "string",
          "description": "ID of the affected component (or 'none')"
        },
        "change_description": {
          "type": "string",
          "description": "Description of the change"
        },
        "author": {
          "type": "string",
          "description": "Author of the change (e.g., LLM, User)"
        }
      },
      "required": ["screen_id", "component_id", "change_description", "author"]
    }
  }
}

## 7. Requirements File (requirements.txt)
```
autogen
openai
jsonschema
python-dotenv
fastapi  # Optional
uvicorn  # Optional
```

## Testing and Usage
- **Run Example**: `python main.py --input_text "* Idea... * Personas... * Outcomes..."`
- **Cursor Vibe Coding**: Send queries via CLI/API for feedback.
- **Debug**: Use Composer for fixes.
- **Extensions**: Add code execution to agents if needed.

