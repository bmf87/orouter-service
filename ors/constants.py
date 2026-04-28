import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("orouter-service.env"))

app_name = "orouter-service"
app_version = "1.0.0"
app_dns = "https://bfavro73-oroutersrv.hf.space"
api_base_url = "https://openrouter.ai/api/v1"
default_model = "openrouter/free"

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# Prompt Template Types
TEMPLATE_TYPE_BASIC = "basic"
TEMPLATE_TYPE_CONVERSATION = "conversation"
TEMPLATE_TYPE_SUMMARIZATION = "summarization"

# Agentic Prompt Template Types
TEMPLATE_TYPE_PLANNER = "planner"
TEMPLATE_TYPE_RESEARCHER = "researcher"
TEMPLATE_TYPE_WRITER = "writer"
TEMPLATE_TYPE_REVIEWER = "reviewer"
