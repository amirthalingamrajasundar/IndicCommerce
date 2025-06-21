"""
LangGraph agent definition and invocation for IndicCommerce.
"""
import os
import json
import logging
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from openai import OpenAI
from src.speech_processing.processor import translate_audio, translate_and_speak, text_to_speech, sarvam_client
from src.utils.vector_store import vector_store
from src.llm.sarvam import chat_completion
from src.prompts.shopping_assistant import prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
llmmodel = "gpt-4o-mini"

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
    messages: List[Any]
    user_language: Optional[str] = None
    english_query: Optional[str] = None
    intent_type: Optional[str] = None
    confidence: float = 0.0
    search_terms: str = ""
    order_id: str = ""
    product_id: str = ""
    cart_action: str = ""
    quantity: int = 0
    query_embedding: Optional[List[float]] = None
    product: Optional[Dict] = None
    llm_response: Optional[str] = None
    response: Optional[Response] = None
    error_message: Optional[str] = None

def text_to_embedding(args: Dict) -> Dict:
    """
    Convert text to embedding vector for semantic search.
    """
    english_query = args.get("english_query", "")
    
    if not english_query:
        return {"error": "English query not found for embedding."}
    
    # TODO: Actual implementation will use an embedding model to generate embeddings
    embedding = english_query
    
    return {"query_embedding": embedding}

def query_vector_db(args: Dict) -> Dict:
    """
    Use the embedding to query a vector database and identify a relevant product.
    """
    logger.info("---QUERYING VECTOR DATABASE---")
    query_embedding = args.get("query_embedding")
    logger.info(f"query_embedding: {query_embedding}")
    if not query_embedding:
        return {"error": "Query embedding not found for DB query."}

    # TODO: Actual implementation will query a vector database to find relevant products
    query_terms = args.get("english_query", "").lower()
    logger.info(f"query_terms: {query_terms}")
    
    if "shirt" in query_terms or "t-shirt" in query_terms:
        price_in_indian_format = "₹999" if "under thousand" in query_terms else "₹1,499"
        product = {
            "id": "prod1", 
            "name": "Premium Cotton Red T-Shirt", 
            "description": "A comfortable and stylish t-shirt made with 100% Indian cotton. Perfect for casual wear.", 
            "price": price_in_indian_format,
            "discount": "₹2,000",
            "sales": "1,20,000+ sold",
            "image_url": "http://example.com/tshirt.jpg"
        }
    elif "pant" in query_terms or "pants" in query_terms or "jeans" in query_terms or "trouser" in query_terms:
        product = {
            "id": "prod2", 
            "name": "Premium Slim-Fit Cotton Pants", 
            "description": "Comfortable slim-fit pants made with breathable cotton. Perfect for formal and casual occasions.", 
            "price": "₹1,999",
            "discount": "Original: ₹2,499",
            "sales": "95,000+ sold",
            "image_url": "http://example.com/pants.jpg"
        }
    else:
        product = {
            "id": "prod3", 
            "name": "IndicCommerce Gift Card", 
            "description": "Gift card valid across 10,000+ stores in India.", 
            "price": "₹1,000",
            "image_url": "http://example.com/giftcard.jpg"
    }
    logger.debug(f"Relevant product: {product}")
    return {"product": product}

def generate_response(args: Dict) -> Dict:
    """
    Construct a response message using Sarvam AI's language processing functions.
    """
    logger.info("---GENERATING RESPONSE---")
    llm_response = args.get("llm_response")
    user_language = args.get("user_language")
    product = args.get("product")
    
    if not llm_response:
        return {"error": "No LLM response."}

    if not user_language:
        user_language = "hi-IN"  
    
    try:
        response_text, response_voice_path = translate_and_speak(
            text=llm_response,
            source_language_code="en-IN",
            target_language_code=user_language,
            speaker_gender="Female"
        )

        logger.info(f"Response text translated to {user_language}: {response_text}")
        logger.info(f"Response voice path: {response_voice_path}")
        
        return {
            "response": {
                "text": response_text,
                "voice_path": response_voice_path,
                "image_url": product['image_url'] if product else None
            }
        }
    except Exception as e:
        logger.error(f"Error in translation/TTS: {e}")
        
        # Fallback: If translation fails, try direct text-to-speech without translation
        try:
            voice_path = text_to_speech(
                text=llm_response,
                language_code="en-IN",  # Fallback to English
                speaker_gender="Female"
            )
            
            return {
                "response": {
                    "text": llm_response,  # Original English text
                    "voice_path": voice_path,
                    "image_url": product['image_url'] if product else None
                }
            }
        except Exception as inner_e:
            logger.error(f"Fallback TTS also failed: {inner_e}")
            return {
                "response": {
                    "text": llm_response,  # Original English text
                    "voice_path": None,
                    "image_url": product['image_url'] if product else None
                }
            }

def handle_error(args: Dict) -> Dict:
    """
    Handle errors and prepare a generic error message.
    """
    logger.info(f"---ERROR HANDLER---")
    error = args.get("error", "An unknown error occurred.")
    logger.debug(f"Error: {error}")
    return {
        "llm_response": "Sorry, I encountered an error while processing your request. Please try again later.",
        "error_message": error # Keep the error message for logging
    }

class EcommerceAgent:
    def __init__(self, model=llmmodel, system_prompt=""):
        """
        Initialize the EcommerceAgent with specified model and system prompt.
        """
        self.system_prompt = system_prompt or """
        You are an intelligent e-commerce assistant for IndicCommerce, designed to serve customers across India who speak various regional languages.
        The e-commerce platform offers product related to clothing, fashion and apparals
        
        Your job is to help Indian customers find products and provide information about them in a culturally appropriate way.
        
        IMPORTANT: Voice messages and regional language processing:
        - Voice messages are already transcribed to English by Sarvam AI before you receive them
        - Audio data is NEVER sent to you, only the transcribed text
        - The user's detected language is provided to you as context
        
        Process the pre-translated user query through these steps:
        1. Identify users intent based on the query received.
        2. If the users ask is about a product related to the e-commerce platform, Generate embedding search text query
        3. Use tool calling to search the vector DB using the embedding to get relevent product data
        4. Generate a helpful response about the product in English
        5. If the users ask is not about a product enquiry the e-commerce platform, Guide the user with an appropriate response or workflow
        
        Always be courteous and respectful to Indian customers and handle errors gracefully with clear feedback.
        When mentioning pricing, always use rupee (₹) symbol and follow Indian number formatting.
        """
        
        graph = StateGraph(AgentState)
        
        graph.add_node("identify_intent", self.identify_intent)
        graph.add_node("generate_embedding", self.generate_embedding)
        graph.add_node("search_products", self.search_products)
        graph.add_node("generate_product_response", self.generate_product_response)
        graph.add_node("handle_cart_update", self.handle_cart_update)
        graph.add_node("handle_summarize_cart", self.handle_summarize_cart)
        graph.add_node("handle_initiate_payment", self.handle_initiate_payment)
        graph.add_node("handle_general_info", self.handle_general_info)
        
        # Add conditional edges based on intent type
        graph.add_conditional_edges(
            "identify_intent",
            self.get_intent_type,
            {
                "product_query": "generate_embedding",
                "cart_update": "handle_cart_update",
                "summarize_cart": "handle_summarize_cart",
                "general_info": "handle_general_info",
                "initiate_payment": "handle_initiate_payment"
            }
        )
        
        # Product search workflow
        graph.add_edge("generate_embedding", "search_products")
        graph.add_edge("search_products", "generate_product_response")
        
        # All paths lead to END
        graph.add_edge("generate_product_response", END)
        graph.add_edge("handle_cart_update", END)
        graph.add_edge("handle_summarize_cart", END)
        graph.add_edge("handle_initiate_payment", END)
        graph.add_edge("handle_general_info", END)
        
        graph.set_entry_point("identify_intent")
        self.graph = graph.compile()
        
    def identify_intent(self, state: AgentState) -> Dict:
        """Identify the specific intent of the user query"""
        logger.info("Identifying user intent")
        
        english_query = state.get("english_query", "")
        user_language = state.get("user_language", "en-IN")
        
        if not english_query:
            logger.error("No query found for intent identification")
            state["intent_type"] = "general_info"
            state["confidence"] = 0.0
            return state
        
        try:
            messages = [
                {"role": "system", "content": "You are an intent classifier for an Indian e-commerce platform. Classify the query into one of these categories:\n1. product_query: User is searching for or asking about products to purchase\n2. summarize_cart: User wants summarize all the existing product added the cart currently\n3. cart_update: User wants to add or remove products from their shopping cart\n4.initiate_payment: User wants to initiate payment for their order\n5. general_info: User is asking general questions about policies, availability, etc.\n\nConsider Indian e-commerce context like 'Cash on Delivery', Indian brands, and regional preferences."}
            ]
            
            lang_note = f"The original query was in {user_language}" if user_language != "en-IN" and user_language != "en" else ""
            
            messages.append({"role": "user", "content": f"Query: {english_query} {lang_note}\n\nClassify this query into one of the 5 categories. Reply with JSON containing:\n- intent_type (string: 'product_query', 'summarize_cart', 'cart_update', 'initiate_payment', or 'general_info')\n- confidence (number between 0-1)\n- search_terms (string, relevant only for product_query)\n- product_id (string, relevant only for cart_update, empty string if not found)\n- cart_action (string, 'add' or 'remove', relevant only for cart_update, empty string if not applicable)\n- quantity (number, relevant only for cart_update, default to 1)\n- order_id (string, relevant only for order_tracking, empty string if not found)"})  
            
            response = client.chat.completions.create(
                model=llmmodel, 
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            intent_data = json.loads(response.choices[0].message.content)
            intent_type = intent_data.get("intent_type", "product_query")  # Default to product query
            confidence = intent_data.get("confidence", 0.0)
            search_terms = intent_data.get("search_terms", "")
            order_id = intent_data.get("order_id", "")
            
            # Extract cart-specific fields if available
            product_id = intent_data.get("product_id", "")
            cart_action = intent_data.get("cart_action", "add")
            quantity = intent_data.get("quantity", 1)
            
            logger.info(f"Intent classification: Type = {intent_type}, Confidence = {confidence}")
            if intent_type == "product_query":
                logger.info(f"Search terms = {search_terms}")
            elif intent_type == "order_tracking":
                logger.info(f"Order ID = {order_id}")
            elif intent_type == "cart_update":
                logger.info(f"Cart update: Action = {cart_action}, Product ID = {product_id}, Quantity = {quantity}")
            
            # Update state with all relevant fields
            state["intent_type"] = intent_type
            state["confidence"] = confidence
            
            # Add intent-specific fields
            state["search_terms"] = search_terms
            state["order_id"] = order_id
            state["product_id"] = product_id
            state["cart_action"] = cart_action
            state["quantity"] = quantity
            
            is_product = (intent_type == "product_query")

            logger.info(f"Intent processing complete: intent_type={intent_type}")
            return state
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            state["intent_type"] = "product_query"
            state["search_terms"] = english_query
            state["confidence"] = 0.5
            return state
    
    def get_intent_type(self, state: AgentState) -> str:
        
        intent_type = state.get('intent_type')
        logger.info(f"ROUTING DECISION: Intent type = {intent_type}")
        
        valid_intents = ["product_query", "cart_update", "summarize_cart", "initiate_payment", "general_info"]
        if intent_type not in valid_intents:
            logger.warning(f"Invalid intent type '{intent_type}', using fallback")
            intent_type = "general_info"
        
        return intent_type
    
    def generate_embedding(self, state: AgentState) -> Dict:
        logger.info("Generating embedding for product search")
        
        # Use search terms identified in intent classification
        search_terms = state.get("search_terms", state.get("english_query", ""))
        
        try:
            embedding_result = text_to_embedding({"english_query": search_terms})
            
            if "query_embedding" in embedding_result:
                state["query_embedding"] = embedding_result["query_embedding"]
                logger.info(f"Generated query_embedding for search '{search_terms}' : {embedding_result['query_embedding']}")
            else:
                logger.warning(f"No embedding returned for: {search_terms}")
            
        except Exception as e:
            logger.error(f"Error in embedding generation: {e}")
            
        return state
    
    def search_products(self, state: AgentState) -> Dict:
        logger.info("Searching product database")
        
        search_terms = state.get("search_terms", state.get("english_query", ""))
        logger.info(f"search terms : {search_terms}")
        
        try:
            # Call the query_vector_db function with text query even if embedding is not available
            search_args = {"english_query": search_terms}
            
            # Add embedding if available
            if "query_embedding" in state:
                search_args["query_embedding"] = state["query_embedding"]
                logger.info(f"Using generated embedding for search")
            
            # Perform the search
            product_result = query_vector_db(search_args)
            
            #TODO update based on the product json
            if "product" in product_result:
                state["product"] = product_result["product"]
                if "price" in product_result["product"]:
                    price = product_result["product"]["price"]
                    logger.info(f"Found product: {product_result['product'].get('name')} at price {price}")
                else:
                    logger.info(f"Found product: {product_result['product'].get('name')}")
            else:
                logger.warning("No products found matching the query")
                
        except Exception as e:
            logger.error(f"Error in product search: {e}")
            
        return state
    
    def generate_product_response(self, state: AgentState) -> Dict:
        """Generate response for product query"""
        logger.info("Generating product response")
        
        product = state.get("product", {})
        user_language = state.get("user_language", "en-IN")
        
        if not product or "error" in state:
            # No product found or error occurred
            response_text = f"I'm sorry, but I couldn't find any products matching your request. Could you please try describing what you're looking for differently?"
        else:
            # Format response with Indian numbering system
            response_text = f"I found a {product.get('name')} for {product.get('price')}. "
            response_text += f"{product.get('description', '')} "
            
            if "sales" in product:
                response_text += f"Over {product.get('sales')} "
                
            if "discount" in product:
                response_text += f"(Regular price: {product.get('discount')}) "
        
        # Add response to state
        state["response"] = {"text": response_text}
        logger.info(f"Generated product response: {response_text[:100]}...")
        
        return state
    
    def handle_cart_update(self, state: AgentState) -> Dict:
        """Handle shopping cart update requests (adding or removing products)"""
        logger.info("Handling shopping cart update request")
        
        english_query = state.get("english_query", "")
        product_id = state.get("product_id", "")
        cart_action = state.get("cart_action", "add")
        quantity = state.get("quantity", 1)
        
        if not product_id and cart_action == "add":
            #TODO: define cart Object
            pass
            
        messages = [
            {"role": "system", "content": "You are a helpful e-commerce assistant specialized in managing shopping carts for an Indian online store. "
                                      "Provide clear confirmation of cart updates with relevant details. "
                                      "Use a helpful, conversational tone and suggest related products when appropriate. "
                                      "Format all monetary values in Indian format (e.g., ₹1,00,000). "
                                      "Make references to Indian shopping preferences and festivals when relevant."}
        ]
        
        content = f"The user query is: '{english_query}'."
        
        messages.append({"role": "user", "content": content})
        
        try:
            response = client.chat.completions.create(
                model=llmmodel,
                messages=messages
            )
            
            response_text = response.choices[0].message.content
            
            state["llm_response"] = response_text
            result = generate_response({
                "llm_response": response_text,
                "user_language": user_language
            })
            
            state["response"] = result.get("response", {"text": response_text})
            logger.info(f"Generated cart update response: {response_text[:100]}...")
            
        except Exception as e:
            logger.error(f"Error generating cart update response: {e}")
            state["response"] = {"text": "I'm having trouble updating your shopping cart. Please try again or visit our website to complete your purchase."}
            
        return state
    def handle_summarize_cart(self, state: AgentState) -> Dict:
        #TODO: implement this function
        logger.info("Handling summarize cart")
        return state
    
    def handle_initiate_payment(self, state: AgentState) -> Dict:
        #TODO: implement this function
        logger.info("handling payment")
        return state
        
    def handle_general_info(self, state: AgentState) -> Dict:
        """Simple handler for general information requests"""
        logger.info("Handling general information request")
        
        english_query = state.get("english_query", "")
        user_language = state.get("user_language", "en-IN")
        
        try:
            response_text = f"I understand you're asking about: '{english_query}'"
            
            if user_language == "hi-IN":
                response_text += "\n\nकृपया मुझे और जानकारी दें ताकि मैं आपकी मदद कर सकूं।"
            elif user_language == "ta-IN":
                response_text += "\n\nதயவுசெய்து எனக்கு மேலும் தகவல் கொடுங்கள், அதனால் நான் உங்களுக்கு உதவ முடியும்."
            elif user_language == "te-IN":
                response_text += "\n\nదయచేసి నాకు మరింత సమాచారం ఇవ్వండి, తద్వారా నేను మీకు సహాయం చేయగలను."
            
            state["llm_response"] = response_text
            
            try:
                result = generate_response({
                    "llm_response": response_text,
                    "user_language": user_language
                })
                state["response"] = result.get("response", {"text": response_text})
            except Exception as inner_e:
                logger.error(f"Error generating response: {inner_e}")
                state["response"] = {"text": response_text}
                
            logger.info(f"Generated default guidance response: {response_text[:100]}...")
            
        except Exception as e:
            logger.error(f"Error in general info processing: {e}")
            state["response"] = {"text": "I apologize, but I'm having trouble processing your request at the moment. Please check our FAQ section or contact our customer care for assistance."}
            
        return state
        
    def invoke(self, initial_state: Dict) -> Dict:
        """
        Invoke the agent with an initial state.
        """
        state = AgentState(
            messages=[],
            intent_type="",
            confidence=0.0,
            search_terms="",
            order_id="",
            product_id="",
            cart_action="",
            quantity=0,
            user_language="en-IN",
            query_embedding=None
        )
        
        for key, value in initial_state.items():
            state[key] = value

        logger.info(f"Invoking agent with query: {state.get('english_query', '[NO QUERY]')}")
        
        result = self.graph.invoke(state)
        
        logger.info("Agent execution completed")
        return result

# Create a compiled agent that can be used externally
ecommerce_agent = EcommerceAgent()

def process_voice_message(audio_path: str) -> Dict:
    """
    Process a voice message and return the agent's response.
    First transcribe using Sarvam AI directly, then use the improved workflow.
    
    Args:
        audio_path: Path to the audio file containing the voice message
        
    Returns:
        Dictionary containing the agent's response using Indian number formatting
    """
    try:
        logger.info(f"Processing voice message using Sarvam AI directly: {audio_path}")
        translation_result = translate_audio(audio_path)
        
        if not translation_result or not translation_result[0]:
            logger.error("Direct speech-to-text translation failed")
            return {"text": "Sorry, I couldn't process your voice message. Please try again."}
        
        english_query = translation_result[0]
        user_language = translation_result[1] if len(translation_result) > 1 else "hi-IN"  # Default to Hindi
        
        logger.info(f"Transcribed text from Sarvam AI: {english_query}")
        logger.info(f"Detected language: {user_language}")
        
        try:
            result = ecommerce_agent.invoke({
                "english_query": english_query,
                "user_language": user_language,
                "intent_type": ""
            })
            
            logger.info(f"Agent invoke completed, result type: {type(result)}")
            
            if isinstance(result, dict) and "response" in result:
                logger.info("Found 'response' key in result from new workflow")
                return result["response"]
            
            if isinstance(result, dict) and "product" in result:
                product = result["product"]
                logger.info(f"Found product in result: {product['name']}")
                response_text = f"I found {product['name']} for {product['price']}. {product['description']}"
                return {"text": response_text}
                
        except Exception as e:
            logger.error(f"Error in agent processing: {str(e)}")
            
        return {"text": f"I understood your message in {user_language}, but couldn't find a product matching '{english_query}'. Could you try describing what you're looking for differently?"}
            
    except Exception as e:
        logger.error(f"Error in voice message processing: {str(e)}")
        return {"text": "I'm having trouble processing your voice message. Could you please try again or send a text message instead?"}

def process_text_message(text: str, source_language_code: str = "auto") -> Dict:
    """
    Process a text message in any language and return the agent's response.
    """
    try:
        if source_language_code != "en-IN" and source_language_code != "en-US" and source_language_code != "en":
            if sarvam_client:
                translation_response = sarvam_client.text.translate(
                    input=text,
                    source_language_code=source_language_code,
                    target_language_code="en-IN"
                )
                english_query = translation_response.translated_text
                user_language = source_language_code
            else:
                english_query = text
                user_language = "en-IN"
        else:
            english_query = text
            user_language = source_language_code
            
        result = ecommerce_agent.invoke({
            "english_query": english_query,
            "user_language": user_language
        })
        
        return result.get("response", {"text": "Sorry, I couldn't process your request."})
    except Exception as e:
        logger.error(f"Error processing text message: {e}")
        return {"text": f"Error processing your message: {str(e)}"}