# config.py
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Only raise error if we're not in testing mode
if not OPENROUTER_API_KEY and not os.getenv("TESTING"):
    raise ValueError("OPENROUTER_API_KEY not found in environment variables. Please set it in your .env file.")

# Model configurations with fallbacks
MODEL_CONFIGS = {
    "primary": "openai/gpt-4o-mini",
    "secondary": "anthropic/claude-3.5-sonnet",
    "fallback": "openai/gpt-3.5-turbo"
}

# Rate limiting and timeout configurations

# Get max rounds from environment variable, default to 25
MAX_ROUNDS = int(os.getenv("MAX_ROUNDS", "25"))
RATE_LIMITS = {
    "requests_per_minute": 60,
    "max_tokens_per_request": 4000,
    "timeout_seconds": 30
}

def get_max_rounds() -> int:
    """
    Get the maximum number of rounds for conversations.
    
    Returns:
        Maximum number of rounds as an integer
    """
    return MAX_ROUNDS

def get_config(model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get OpenRouter configuration for a specific model.
    
    Args:
        model_name: Name of the model to use. If None, uses primary model.
    
    Returns:
        Dictionary containing the model configuration
    """
    if model_name is None:
        model_name = MODEL_CONFIGS["primary"]
    
    config = {
        "model": model_name,
        "base_url": "https://openrouter.ai/api/v1",
        "api_type": "openai",
        "timeout": RATE_LIMITS["timeout_seconds"],
        "max_tokens": RATE_LIMITS["max_tokens_per_request"]
    }
    
    # Only add API key if it exists
    if OPENROUTER_API_KEY:
        config["api_key"] = OPENROUTER_API_KEY
    
    return config

def get_fallback_config() -> Dict[str, Any]:
    """
    Get fallback model configuration for error recovery.
    
    Returns:
        Dictionary containing the fallback model configuration
    """
    return get_config(MODEL_CONFIGS["fallback"])

def validate_config() -> bool:
    """
    Validate that all required configuration is present.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        # For testing, we don't require API key
        if os.getenv("TESTING"):
            return True
        
        if not OPENROUTER_API_KEY:
            return False
        
        # Test configuration by creating a config object
        test_config = get_config()
        required_keys = ["model", "base_url", "api_type"]
        
        return all(key in test_config for key in required_keys)
    
    except Exception:
        return False

if __name__ == "__main__":
    # Test configuration
    if validate_config():
        print("✅ Configuration is valid")
        print(f"Primary model: {MODEL_CONFIGS['primary']}")
        print(f"Secondary model: {MODEL_CONFIGS['secondary']}")
        print(f"Fallback model: {MODEL_CONFIGS['fallback']}")
    else:
        print("❌ Configuration is invalid")
        exit(1) 