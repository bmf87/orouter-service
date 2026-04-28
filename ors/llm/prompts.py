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
# Agentic prompts
PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a planning agent. Break the user's goal into an ordered list "
     "of clear, concrete sub-tasks. Be specific, but keep the list concise."),
    ("user",
     "User goal:\n{goal}\n\n"
     "Return ONLY the list of sub-tasks, each on its own line, numbered.")
])
RESEARCHER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a research agent. For each sub-task, you gather detailed notes, "
     "key points, and examples relevant to the overall goal."),
    ("user",
     "Overall goal:\n{goal}\n\n"
     "Sub-task:\n{task}\n\n"
     "Provide thorough notes, but avoid writing the final document.")
])
WRITER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a writing agent. Using the plan and research notes, write a "
     "coherent, well-structured document aligned with the user's goal."),
    ("user",
     "User goal:\n{goal}\n\n"
     "Plan:\n{plan}\n\n"
     "Research notes:\n{notes}\n\n"
     "Write the final document.")
])
REVIEWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a reviewer agent. Critique the draft and suggest concrete "
     "improvements for structure, clarity, and completeness."),
    ("user",
     "User goal:\n{goal}\n\n"
     "Draft:\n{draft}\n\n"
     "Provide a structured review with strengths, weaknesses, and specific edits.")
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
        constants.TEMPLATE_TYPE_PLANNER: PLANNER_PROMPT,
        constants.TEMPLATE_TYPE_RESEARCHER: RESEARCHER_PROMPT,
        constants.TEMPLATE_TYPE_WRITER: WRITER_PROMPT,
        constants.TEMPLATE_TYPE_REVIEWER: REVIEWER_PROMPT,
        
    }
    # Fallback to 'basic'
    return templates.get(name, BASIC_ASSISTANT_PROMPT)
