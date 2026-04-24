from langchain_core.prompts import ChatPromptTemplate
#
# Define modular prompt templates here. Using Langchain's ChatPromptTemplate
#   - industry standard to define prompts
#
BASIC_ASSISTANT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant that answers questions and provides detailed responses."),
    ("user", "{user_prompt}")
])

def get_prompt_template(name: str) -> ChatPromptTemplate:
    """
    Registry function to pull the correct templates by string key.
    """
    templates = {
        "basic": BASIC_ASSISTANT_PROMPT,
        # Add more specialized templates here, e.g:
        # "code_review": CODE_REVIEW_PROMPT,
        # "summarization": SUMMARIZATION_PROMPT,
    }
    # Fallback to 'basic' if not found
    return templates.get(name, BASIC_ASSISTANT_PROMPT)
