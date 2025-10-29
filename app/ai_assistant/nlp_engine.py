from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification
import torch
from typing import Dict, List, Optional
from .models import ExtractedEntities, Intent
import re

class NLPEngine:
    def __init__(self):
        """Initialize NLP engine with required models and pipelines."""
        # Initialize text generation model for intent understanding and response generation
        self.text_generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            max_length=128
        )
        
        # Initialize NER model for entity extraction
        self.ner_pipeline = pipeline(
            "token-classification",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
        
        # Define intent classification prompt template
        self.intent_prompt = """
        Classify the intent of this message into one of these categories:
        - buy_product: User wants to purchase something
        - check_availability: User wants to check if product is available
        - get_price: User wants to know the price
        - unknown: None of the above
        
        Message: {message}
        Intent:
        """

    def extract_size(self, text: str) -> Optional[str]:
        """Extract size information from text using regex patterns."""
        # Common size patterns
        size_patterns = {
            r'\b(XS|S|M|L|XL|XXL|XXXL)\b': lambda x: x,  # Clothing sizes
            r'\b(UK|US|EU)?\s*(\d{1,2}\.?\d?)\b': lambda x: x.group(2),  # Shoe sizes
        }
        
        for pattern, handler in size_patterns.items():
            match = re.search(pattern, text.upper())
            if match:
                return handler(match)
        return None

    def extract_quantity(self, text: str) -> int:
        """Extract quantity information from text."""
        quantity_patterns = [
            r'\b(\d+)\s*(pieces?|pcs?|items?)\b',
            r'\b(\d+)\b'
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return 1  # Default quantity

    def analyze_message(self, message: str) -> ExtractedEntities:
        """
        Analyze user message and extract relevant entities using AI models.
        
        Args:
            message: User's input message
            
        Returns:
            ExtractedEntities containing intent, product name, size, and quantity
        """
        # Use T5 model for intent classification
        intent_input = self.intent_prompt.format(message=message)
        intent_result = self.text_generator(intent_input, max_length=32)[0]['generated_text'].strip().lower()
        intent = Intent.UNKNOWN
        for possible_intent in Intent:
            if possible_intent.value in intent_result:
                intent = possible_intent
                break
        
        # Use BERT for named entity recognition
        ner_results = self.ner_pipeline(message)
        
        # Extract product information from NER results
        product_words = []
        for entity in ner_results:
            # Look for organizations (brands) and product types
            if entity['entity_group'] in ['ORG', 'MISC']:
                product_words.append(entity['word'])
        
        # Join product words and clean up
        product_name = ' '.join(product_words) if product_words else None
        if product_name:
            # Use T5 to clean and standardize product name
            clean_prompt = f"Convert this product mention to a standard product name: {product_name}"
            product_name = self.text_generator(clean_prompt, max_length=32)[0]['generated_text'].strip()
        
        # Extract size and quantity using regex + AI verification
        size = self.extract_size(message)
        if size:
            # Verify size with T5
            size_prompt = f"Is {size} a valid clothing or shoe size? Answer yes or no."
            size_valid = self.text_generator(size_prompt, max_length=32)[0]['generated_text'].strip().lower()
            if 'no' in size_valid:
                size = None
        
        quantity = self.extract_quantity(message)
        
        return ExtractedEntities(
            product_name=product_name,
            size=size,
            quantity=quantity,
            intent=intent
        )

    def _map_intent(self, raw_intent: str) -> Intent:
        """Map raw intent to Intent enum."""
        intent_mapping = {
            'buy': Intent.BUY_PRODUCT,
            'check': Intent.CHECK_AVAILABILITY,
            'price': Intent.GET_PRICE
        }
        
        for key, value in intent_mapping.items():
            if key in raw_intent.lower():
                return value
        return Intent.UNKNOWN