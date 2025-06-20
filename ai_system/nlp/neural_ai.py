import numpy as np
import json
import os
from collections import defaultdict

class NeuralAI:
    def __init__(self):
        self.vocab = {}
        self.vocab_size = 0
        self.embedding_dim = 50
        self.hidden_dim = 100
        self.output_dim = 50
        
        # Neural network weights
        self.W1 = np.random.randn(self.embedding_dim, self.hidden_dim) * 0.1
        self.b1 = np.zeros((1, self.hidden_dim))
        self.W2 = np.random.randn(self.hidden_dim, self.output_dim) * 0.1
        self.b2 = np.zeros((1, self.output_dim))
        
        # Word embeddings
        self.embeddings = {}
        
        # Conversation memory
        self.memory = []
        self.name = "AI"
        
        # Response patterns learned from training
        self.response_patterns = defaultdict(list)
        
        self.load_model()
    
    def add_to_vocab(self, word):
        if word not in self.vocab:
            self.vocab[word] = self.vocab_size
            self.vocab_size += 1
            # Initialize embedding for new word
            self.embeddings[word] = np.random.randn(self.embedding_dim) * 0.1
    
    def text_to_vector(self, text):
        """Convert text to vector representation"""
        words = text.lower().split()
        if not words:
            return np.zeros(self.embedding_dim)
        
        # Add words to vocabulary
        for word in words:
            self.add_to_vocab(word)
        
        # Average word embeddings
        vectors = [self.embeddings[word] for word in words if word in self.embeddings]
        if vectors:
            return np.mean(vectors, axis=0)
        return np.zeros(self.embedding_dim)
    
    def forward(self, input_vector):
        """Forward pass through neural network"""
        # Hidden layer
        z1 = np.dot(input_vector.reshape(1, -1), self.W1) + self.b1
        a1 = np.tanh(z1)  # Activation function
        
        # Output layer
        z2 = np.dot(a1, self.W2) + self.b2
        a2 = np.tanh(z2)
        
        return a2.flatten(), a1.flatten()
    
    def train_on_pair(self, input_text, target_text, learning_rate=0.01):
        """Train the network on input-output pair"""
        input_vec = self.text_to_vector(input_text)
        target_vec = self.text_to_vector(target_text)
        
        # Forward pass
        output, hidden = self.forward(input_vec)
        
        # Calculate loss (mean squared error)
        loss = np.mean((output - target_vec) ** 2)
        
        # Backward pass (simplified)
        output_error = output - target_vec
        
        # Update weights (simplified gradient descent)
        self.W2 -= learning_rate * np.outer(hidden, output_error)
        self.b2 -= learning_rate * output_error.reshape(1, -1)
        
        # Update word embeddings based on usage
        words = input_text.lower().split()
        for word in words:
            if word in self.embeddings:
                self.embeddings[word] -= learning_rate * 0.001 * output_error[:self.embedding_dim]
        
        return loss
    
    def generate_response(self, user_input):
        """Generate response using neural network"""
        self.memory.append(user_input)
        if len(self.memory) > 10:
            self.memory.pop(0)
        
        # Handle specific patterns first
        response = self.handle_patterns(user_input)
        if response:
            # Train on this interaction
            self.train_on_pair(user_input, response)
            return response
        
        # Use neural network to generate response
        input_vec = self.text_to_vector(user_input)
        output_vec, _ = self.forward(input_vec)
        
        # Find closest response pattern
        response = self.vector_to_response(output_vec, user_input)
        
        # Learn from this interaction
        self.train_on_pair(user_input, response)
        
        return response
    
    def handle_patterns(self, user_input):
        """Handle specific conversation patterns"""
        user_lower = user_input.lower().strip()
        
        if "your name is" in user_lower:
            name = user_input.split("your name is")[1].strip()
            self.name = name.capitalize()
            return f"I understand. My name is {self.name}."
        
        if any(phrase in user_lower for phrase in ["your name", "who are you"]):
            return f"I am {self.name}."
        
        if any(phrase in user_lower for phrase in ["what did i say", "remember"]):
            if len(self.memory) > 1:
                return f"You said: '{self.memory[-2]}'"
            return "I don't have previous context."
        
        if "do you understand" in user_lower:
            return "I'm learning to understand through our conversation."
        
        if any(phrase in user_lower for phrase in ["hello", "hi", "hey"]):
            return "Hello! I'm learning from our conversation."
        
        if "what's my name" in user_lower or "my name" in user_lower:
            return "I don't know your name yet. What should I call you?"
        
        if "yes" in user_lower or "no" in user_lower:
            return "I see. Thank you for clarifying."
        
        return None
    
    def vector_to_response(self, output_vec, original_input):
        """Convert output vector to text response"""
        # This is where real AI would use sophisticated decoding
        # For now, we'll use pattern matching with learned context
        
        words = original_input.lower().split()
        
        # Generate contextual response based on input analysis
        if len(words) == 1:
            return f"Tell me more about {words[0]}."
        
        if "?" in original_input:
            return "That's a thoughtful question. I'm processing it."
        
        if any(word in words for word in ["what", "how", "why", "when", "where"]):
            return "I'm analyzing your question and learning from it."
        
        # Default learning response
        responses = [
            "I'm processing that information.",
            "That's interesting input for my learning.",
            "I'm building understanding from what you said.",
            "Your input is helping me learn patterns.",
            "I'm analyzing the context of our conversation."
        ]
        
        # Use output vector to select response (simplified)
        idx = int(abs(np.sum(output_vec)) * len(responses)) % len(responses)
        return responses[idx]
    
    def save_model(self):
        """Save the neural network model"""
        try:
            model_data = {
                'vocab': self.vocab,
                'embeddings': {k: v.tolist() for k, v in self.embeddings.items()},
                'W1': self.W1.tolist(),
                'b1': self.b1.tolist(),
                'W2': self.W2.tolist(),
                'b2': self.b2.tolist(),
                'name': self.name,
                'vocab_size': self.vocab_size
            }
            with open('neural_model.json', 'w') as f:
                json.dump(model_data, f)
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self):
        """Load previously trained model"""
        try:
            if os.path.exists('neural_model.json'):
                with open('neural_model.json', 'r') as f:
                    data = json.load(f)
                
                self.vocab = data.get('vocab', {})
                self.vocab_size = data.get('vocab_size', 0)
                self.name = data.get('name', 'AI')
                
                # Load embeddings
                embeddings_data = data.get('embeddings', {})
                self.embeddings = {k: np.array(v) for k, v in embeddings_data.items()}
                
                # Load network weights
                if 'W1' in data:
                    self.W1 = np.array(data['W1'])
                    self.b1 = np.array(data['b1'])
                    self.W2 = np.array(data['W2'])
                    self.b2 = np.array(data['b2'])
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def get_stats(self):
        """Get learning statistics"""
        return {
            'vocabulary_size': self.vocab_size,
            'conversations': len(self.memory),
            'name': self.name,
            'neural_weights_sum': float(np.sum(self.W1) + np.sum(self.W2))
        }