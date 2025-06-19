import logging
import sys
from typing import Any, Dict, Optional

# Configure log levels to reduce framework's detailed log output
logging.getLogger("autogen_core").setLevel(logging.WARNING)
logging.getLogger("autogen_agentchat").setLevel(logging.WARNING)
logging.getLogger("autogen_core.events").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

def log_request(logger: logging.Logger, route: str, request_data: Dict[str, Any]) -> None:
    """
    Log API request
    
    Args:
        logger (logging.Logger): Logger instance
        route (str): Route path
        request_data (dict): Request data
    """
    logger.info(f"API Request to {route}: {request_data}")

def log_response(logger: logging.Logger, route: str, response_data: Dict[str, Any], 
                status_code: int = 200) -> None:
    """
    Log API response
    
    Args:
        logger (logging.Logger): Logger instance
        route (str): Route path
        response_data (dict): Response data
        status_code (int): HTTP status code
    """
    # Remove potentially large data, keep only structure
    if "data" in response_data and isinstance(response_data["data"], dict):
        # Keep only top-level keys
        data_keys = list(response_data["data"].keys())
        response_summary = {**response_data, "data": f"contains {len(data_keys)} keys: {data_keys}"}
    else:
        response_summary = response_data
        
    logger.info(f"API Response from {route} (status: {status_code}): {response_summary}")

def log_error(logger: logging.Logger, route: str, error: Exception, 
             request_data: Optional[Dict[str, Any]] = None) -> None:
    """
    Log API error
    
    Args:
        logger (logging.Logger): Logger instance
        route (str): Route path
        error (Exception): Error exception
        request_data (dict, optional): Request data
    """
    if request_data:
        logger.error(f"Error in {route} with request {request_data}: {str(error)}", exc_info=True)
    else:
        logger.error(f"Error in {route}: {str(error)}", exc_info=True)