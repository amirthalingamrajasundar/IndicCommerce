"""
LangGraph agent definition and invocation.
"""
from typing import Dict, TypedDict, List
import os
import logging
import json
from langgraph.graph import StateGraph, END
from openai import OpenAI

from src.speech_processing.processor import translate_audio, translate_and_speak
from src.utils.vector_store import get_vector_store
from src.llm.sarvam import chat_completion
from src.prompts.shopping_assistant import get_prompt
from src.db.firestore import FirestoreClient

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
llmmodel = "gpt-4o-mini"

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
    intent_type: str = None
    confidence: float = None
    search_terms: str = None
    product_id: str = None
    cart_action: str = None
    quantity: int = None

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
    try:
        english_query = state.get("english_query")

        if not english_query:
            return {"error_message": "English query not found in state for DB query."}

        vector_store = get_vector_store()
        products = vector_store.search(english_query, limit=3)

        state['products'] = products
        logger.debug(f"Relevant products: {state['products']}")
        return {"products": state['products']}
    except Exception as e:
        return {
            "error_message": f"Error in query_vector_db_node: {e}"
        }

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
    
def identify_intent_node(state: AgentState):
    """Identify the specific intent of the user query"""
    logger.info("Identifying user intent")
    
    english_query = state.get("english_query", "")
    user_language = state.get("user_language", "en-IN")
    
    if not english_query:
        logger.error("No query found for intent identification")
        return {"error_message": "No query found for intent identification"}
    
    try:
        messages = [
            {"role": "system", "content": "You are an intent classifier for an Indian e-commerce platform. Classify the query into one of these categories:\r\n1. product_query: User is searching for or asking about products to purchase\r\n2. summarize_cart: User wants summarize all the existing product added the cart currently\r\n3. cart_update: User wants to add or remove products from their shopping cart\r\n4.initiate_payment: User wants to initiate payment for their order\r\n5. general_info: User is asking general questions about policies, availability, etc.\r\n\r\nConsider Indian e-commerce context like 'Cash on Delivery', Indian brands, and regional preferences."}
        ]
        
        lang_note = f"The original query was in {user_language}" if user_language != "en-IN" and user_language != "en" else ""
        
        messages.append({"role": "user", "content": f"Query: {english_query} {lang_note}\n\nClassify this query into one of the 5 categories. Reply with JSON containing:\n- intent_type (string: 'product_query', 'summarize_cart', 'cart_update', 'initiate_payment', or 'general_info')\n- confidence (number between 0-1)\n- search_terms (string, relevant only for product_query)\n- product_id (string, relevant only for cart_update, empty string if not found)\n- cart_action (string, 'add' or 'remove', relevant only for cart_update, empty string if not applicable)\n- quantity (number, relevant only for cart_update, default to 1)"})        
        response = client.chat.completions.create(
            model=llmmodel, 
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        intent_data = json.loads(response.choices[0].message.content)
        confidence = intent_data.get("confidence", 0.0)
        intent_type = intent_data.get("intent_type", "")
        product_id = intent_data.get("product_id", "")
        cart_action = intent_data.get("cart_action", "add")
        quantity = intent_data.get("quantity", 1)
        
        logger.info(f"Intent classification: Type = {intent_type}, Confidence = {confidence}")
        if intent_type == "cart_update":
            logger.info(f"Cart update: Action = {cart_action}, Product ID = {product_id}, Quantity = {quantity}")
        
        # Update state with all relevant fields
        state["intent_type"] = intent_type
        state["confidence"] = confidence
        
        # Add intent-specific fields
        state["product_id"] = product_id
        state["cart_action"] = cart_action
        state["quantity"] = quantity
        
        is_product = (intent_type == "product_query")

        logger.info(f"Intent processing complete: intent_type={intent_type}")
        return {
            "intent_type": intent_type,
            "confidence": confidence,
            "product_id": product_id,
            "cart_action": cart_action,
            "quantity": quantity,
            "is_product": is_product
        }
            
    except Exception as e:
        logger.error(f"Error in intent classification: {e}")
        state["intent_type"] = ""
        state["search_terms"] = english_query
        state["confidence"] = 0.5
        return {
            "error_message": f"Error in intent classification: {e}"
        }

def get_intent_type(state: AgentState) -> str:  
    intent_type = state.get('intent_type', "product_query")
    logger.info(f"ROUTING DECISION: Intent type = {intent_type}")   
    
    # These must match the exact keys in the conditional edges dictionary
    valid_intents = ["product_query", "cart_update", "summarize_cart", "initiate_payment", "general_info"]
    
    if not intent_type or intent_type not in valid_intents:
        logger.warning(f"Invalid intent type '{intent_type}', using fallback to product_query")
        # Always return a valid value that matches your edge routing dictionary
        return "product_query"
    
    return intent_type

def handle_cart_update(state: AgentState):
    #TODO: implement this function
    logger.info("Handling cart update")
    return {}

def handle_summarize_cart(state: AgentState):
    #TODO: implement this function
    logger.info("Handling summarize cart")
    return {}

def handle_initiate_payment(state: AgentState):
    #TODO: implement this function
    logger.info("handling payment initiation")
    return {}
    

# Define Graph
workflow = StateGraph(AgentState)

# TODO: Intent identification node - Router
workflow.add_node("get_user_info", get_user_info_node)
workflow.add_node("speech_to_text", convert_speech_to_text_node)
workflow.add_node("query_vector_db", query_vector_db_node)
workflow.add_node("call_llm", call_llm_node)
workflow.add_node("generate_response", generate_response_node)
workflow.add_node("error_handler", handle_error_node)
workflow.add_node("identify_intent", identify_intent_node)
workflow.add_node("handle_cart_update", handle_cart_update)
workflow.add_node("handle_summarize_cart", handle_summarize_cart)
workflow.add_node("handle_initiate_payment", handle_initiate_payment)


# Define Edges
workflow.set_entry_point("get_user_info")

def check_for_error(state: AgentState):
    if state.get("error_message"):
        return "error_handler"
    else:
        return "DEFAULT"  

workflow.add_conditional_edges(
    "get_user_info",
    check_for_error,
    {
        "speech_to_text": "speech_to_text",
        "error_handler": "error_handler",
    } 
)



workflow.add_conditional_edges(
    "speech_to_text",
    check_for_error,
    {
        "DEFAULT": "identify_intent",
        "error_handler": "error_handler"
    }
)

workflow.add_conditional_edges(
    "query_vector_db",
    check_for_error,
    {
        "DEFAULT": "call_llm",
        "error_handler": "error_handler",
    }
)
workflow.add_conditional_edges(
    "call_llm",
    check_for_error,
    {
        "DEFAULT": "generate_response",
        "error_handler": "error_handler",
    }
)

workflow.add_conditional_edges(
    "identify_intent",
    get_intent_type,
    {
        "product_query": "query_vector_db",
        "cart_update": "handle_cart_update",
        "summarize_cart": "handle_summarize_cart",
        "general_info": "error_handler",
        "initiate_payment": "handle_initiate_payment"
    }
)

workflow.add_conditional_edges(
    "handle_cart_update",
    check_for_error,
    {
        "DEFAULT": "generate_response",
        "error_handler": "error_handler"
    }
)

workflow.add_conditional_edges(
    "handle_summarize_cart",
    check_for_error,
    {
        "DEFAULT": "generate_response",
        "error_handler": "error_handler"
    }
)

workflow.add_conditional_edges(
    "handle_initiate_payment",
    check_for_error,
    {
        "DEFAULT": "generate_response",
        "error_handler": "error_handler"
    }
)

workflow.add_edge("error_handler", "generate_response")
workflow.add_edge("generate_response", END)

# Compile the graph
compiled_graph = workflow.compile()