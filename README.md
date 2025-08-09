# Agent Product Team

A sophisticated multi-agent system using Microsoft AutoGen and OpenRouter to collaboratively generate app wireframes using the OPUS framework (Outcome, Purpose, User, Scenario). The system simulates a product development team with specialized agents that discuss, critique, and reach consensus on MVP designs.

## 🎯 Features

- **Multi-Agent Collaboration**: 6 specialized agents (Product Manager, Designer, Frontend Engineer, Backend Engineer, QA Engineer, Customer Advocate)
- **OPUS Framework Integration**: Structured design thinking using Outcome, Purpose, User, Scenario methodology
- **Enhanced Termination Logic**: Prevents infinite loops with multi-layer detection
- **Smart Memory Management**: Automatic cleanup and conversation history
- **Consensus Detection**: Advanced agreement tracking and stalemate prevention
- **JSON Schema Validation**: Strict wireframe output validation
- **CLI & Interactive Modes**: Flexible user interfaces
- **OpenRouter Integration**: Multiple LLM model support
- **Cursor Integration**: OPUS-structured output for code generation

## 🏗️ Architecture

```
agent-product-team/
├── multi-agent-team/          # Core multi-agent system
│   ├── main.py               # Main application with CLI
│   ├── agents.py             # Agent definitions and group chat
│   ├── config.py             # OpenRouter configuration
│   ├── memory.py             # Conversation memory management
│   ├── utils.py              # Input parsing and JSON utilities
│   ├── conversation_state.py # Conversation tracking and termination
│   ├── consensus.py          # Consensus detection algorithms
│   ├── schema.json           # Wireframe JSON schema
│   ├── requirements.txt      # Python dependencies
│   ├── env.example          # Environment configuration example
│   └── tests/               # Test suite
├── OPUS_IMPLEMENTATION.md    # OPUS framework implementation guide
├── implementation.md         # Complete implementation documentation
├── implementation_plan.md    # Implementation plan and phases
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- OpenRouter API key
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-product-team.git
cd agent-product-team

# Navigate to the multi-agent-team directory
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

## 🤖 Agents

The system includes 6 specialized agents with OPUS framework expertise:

1. **Max (Product Manager)**: OPUS Outcome/Purpose focus - Leads consensus and defines user outcomes and business purpose
2. **Alex (Product Designer)**: OPUS User/Scenario focus - Designs UX flows and user scenarios
3. **Sam (Frontend Engineer)**: OPUS Technical feasibility - Ensures frontend implementation supports user outcomes
4. **BackendEngineer (NEW)**: OPUS Data/API focus - Designs backend architecture and APIs
5. **Jamie (QA Engineer)**: OPUS Testing/Edge cases - Validates features work in all scenarios
6. **Customer Advocate**: OPUS User value focus - Represents user needs and pain points

## 🎯 OPUS Framework

The system implements the **OPUS framework** for structured design thinking:

- **Outcome**: What users want to achieve
- **Purpose**: Why the feature exists
- **User**: Who the feature is for
- **Scenario**: When/how the feature is used

### OPUS Integration Benefits

- **Structured Design**: Systematic approach to design thinking
- **User-Focused**: Explicit focus on user outcomes and scenarios
- **Purpose-Driven**: Clear understanding of why features exist
- **Scenario-Based**: Design based on real user scenarios
- **Better Code Generation**: OPUS-structured output for Cursor integration

## 📊 Output Format

The system outputs a structured JSON response with OPUS elements:

```json
{
  "app": {
    "name": "App Name",
    "description": "App description",
    "opus_framework": {
      "outcome": "What users want to achieve",
      "purpose": "Why the app exists",
      "user": "Who the app is for",
      "scenario": "When/how the app is used"
    },
    "screens": [
      {
        "screen_id": "screen_name",
        "name": "Screen Name",
        "opus": {
          "outcome": "Screen-specific outcome",
          "purpose": "Screen-specific purpose",
          "user": "Screen-specific user",
          "scenario": "Screen-specific scenario"
        },
        "components": [...]
      }
    ],
    "backend_architecture": {
      "data_models": [...],
      "api_endpoints": [...]
    }
  }
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `multi-agent-team` directory:

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
# Navigate to multi-agent-team directory
cd multi-agent-team

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

## 📚 Documentation

- **[OPUS Implementation Guide](OPUS_IMPLEMENTATION.md)**: Complete guide to OPUS framework integration
- **[Implementation Documentation](implementation.md)**: Detailed implementation documentation
- **[Implementation Plan](implementation_plan.md)**: Implementation phases and roadmap

## 🔄 Development Phases

### Phase 1: Core OPUS Integration (Weeks 1-2)
- Implement basic OPUS framework in agent prompts
- Add OPUS-structured discussions
- Create OPUS-based debate mechanics

### Phase 2: Backend Engineer Integration (Weeks 3-4)
- Add backend engineer agent
- Implement backend architecture considerations
- Integrate backend perspective into OPUS discussions

### Phase 3: Enhanced Output & Integration (Weeks 5-6)
- Transform wireframe JSON to include OPUS elements
- Implement Cursor-compatible OPUS output
- Add OPUS-based code generation prompts

### Phase 4: Optimization & Testing (Weeks 7-8)
- Optimize OPUS implementation
- Test OPUS framework effectiveness
- Validate Cursor integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

1. Check the [documentation](OPUS_IMPLEMENTATION.md)
2. Review [implementation details](implementation.md)
3. Open an [issue](https://github.com/yourusername/agent-product-team/issues)

## 🎯 Roadmap

- [ ] Complete OPUS framework integration
- [ ] Backend engineer agent implementation
- [ ] Enhanced output format with OPUS elements
- [ ] Cursor integration for code generation
- [ ] Advanced debate mechanics
- [ ] Performance optimization
- [ ] Comprehensive testing suite

---

**Project Status**: Active Development  
**Last Updated**: January 2024  
**Version**: 1.0.0 