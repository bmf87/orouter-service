from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from openai import RateLimitError, APIError 

from ors.app.routers import chat, model
from ors.llm.llm_loader import LLMFactory
from ors.llm.orouter_inv import get_free_models 
from ors.utils.logging_utils import get_logger, set_log_level, DEBUG
from ors.security.auth import (
    authenticate_client, create_access_token, Client,
    ClientCredentials, get_current_client, Token
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
app.include_router(model.router)
app.include_router(chat.router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.get("/info", tags=["default"])
async def service_info(request: Request, 
    current_client: Client = Depends(get_current_client)):
    routes = []
    for route in request.app.routes:
        if isinstance(route, APIRoute):
            routes.append(route.path)
    

    return {
        "name": constants.app_name,
        "version": constants.app_version,
        "routes": sorted(set(routes)),
    }

@app.get("/health", tags=["default"])
async def health(current_client: Client = Depends(get_current_client)):
    return {"status": "ok"} 

@app.post("/token", response_model=Token,  tags=["default"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Issue a token using client_id/client_secret.

    Use:
        client_id     -> form_data.client_id
        client_secret -> form_data.client_secret
    """
    #log.debug("Starting Authentication for client...")
    #log.debug(f"[Authentication] Client ID {form_data.client_id}")
    #log.debug(f"[Authentication] Client Secret {form_data.client_secret}")
    client = authenticate_client(form_data.client_id, form_data.client_secret)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client_id or client_secret",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(client)
    return {"access_token": token, "token_type": "bearer"}