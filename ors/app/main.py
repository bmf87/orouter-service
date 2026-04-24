from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from openai import RateLimitError, APIError 
from ors.llm.llm_loader import LLMFactory
from ors.llm.orouter_inv import get_free_models 
from ors.utils.logging_utils import get_logger, set_log_level, DEBUG
from ors.security.auth import (
    Token, ClientCredentials, Client, authenticate_client,
    create_access_token, get_current_client,
)
from ors import constants

log = get_logger(__name__)
set_log_level(DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(f"[Startup] {app.title} loading free models...")
    
    # app.state: Starlette's custom State object (not a plain dict. 
    # Just assign attributes natively.
    app.state.free_models = []
    app.state.llm_factory = None
    
    app.state.free_models = get_free_models()
    log.info(f"[Startup] {app.title} loaded {len(app.state.free_models)} free models.")
    log.info(f"[Startup] {app.title}\Models loaded:\n {app.state.free_models}")
    app.state.llm_factory = LLMFactory(dynamic_free_model_repo=app.state.free_models)
    
    yield
    log.info(f"[Shutdown] {app.title} shutting down...")    
    app.state.free_models = []

app = FastAPI(title=constants.app_name, lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"} 

@app.get("/models")
def get_models(free_models: bool = True, 
    current_client: Client = Depends(get_current_client)):
    """
    Get all available models for a repository.
    """
    factory = app.state.llm_factory
    return factory.get_models(factory.free_model_repo if free_models else factory.paid_model_repo)

@app.get("/providers")
def get_providers(free_models: bool = True, 
    current_client: Client = Depends(get_current_client)):
    """
    Get all available model providers for a repository.
    """
    factory = app.state.llm_factory
    return factory.get_providers(free_models)

@app.get("/models/{provider}")
def get_models_by_provider(provider: str, free_models: bool = True,
     current_client: Client = Depends(get_current_client)):
    """
    Get all available models for a specific model provider.
    """
    try:
        factory = app.state.llm_factory
        return factory.get_model_by_provider(provider.lower(), free_models)
    except ValueError as e:
        log.error(f"[Provider Not Found] {provider} not found in model repository.")
        raise HTTPException(status_code=404, detail=str(e)) from e

@app.post("/chat")
def chat(user_prompt: str, model_id: str = constants.default_model, free_models: bool = True, 
    current_client: Client = Depends(get_current_client)):
    
    log.debug(f"[Chat] Received request for model {model_id} with prompt: {user_prompt}")
    try:
        factory = app.state.llm_factory
        llm = factory.get_llm(model_id, free_models)
        response = llm.invoke(user_prompt)
        return response.content 
    except RateLimitError as e:
        log.error(f"[RateLimitError] Encountered for {llm.model_name}. Details: {e}")
        response_message = f"The free model {llm.model_name} is temporarily rate-limited. Please try again in a moment."
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
            raise HTTPException(status_code=429, detail=f"The free model {llm.model_name} is temporarily rate-limited upstream. Please try again.") from e
            
        log.error(f"[APIError {status_code}] Encountered: {e}")
        # Other OpenAI/OpenRouter errors
        raise HTTPException(status_code=status_code, detail=str(e)) from e

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Issue a token using client_id/client_secret.

    Use:
        client_id     -> form_data.client_id
        client_secret -> form_data.client_secret
    """
    log.debug("Starting Authentication for client...")
    log.debug(f"[Authentication] Client ID {form_data.client_id}")
    log.debug(f"[Authentication] Client Secret {form_data.client_secret}")
    client = authenticate_client(form_data.client_id, form_data.client_secret)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client_id or client_secret",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(client)
    return {"access_token": token, "token_type": "bearer"}