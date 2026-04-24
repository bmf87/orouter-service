import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("orouter-service.env"))

app_name = "orouter-service"
api_base_url = "https://openrouter.ai/api/v1"

app_dns = "http://127.0.0.1:8000"
default_model = "openrouter/free"

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
