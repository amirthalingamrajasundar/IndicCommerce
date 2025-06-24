"""
Intent Classification Test Script

This script tests the intent identification functionality by directly implementing
the intent classification logic from ecom_agent.py and running various user inputs
through it to calculate classification accuracy.

Usage:
    python intent_classification_test.py --llm gpt-4o-mini
    python intent_classification_test.py --llm sarvam

Results will be saved with the LLM name in the filename.
"""

import os
import sys
import json
import pandas as pd
from tqdm import tqdm
import logging
from typing import Dict, List, Tuple, Any
import time
import argparse
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file and clean them
load_dotenv()

# Helper function to get clean environment variables
def get_clean_env(key, default=""):
    """Get environment variable and strip any whitespace or newlines."""
    value = os.environ.get(key, default)
    if value:
        return value.strip()
    return default

# Set up argument parser for LLM selection
parser = argparse.ArgumentParser(description="Test intent classification with different LLMs")
parser.add_argument("--llm", type=str, choices=["gpt-4o-mini", "sarvam"], default="gpt-4o-mini",
                    help="LLM to use for classification (gpt-4o-mini or sarvam)")

# Parse arguments
args = parser.parse_args()
selected_llm = args.llm

# Configure OpenAI client if using OpenAI models
if selected_llm == "gpt-4o-mini":
    openai_api_key = get_clean_env("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_api_key)
    llmmodel = "gpt-4o-mini"

# Sarvam API details if using Sarvam - will be fetched when needed
# using get_clean_env()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Standard formatting of numbers is used throughout

class MockAgentState(dict):
    """Mock AgentState class to simulate the agent state."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get(self, key, default=None):
        return super().get(key, default)

def identify_intent_node(state: dict) -> Dict[str, Any]:
    """Identify the specific intent of the user query"""
    logger.info("Identifying user intent using LLM: {}".format(selected_llm))
    
    english_query = state.get("english_query", "")
    user_language = state.get("user_language", "en-IN")
    
    if not english_query:
        logger.error("No query found for intent identification")
        return {"error_message": "No query found for intent identification"}
    
    # System prompt for classification
    system_prompt = """You are an intent classifier for an Indian e-commerce platform. Classify the query into one of these categories:
1. product_query: User is searching for or asking about products to purchase
2. summarize_cart: User wants summarize all the existing product added the cart currently
3. cart_update: User wants to add or remove products from their shopping cart
4.initiate_payment: User wants to initiate payment for their order
5. general_info: User is asking general questions about policies, availability, etc.

Consider Indian e-commerce context like 'Cash on Delivery', Indian brands, and regional preferences."""
    
    # User prompt
    lang_note = f"The original query was in {user_language}" if user_language != "en-IN" and user_language != "en" else ""
    user_prompt = f"Query: {english_query} {lang_note}\n\nClassify this query into one of the 5 categories. Reply with JSON containing:\n- intent_type (string: 'product_query', 'summarize_cart', 'cart_update', 'initiate_payment', or 'general_info')\n- confidence (number between 0-1)\n- search_terms (string, relevant only for product_query)\n- product_id (string, relevant only for cart_update, empty string if not found)\n- cart_action (string, 'add' or 'remove', relevant only for cart_update, empty string if not applicable)\n- quantity (number, relevant only for cart_update, default to 1)"
    
    try:
        if selected_llm == "gpt-4o-mini":
            # Use OpenAI API for classification
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = client.chat.completions.create(
                model=llmmodel, 
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            intent_data = json.loads(response.choices[0].message.content)
        
        elif selected_llm == "sarvam":
            # Use Sarvam AI API for classification
            sarvam_url = "https://api.sarvam.ai/v1/chat/completions"
            
            # Get clean API key from environment
            api_key = get_clean_env("SARVAM_API_KEY")
            if not api_key:
                raise ValueError("SARVAM_API_KEY not found in environment variables")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "model": "sarvam-m",  # Correct model name for Sarvam API
                "max_tokens": 500
            }
            
            try:
                response = requests.post(sarvam_url, headers=headers, json=payload)
                response.raise_for_status()  # Raise exception for HTTP errors
                response_data = response.json()
                intent_data = json.loads(response_data["choices"][0]["message"]["content"])
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error when calling Sarvam API: {e}")
                logger.error(f"Response content: {response.text}")
                raise
            except Exception as e:
                logger.error(f"Error using Sarvam API: {e}")
                raise
        
        # Process the response (common for both LLMs)
        confidence = intent_data.get("confidence", 0.0)
        intent_type = intent_data.get("intent_type", "")
        product_id = intent_data.get("product_id", "")
        cart_action = intent_data.get("cart_action", "add")
        quantity = intent_data.get("quantity", 1)
        
        logger.info(f"Intent classification: Type = {intent_type}, Confidence = {confidence}")
        if intent_type == "cart_update":
            logger.info(f"Cart update: Action = {cart_action}, Product ID = {product_id}, Quantity = {quantity}")
        
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
        return {
            "error_message": f"Error in intent classification: {e}"
        }

def run_intent_classification(query: str, user_language: str = "en-IN") -> Dict[str, Any]:
    """
    Run the intent classification on a given query.
    
    Args:
        query: The query text to classify
        user_language: The language of the user
        
    Returns:
        Dictionary containing classification results
    """
    # Create a mock state object
    state = MockAgentState()
    state["english_query"] = query
    state["user_language"] = user_language
    
    # Call the intent identification node
    try:
        result = identify_intent_node(state)
        # If there's an error, handle it
        if "error_message" in result:
            logger.error(f"Error in classification: {result['error_message']}")
            return {
                "intent_type": "error",
                "confidence": 0.0,
                "error": result["error_message"]
            }
        return result
    except Exception as e:
        logger.error(f"Exception in classification: {e}")
        return {
            "intent_type": "error",
            "confidence": 0.0,
            "error": str(e)
        }

def generate_test_cases() -> List[Dict[str, str]]:
    """
    Generate a list of test cases with queries and expected intents.
    
    Returns:
        List of dictionaries, each containing a query and its expected intent
    """
    test_cases = [
        # Product queries - 15 test cases
        {"query": "I want to buy a new phone", "expected_intent": "product_query"},
        {"query": "Show me red sarees", "expected_intent": "product_query"},
        {"query": "What are the best laptops under 50000 rupees?", "expected_intent": "product_query"},
        {"query": "Do you have Nike shoes?", "expected_intent": "product_query"},
        {"query": "I'm looking for kitchen appliances", "expected_intent": "product_query"},
        {"query": "Show me Banarasi silk sarees", "expected_intent": "product_query"},
        {"query": "Search for Patanjali products", "expected_intent": "product_query"},
        {"query": "I need a washing machine with dryer", "expected_intent": "product_query"},
        {"query": "Are OnePlus mobiles available?", "expected_intent": "product_query"},
        {"query": "Show me cotton kurtas for men", "expected_intent": "product_query"},
        {"query": "Find me good quality spices", "expected_intent": "product_query"},
        {"query": "Do you sell Ayurvedic medicines?", "expected_intent": "product_query"},
        {"query": "Looking for gold jewelry", "expected_intent": "product_query"},
        {"query": "I need a good pressure cooker", "expected_intent": "product_query"},
        {"query": "Show me Diwali gift hampers", "expected_intent": "product_query"},
        
        # Cart update queries - 12 test cases
        {"query": "Add this product to my cart", "expected_intent": "cart_update"},
        {"query": "Remove the blue shirt from my cart", "expected_intent": "cart_update"},
        {"query": "I want to buy 3 of these", "expected_intent": "cart_update"},
        {"query": "Please add 2 more of this item", "expected_intent": "cart_update"},
        {"query": "Delete all items from my cart", "expected_intent": "cart_update"},
        {"query": "Increase the quantity of rice to 5kg", "expected_intent": "cart_update"},
        {"query": "Remove Himalaya face wash from cart", "expected_intent": "cart_update"},
        {"query": "I'd like to add this dupatta to my cart", "expected_intent": "cart_update"},
        {"query": "Add a dozen bananas to my order", "expected_intent": "cart_update"},
        {"query": "Put this masala in my basket", "expected_intent": "cart_update"},
        {"query": "I don't want the Haldiram's snacks anymore", "expected_intent": "cart_update"},
        {"query": "Change quantity of dal to 2kg", "expected_intent": "cart_update"},
        
        # Summarize cart queries - 10 test cases
        {"query": "What's in my cart?", "expected_intent": "summarize_cart"},
        {"query": "Show me my shopping cart", "expected_intent": "summarize_cart"},
        {"query": "Can you tell me what I've added so far?", "expected_intent": "summarize_cart"},
        {"query": "List all items in my cart", "expected_intent": "summarize_cart"},
        {"query": "What is my cart total?", "expected_intent": "summarize_cart"},
        {"query": "How many items are in my basket?", "expected_intent": "summarize_cart"},
        {"query": "Show me the contents of my cart", "expected_intent": "summarize_cart"},
        {"query": "What am I buying today?", "expected_intent": "summarize_cart"},
        {"query": "Review my shopping list", "expected_intent": "summarize_cart"},
        {"query": "What's the total cost of my items?", "expected_intent": "summarize_cart"},
        
        # Payment queries - 12 test cases
        {"query": "I want to checkout", "expected_intent": "initiate_payment"},
        {"query": "Process my payment", "expected_intent": "initiate_payment"},
        {"query": "Pay with cash on delivery", "expected_intent": "initiate_payment"},
        {"query": "Can I pay using UPI?", "expected_intent": "initiate_payment"},
        {"query": "Complete my order", "expected_intent": "initiate_payment"},
        {"query": "Proceed to payment", "expected_intent": "initiate_payment"},
        {"query": "I want to pay through PhonePe", "expected_intent": "initiate_payment"},
        {"query": "Do you accept RuPay cards?", "expected_intent": "initiate_payment"},
        {"query": "Is Bharat QR payment available?", "expected_intent": "initiate_payment"},
        {"query": "I'd like to use my SBI debit card", "expected_intent": "initiate_payment"},
        {"query": "Does COD have extra charges?", "expected_intent": "initiate_payment"},
        {"query": "I want to use EMI option", "expected_intent": "initiate_payment"},
        
        # General info queries - 15 test cases
        {"query": "What is your return policy?", "expected_intent": "general_info"},
        {"query": "How long does shipping take?", "expected_intent": "general_info"},
        {"query": "Do you deliver to Chennai?", "expected_intent": "general_info"},
        {"query": "Is COD available?", "expected_intent": "general_info"},
        {"query": "How to contact customer service?", "expected_intent": "general_info"},
        {"query": "What are your store timings?", "expected_intent": "general_info"},
        {"query": "Do you have any Diwali offers?", "expected_intent": "general_info"},
        {"query": "How do I track my order?", "expected_intent": "general_info"},
        {"query": "What is the warranty period for electronics?", "expected_intent": "general_info"},
        {"query": "Do you have any offline stores in Mumbai?", "expected_intent": "general_info"},
        {"query": "Is there a minimum order value for free shipping?", "expected_intent": "general_info"},
        {"query": "How can I return a damaged product?", "expected_intent": "general_info"},
        {"query": "Do you ship internationally?", "expected_intent": "general_info"},
        {"query": "What's your GST number?", "expected_intent": "general_info"},
        {"query": "Are you open during lockdown?", "expected_intent": "general_info"},
        
        # Edge cases and ambiguous queries - 6 test cases
        {"query": "I like this", "expected_intent": "product_query"},
        {"query": "Can you help me?", "expected_intent": "general_info"},
        {"query": "Yes", "expected_intent": "general_info"},
        {"query": "No", "expected_intent": "general_info"},
        {"query": "Maybe", "expected_intent": "general_info"},
        {"query": "", "expected_intent": "error"}
    ]
    
    # Add regional language examples - 10 test cases
    regional_test_cases = [
        # Hindi queries
        {"query": "मुझे एक नया फोन चाहिए", "expected_intent": "product_query", "language": "hi-IN"},
        {"query": "मेरे कार्ट में क्या है?", "expected_intent": "summarize_cart", "language": "hi-IN"},
        {"query": "इसे मेरे कार्ट में डालें", "expected_intent": "cart_update", "language": "hi-IN"},
        {"query": "ऑर्डर पूरा करें", "expected_intent": "initiate_payment", "language": "hi-IN"},
        
        # Tamil queries
        {"query": "என் கார்ட்டில் என்ன இருக்கிறது?", "expected_intent": "summarize_cart", "language": "ta-IN"},
        {"query": "புதிய மொபைல் போன் வாங்க விரும்புகிறேன்", "expected_intent": "product_query", "language": "ta-IN"},
        
        # Telugu queries
        {"query": "ఈ ఉత్పత్తిని నా కార్ట్‌కి జోడించండి", "expected_intent": "cart_update", "language": "te-IN"},
        
        # Malayalam queries
        {"query": "തിരിച്ചയയ്ക്കൽ നയം എന്താണ്?", "expected_intent": "general_info", "language": "ml-IN"},
        
        # Bengali queries
        {"query": "আমি একটি নতুন মোবাইল কিনতে চাই", "expected_intent": "product_query", "language": "bn-IN"},
        {"query": "আমার কার্টে কী কী আছে?", "expected_intent": "summarize_cart", "language": "bn-IN"}
    ]
    
    # Add the regional test cases with language information
    for case in regional_test_cases:
        test_cases.append({
            "query": case["query"],
            "expected_intent": case["expected_intent"],
            "language": case["language"]
        })
    
    return test_cases

def evaluate_classification(test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Run the test cases and evaluate the classification accuracy.
    
    Args:
        test_cases: List of test cases
        
    Returns:
        Dictionary with accuracy metrics
    """
    results = []
    correct_count = 0
    total_count = len(test_cases)
    
    # Track regional test cases separately
    regional_results = []
    
    # Run each test case
    for i, test_case in enumerate(tqdm(test_cases, desc="Processing test cases")):
        query = test_case["query"]
        expected_intent = test_case["expected_intent"]
        language = test_case.get("language", "en-IN")
        
        # Run the classification
        result = run_intent_classification(query, language)
        actual_intent = result.get("intent_type", "error")
        confidence = result.get("confidence", 0.0)
        
        # Check if the classification is correct
        is_correct = (actual_intent == expected_intent)
        if is_correct:
            correct_count += 1
        
        # Create result entry
        result_entry = {
            "query": query,
            "language": language,
            "expected_intent": expected_intent,
            "actual_intent": actual_intent,
            "confidence": confidence,
            "is_correct": is_correct
        }
        
        # Store the result
        results.append(result_entry)
        
        # If it's a regional test case, store it separately as well
        if language != "en-IN" and language != "en":
            regional_results.append(result_entry)
        
        # Add a small delay to avoid rate limiting
        if i < total_count - 1:
            time.sleep(0.5)
    
    # Calculate overall accuracy
    accuracy = correct_count / total_count if total_count > 0 else 0
    
    # Intent types used in the system
    intent_types = ["product_query", "cart_update", "summarize_cart", "initiate_payment", "general_info", "error"]
    
    # Calculate per-class metrics
    class_metrics = {}
    
    # Variables for precision, recall, F1 scores
    true_positives = {intent: 0 for intent in intent_types}
    false_positives = {intent: 0 for intent in intent_types}
    false_negatives = {intent: 0 for intent in intent_types}
    
    for intent_type in intent_types:
        # Filter results for this intent type
        class_results = [r for r in results if r["expected_intent"] == intent_type]
        if not class_results:
            continue
            
        correct_for_class = sum(1 for r in class_results if r["is_correct"])
        class_accuracy = correct_for_class / len(class_results) if class_results else 0
        
        class_metrics[intent_type] = {
            "count": len(class_results),
            "correct": correct_for_class,
            "accuracy": class_accuracy
        }
        
        # Calculate true positives and false negatives for this class
        true_positives[intent_type] = sum(1 for r in results 
                                         if r["expected_intent"] == intent_type 
                                         and r["actual_intent"] == intent_type)
        false_negatives[intent_type] = sum(1 for r in results 
                                          if r["expected_intent"] == intent_type 
                                          and r["actual_intent"] != intent_type)
    
    # Calculate false positives
    for intent_type in intent_types:
        false_positives[intent_type] = sum(1 for r in results 
                                          if r["expected_intent"] != intent_type 
                                          and r["actual_intent"] == intent_type)
    
    # Calculate precision, recall, F1 for each class
    precision = {}
    recall = {}
    f1_score = {}
    
    for intent_type in intent_types:
        tp = true_positives[intent_type]
        fp = false_positives[intent_type]
        fn = false_negatives[intent_type]
        
        precision[intent_type] = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall[intent_type] = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # Calculate F1 score
        if precision[intent_type] + recall[intent_type] > 0:
            f1_score[intent_type] = 2 * (precision[intent_type] * recall[intent_type]) / \
                                  (precision[intent_type] + recall[intent_type])
        else:
            f1_score[intent_type] = 0
    
    # Calculate macro-average precision, recall, F1
    non_zero_intents = [intent for intent in intent_types if 
                       (true_positives[intent] + false_positives[intent] > 0) and 
                       (true_positives[intent] + false_negatives[intent] > 0)]
    
    if non_zero_intents:
        macro_precision = sum(precision[i] for i in non_zero_intents) / len(non_zero_intents)
        macro_recall = sum(recall[i] for i in non_zero_intents) / len(non_zero_intents)
        
        if macro_precision + macro_recall > 0:
            macro_f1 = 2 * (macro_precision * macro_recall) / (macro_precision + macro_recall)
        else:
            macro_f1 = 0
    else:
        macro_precision = macro_recall = macro_f1 = 0
    
    # Calculate confusion matrix
    confusion_matrix = {}
    for actual in intent_types:
        confusion_matrix[actual] = {}
        for predicted in intent_types:
            confusion_matrix[actual][predicted] = 0
    
    # Fill confusion matrix
    for result in results:
        expected = result["expected_intent"]
        actual = result["actual_intent"]
        if expected in confusion_matrix and actual in confusion_matrix[expected]:
            confusion_matrix[expected][actual] += 1
    
    # Calculate regional metrics
    regional_metrics = {}
    if regional_results:
        regional_correct = sum(1 for r in regional_results if r["is_correct"])
        regional_accuracy = regional_correct / len(regional_results) if regional_results else 0
        
        # Group by language
        language_metrics = {}
        languages = set(r["language"] for r in regional_results)
        
        for lang in languages:
            lang_results = [r for r in regional_results if r["language"] == lang]
            lang_correct = sum(1 for r in lang_results if r["is_correct"])
            lang_accuracy = lang_correct / len(lang_results) if lang_results else 0
            
            language_metrics[lang] = {
                "count": len(lang_results),
                "correct": lang_correct,
                "accuracy": lang_accuracy
            }
        
        regional_metrics = {
            "total": len(regional_results),
            "correct": regional_correct,
            "accuracy": regional_accuracy,
            "by_language": language_metrics
        }
    
    return {
        "total_cases": total_count,
        "correct_classifications": correct_count,
        "overall_accuracy": accuracy,
        "class_metrics": class_metrics,
        "confusion_matrix": confusion_matrix,
        "detailed_results": results,
        "regional_metrics": regional_metrics,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1
    }

def format_results(evaluation_results: Dict[str, Any]) -> str:
    """
    Format the evaluation results as a readable string.
    
    Args:
        evaluation_results: The evaluation results dictionary
        
    Returns:
        Formatted string with the results
    """
    total_cases = evaluation_results["total_cases"]
    correct = evaluation_results["correct_classifications"]
    accuracy = evaluation_results["overall_accuracy"] * 100
    
    result_str = f"Intent Classification Test Results - {selected_llm.upper()}\n"
    result_str += f"=" * (36 + len(selected_llm)) + "\n\n"
    result_str += f"LLM: {selected_llm}\n"
    result_str += f"Total test cases: {total_cases}\n"
    result_str += f"Correct classifications: {correct}\n"
    result_str += f"Overall accuracy: {accuracy:.2f}%\n\n"
    
    # Add overall precision, recall, F1 scores
    result_str += "Overall Performance Metrics:\n"
    result_str += "-------------------------\n"
    result_str += f"Macro Precision: {evaluation_results['macro_precision']:.4f}\n"
    result_str += f"Macro Recall: {evaluation_results['macro_recall']:.4f}\n"
    result_str += f"Macro F1 Score: {evaluation_results['macro_f1']:.4f}\n\n"
    
    # Class-wise metrics
    result_str += "Class-wise Metrics:\n"
    result_str += "------------------\n"
    result_str += f"{'Intent Type':<20}{'Accuracy':<10}{'Precision':<10}{'Recall':<10}{'F1 Score':<10}{'Support':<10}\n"
    result_str += "-" * 70 + "\n"
    
    for intent_type, metrics in evaluation_results["class_metrics"].items():
        count = metrics["count"]
        correct = metrics["correct"]
        class_acc = metrics["accuracy"] * 100
        precision = evaluation_results["precision"][intent_type] * 100
        recall = evaluation_results["recall"][intent_type] * 100
        f1 = evaluation_results["f1_score"][intent_type] * 100
        
        result_str += f"{intent_type:<20}{class_acc:.2f}%{precision:.2f}%{recall:.2f}%{f1:.2f}%{count:<10}\n"
    
    # Regional metrics if available
    if "regional_metrics" in evaluation_results and evaluation_results["regional_metrics"]:
        regional_metrics = evaluation_results["regional_metrics"]
        result_str += "\nRegional Language Performance:\n"
        result_str += "----------------------------\n"
        result_str += f"Total regional test cases: {regional_metrics['total']}\n"
        result_str += f"Correct classifications: {regional_metrics['correct']}\n"
        result_str += f"Overall regional accuracy: {regional_metrics['accuracy']*100:.2f}%\n\n"
        
        result_str += "Performance by Language:\n"
        result_str += "---------------------\n"
        result_str += f"{'Language':<10}{'Accuracy':<10}{'Support':<10}\n"
        result_str += "-" * 30 + "\n"
        for lang, lang_metrics in regional_metrics["by_language"].items():
            result_str += f"{lang:<10}{lang_metrics['accuracy']*100:.2f}%{lang_metrics['count']:<10}\n"
        
    # Add confusion matrix
    result_str += "\nConfusion Matrix:\n"
    result_str += "---------------\n"
    confusion_matrix = evaluation_results["confusion_matrix"]
    intent_types = list(confusion_matrix.keys())
    
    # Header row
    result_str += f"{'Actual\\Predicted':<20}"
    for predicted in intent_types:
        result_str += f"{predicted:<15}"
    result_str += "\n"
    
    # Data rows
    for actual in intent_types:
        result_str += f"{actual:<20}"
        for predicted in intent_types:
            value = confusion_matrix[actual].get(predicted, 0)
            result_str += f"{value:<15}"
        result_str += "\n"
    
    return result_str

def save_results(evaluation_results: Dict[str, Any], output_path: str = "intent_classification_results.json"):
    """
    Save the evaluation results to files.
    
    Args:
        evaluation_results: The evaluation results dictionary
        output_path: Path to save the results
    """
    # Add LLM name to the output paths
    llm_specific_path = output_path.replace(".json", f"_{selected_llm}.json")
    
    # Make sure directory exists
    output_dir = os.path.dirname(llm_specific_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Save the detailed results as JSON
    with open(llm_specific_path, "w") as f:
        json.dump(evaluation_results, f, indent=2)
    
    # Save the detailed results as a CSV for easier analysis
    pd.DataFrame(evaluation_results["detailed_results"]).to_csv(
        llm_specific_path.replace(".json", ".csv"), index=False
    )
    
    # Save the formatted results as a text file
    with open(llm_specific_path.replace(".json", ".txt"), "w") as f:
        f.write(format_results(evaluation_results))
    
    logger.info(f"Results saved to {llm_specific_path} and related files")

def main():
    """Main function to run the intent classification test."""
    logger.info(f"Starting intent classification test using {selected_llm} LLM")
    
    # Check for API keys based on selected LLM
    if selected_llm == "gpt-4o-mini" and not get_clean_env("OPENAI_API_KEY"):
        logger.error("OpenAI API key not found in environment variables. Please set OPENAI_API_KEY.")
        return
    
    if selected_llm == "sarvam" and not get_clean_env("SARVAM_API_KEY"):
        logger.error("Sarvam API key not found in environment variables. Please set SARVAM_API_KEY.")
        return
        
    # Generate test cases
    test_cases = generate_test_cases()
    logger.info(f"Generated {len(test_cases)} test cases")
    
    # Evaluate the classification
    evaluation_results = evaluate_classification(test_cases)
    
    # Format and display the results
    formatted_results = format_results(evaluation_results)
    print("\n" + formatted_results)
    
    # Save the results with LLM name in the filename (in current directory)
    save_results(evaluation_results, f"intent_classification_results.json")
    
    logger.info(f"Intent classification test with {selected_llm} completed successfully")
    logger.info(f"Results are saved in the current directory with prefix '{selected_llm}'")



if __name__ == "__main__":
    main()
