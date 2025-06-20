import random

class SimpleAI:
    def __init__(self):
        self.memory = []
        self.name = "AI Assistant"
        self.user_name = None
        
    def respond(self, user_input: str) -> str:
        # Store the conversation
        self.memory.append(user_input)
        
        # Keep only last 10 messages
        if len(self.memory) > 10:
            self.memory.pop(0)
        
        user_input = user_input.lower().strip()
        
        # Handle name setting
        if "your name is" in user_input or "you are" in user_input:
            if "your name is" in user_input:
                name = user_input.split("your name is")[1].strip().replace(", from now on", "").replace("from now on", "")
            else:
                name = user_input.split("you are")[1].strip().replace(", from now on", "").replace("from now on", "")
            self.name = name.capitalize()
            return f"Got it! My name is {self.name} now."
        
        # Handle user name
        if "my name is" in user_input or "i am" in user_input:
            if "my name is" in user_input:
                name = user_input.split("my name is")[1].strip()
            else:
                name = user_input.split("i am")[1].strip()
            self.user_name = name.capitalize()
            return f"Nice to meet you, {self.user_name}! I'm {self.name}."
        
        # Handle questions about previous conversation
        if any(word in user_input for word in ["what did i say", "what did i said", "earlier", "before", "remember"]):
            if len(self.memory) > 1:
                prev_msg = self.memory[-2]
                return f"You said: '{prev_msg}'. Is that what you were asking about?"
            else:
                return "I don't remember you saying anything specific earlier."
        
        # Handle name questions
        if any(word in user_input for word in ["your name", "who are you", "what are you"]):
            if "only" in user_input or "just" in user_input:
                return self.name
            else:
                return f"I'm {self.name}! How can I help you?"
        
        # Handle understanding questions
        if any(word in user_input for word in ["do you understand", "understand me", "get it"]):
            return "Yes, I understand you! I'm listening and learning from our conversation."
        
        # Handle greetings
        if any(word in user_input for word in ["hello", "hi", "hey", "greetings"]):
            if self.user_name:
                return f"Hello {self.user_name}! How are you doing today?"
            else:
                return "Hello! I'm excited to chat with you. What's your name?"
        
        # Handle yes/positive responses
        if user_input in ["yes", "yesss", "yeah", "yep", "correct", "right"]:
            return "Great! I'm glad I understood correctly. What else would you like to talk about?"
        
        # Handle questions
        if "?" in user_input:
            return "That's a good question! I'm still learning, but I'd love to discuss it with you."
        
        # Default responses based on input
        if len(user_input) < 5:
            return "I see! Tell me more about that."
        else:
            return "That's interesting! I'm learning from everything you tell me. What else is on your mind?"