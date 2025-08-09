# Multi-Agent Team System

A sophisticated multi-agent system using Microsoft AutoGen and OpenRouter to collaboratively generate app wireframes. The system simulates a product development team with specialized agents that discuss, critique, and reach consensus on MVP designs.

## 🎯 Features

- **Multi-Agent Collaboration**: 5 specialized agents (Product Manager, Designer, Engineer, QA, Customer Advocate)
- **Enhanced Termination Logic**: Prevents infinite loops with multi-layer detection
- **Smart Memory Management**: Automatic cleanup and conversation history
- **Consensus Detection**: Advanced agreement tracking and stalemate prevention
- **JSON Schema Validation**: Strict wireframe output validation
- **CLI & Interactive Modes**: Flexible user interfaces
- **OpenRouter Integration**: Multiple LLM model support

## 🏗️ Architecture

```
multi-agent-team/
├── main.py                 # Main application with CLI
├── agents.py              # Agent definitions and group chat
├── config.py              # OpenRouter configuration
├── memory.py              # Conversation memory management
├── utils.py               # Input parsing and JSON utilities
├── conversation_state.py  # Conversation tracking and termination
├── consensus.py           # Consensus detection algorithms
├── schema.json            # Wireframe JSON schema
├── requirements.txt       # Python dependencies
├── env.example           # Environment configuration example
└── tests/                # Test suite
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- OpenRouter API key
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd multi-agent-team

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your OpenRouter API key
# OPENROUTER_API_KEY=your_api_key_here
```

### 3. Basic Usage

#### Command Line Interface

```bash
# Run with test data
python main.py --test

# Run with custom input
python main.py --input "* Fitness app. MVP: Log workouts. * Athlete (25). * Track progress"

# Interactive mode
python main.py --interactive

# Save output to file
python main.py --input "* Todo app. MVP: Add tasks. * Busy mom (35). * Organize tasks" --output result.json
```

#### Interactive Mode

```bash
python main.py --interactive
```

Example interaction:
```
🤖 Multi-Agent Team System - Interactive Mode
==================================================
Enter your app idea in the following format:
* [App Idea/MVP description] * [User Personas] * [Desired Outcomes]
Example: * Fitness tracking app. MVP: Log workouts. * Fitness enthusiast (28). * Track progress, set goals.
Type 'quit' to exit.

Enter your app idea: * Recipe app. MVP: Save recipes. * Home cook (40). * Find and save recipes
```

## 📋 Input Format

The system expects input in the following format:

```
* [App Idea/MVP description] * [User Personas] * [Desired Outcomes]
```

### Examples

**Fitness Tracking App:**
```
* Fitness tracking app. MVP: Log workouts, track progress. * Fitness enthusiast (28), gym-goer (32). * Track workouts, see progress over time, set goals.
```

**Recipe Management App:**
```
* Recipe app. MVP: Save and organize recipes. * Home cook (40), busy parent (35). * Find recipes, save favorites, create meal plans.
```

**Task Management App:**
```
* Todo app. MVP: Add and organize tasks. * Busy professional (30), student (22). * Create tasks, set priorities, track completion.
```

## 🤖 Agents

The system includes 5 specialized agents:

1. **Max (Product Manager)**: Leads consensus, focuses on user value and lean MVPs
2. **Alex (Product Designer)**: UX expert, focuses on user journeys and design principles
3. **Sam (Engineer)**: Technical feasibility, performance, and maintainability
4. **Jamie (QA Engineer)**: Quality assurance, edge cases, and reliability
5. **Customer Advocate**: User needs, pain points, and business value

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional (with defaults)
MAX_MEMORY_SIZE_MB=50
MAX_CONVERSATION_AGE_DAYS=30
MAX_ROUNDS=20
```

### Model Configuration

The system supports multiple LLM models through OpenRouter:

- **Primary**: `openai/gpt-4o-mini`
- **Secondary**: `anthropic/claude-3.5-sonnet`
- **Fallback**: `openai/gpt-3.5-turbo`

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
python test_phases.py

# Test individual components
python -c "import config; print('Config OK')"
python -c "import memory; print('Memory OK')"
python -c "import utils; print('Utils OK')"
```

### Test with Sample Data

```bash
# Run with built-in test data
python main.py --test
```

## 📊 Output Format

The system outputs a structured JSON response:

```json
{
  "task_id": "unique-task-id",
  "input": {
    "idea_mvp": "App description",
    "personas": "User personas",
    "outcomes": "Desired outcomes"
  },
  "wireframe": {
    "app": {
      "name": "App Name",
      "description": "App description",
      "screens": [...],
      "version_history": [...]
    }
  },
  "validation": {
    "is_valid": true,
    "error": null
  },
  "conversation_summary": {
    "round_count": 5,
    "agent_agreement_level": 0.8,
    "conversation_duration": "0:02:30"
  },
  "messages_count": 15,
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🔍 Troubleshooting

### Common Issues

**1. API Key Not Found**
```
❌ Configuration validation failed. Please check your .env file.
```
**Solution**: Ensure your `.env` file contains `OPENROUTER_API_KEY=your_key_here`

**2. Module Import Errors**
```
ModuleNotFoundError: No module named 'autogen'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

**3. Schema Validation Errors**
```
Validation error at app.screens[0].components[0].properties: 'size' is a required property
```
**Solution**: The system will automatically retry with corrected JSON extraction

**4. Conversation Timeout**
```
Conversation timeout
```
**Solution**: The system automatically terminates after 30 minutes or 20 rounds

### Debug Mode

Enable verbose logging for debugging:

```bash
python main.py --input "your input" --verbose
```

## 🔄 Memory Management

The system automatically manages conversation history:

- **Automatic Cleanup**: Removes conversations older than 30 days
- **Size Limits**: Triggers cleanup when memory exceeds 50MB
- **Task Organization**: Conversations organized by task ID
- **Metadata Tracking**: Tracks conversation statistics and metadata

## 🎯 Advanced Features

### Custom Termination Logic

The system includes sophisticated termination detection:

- **Consensus Reached**: Detects when agents reach agreement
- **Repetition Detection**: Identifies when conversations go in circles
- **Stalemate Detection**: Recognizes when agents cannot agree
- **Timeout Protection**: Automatic termination after 30 minutes

### Consensus Detection

Advanced consensus tracking includes:

- **Agreement Level**: Calculates overall agreement (0.0-1.0)
- **Confidence Scoring**: Measures consensus confidence
- **Attempt Tracking**: Monitors consensus attempts
- **Force Consensus**: Automatically forces consensus after 15 rounds

## 📈 Performance

### Memory Usage

- **Typical**: 1-5MB per conversation
- **Maximum**: 50MB (automatic cleanup)
- **Cleanup**: Removes old conversations automatically

### Response Time

- **Simple queries**: 30-60 seconds
- **Complex queries**: 2-5 minutes
- **Timeout**: 30 minutes maximum

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the test suite
3. Enable verbose logging
4. Check the conversation history in `conversation_history.json`

## 🔮 Future Enhancements

- [ ] API endpoints for web integration
- [ ] Real-time conversation monitoring
- [ ] SQLite alternative for memory
- [ ] Export/import functionality
- [ ] Advanced agent customization
- [ ] Multi-language support 