import requests

from .logging import logger


def validate_api_key(api_key: str) -> bool:
    """
    Validate OpenAI API key format.

    Args:
        api_key (str): API key to validate

    Returns:
        bool: True if the key format is valid
    """
    if not api_key:
        return False

    # Check if key follows OpenAI format
    # This is a simple format check, not a real validation
    return bool(api_key.startswith(("sk-", "org-")))


def sanitize_parameters(parameters: dict) -> dict:
    """
    Sanitize parameters to prevent injection attacks.

    Args:
        parameters (dict): Parameters to sanitize

    Returns:
        dict: Sanitized parameters
    """
    sanitized = {}

    for key, value in parameters.items():
        if isinstance(value, str):
            # Basic sanitization for strings
            sanitized[key] = value.replace("<script>", "").replace("</script>", "")
        elif isinstance(value, dict | list):
            # Recursively sanitize nested structures
            sanitized[key] = (
                sanitize_parameters(value)
                if isinstance(value, dict)
                else [sanitize_parameters(item) if isinstance(item, dict) else item for item in value]
            )
        else:
            # Keep other types as is
            sanitized[key] = value

    return sanitized


def validate_api_key_with_openai(api_key: str) -> bool:
    """
    Validate OpenAI API key by making a test request.

    Args:
        api_key (str): OpenAI API key

    Returns:
        bool: True if the key is valid
    """
    if not api_key:
        return False

    try:
        # Make a minimal request to check key validity
        response = requests.get(
            "https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10
        )

        if response.status_code == 200:
            logger.info("OpenAI API key is valid")
            return True
        else:
            logger.error(f"OpenAI API key validation failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        logger.error("OpenAI API key validation error: RequestException")
        return False
