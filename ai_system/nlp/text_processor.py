import re
import random
from typing import List, Dict, Any

class TextProcessor:
    def __init__(self):
        self.vocabulary = set()
        self.word_patterns = {}
        self.response_templates = {
            'greeting': ['Hello!', 'Hi there!', 'Hey!', 'Greetings!'],
            'question': ['That\'s interesting!', 'Let me think about that...', 'Good question!'],
            'agreement': ['I agree!', 'Exactly!', 'That makes sense!'],
            'uncertainty': ['I\'m not sure about that', 'That\'s complex', 'I need to learn more'],
            'excitement': ['That\'s awesome!', 'Amazing!', 'Incredible!', 'Wow!']
        }
    
    def tokenize(self, text: str) -> List[str]:
        # Simple tokenization
        text = re.sub(r'[^\w\s]', '', text.lower())
        tokens = text.split()
        self.vocabulary.update(tokens)
        return tokens
    
    def analyze_sentiment(self, text: str) -> str:
        positive_words = ['good', 'great', 'awesome', 'amazing', 'love', 'like', 'happy', 'excited']
        negative_words = ['bad', 'terrible', 'hate', 'sad', 'angry', 'disappointed']
        
        tokens = self.tokenize(text)
        positive_count = sum(1 for word in tokens if word in positive_words)
        negative_count = sum(1 for word in tokens if word in negative_words)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def detect_intent(self, text: str) -> str:
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        elif '?' in text:
            return 'question'
        elif any(word in text_lower for word in ['yes', 'agree', 'correct', 'right']):
            return 'agreement'
        elif any(word in text_lower for word in ['wow', 'amazing', 'awesome', 'incredible']):
            return 'excitement'
        else:
            return 'statement'
    
    def generate_response(self, text: str, context: Dict[str, Any] = None) -> str:
        intent = self.detect_intent(text)
        sentiment = self.analyze_sentiment(text)
        
        # Choose response based on intent
        if intent in self.response_templates:
            base_response = random.choice(self.response_templates[intent])
        else:
            base_response = random.choice(self.response_templates['question'])
        
        # Add context-aware elements
        if context and 'topic' in context:
            base_response += f" Regarding {context['topic']}, "
        
        # Add sentiment-appropriate continuation
        if sentiment == 'positive':
            base_response += " I'm glad you're enthusiastic about this!"
        elif sentiment == 'negative':
            base_response += " I understand your concerns."
        
        return base_response
    
    def extract_keywords(self, text: str) -> List[str]:
        tokens = self.tokenize(text)
        # Simple keyword extraction (remove common words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        keywords = [word for word in tokens if word not in stop_words and len(word) > 2]
        return keywords
    
    def learn_pattern(self, input_text: str, response: str):
        keywords = self.extract_keywords(input_text)
        for keyword in keywords:
            if keyword not in self.word_patterns:
                self.word_patterns[keyword] = []
            self.word_patterns[keyword].append(response)