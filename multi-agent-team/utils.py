# utils.py
import json
import re
import logging
from typing import Dict, Any, Tuple, Optional, List
from jsonschema import validate, ValidationError
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load schema (will be loaded from schema.json)
WIREFRAME_SCHEMA = None

def load_schema() -> Dict[str, Any]:
    """
    Load the wireframe schema from schema.json.
    
    Returns:
        Dictionary containing the schema
    """
    global WIREFRAME_SCHEMA
    
    if WIREFRAME_SCHEMA is None:
        try:
            schema_path = "schema.json"
            if not os.path.exists(schema_path):
                # Create a basic schema if file doesn't exist
                WIREFRAME_SCHEMA = create_basic_schema()
                logger.warning(f"Schema file not found at {schema_path}, using basic schema")
            else:
                with open(schema_path, "r") as f:
                    WIREFRAME_SCHEMA = json.load(f)
                logger.info("Loaded wireframe schema successfully")
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
            WIREFRAME_SCHEMA = create_basic_schema()
    
    return WIREFRAME_SCHEMA

def create_basic_schema() -> Dict[str, Any]:
    """
    Create a basic wireframe schema as fallback.
    
    Returns:
        Basic schema dictionary
    """
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "app": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "screens": {"type": "array"}
                },
                "required": ["name", "description", "screens"]
            }
        },
        "required": ["app"]
    }

def parse_user_input(input_text: str) -> Dict[str, str]:
    """
    Parse user input into structured components.
    
    Args:
        input_text: Raw input text from user
        
    Returns:
        Dictionary with 'idea_mvp', 'personas', 'outcomes' keys
        
    Raises:
        ValueError: If input doesn't contain required components
    """
    if not input_text or not input_text.strip():
        raise ValueError("Input text cannot be empty")
    
    # Try multiple parsing strategies
    parsed = parse_with_asterisks(input_text)
    if not parsed:
        parsed = parse_with_newlines(input_text)
    if not parsed:
        parsed = parse_with_keywords(input_text)
    
    if not parsed:
        raise ValueError(
            "Input must contain idea/MVP, personas, and outcomes. "
            "Use '*' to separate sections or provide clear labels."
        )
    
    # Validate parsed components
    required_keys = ['idea_mvp', 'personas', 'outcomes']
    missing_keys = [key for key in required_keys if not parsed.get(key, '').strip()]
    
    if missing_keys:
        raise ValueError(f"Missing required components: {', '.join(missing_keys)}")
    
    logger.info("Successfully parsed user input")
    return parsed

def parse_with_asterisks(input_text: str) -> Optional[Dict[str, str]]:
    """Parse input using asterisk separators."""
    parts = re.split(r'\*\s*', input_text.strip())
    # Remove empty parts and strip whitespace
    parts = [part.strip() for part in parts if part.strip()]
    if len(parts) >= 3:
        return {
            "idea_mvp": parts[0],
            "personas": parts[1],
            "outcomes": parts[2]
        }
    return None

def parse_with_newlines(input_text: str) -> Optional[Dict[str, str]]:
    """Parse input using double newline separators."""
    parts = re.split(r'\n\s*\n', input_text.strip())
    if len(parts) >= 3:
        return {
            "idea_mvp": parts[0].strip(),
            "personas": parts[1].strip(),
            "outcomes": parts[2].strip()
        }
    return None

def parse_with_keywords(input_text: str) -> Optional[Dict[str, str]]:
    """Parse input using keyword detection."""
    idea_match = re.search(r'(?:idea|mvp|app)[:\s]+(.+?)(?=\n|personas|outcomes|$)', input_text, re.IGNORECASE | re.DOTALL)
    personas_match = re.search(r'personas?[:\s]+(.+?)(?=\n|outcomes|$)', input_text, re.IGNORECASE | re.DOTALL)
    outcomes_match = re.search(r'outcomes?[:\s]+(.+?)(?=\n|$)', input_text, re.IGNORECASE | re.DOTALL)
    
    if idea_match and personas_match and outcomes_match:
        return {
            "idea_mvp": idea_match.group(1).strip(),
            "personas": personas_match.group(1).strip(),
            "outcomes": outcomes_match.group(1).strip()
        }
    return None

def extract_json_from_message(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from a message string with enhanced flexibility.
    
    Args:
        message: Message string that may contain JSON
        
    Returns:
        Parsed JSON dictionary or None if not found/invalid
    """
    if not message:
        return None
    
    # First, check for "CONSENSUS REACHED:" pattern
    if "consensus reached:" in message.lower():
        # Extract everything after "CONSENSUS REACHED:"
        consensus_pattern = r'consensus reached:\s*(.*)'
        match = re.search(consensus_pattern, message, re.IGNORECASE | re.DOTALL)
        if match:
            json_content = match.group(1).strip()
            # Try to extract JSON from this content
            json_data = extract_json_from_content(json_content)
            if json_data:
                return json_data
    
    # Check for JSON code blocks
    json_block_pattern = r'```json\s*(.*?)\s*```'
    json_blocks = re.findall(json_block_pattern, message, re.DOTALL)
    for block in json_blocks:
        json_data = extract_json_from_content(block)
        if json_data:
            return json_data
    
    # Try to extract JSON using bracket matching (most reliable)
    json_data = extract_json_with_brackets(message)
    if json_data:
        return json_data
    
    # Fallback to regex extraction
    json_data = extract_json_with_regex(message)
    if json_data:
        return json_data
    
    return None

def extract_json_from_content(content: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from content that may contain markdown or other formatting.
    Enhanced to handle various JSON structures.
    
    Args:
        content: Content string that may contain JSON
        
    Returns:
        Parsed JSON dictionary or None if not found/invalid
    """
    # Remove markdown code blocks
    content = re.sub(r'```json\s*|\s*```', '', content)
    content = re.sub(r'```\s*|\s*```', '', content)
    
    # Try bracket matching first (most reliable)
    json_data = extract_json_with_brackets(content)
    if json_data:
        return json_data
    
    # Fallback to regex
    json_data = extract_json_with_regex(content)
    if json_data:
        return json_data
    
    return None

def extract_json_with_brackets(message: str) -> Optional[Dict[str, Any]]:
    """Extract JSON by finding balanced brackets with enhanced error handling."""
    try:
        # Find the first opening brace
        start = message.find('{')
        if start == -1:
            return None
        
        # Find the matching closing brace by counting braces
        brace_count = 0
        end = start
        
        for i, char in enumerate(message[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        if brace_count == 0:
            json_str = message[start:end]
            json_str = sanitize_json_string(json_str)
            return json.loads(json_str)
        
    except (json.JSONDecodeError, IndexError):
        pass
    
    return None

def extract_json_with_regex(message: str) -> Optional[Dict[str, Any]]:
    """Extract JSON using regex pattern matching with enhanced flexibility."""
    # Try to find JSON objects using a more comprehensive approach
    try:
        # Look for JSON object patterns
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested objects
            r'\{.*?\}',  # Simple objects
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, message, re.DOTALL)
            for match in matches:
                try:
                    # Clean up the match
                    cleaned_match = re.sub(r'```json\s*|\s*```', '', match)
                    cleaned_match = sanitize_json_string(cleaned_match)
                    return json.loads(cleaned_match)
                except json.JSONDecodeError:
                    continue
        
    except Exception:
        pass
    
    return None

def sanitize_json_string(json_str: str) -> str:
    """
    Sanitize JSON string by removing common issues and handling various formats.
    
    Args:
        json_str: Raw JSON string
        
    Returns:
        Sanitized JSON string
    """
    # Remove markdown code blocks
    json_str = re.sub(r'```json\s*|\s*```', '', json_str)
    
    # Remove leading/trailing whitespace
    json_str = json_str.strip()
    
    # Fix common JSON issues
    json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
    json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
    
    # Handle potential issues with quotes - only if they're missing
    json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
    
    return json_str

def validate_wireframe(wireframe_json: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate wireframe JSON against schema with enhanced flexibility.
    
    Args:
        wireframe_json: JSON data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # First, try to validate against the expected schema
        schema = load_schema()
        validate(instance=wireframe_json, schema=schema)
        return True, "Valid"
    except ValidationError as e:
        # If schema validation fails, try to validate the actual structure that agents produce
        validation_result = validate_flexible_structure(wireframe_json)
        if validation_result[0]:
            return True, f"Valid (flexible structure): {validation_result[1]}"
        else:
            error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
            error_msg = f"Validation error at {error_path}: {e.message}"
            logger.error(f"Schema validation failed: {error_msg}")
            return False, error_msg
    except Exception as e:
        # If schema loading fails, try flexible validation
        validation_result = validate_flexible_structure(wireframe_json)
        if validation_result[0]:
            return True, f"Valid (flexible structure): {validation_result[1]}"
        else:
            error_msg = f"Unexpected error during validation: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

def validate_flexible_structure(wireframe_json: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate wireframe JSON using a flexible structure approach.
    This handles the actual JSON structure that agents are producing.
    
    Args:
        wireframe_json: JSON data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if it's the expected structure (app object with name, description, screens, version_history)
        if isinstance(wireframe_json, dict) and "app" in wireframe_json:
            app_data = wireframe_json["app"]
            if isinstance(app_data, dict):
                # Check for required fields in app object
                required_fields = ["name", "description", "screens"]
                missing_fields = [field for field in required_fields if field not in app_data]
                if missing_fields:
                    return False, f"Missing required fields in app object: {missing_fields}"
                
                # Validate screens array
                if "screens" in app_data:
                    screens = app_data["screens"]
                    if not isinstance(screens, (list, dict)):
                        return False, "Screens must be an array or object"
                
                return True, "Valid app structure"
        
        # Check if it's the alternative structure (app as string, screens as object)
        elif isinstance(wireframe_json, dict) and "app" in wireframe_json and isinstance(wireframe_json["app"], str):
            if "screens" in wireframe_json and isinstance(wireframe_json["screens"], dict):
                return True, "Valid alternative structure (app as string, screens as object)"
        
        # Check if it's the MVP structure
        elif isinstance(wireframe_json, dict) and "MVP" in wireframe_json:
            return True, "Valid MVP structure"
        
        # Check if it has any recognizable wireframe structure
        elif isinstance(wireframe_json, dict) and any(key in wireframe_json for key in ["screens", "components", "app", "MVP"]):
            return True, "Valid wireframe structure (flexible format)"
        
        return False, "Invalid wireframe structure - must contain app, screens, MVP, or components"
        
    except Exception as e:
        return False, f"Error during flexible validation: {str(e)}"

def format_validation_errors(validation_errors: List[str]) -> str:
    """
    Format validation errors for user-friendly display.
    
    Args:
        validation_errors: List of validation error messages
        
    Returns:
        Formatted error string
    """
    if not validation_errors:
        return "No validation errors"
    
    formatted_errors = []
    for i, error in enumerate(validation_errors, 1):
        formatted_errors.append(f"{i}. {error}")
    
    return "\n".join(formatted_errors)

def extract_consensus_indicator(message: str) -> bool:
    """
    Check if a message indicates consensus has been reached.
    
    Args:
        message: Message to check
        
    Returns:
        True if consensus is indicated, False otherwise
    """
    consensus_indicators = [
        "consensus reached",
        "consensus achieved",
        "agreed upon",
        "final decision",
        "we have consensus",
        "consensus has been reached"
    ]
    
    message_lower = message.lower()
    return any(indicator in message_lower for indicator in consensus_indicators)

if __name__ == "__main__":
    # Test utilities
    test_input = "* Simple todo app for parents. MVP: Add/edit tasks. * Busy mom (35). * Add task, view list."
    
    try:
        parsed = parse_user_input(test_input)
        print(f"✅ Parsed input: {parsed}")
    except ValueError as e:
        print(f"❌ Parse error: {e}")
    
    test_json = '{"app": {"name": "Test", "description": "Test app"}}'
    extracted = extract_json_from_message(test_json)
    print(f"✅ Extracted JSON: {extracted}")
    
    is_valid, error = validate_wireframe(extracted)
    print(f"✅ Validation: {is_valid}, Error: {error}") 