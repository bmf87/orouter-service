import jwt
from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from ors.utils.logging_utils import get_logger, set_log_level, DEBUG
from pydantic import BaseModel
from ors.config.auth_config import (
    VALID_CLIENTS, JWT_SECRET_KEY, JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE
)


log = get_logger(__name__)
set_log_level(DEBUG)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Identity model for JWT
class Client(BaseModel):
    client_id: str

# Identity model for client credentials
class ClientCredentials(BaseModel):
    client_id: str
    client_secret: str


def authenticate_client(client_id: str, client_secret: str) -> Optional[Client]:
    """
    Simple client-id/secret check. May replace in future with more complex logic.

    Args:
        client_id: str - Client ID to authenticate
        client_secret: str - Client secret to authenticate
    
    Returns:
        Optional[Client] - Client object if authentication is successful, None otherwise    
    """
    log.debug(f"[Authentication] Client ID {client_id}")
    valid_secret = VALID_CLIENTS.get(client_id)
    if not valid_secret:
        log.error(f"[Authentication Failed] Client ID {client_id} not found")
        return None
    if client_secret != valid_secret:
        log.error(f"[Authentication Failed] Invalid client secret for client ID {client_id}")
        return None
    log.info(f"[Authentication Success] Client ID {client_id} authenticated")
    return Client(client_id=client_id)


def create_access_token(client: Client) -> str:
    """
    Create a signed JWT for the client.

    Args:
        client: Client - Client object with client_id
    
    Returns:
        str - JWT access token
    """
    now = datetime.now(timezone.utc)
    exp = now + JWT_ACCESS_TOKEN_EXPIRE
    payload = {
        "sub": client.client_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


# Security scheme: Bearer token (Authorization: Bearer <token>)
bearer_scheme = HTTPBearer(auto_error=True)


def get_current_client(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),) -> Client:
    """
    FastAPI dependency to validate the bearer token on any protected endpoints.

    Args:
        credentials: HTTPAuthorizationCredentials - Bearer token from the request header
    
    Returns:
        Client - Client object with client_id
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        client_id: str = payload.get("sub")
        log.info(f"[Token Validation] Client ID {client_id} found in get_current_client")
        if client_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )

    if client_id not in VALID_CLIENTS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown client",
        )

    return Client(client_id=client_id)