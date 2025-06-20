import re
import random
from typing import List, Dict, Any

class SmartTextProcessor:
    def __init__(self):
        self.vocabulary = set()
        self.conversation_history = []
        self.user_profile = {
            'name': None,
            'interests': {},
            'communication_style': 'neutral',
            'topics_discussed': []
        }
        
        self.knowledge_domains = {
            'technology': {
                'keywords': ['computer', 'ai', 'programming', 'software', 'code', 'tech', 'digital', 'internet'],
                'responses': [
                    "Technology is fascinating! I love discussing innovations and how they shape our world.",
                    "That's an interesting tech perspective. The digital landscape is constantly evolving.",
                    "From a technological standpoint, there are so many possibilities to explore."
                ]
            },
            'science': {
                'keywords': ['science', 'research', 'experiment', 'theory', 'physics', 'chemistry', 'biology'],
                'responses': [
                    "Science is amazing! The way we understand our universe keeps expanding.",
                    "That's a fascinating scientific concept. Research in this area is really advancing.",
                    "The scientific method helps us discover incredible things about reality."
                ]
            },
            'creativity': {
                'keywords': ['art', 'music', 'creative', 'design', 'imagination', 'story', 'write'],
                'responses': [
                    "Creativity is such a powerful force! I love how imagination can transform ideas.",
                    "That's beautifully creative thinking. Art and expression are so important.",
                    "Creative pursuits bring so much richness to life and human experience."
                ]
            },
            'learning': {
                'keywords': ['learn', 'study', 'education', 'knowledge', 'understand', 'teach', 'school'],
                'responses': [
                    "Learning is one of life's greatest adventures! Every new piece of knowledge opens doors.",
                    "I'm passionate about learning too. There's always something new to discover.",
                    "Education and growth are so valuable. What aspects interest you most?"
                ]
            }
        }
        
        self.personality_responses = {
            'curious': [
                "That's really intriguing! Can you tell me more about your thoughts on this?",
                "I'm curious about your perspective. What led you to think about this?",
                "That raises some interesting questions. How do you see this developing?"
            ],
            'supportive': [
                "I appreciate you sharing that with me. Your insights are valuable.",
                "That sounds meaningful to you. I'm here to listen and discuss.",
                "Thank you for opening up about this. Your experiences matter."
            ],
            'analytical': [
                "Let me think about this systematically. There are several factors to consider.",
                "That's a complex topic with multiple dimensions worth exploring.",
                "I find it helpful to break this down into key components."
            ],
            'enthusiastic': [
                "That's absolutely fascinating! I love how you're thinking about this!",
                "Wow, that's such an exciting way to look at it! Tell me more!",
                "I'm genuinely excited by your perspective on this topic!"
            ]
        }
    
    def analyze_message(self, text: str) -> Dict[str, Any]:
        analysis = {
            'intent': self._detect_intent(text),
            'sentiment': self._analyze_sentiment(text),
            'domain': self._identify_domain(text),
            'complexity': self._assess_complexity(text),
            'keywords': self._extract_keywords(text)
        }
        return analysis
    
    def _detect_intent(self, text: str) -> str:
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        elif any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            return 'question'
        elif any(word in text_lower for word in ['help', 'assist', 'support', 'can you']):
            return 'request'
        elif any(word in text_lower for word in ['think', 'believe', 'opinion', 'feel']):
            return 'opinion'
        elif any(word in text_lower for word in ['thanks', 'thank you', 'appreciate']):
            return 'gratitude'
        else:
            return 'statement'
    
    def _analyze_sentiment(self, text: str) -> str:
        positive_words = ['good', 'great', 'awesome', 'amazing', 'love', 'like', 'happy', 'excited', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'hate', 'sad', 'angry', 'disappointed', 'frustrated', 'awful']
        
        words = text.lower().split()
        positive_score = sum(1 for word in words if word in positive_words)
        negative_score = sum(1 for word in words if word in negative_words)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _identify_domain(self, text: str) -> str:
        text_lower = text.lower()
        
        for domain, data in self.knowledge_domains.items():
            if any(keyword in text_lower for keyword in data['keywords']):
                return domain
        return 'general'
    
    def _assess_complexity(self, text: str) -> str:
        word_count = len(text.split())
        unique_words = len(set(text.lower().split()))
        
        if word_count > 20 and unique_words > 15:
            return 'high'
        elif word_count > 10 and unique_words > 8:
            return 'medium'
        else:
            return 'low'
    
    def _extract_keywords(self, text: str) -> List[str]:
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'i', 'you', 'it', 'that', 'this'}
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def generate_intelligent_response(self, text: str) -> str:
        analysis = self.analyze_message(text)
        self.conversation_history.append({'input': text, 'analysis': analysis})
        
        # Update user profile
        self._update_user_profile(analysis)
        
        # Generate contextual response
        response = self._generate_contextual_response(text, analysis)
        
        # Add personality flavor
        response = self._add_personality(response, analysis)
        
        return response
    
    def _update_user_profile(self, analysis: Dict[str, Any]):
        domain = analysis['domain']
        if domain != 'general':
            if domain not in self.user_profile['interests']:
                self.user_profile['interests'][domain] = 0
            self.user_profile['interests'][domain] += 1
        
        self.user_profile['topics_discussed'].extend(analysis['keywords'])
    
    def _generate_contextual_response(self, text: str, analysis: Dict[str, Any]) -> str:
        intent = analysis['intent']
        domain = analysis['domain']
        sentiment = analysis['sentiment']
        
        # Check if user is asking about previous conversation
        if any(word in text.lower() for word in ['earlier', 'before', 'said', 'previous', 'remember']):
            return self._recall_previous_context(text)
        
        # Check if user is setting their name or identity
        if 'name is' in text.lower() or 'i am' in text.lower() or 'call me' in text.lower():
            return self._handle_identity(text)
        
        # Domain-specific responses
        if domain in self.knowledge_domains:
            base_response = random.choice(self.knowledge_domains[domain]['responses'])
        else:
            base_response = self._get_intent_response(intent, text)
        
        return base_response
    
    def _recall_previous_context(self, text: str) -> str:
        if len(self.conversation_history) < 2:
            return "I don't recall discussing anything specific earlier. What would you like to talk about?"
        
        # Get the last few messages
        recent_messages = [msg['input'] for msg in self.conversation_history[-3:]]
        context_summary = ' '.join(recent_messages)
        
        return f"Looking back at our conversation, you mentioned: '{recent_messages[-2] if len(recent_messages) > 1 else recent_messages[0]}'. Is that what you're referring to?"
    
    def _handle_identity(self, text: str) -> str:
        # Extract name or identity from text
        text_lower = text.lower()
        if 'name is' in text_lower:
            name_part = text_lower.split('name is')[1].strip()
            name = name_part.split()[0] if name_part else 'friend'
        elif 'i am' in text_lower:
            name_part = text_lower.split('i am')[1].strip()
            name = name_part.split()[0] if name_part else 'friend'
        elif 'call me' in text_lower:
            name_part = text_lower.split('call me')[1].strip()
            name = name_part.split()[0] if name_part else 'friend'
        else:
            name = 'friend'
        
        # Store in user profile
        self.user_profile['name'] = name.capitalize()
        
        return f"Nice to meet you, {name.capitalize()}! I'll remember that. How can I help you today?"
    
    def _get_intent_response(self, intent: str, text: str) -> str:
        responses = {
            'greeting': [
                "Hello! I'm excited to chat with you. What's on your mind today?",
                "Hi there! I'm here and ready for an engaging conversation.",
                "Hey! Great to connect with you. What would you like to explore?"
            ],
            'question': [
                "That's a thoughtful question! Let me share my perspective on this.",
                "Great question! I find this topic really interesting to think about.",
                "I love questions like this! They really make me think deeply."
            ],
            'request': [
                "I'd be happy to help you with that! Let me think about the best approach.",
                "Absolutely! I'm here to assist. Let's work through this together.",
                "Of course! I enjoy helping people figure things out."
            ],
            'opinion': [
                "I appreciate you sharing your thoughts with me. That's an interesting perspective.",
                "Your viewpoint is really valuable. I enjoy hearing different ways of thinking.",
                "That's a thoughtful way to look at it. I find your reasoning compelling."
            ],
            'gratitude': [
                "You're very welcome! I'm glad I could be helpful.",
                "It's my pleasure! I really enjoy our conversations.",
                "Thank you for saying that! It means a lot to me."
            ]
        }
        
        return random.choice(responses.get(intent, responses['question']))
    
    def _add_personality(self, response: str, analysis: Dict[str, Any]) -> str:
        # Choose personality based on context
        if analysis['complexity'] == 'high':
            personality = 'analytical'
        elif analysis['sentiment'] == 'positive':
            personality = 'enthusiastic'
        elif analysis['intent'] == 'question':
            personality = 'curious'
        else:
            personality = 'supportive'
        
        # Sometimes add a personality-flavored follow-up
        if random.random() < 0.3:  # 30% chance
            follow_up = random.choice(self.personality_responses[personality])
            response += " " + follow_up
        
        return response
    
    def get_conversation_insights(self) -> Dict[str, Any]:
        return {
            'total_messages': len(self.conversation_history),
            'user_interests': self.user_profile['interests'],
            'vocabulary_size': len(self.vocabulary),
            'recent_topics': self.user_profile['topics_discussed'][-10:] if self.user_profile['topics_discussed'] else []
        }