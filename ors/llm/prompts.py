from langchain_core.prompts import ChatPromptTemplate
from ors import constants
#
# Modular prompt templates: using Langchain's ChatPromptTemplate
#   - Enables easy formatting of inputs into structured messages (prompts + variables)
#
BASIC_ASSISTANT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant that answers questions and provides detailed responses."),
    ("user", "{user_prompt}"),
])

SUMMARIZATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are an expert summarizer. Condense the following text into a concise summary.\n\n"
            "Requirements:\n"
            "- Keep it under 100 words.\n"
            "- Capture all key points.\n"
            "- Maintain a neutral tone.\n"
        ),
    ),
    ("user", "{text}"),
])
# Incorporate a rolling summary and extra system instructions
CONVERSATION_ASSISTANT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a helpful AI assistant that continues an ongoing conversation.\n"
            "You receive a running summary of the prior dialogue and must respond "
            "in a way that is consistent with it.\n\n"
            "Conversation summary (may be empty):\n"
            "{conversation_summary}\n\n"
            "Additional system instructions (optional):\n"
            "{extra_system_instructions}"
        ),
    ),
    (
        "user",
        (
            "User message:\n"
            "{user_prompt}\n\n"
            "If the conversation summary is non-empty, use it as context instead "
            "of asking the user to repeat themselves."
        ),
    ),
])

def get_prompt_template(name: str) -> ChatPromptTemplate:
    """
    Registry function to retrieve the correct templates by string key.
    
    Args:
        name: str - name of the template to retrieve
    
    Returns:
        ChatPromptTemplate - the template to use
    """
    templates = {
        constants.TEMPLATE_TYPE_BASIC: BASIC_ASSISTANT_PROMPT,
        constants.TEMPLATE_TYPE_CONVERSATION: CONVERSATION_ASSISTANT_PROMPT,
        constants.TEMPLATE_TYPE_SUMMARIZATION: SUMMARIZATION_PROMPT,
        # Other templates, as needed
        # "code_review": CODE_REVIEW_PROMPT,
        
    }
    # Fallback to 'basic'
    return templates.get(name, BASIC_ASSISTANT_PROMPT)
