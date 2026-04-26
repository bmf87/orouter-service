# python -c "from ors.llm.orouter_inv import get_free_models; print(get_free_models())"
import os
from typing import List, Dict, Any
from collections import defaultdict
from openrouter import OpenRouter
from ors import constants
from ors.config.api_config import ModelInfo

def get_models() -> List[Dict[str, Any]]:
    """
    Fetches the list of all available models from OpenRouter.

    Returns:
        List[Dict[str, Any]]: A list of model dictionaries containing 
                              metadata and pricing information.
    """
    or_client = OpenRouter(
        api_key=constants.openrouter_api_key,
        http_referer=constants.app_dns,
        x_open_router_title=constants.app_name,
    )
    
    # Calls GET /models
    models_response = or_client.models.list()
    
    # Safely extract the data payload whether it's wrapped in a dict or object
    if isinstance(models_response, dict):
        return models_response.get("data", [])
    elif hasattr(models_response, "data"):
        return models_response.data
    return models_response

def is_free(model: Dict[str, Any]) -> bool:
    """
    Determines whether a given OpenRouter model is free to use based on its ID or pricing payload.

    Args:
        model (Dict[str, Any]): A dictionary representing an OpenRouter model.

    Returns:
        bool: True if the model is free, False otherwise.
    """
    mid = model.get("id", "")
    pricing = model.get("pricing") or {}
    
    prompt = float(pricing.get("prompt", 0) or 0)
    completion = float(pricing.get("completion", 0) or 0)
    
    return (":free" in mid) or (prompt == 0 and completion == 0)

def get_free_models() -> Dict[str, List[ModelInfo]]:
    """
    Fetches all available models and categorizes them by provider, matching the 
    api_config.py structure to use same model loading logic.

    Returns:
        Dict[str, List[ModelInfo]]: Maps providers to their available free models.
    """
    models = get_models()
    
    free_models_repo = defaultdict(list)
    for m in models:
        # Guarantee it's parsed as a dict internally
        model_dict = getattr(m, "model_dump", lambda: m)() if not isinstance(m, dict) else m
        if is_free(model_dict):
            model_id = model_dict.get("id", "")
            context = model_dict.get("context_length")
            
            provider = model_id.split('/')[0] if '/' in model_id else "unknown"
            
            model_info = ModelInfo(
                id=model_id,
                tier="free",
                context=context
            )
            free_models_repo[provider].append(model_info)
            
    return dict(free_models_repo)

