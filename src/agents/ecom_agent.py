"""
LangGraph agent definition and invocation.
"""
from typing import TypedDict, Annotated, List
import operator
import logging

from langgraph.graph import StateGraph, END

from src.speech_processing.processor import translate_audio, translate_and_speak

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Agent State
class Response(TypedDict):
    """
    Represents a response to be sent back to the user.
    """
    text: str
    voice_path: str = None
    image_url: str = None

class AgentState(TypedDict):
    """
    Represents the state of our LangGraph agent.
    """
    regional_audio_path: str
    user_language: str
    english_query: str
    query_embedding: List[float]
    product: dict
    llm_response: str
    response: Response
    error_message: str = None

# Define Nodes

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

def text_to_embedding_node(state: AgentState):
    """
    Converts the English text (user query) into an embedding.
    Input: state['english_query']
    Output: state['query_embedding'] or state['error_message']
    """
    logger.info("---CONVERTING TEXT TO EMBEDDING---")
    english_query = state.get("english_query")
    if not english_query:
        return {"error_message": "English query not found in state for embedding."}
    
    # Placeholder: Actual implementation will use an embedding model to generate embeddings

    # Dummy implementation
    state['query_embedding'] = [0.1, 0.2, 0.3] # Dummy embedding
    logger.debug(f"Query embedding: {state['query_embedding']}")
    return {"query_embedding": state['query_embedding']}

def query_vector_db_node(state: AgentState):
    """
    Uses the embedding to query a vector database and identify a relevant product.
    Input: state['query_embedding']
    Output: state['product'] or state['error_message']
    """
    logger.info("---QUERYING VECTOR DATABASE---")
    query_embedding = state.get("query_embedding")
    if not query_embedding:
        return {"error_message": "Query embedding not found in state for DB query."}

    # Placeholder: Actual implementation will query a vector database to find relevant products

    # Dummy implementation
    state['product'] = {
        "id": "prod1", 
        "name": "Awesome T-Shirt", 
        "description": "A very comfortable and stylish t-shirt.", 
        "price": "₹499", 
        "image_url": "http://example.com/image.jpg"
    }
    logger.debug(f"Relevant product: {state['product']}")
    return {"product": state['product']}

def call_llm_node(state: AgentState):
    """
    Calls the LLM to generate a response based on the user's query and relevant product.
    This is a placeholder function for future LLM integration.
    """
    logger.info("---CALLING LLM---")
    # Placeholder: Actual implementation will call an LLM to generate a response
    # For now, we just return a dummy response
    state['llm_response'] = "Here is a product that matches your query."
    logger.debug(f"LLM response: {state['llm_response']}")
    return {"llm_response": state['llm_response']}

def generate_response_node(state: AgentState):
    """
    Constructs a response message.
    Input: state['product']
    Output: state['response'] or state['error_message']
    """
    logger.info("---GENERATING RESPONSE---")
    llm_response = state.get("llm_response")
    if not llm_response:
        return {"error_message": "No LLM response."}

    response_text, response_voice_path = translate_and_speak(
        llm_response,
        "en-IN",
        state.get("user_language")
    )

    logger.info(f"Response text: {response_text}")
    logger.info(f"Response voice path: {response_voice_path}")
    
    return {
        "response": {
            "text": response_text,
            "voice_path": response_voice_path,
            "image_url": state['product']['image_url']
        }
    }

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

workflow.add_node("speech_to_text", convert_speech_to_text_node)
workflow.add_node("text_to_embedding", text_to_embedding_node)
workflow.add_node("query_vector_db", query_vector_db_node)
workflow.add_node("call_llm", call_llm_node)
workflow.add_node("generate_response", generate_response_node)
workflow.add_node("error_handler", handle_error_node)

# Define Edges
workflow.set_entry_point("speech_to_text")

def decide_next_step(state: AgentState):
    if state.get("error_message"):
        return "error_handler"
    if not state.get("query_embedding"):
        return "text_to_embedding"
    if not state.get("product"):
        return "query_vector_db"
    if not state.get("llm_response"): # Check if response is generated
        return "call_llm"
    if not state.get("response"):
        return "generate_response"
    return END

workflow.add_conditional_edges(
    "speech_to_text",
    decide_next_step,
    {
        "text_to_embedding": "text_to_embedding",
        "error_handler": "error_handler",
    }
)
workflow.add_conditional_edges(
    "text_to_embedding",
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