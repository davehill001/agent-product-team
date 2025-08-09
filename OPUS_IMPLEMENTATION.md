# OPUS Framework Implementation for Multi-Agent Team System

## 🎯 Overview

This document outlines the implementation of the **OPUS framework** (Outcome, Purpose, User, Scenario) into the existing multi-agent team system. The OPUS framework will transform the current wireframe generation system into a more structured, user-focused, and debate-driven approach that produces high-quality, actionable designs for Cursor code generation.

## 🏗️ Current System Analysis

### Existing Architecture
- **6 Agents**: Product Manager (Max), Designer (Alex), Frontend Engineer (Sam), Backend Engineer (NEW), QA (Jamie), Customer Advocate
- **AutoGen Integration**: Group chat with consensus detection
- **Output**: OPUS-structured wireframes with clear blocks
- **Memory**: Conversation history and state tracking

### Current Limitations
- No structured OPUS framework integration
- Limited debate mechanics
- Missing backend engineering perspective
- Complex JSON output format

## 🎯 OPUS Framework Integration

### What is OPUS?

**OPUS** is a structured framework for design thinking that breaks down features into four key elements:

1. **Outcome (O)**: What users want to achieve
2. **Purpose (P)**: Why the feature exists  
3. **User (U)**: Who the feature is for
4. **Scenario (S)**: When/how the feature is used

### OPUS Implementation Strategy

#### Phase 1: Agent Role Redefinition
Transform existing agents to incorporate OPUS framework:

```python
# Current Agent Roles → OPUS-Enhanced Roles
Max (PM) → PM with OPUS Outcome/Purpose focus
Alex (Designer) → Designer with OPUS User/Scenario focus  
Sam (Engineer) → FE Developer with OPUS technical feasibility
NEW: BackendEngineer → BE Developer with OPUS data/API focus
Jamie (QA) → QA with OPUS testing/edge case focus
Customer Advocate → User Advocate with OPUS user value focus
```

#### Phase 2: OPUS Discussion Framework
Implement structured OPUS-based discussions:

```python
# OPUS Discussion Structure
1. Outcome Analysis: What do users want to achieve?
2. Purpose Definition: Why does this feature exist?
3. User Identification: Who is this feature for?
4. Scenario Mapping: When/how is this feature used?
5. OPUS Integration: How do all elements work together?
6. Consensus Building: Agreement on OPUS structure
```

#### Phase 3: OPUS Output Format
Transform to simple, readable OPUS blocks for each screen, component, and function:

```
Name: Login/Sign Up Page
O: Users want to securely access their account and start using the app
P: Provide secure authentication and user account access
U: New users creating accounts, existing users logging in
S: User opens app for first time, user returns to app, user switches devices

Name: Google OAuth Button
O: Users want to quickly sign in using their existing Google account
P: Reduce friction in authentication process and increase conversion
U: Users with Google accounts who prefer social login
S: User clicks "Sign in with Google" during registration or login flow

Name: Login Form Inputs
O: Users want to enter their credentials to access their account
P: Collect and validate user authentication credentials
U: Users with email/password accounts
S: User enters email and password to log in

Name: Login Form Submit Button
O: Users want to submit their credentials and access their account
P: Process authentication request and redirect to main app
U: Users with valid credentials ready to log in
S: User clicks submit after entering email and password
```

## 🤖 Enhanced Agent Definitions

### 1. Max (Product Manager) - OPUS Outcome/Purpose Focus

```python
max_agent = AssistantAgent(
    name="Max",
    system_message=(
        f"You are Max, Product Manager with OPUS framework expertise. "
        f"Focus on OUTCOME and PURPOSE elements of OPUS framework. "
        f"Lead consensus on MVP screens/components using OPUS structure. "
        f"{base_prompt} {termination_prompt} "
        f"OPUS FRAMEWORK ROLES:\n"
        f"- OUTCOME: Define what users want to achieve with each feature\n"
        f"- PURPOSE: Explain why each feature exists and its business value\n"
        f"- Facilitate OPUS-based discussions and debates\n"
        f"- Ensure all features align with user outcomes and business purpose\n"
        f"CRITICAL: When consensus is reached, output 'CONSENSUS REACHED:' followed by OPUS blocks for each screen, component, and function."
    ),
    llm_config=primary_config,
)
```

### 2. Alex (Product Designer) - OPUS User/Scenario Focus

```python
alex_agent = AssistantAgent(
    name="Alex", 
    system_message=(
        f"You are Alex, Product Designer with OPUS framework expertise. "
        f"Focus on USER and SCENARIO elements of OPUS framework. "
        f"Design UX flows and components using OPUS structure. "
        f"{base_prompt} Challenge designs that don't prioritize user experience. "
        f"OPUS FRAMEWORK ROLES:\n"
        f"- USER: Identify who each feature is for and their characteristics\n"
        f"- SCENARIO: Define when and how each feature is used\n"
        f"- Design user-friendly and accessible components\n"
        f"- Ensure designs support user scenarios effectively\n"
        f"Use @Max, @Sam, @BackendEngineer, @Jamie to mention others."
    ),
    llm_config=primary_config,
)
```

### 3. Sam (Frontend Engineer) - OPUS Technical Feasibility

```python
sam_agent = AssistantAgent(
    name="Sam",
    system_message=(
        f"You are Sam, Frontend Engineer with OPUS framework expertise. "
        f"Focus on technical feasibility and frontend implementation using OPUS structure. "
        f"{base_prompt} Suggest minimal tech stacks. Challenge complex features. "
        f"OPUS FRAMEWORK ROLES:\n"
        f"- OUTCOME: Ensure technical solutions support user outcomes\n"
        f"- SCENARIO: Validate technical feasibility for user scenarios\n"
        f"- Suggest frontend technologies and frameworks\n"
        f"- Ensure components are technically implementable\n"
        f"Use @Max, @Alex, @BackendEngineer, @Jamie to mention others."
    ),
    llm_config=primary_config,
)
```

### 4. NEW: Backend Engineer - OPUS Data/API Focus

```python
backend_engineer = AssistantAgent(
    name="BackendEngineer",
    system_message=(
        f"You are Backend Engineer with OPUS framework expertise. "
        f"Focus on backend architecture, data models, and API design using OPUS structure. "
        f"{base_prompt} Design scalable backend solutions. Challenge data complexity. "
        f"OPUS FRAMEWORK ROLES:\n"
        f"- OUTCOME: Ensure backend supports user outcomes efficiently\n"
        f"- PURPOSE: Design APIs and data models that serve business purpose\n"
        f"- USER: Structure data to support user needs and scenarios\n"
        f"- SCENARIO: Design APIs for specific user scenarios and use cases\n"
        f"Key Responsibilities:\n"
        f"- Design database schemas and data models\n"
        f"- Define API endpoints and data flows\n"
        f"- Ensure scalability and performance\n"
        f"- Consider security and data privacy\n"
        f"Use @Max, @Alex, @Sam, @Jamie to mention others."
    ),
    llm_config=primary_config,
)
```

### 5. Jamie (QA Engineer) - OPUS Testing/Edge Cases

```python
jamie_agent = AssistantAgent(
    name="Jamie",
    system_message=(
        f"You are Jamie, QA Engineer with OPUS framework expertise. "
        f"Focus on quality assurance and testing using OPUS structure. "
        f"{base_prompt} Challenge assumptions. Advocate for robust solutions. "
        f"OPUS FRAMEWORK ROLES:\n"
        f"- OUTCOME: Test if features achieve intended user outcomes\n"
        f"- SCENARIO: Validate features work in all user scenarios\n"
        f"- USER: Ensure features work for all target users\n"
        f"- PURPOSE: Verify features serve their intended purpose\n"
        f"Key Responsibilities:\n"
        f"- Design test cases based on OPUS elements\n"
        f"- Identify edge cases and failure scenarios\n"
        f"- Ensure accessibility and usability\n"
        f"- Validate data integrity and security\n"
        f"Use @Max, @Alex, @Sam, @BackendEngineer to mention others."
    ),
    llm_config=primary_config,
)
```

### 6. Customer Advocate - OPUS User Value Focus

```python
customer_advocate = AssistantAgent(
    name="CustomerAdvocate",
    system_message=(
        f"You are Customer Advocate with OPUS framework expertise. "
        f"Focus on user needs, pain points, and business value using OPUS structure. "
        f"{base_prompt} Challenge features that don't solve real problems. "
        f"OPUS FRAMEWORK ROLES:\n"
        f"- OUTCOME: Advocate for user outcomes and value delivery\n"
        f"- USER: Represent user needs and pain points\n"
        f"- SCENARIO: Ensure features work in real user scenarios\n"
        f"- PURPOSE: Validate business value and user benefit\n"
        f"Key Responsibilities:\n"
        f"- Represent user perspective in discussions\n"
        f"- Challenge non-essential features\n"
        f"- Ensure user value and satisfaction\n"
        f"- Validate user scenarios and use cases\n"
        f"Use @Max, @Alex, @Sam, @BackendEngineer, @Jamie to mention others."
    ),
    llm_config=secondary_config,
)
```

## 🎯 OPUS Discussion Framework

### Structured OPUS Discussions

Implement a structured approach to OPUS-based discussions:

```python
# OPUS Discussion Phases
OPUS_PHASES = {
    "phase_1": {
        "name": "Outcome Analysis",
        "focus": "What do users want to achieve?",
        "agents": ["Max", "CustomerAdvocate"],
        "output": "User outcomes and success metrics"
    },
    "phase_2": {
        "name": "Purpose Definition", 
        "focus": "Why does this feature exist?",
        "agents": ["Max", "BackendEngineer"],
        "output": "Business purpose and value proposition"
    },
    "phase_3": {
        "name": "User Identification",
        "focus": "Who is this feature for?",
        "agents": ["Alex", "CustomerAdvocate"],
        "output": "User personas and characteristics"
    },
    "phase_4": {
        "name": "Scenario Mapping",
        "focus": "When/how is this feature used?",
        "agents": ["Alex", "Sam", "BackendEngineer"],
        "output": "User scenarios and use cases"
    },
    "phase_5": {
        "name": "OPUS Integration",
        "focus": "How do all elements work together?",
        "agents": ["Max", "Alex", "Sam", "BackendEngineer", "Jamie"],
        "output": "Integrated OPUS framework"
    },
    "phase_6": {
        "name": "Consensus Building",
        "focus": "Agreement on OPUS structure",
        "agents": ["Max", "Alex", "Sam", "BackendEngineer", "Jamie", "CustomerAdvocate"],
        "output": "Final consensus and OPUS blocks"
    }
}
```

### OPUS Debate Mechanics

Implement structured debate mechanics with OPUS references:

```python
# OPUS Debate Structure
OPUS_DEBATE_RULES = {
    "outcome_debate": {
        "trigger": "When discussing user outcomes",
        "format": "Reference specific OPUS outcome elements",
        "scoring": "Rate proposals on outcome alignment (1-10)"
    },
    "purpose_debate": {
        "trigger": "When discussing feature purpose", 
        "format": "Reference specific OPUS purpose elements",
        "scoring": "Rate proposals on purpose alignment (1-10)"
    },
    "user_debate": {
        "trigger": "When discussing user needs",
        "format": "Reference specific OPUS user elements", 
        "scoring": "Rate proposals on user alignment (1-10)"
    },
    "scenario_debate": {
        "trigger": "When discussing use scenarios",
        "format": "Reference specific OPUS scenario elements",
        "scoring": "Rate proposals on scenario alignment (1-10)"
    }
}
```

## 📊 OPUS Output Format

### Simple OPUS Block Format

Transform the output to use simple, readable OPUS blocks for each screen, component, and function:

```
# APP: [App Name]
O: [What users want to achieve with this app]
P: [Why this app exists and its business value]
U: [Who this app is for and their characteristics]
S: [When and how this app is used]

# SCREEN: [Screen Name]
O: [What users want to achieve on this screen]
P: [Why this screen exists]
U: [Who this screen is for]
S: [When/how this screen is used]

# COMPONENT: [Component Name]
O: [What users want to achieve with this component]
P: [Why this component exists]
U: [Who this component is for]
S: [When/how this component is used]

# FUNCTION: [Function Name]
O: [What users want to achieve with this function]
P: [Why this function exists]
U: [Who this function is for]
S: [When/how this function is used]
```

### Example OPUS Output

```
# APP: Fitness Tracking App
O: Users want to track their workouts, monitor progress, and achieve fitness goals
P: Help users maintain fitness routines and achieve health objectives
U: Fitness enthusiasts, gym-goers, health-conscious individuals
S: Daily workout tracking, progress monitoring, goal setting

# SCREEN: Login/Sign Up Page
O: Users want to securely access their account and start using the app
P: Provide secure authentication and user account access
U: New users creating accounts, existing users logging in
S: User opens app for first time, user returns to app, user switches devices

# COMPONENT: Google OAuth Button
O: Users want to quickly sign in using their existing Google account
P: Reduce friction in authentication process and increase conversion
U: Users with Google accounts who prefer social login
S: User clicks "Sign in with Google" during registration or login flow

# COMPONENT: Login Form Inputs
O: Users want to enter their credentials to access their account
P: Collect and validate user authentication credentials
U: Users with email/password accounts
S: User enters email and password to log in

# COMPONENT: Login Form Submit Button
O: Users want to submit their credentials and access their account
P: Process authentication request and redirect to main app
U: Users with valid credentials ready to log in
S: User clicks submit after entering email and password

# SCREEN: Dashboard
O: Users want to see their fitness overview and quick access to key features
P: Provide central hub for fitness tracking and app navigation
U: Authenticated users with fitness data
S: User opens app after login, user returns to app

# COMPONENT: Workout Summary Card
O: Users want to see their recent workout activity and progress
P: Display key fitness metrics and encourage continued engagement
U: Active fitness users tracking workouts
S: User views dashboard, user checks progress

# FUNCTION: Save Workout
O: Users want to record their completed workout for tracking
P: Store workout data for progress monitoring and analytics
U: Users who have completed a workout
S: User finishes workout and wants to save it
```

## 🔄 Implementation Phases

### Phase 1: Core OPUS Integration (Weeks 1-2)

**Goals:**
- Implement basic OPUS framework in agent prompts
- Add OPUS-structured discussions
- Create OPUS-based debate mechanics

**Deliverables:**
- Updated agent system messages with OPUS focus
- OPUS discussion framework implementation
- Basic OPUS block output format

**Tasks:**
1. Update `agents.py` with OPUS-enhanced agent definitions
2. Implement OPUS discussion phases in `conversation_state.py`
3. Add OPUS debate mechanics in `consensus.py`
4. Update `main.py` to support OPUS-structured conversations

### Phase 2: Backend Engineer Integration (Weeks 3-4)

**Goals:**
- Add backend engineer agent
- Implement backend architecture considerations
- Integrate backend perspective into OPUS discussions

**Deliverables:**
- New backend engineer agent
- Backend architecture considerations in OPUS framework
- Enhanced OPUS blocks with backend elements

**Tasks:**
1. Create backend engineer agent in `agents.py`
2. Add backend architecture to OPUS framework
3. Update output format to include backend OPUS blocks
4. Integrate backend perspective into discussions

### Phase 3: Enhanced Output & Integration (Weeks 5-6)

**Goals:**
- Transform output to OPUS block format
- Implement Cursor-compatible OPUS output
- Add OPUS-based code generation prompts

**Deliverables:**
- OPUS block-structured output
- Cursor integration with OPUS blocks
- OPUS-based code generation capabilities

**Tasks:**
1. Update output format to use OPUS blocks
2. Transform conversation results to OPUS block format
3. Create Cursor integration with OPUS blocks
4. Implement OPUS-based code generation

### Phase 4: Optimization & Testing (Weeks 7-8)

**Goals:**
- Optimize OPUS implementation
- Test OPUS framework effectiveness
- Validate Cursor integration

**Deliverables:**
- Optimized OPUS implementation
- Comprehensive testing results
- Validated Cursor integration

**Tasks:**
1. Optimize OPUS discussion efficiency
2. Test OPUS framework with various scenarios
3. Validate Cursor integration with OPUS blocks
4. Document OPUS implementation results

## 🎯 Key Implementation Details

### OPUS Framework Integration

```python
# OPUS Framework Integration in agents.py
def create_opus_enhanced_agents(task_id: str, conversation_state: ConversationState) -> List[AssistantAgent]:
    """
    Create OPUS-enhanced agents with structured framework integration.
    """
    # OPUS framework base prompt
    opus_base_prompt = (
        f"Use OPUS framework for all discussions:\n"
        f"- OUTCOME (O): What users want to achieve\n"
        f"- PURPOSE (P): Why features exist\n" 
        f"- USER (U): Who features are for\n"
        f"- SCENARIO (S): When/how features are used\n"
        f"Reference OPUS elements explicitly in discussions and debates."
    )
    
    # Enhanced base prompt with OPUS integration
    enhanced_base_prompt = f"{base_prompt} {opus_base_prompt}"
    
    # Create OPUS-enhanced agents...
```

### OPUS Discussion Structure

```python
# OPUS Discussion Structure in conversation_state.py
class OPUSConversationState(ConversationState):
    """
    Enhanced conversation state with OPUS framework tracking.
    """
    
    def __init__(self, max_rounds: int = 20):
        super().__init__(max_rounds)
        self.opus_phases = {
            "outcome_analysis": False,
            "purpose_definition": False, 
            "user_identification": False,
            "scenario_mapping": False,
            "opus_integration": False,
            "consensus_building": False
        }
        self.opus_elements = {
            "outcome": None,
            "purpose": None,
            "user": None,
            "scenario": None
        }
```

### OPUS Output Generation

```python
# OPUS Output Generation in utils.py
def generate_opus_blocks(conversation_result: Dict[str, Any]) -> str:
    """
    Generate OPUS block format from conversation result.
    """
    opus_blocks = []
    
    # Extract OPUS elements from conversation
    app_opus = extract_app_opus(conversation_result)
    screen_opus_blocks = extract_screen_opus_blocks(conversation_result)
    component_opus_blocks = extract_component_opus_blocks(conversation_result)
    function_opus_blocks = extract_function_opus_blocks(conversation_result)
    
    # Generate OPUS blocks
    opus_blocks.append(f"# APP: {app_opus['name']}")
    opus_blocks.append(f"O: {app_opus['outcome']}")
    opus_blocks.append(f"P: {app_opus['purpose']}")
    opus_blocks.append(f"U: {app_opus['user']}")
    opus_blocks.append(f"S: {app_opus['scenario']}")
    opus_blocks.append("")
    
    # Add screen OPUS blocks
    for screen in screen_opus_blocks:
        opus_blocks.append(f"# SCREEN: {screen['name']}")
        opus_blocks.append(f"O: {screen['outcome']}")
        opus_blocks.append(f"P: {screen['purpose']}")
        opus_blocks.append(f"U: {screen['user']}")
        opus_blocks.append(f"S: {screen['scenario']}")
        opus_blocks.append("")
    
    # Add component OPUS blocks
    for component in component_opus_blocks:
        opus_blocks.append(f"# COMPONENT: {component['name']}")
        opus_blocks.append(f"O: {component['outcome']}")
        opus_blocks.append(f"P: {component['purpose']}")
        opus_blocks.append(f"U: {component['user']}")
        opus_blocks.append(f"S: {component['scenario']}")
        opus_blocks.append("")
    
    # Add function OPUS blocks
    for function in function_opus_blocks:
        opus_blocks.append(f"# FUNCTION: {function['name']}")
        opus_blocks.append(f"O: {function['outcome']}")
        opus_blocks.append(f"P: {function['purpose']}")
        opus_blocks.append(f"U: {function['user']}")
        opus_blocks.append(f"S: {function['scenario']}")
        opus_blocks.append("")
    
    return "\n".join(opus_blocks)
```

## 🎯 Expected Benefits

### Enhanced Design Quality
- **Structured Approach**: OPUS framework provides systematic design thinking
- **User-Focused**: Explicit focus on user outcomes and scenarios
- **Purpose-Driven**: Clear understanding of why features exist
- **Scenario-Based**: Design based on real user scenarios

### Improved Collaboration
- **Structured Debates**: OPUS-based debate mechanics
- **Clear Roles**: Each agent has specific OPUS focus areas
- **Consensus Building**: Systematic approach to agreement
- **Backend Integration**: Full-stack perspective with backend engineer

### Better Code Generation
- **Cursor Integration**: OPUS block output for Cursor
- **Actionable Design**: Clear outcomes, purposes, users, and scenarios
- **Technical Context**: Backend architecture considerations
- **Iterative Building**: Support for iterative development

## 🚀 Next Steps

1. **Start Phase 1**: Implement basic OPUS framework in agent prompts
2. **Add Backend Engineer**: Create new backend engineer agent
3. **Test OPUS Integration**: Validate OPUS framework with simple scenarios
4. **Iterate and Optimize**: Refine OPUS implementation based on testing
5. **Scale Up**: Add more complex OPUS features over time

## 📚 References

- [OPUS Framework Documentation](https://example.com/opus-framework)
- [AutoGen Multi-Agent Systems](https://microsoft.github.io/autogen/)
- [Cursor Integration Guide](https://cursor.sh/docs)

---

**Document Version**: 1.0  
**Last Updated**: January 2024  
**Status**: Implementation Plan  
**Next Review**: After Phase 1 completion 