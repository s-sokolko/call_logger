# app/utils/helpers.py
"""Helper utility functions."""
from typing import Dict, Any, Union, List


def get_param(params: Dict[str, Any], name: str, default: Any = "unknown") -> str:
    """
    Extract a parameter from query parameters.
    
    Handles both single values and lists of values, returning the first value in a list.
    
    Args:
        params: Dictionary of query parameters
        name: Parameter name to extract
        default: Default value if parameter is not found
        
    Returns:
        Parameter value as a string
    """
    value = params.get(name, default)
    if isinstance(value, list) and value:
        return value[0]
    return value


def determine_phone_type(params: Dict[str, Any]) -> str:
    """
    Determine the phone type based on query parameters.
    
    Args:
        params: Dictionary of query parameters
        
    Returns:
        Phone type: "yealink", "cisco", or "unknown"
    """
    if "phone" in params:
        return "yealink"
    elif "mac" in params:
        return "cisco"
    else:
        return "unknown"

