from fastapi import (
    APIRouter, Depends, Request,
    HTTPException, status
)
from pydantic import BaseModel 
from openai import RateLimitError, APIError
from ors.utils.logging_utils import get_logger, set_log_level, DEBUG
from ors.security.auth import Client, get_current_client
from ors import constants

log = get_logger(__name__)
set_log_level(DEBUG)

router = APIRouter(
    prefix="/model",
    tags=["model"],
)

@router.get("/models")
async def get_models(request: Request, free_models: bool = True, 
    current_client: Client = Depends(get_current_client)):
    """
    Get all available models for a repository.
    """
    factory = request.app.state.llm_factory
    return factory.get_models(factory.free_model_repo if free_models else factory.paid_model_repo)

@router.get("/providers")
async def get_providers(request: Request, free_models: bool = True, 
    current_client: Client = Depends(get_current_client)):
    """
    Get all available model providers for a repository.
    """
    factory = request.app.state.llm_factory
    return factory.get_providers(free_models)

@router.get("/{provider}/models")
async def get_models_by_provider(request: Request, provider: str, free_models: bool = True,
     current_client: Client = Depends(get_current_client)):
    """
    Get all available models for a specific model provider.
    """
    try:
        factory = request.app.state.llm_factory
        return factory.get_model_by_provider(provider.lower(), free_models)
    except ValueError as e:
        log.error(f"[Provider Not Found] {provider} not found in model repository.")
        raise HTTPException(status_code=404, detail=str(e)) from e