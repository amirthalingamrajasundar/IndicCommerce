"""
LangGraph agent definition and invocation.
"""
from typing import Dict, TypedDict, Annotated, List
import operator
import logging

from langgraph.graph import StateGraph, END

from src.speech_processing.processor import translate_audio, translate_and_speak
from src.utils.vector_store import get_vector_store
from src.llm.sarvam import chat_completion
from src.prompts.shopping_assistant import get_prompt
from src.db.firestore import FirestoreClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Agent State
class Response(TypedDict):
    """
    Represents a response to be sent back to the user.
    """
    text: str
    voice_url: str = None
    image_url: str = None

class AgentState(TypedDict):
    """
    Represents the state of our LangGraph agent.
    """
    regional_audio_path: str
    user_language: str
    cart: List[str]  # List of product ids in the user's cart
    history: List[Dict[str, str]]  # List of previous interactions
    english_query: str
    products: List[dict]
    llm_response: str
    response: Response
    error_message: str = None
    user_id: str  # Unique identifier for the user

# Define Nodes

def get_user_info_node(state: AgentState):
    """
    Retrieves user information from Firestore.
    Input: state['user_id']
    Output: state['user_language'] or state['error_message']
    """
    logger.info("---RETRIEVING USER INFO---")
    user_id = state.get("user_id")

    if not user_id:
        return {"error_message": "User ID not found in state for user info retrieval."}

    try:
        # Initialize Firestore client
        firestore_client = FirestoreClient()
        user_data = firestore_client.get_full_user_data(user_id)
        if not user_data:
            logger.warning(f"No user data found for user_id: {user_id}")
        logger.debug(f"User data: {user_data}")
        state['user_language'] = user_data.get("preferred-language", "en-IN")
        state['history'] = user_data.get("history", [])
        state['cart'] = user_data.get("cart", [])
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        state['error_message'] = str(e)

def convert_speech_to_text_node(state: AgentState):
    """
    Converts regional voice message to English text.
    Input: state['regional_audio_path']
    Output: state['english_query'], state['user_language'] or state['error_message']
    """
    logger.info("---CONVERTING SPEECH TO TEXT---")
    audio_path = state.get("regional_audio_path")

    if not audio_path:
        return {"error_message": "Audio path not found in state for STT."}
    
    try:
        #Translate regional audio to English
        english_text, user_language = translate_audio(audio_path)

        if not english_text:
            logger.error("Translation to English failed.")
            return {"error_message": "Translation to English failed."}
        
        logger.debug(f"English query: {english_text}")
        return {"english_query": english_text, "user_language": user_language}
    except Exception as e:
        import traceback
        # Ensure newline characters in the traceback are properly escaped for the string
        trace = traceback.format_exc().replace('\n', '\\n')
        error_details = f"Error in convert_speech_to_text_node: {e}, trace: {trace}"
        logger.error(error_details)
        return {"error_message": f"Speech to text/translation pipeline failed: {str(e)}"}

def query_vector_db_node(state: AgentState):
    """
    Query the vector database and identify relevant products.
    Input: state['english_query']
    Output: state['products'] or state['error_message']
    """
    logger.info("---QUERYING VECTOR DATABASE---")
    english_query = state.get("english_query")

    if not english_query:
        return {"error_message": "English query not found in state for DB query."}

    vector_store = get_vector_store()
    products = vector_store.search(english_query, limit=3)

    state['products'] = products
    logger.debug(f"Relevant products: {state['products']}")
    return {"products": state['products']}

def call_llm_node(state: AgentState):
    """
    Calls the LLM to generate a response based on the user's query and relevant products.
    This is a placeholder function for future LLM integration.
    """
    logger.info("---CALLING LLM---")
    english_query = state.get("english_query")
    products = state.get("products", [])
    llm_prompt = get_prompt(
        history=state.get("history", []),
        products=products,
        query=english_query,
    )
    logger.debug(f"LLM prompt: {llm_prompt}")
    state['llm_response'] = chat_completion(
        prompt=llm_prompt,
    )
    # Store conversation
    # Initialize Firestore client
    firestore_client = FirestoreClient()
    firestore_client.save_conversation(state["user_id"], [
        {"role": "user", "content": english_query},
        {"role": "assistant", "content": state['llm_response']},
    ])
    logger.info(f"LLM response: {state['llm_response']}")
    return {"llm_response": state['llm_response']}

def generate_response_node(state: AgentState):
    """
    Constructs a response message.
    Input: state['products']
    Output: state['response'] or state['error_message']
    """
    logger.info("---GENERATING RESPONSE---")
    llm_response = state.get("llm_response")

    if not llm_response:
        return {"error_message": "No LLM response."}

    response_text, response_voice_url = translate_and_speak(
        llm_response,
        "en-IN",
        state.get("user_language")
    )

    state['response'] = {
        "text": response_text,
        "voice_url": response_voice_url,
        "image_url": state['products'][0]['image_url'] if state['products'] else None
    }

    logger.info(f"Response text: {response_text}")
    logger.info(f"Response voice URL: {response_voice_url}")

    return {"response": state['response']}

def handle_error_node(state: AgentState):
    """
    Handles errors and prepares a generic error message.
    """
    logger.info(f"---ERROR HANDLER---")
    error = state.get("error_message", "An unknown error occurred.")
    logger.debug(f"Error: {error}")
    return {
        "llm_response": "Sorry, I encountered an error while processing your request. Please try again later.",
        "error_message": error # Keep the error message for logging
    }

# Define Graph
workflow = StateGraph(AgentState)

# TODO: Intent identification node - Router
workflow.add_node("get_user_info", get_user_info_node)
workflow.add_node("speech_to_text", convert_speech_to_text_node)
workflow.add_node("query_vector_db", query_vector_db_node)
workflow.add_node("call_llm", call_llm_node)
workflow.add_node("generate_response", generate_response_node)
workflow.add_node("error_handler", handle_error_node)

# Define Edges
workflow.set_entry_point("get_user_info")

def decide_next_step(state: AgentState):
    if state.get("error_message"):
        return "error_handler"
    if not state.get("english_query"):
        return "speech_to_text"
    if not state.get("products"):
        return "query_vector_db"
    if not state.get("llm_response"): # Check if response is generated
        return "call_llm"
    if not state.get("response"):
        return "generate_response"
    return END

workflow.add_conditional_edges(
    "get_user_info",
    decide_next_step,
    {
        "speech_to_text": "speech_to_text",
        "error_handler": "error_handler",
    } 
)

workflow.add_conditional_edges(
    "speech_to_text",
    decide_next_step,
    {
        "query_vector_db": "query_vector_db",
        "error_handler": "error_handler",
    }
)

workflow.add_conditional_edges(
    "query_vector_db",
    decide_next_step,
    {
        "call_llm": "call_llm",
        "error_handler": "error_handler",
    }
)
workflow.add_conditional_edges(
    "call_llm",
    decide_next_step,
    {
        "generate_response": "generate_response",
        "error_handler": "error_handler",
    }
)

workflow.add_edge("error_handler", "generate_response")
workflow.add_edge("generate_response", END)

# Compile the graph
compiled_graph = workflow.compile()