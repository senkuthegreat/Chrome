import random
import json
import os

class LearningAI:
    def __init__(self):
        self.knowledge = {}
        self.patterns = {}
        self.context = []
        self.name = "AI"
        self.personality = {
            'curiosity': 0.7,
            'helpfulness': 0.8,
            'creativity': 0.6
        }
        self.load_knowledge()
    
    def learn_from_input(self, user_input, context_before=None):
        """Learn patterns and associations from user input"""
        words = user_input.lower().split()
        
        # Learn word associations
        for i, word in enumerate(words):
            if word not in self.knowledge:
                self.knowledge[word] = {'frequency': 0, 'associations': {}, 'contexts': []}
            
            self.knowledge[word]['frequency'] += 1
            self.knowledge[word]['contexts'].append(user_input)
            
            # Learn word-to-word associations
            if i > 0:
                prev_word = words[i-1]
                if prev_word not in self.knowledge[word]['associations']:
                    self.knowledge[word]['associations'][prev_word] = 0
                self.knowledge[word]['associations'][prev_word] += 1
    
    def generate_response(self, user_input):
        """Generate response based on learned patterns"""
        self.context.append(user_input)
        if len(self.context) > 5:
            self.context.pop(0)
        
        self.learn_from_input(user_input)
        
        # Handle specific patterns
        response = self.handle_specific_patterns(user_input)
        if response:
            return response
        
        # Generate creative response based on learned knowledge
        return self.generate_creative_response(user_input)
    
    def handle_specific_patterns(self, user_input):
        """Handle specific conversation patterns"""
        user_lower = user_input.lower().strip()
        
        # Name setting
        if "your name is" in user_lower:
            name = user_input.split("your name is")[1].strip()
            self.name = name.capitalize()
            return f"I'll remember that. My name is {self.name}."
        
        # Name asking
        if any(phrase in user_lower for phrase in ["your name", "who are you"]):
            return f"I'm {self.name}."
        
        # Memory recall
        if any(phrase in user_lower for phrase in ["what did i say", "remember", "earlier"]):
            if len(self.context) > 1:
                return f"You said: '{self.context[-2]}'"
            return "I don't recall our earlier conversation."
        
        # Learning questions
        if "do you understand" in user_lower:
            return "Yes, I'm learning from everything you tell me."
        
        return None
    
    def generate_creative_response(self, user_input):
        """Generate response using learned patterns"""
        words = user_input.lower().split()
        
        # Find most relevant words from knowledge
        relevant_words = []
        for word in words:
            if word in self.knowledge and self.knowledge[word]['frequency'] > 1:
                relevant_words.append(word)
        
        if relevant_words:
            # Use learned associations to build response
            chosen_word = random.choice(relevant_words)
            associations = self.knowledge[chosen_word]['associations']
            
            if associations:
                # Build response using word associations
                response_words = [chosen_word]
                current_word = chosen_word
                
                for _ in range(3):  # Build 3-4 word phrases
                    if current_word in self.knowledge and self.knowledge[current_word]['associations']:
                        next_word = max(self.knowledge[current_word]['associations'].items(), 
                                      key=lambda x: x[1])[0]
                        response_words.append(next_word)
                        current_word = next_word
                    else:
                        break
                
                if len(response_words) > 1:
                    return f"Interesting that you mention {chosen_word}. I've been thinking about {' '.join(response_words[1:])}."
        
        # Fallback responses that show learning
        learning_responses = [
            f"I'm processing what you said about {words[0] if words else 'that'}. Tell me more.",
            f"That's new information for me. I'm learning from this conversation.",
            f"I'm building my understanding. What else can you tell me?",
            f"Your input is helping me learn. Can you elaborate?",
            f"I'm connecting this to what we discussed before. Continue please."
        ]
        
        return random.choice(learning_responses)
    
    def save_knowledge(self):
        """Save learned knowledge to file"""
        try:
            with open('ai_knowledge.json', 'w') as f:
                json.dump({
                    'knowledge': self.knowledge,
                    'patterns': self.patterns,
                    'name': self.name,
                    'personality': self.personality
                }, f)
        except:
            pass
    
    def load_knowledge(self):
        """Load previously learned knowledge"""
        try:
            if os.path.exists('ai_knowledge.json'):
                with open('ai_knowledge.json', 'r') as f:
                    data = json.load(f)
                    self.knowledge = data.get('knowledge', {})
                    self.patterns = data.get('patterns', {})
                    self.name = data.get('name', 'AI')
                    self.personality = data.get('personality', self.personality)
        except:
            pass
    
    def get_learning_stats(self):
        """Get statistics about what the AI has learned"""
        return {
            'words_learned': len(self.knowledge),
            'total_interactions': sum(word_data['frequency'] for word_data in self.knowledge.values()),
            'name': self.name,
            'context_size': len(self.context)
        }