from langchain_openai import ChatOpenAI
from fastapi import HTTPException
from openai import RateLimitError, APIError 
from ors.llm.prompts import get_prompt_template
from ors.utils.logging_utils import get_logger, set_log_level

log = get_logger(__name__)


def invoke_llm(llm: ChatOpenAI, user_prompt: str, prompt_type: str = "basic") -> str:
    """
    Invokes the LLM using separated Langchain templates and LCEL (LangChain Expression Language).
    
    """
    response_message = ""
    try:
        # Retrieve prompt based on template type
        template = get_prompt_template(prompt_type)
        
        # Bind template to LLM (LCEL pattern)
        chain = template | llm
        response = chain.invoke({"user_prompt": user_prompt})
        response_message = response.content
         
    except Exception as e:
        log.error(f"[Unexpected Exception - {type(e).__name__}] Encountered: {e}")
        # Fallback for anything unexpected
        raise HTTPException(status_code=500, detail="Unexpected error in LLM backend") from e