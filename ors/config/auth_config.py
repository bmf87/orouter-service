import os, json
from dotenv import load_dotenv, find_dotenv
from datetime import timedelta
from ors.utils.logging_utils import get_logger, set_log_level, DEBUG

log = get_logger(__name__)
set_log_level(DEBUG)

load_dotenv(find_dotenv("orouter-service.env"))

clients_raw = os.getenv("USER_DATABASE")
if clients_raw:
    VALID_CLIENTS = json.loads(clients_raw)
else:
    VALID_CLIENTS = {}

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE = timedelta(hours=1)