from fastapi import (
    APIRouter, Depends, Request,
    HTTPException, status
)
from pydantic import BaseModel 
from openai import RateLimitError, APIError

from ors.security.auth import Client, get_current_client
from ors.llm.llm_loader import LLMFactory
from ors.llm.inference import invoke_llm
from ors.llm.orouter_inv import get_free_models 
from ors.utils.logging_utils import get_logger, set_log_level, DEBUG
from ors import constants

log = get_logger(__name__)
#set_log_level(DEBUG)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

class ChatRequest(BaseModel):
    free_models: bool = True
    model_id: str = constants.default_model
    prompt_type: str = "basic"
    user_prompt: str
    conversation_summary: str | None = None
    extra_system_instructions: str | None = None

class SummarizeRequest(BaseModel):
    free_models: bool = True
    model_id: str = constants.default_model
    text: str

@router.post("/completions")
async def chat(
    request: Request, 
    body: ChatRequest, 
    current_client: Client = Depends(get_current_client)):
    
    log.debug(f"[Chat] Received request for model {body.model_id} with prompt: {body.user_prompt}")
    try:
        factory = request.app.state.llm_factory
        orouter_llm = factory.get_llm(body.model_id, body.free_models)
        prompt_kwargs = {
            "user_prompt": body.user_prompt,
            "conversation_summary": body.conversation_summary or "",
            "extra_system_instructions": body.extra_system_instructions or "",
        }
        response = invoke_llm(orouter_llm, body.prompt_type, prompt_kwargs)
        #response = llm.invoke(user_prompt)
        # already string
        return response
    except RateLimitError as e:
        log.error(f"[RateLimitError] Encountered for {orouter_llm.model_name}. Details: {e}")
        response_message = f"The model {orouter_llm.model_name} is temporarily rate-limited. Please try again later."
        try:
            # Extract upstream message: new client exposes details via e.response or e.body
            err = getattr(e, "response", None) or getattr(e, "body", None)
            if isinstance(err, dict):
                raw = (
                    err.get("error", {})
                       .get("metadata", {})
                       .get("raw")
                )
                if raw:
                    response_message += f" Details: {raw}"
        except Exception:
            pass
        # Convert to FastAPI-friendly error
        raise HTTPException(status_code=429, detail=response_message) from e
    
    except APIError as e:
        status_code = getattr(e, "status_code", 502)
        error_msg = str(e).lower()
        
        # OpenRouter often wraps provider 429 rate limits into a 502 or 400 error.
        if "rate limit" in error_msg or "429" in error_msg:
            log.error(f"[Upstream Rate Limit via APIError] Encountered: {e}")
            raise HTTPException(status_code=429, detail=f"The free model {orouter_llm.model_name} is temporarily rate-limited upstream. Please try again.") from e
            
        log.error(f"[APIError {status_code}] Encountered: {e}")
        # Other OpenAI/OpenRouter errors
        raise HTTPException(status_code=status_code, detail=str(e)) from e
    
@router.post("/summarize")
async def summarize(
    request: Request,
    body: SummarizeRequest,
    current_client: Client = Depends(get_current_client)):

    log.debug(f"[Summarize] Received request for model {body.model_id} with text: {body.text}")
    try:
        factory = request.app.state.llm_factory
        orouter_llm = factory.get_llm(body.model_id, body.free_models)
        prompt_kwargs = {"text": body.text}
        summary = invoke_llm(orouter_llm, prompt_type=constants.TEMPLATE_TYPE_SUMMARIZATION, prompt_kwargs=prompt_kwargs)
        return {"summary": summary}
    except RateLimitError as e:
        log.error(f"[RateLimitError] Encountered for {orouter_llm.model_name}. Details: {e}")
        response_message = f"The model {orouter_llm.model_name} is temporarily rate-limited. Please try again later."
        try:
            # Extract upstream message: new client exposes details via e.response or e.body
            err = getattr(e, "response", None) or getattr(e, "body", None)
            if isinstance(err, dict):
                raw = (
                    err.get("error", {})
                       .get("metadata", {})
                       .get("raw")
                )
                if raw:
                    response_message += f" Details: {raw}"
        except Exception:
            pass
        # Convert to FastAPI-friendly error
        raise HTTPException(status_code=429, detail=response_message) from e
    
    except APIError as e:
        status_code = getattr(e, "status_code", 502)
        error_msg = str(e).lower()
        
        # OpenRouter often wraps provider 429 rate limits into a 502 or 400 error.
        if "rate limit" in error_msg or "429" in error_msg:
            log.error(f"[Upstream Rate Limit via APIError] Encountered: {e}")
            raise HTTPException(status_code=429, detail=f"The free model {orouter_llm.model_name} is temporarily rate-limited upstream. Please try again.") from e
            
        log.error(f"[APIError {status_code}] Encountered: {e}")
        # Other OpenAI/OpenRouter errors
        raise HTTPException(status_code=status_code, detail=str(e)) from e