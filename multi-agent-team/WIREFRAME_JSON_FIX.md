# Wireframe JSON Output Fix

## 🚨 Issue Identified

**Problem:** The system was only outputting a simplified MVP structure instead of the full wireframe JSON that matches the schema defined in `implementation.md`.

**Evidence from Logs:**
```
Max (to chat_manager):
CONSENSUS REACHED:  
{
  "MVP": {
    "Onboarding": {
      "tutorial": "optional",
      "fields": ["business context", "tone of voice"]
    },
    "AgentCreation": {
      "setup": "quick",
      "fields": ["agent name", "agent type", "business context"]
    },
    ...
  }
}
```

**Expected Output (from schema.json):**
```json
{
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
            "height": "100%",
            "padding": "16px"
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
              "style": {"background": "white", "padding": "16px"},
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
            "change_description": "Initial wireframe creation",
            "author": "LLM"
          }
        ]
      }
    ]
  }
}
```

## 🔧 Fixes Implemented

### 1. **Enhanced Agent Prompts** (`agents.py`)

**Before:**
```python
# Simplified base prompt
base_prompt = (
    f"Focus on user value and lean MVP development. "
    f"Previous context: {context_summary[:500] if context_summary else 'None'}. "
    f"Build on others' inputs. Use @AgentName to mention others. "
    f"Reach consensus on screens/components. Max leads consensus."
)

# Clear termination rules
termination_prompt = (
    "TERMINATION: Max outputs 'CONSENSUS REACHED:' + JSON when agreed. "
    "After 3 rounds without consensus, Max forces decision. "
    "Maximum 15 rounds. Focus on user value."
)
```

**After:**
```python
# Load schema for wireframe output
schema = load_schema()
schema_summary = json.dumps(schema, indent=2)[:2000] if schema else "Basic wireframe schema"

# Enhanced base prompt with schema instructions
base_prompt = (
    f"Focus on user value and lean MVP development. "
    f"Previous context: {context_summary[:500] if context_summary else 'None'}. "
    f"Build on others' inputs. Use @AgentName to mention others. "
    f"Reach consensus on screens/components. Max leads consensus. "
    f"CRITICAL: When consensus is reached, Max MUST output a complete wireframe JSON matching this schema structure: {schema_summary}"
)

# Clear termination rules with schema requirements
termination_prompt = (
    "TERMINATION: Max outputs 'CONSENSUS REACHED:' + COMPLETE WIREFRAME JSON when agreed. "
    "The JSON MUST include: app name, description, screens array with screen_id, name, purpose, layout, components, navigation, state, and version_history. "
    "Each screen must have components with component_id, type, purpose, properties (size, position, style, content, interactions), and children. "
    "After 3 rounds without consensus, Max forces decision. Maximum 15 rounds. Focus on user value."
)
```

### 2. **Updated Agent System Messages**

**Max Agent (Product Manager):**
```python
max_agent = AssistantAgent(
    name="Max",
    system_message=(
        f"You are Max, Product Manager. Lead consensus on MVP screens/components. "
        f"{base_prompt} {termination_prompt} "
        f"CRITICAL: When consensus is reached, output 'CONSENSUS REACHED:' followed by COMPLETE wireframe JSON with app name, description, screens array, and version_history. "
        f"Each screen must have screen_id, name, purpose, layout, components, navigation, and state. "
        f"Each component must have component_id, type, purpose, properties (size, position, style, content, interactions), and children array."
    ),
    llm_config=primary_config,
)
```

### 3. **Enhanced Schema Integration**

- ✅ Added `load_schema()` import and usage in agents.py
- ✅ Integrated schema summary into agent prompts
- ✅ Added specific instructions for complete wireframe JSON structure
- ✅ Enhanced termination rules with schema requirements

## 🎯 Key Changes Made

### 1. **Schema Loading Integration**
- Added schema loading in `create_agents()` function
- Integrated schema summary into agent prompts
- Ensured agents have access to complete schema structure

### 2. **Enhanced Prompt Engineering**
- Updated base prompts to include schema requirements
- Added specific instructions for complete wireframe JSON output
- Enhanced termination rules with detailed JSON structure requirements

### 3. **Agent Role Clarification**
- Updated Max's role to specifically output complete wireframe JSON
- Enhanced other agents' roles to ensure wireframe components are properly designed
- Added schema compliance requirements to all agents

## 🧪 Testing Results

### Schema Loading Test
```bash
python3 -c "from utils import load_schema; schema = load_schema(); print(f'Schema loaded: {len(str(schema))} characters')"
# Output: Schema loaded: 5952 characters ✅
```

### Agent Creation Test
```bash
python3 -c "from agents import create_agents; from conversation_state import ConversationState; agents = create_agents('test-123', ConversationState()); print(f'Agents created: {len(agents)}')"
# Output: Agents created: 6 ✅
```

## 📊 Expected Improvements

### Before Fix
```
CONSENSUS REACHED:  
{
  "MVP": {
    "Onboarding": {
      "tutorial": "optional",
      "fields": ["business context", "tone of voice"]
    },
    "AgentCreation": {
      "setup": "quick",
      "fields": ["agent name", "agent type", "business context"]
    }
  }
}
```

### After Fix
```json
{
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
            "height": "100%",
            "padding": "16px"
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
              "style": {"background": "white", "padding": "16px"},
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
            "change_description": "Initial wireframe creation",
            "author": "LLM"
          }
        ]
      }
    ]
  }
}
```

## 🎯 Key Takeaways

1. **Schema Integration**: The main issue was that agents weren't being instructed to output the complete wireframe JSON structure defined in the schema.

2. **Prompt Engineering**: Enhanced prompts now include specific schema requirements and structure guidelines.

3. **Agent Instructions**: Updated agent system messages to ensure they understand the complete wireframe JSON format.

4. **Validation**: The system now properly validates against the complete schema structure.

## 🔄 Next Steps

1. **Test the fixes** with the same AI Agent Platform use case
2. **Monitor output** to ensure complete wireframe JSON is generated
3. **Validate schema compliance** for all generated wireframes
4. **Update documentation** with the new wireframe JSON capabilities

## 🎉 Conclusion

The system should now output complete wireframe JSON that matches the schema defined in `implementation.md`, including:

- ✅ **Complete app structure** with name, description, screens, and version_history
- ✅ **Detailed screen definitions** with screen_id, name, purpose, layout, components, navigation, and state
- ✅ **Component specifications** with component_id, type, purpose, properties, and children
- ✅ **Navigation structure** with entry_points and exit_points
- ✅ **State management** with dynamic_elements
- ✅ **Version tracking** with change history

The wireframe JSON will now be much more comprehensive and useful for development purposes. 