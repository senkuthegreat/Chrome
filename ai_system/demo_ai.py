import time
import threading
from core.neural_network import SimpleNeuralNetwork
from memory.memory_system import MemorySystem
from nlp.text_processor import TextProcessor

class DemoAI:
    def __init__(self):
        self.neural_network = SimpleNeuralNetwork(input_size=100, hidden_size=50, output_size=10)
        self.memory = MemorySystem()
        self.text_processor = TextProcessor()
        
        self.is_running = False
        self.learning_mode = True
        
        # Load existing memory if available
        self.memory.load_memory('ai_memory.json')
        
        print("🤖 AI System initialized!")
        print("📚 Learning mode: ON")
        print("🧠 Memory system: ACTIVE")
        
    def process_input(self, user_input: str) -> str:
        # Store the interaction in memory
        experience = {
            'type': 'user_interaction',
            'input': user_input,
            'context': 'chat'
        }
        self.memory.add_experience(experience)
        
        # Check if it's a PC control command (simulate for demo)
        control_keywords = ['click', 'type', 'open', 'move', 'press', 'scroll', 'screenshot', 'browse']
        if any(keyword in user_input.lower() for keyword in control_keywords):
            response = self._simulate_pc_control(user_input)
        else:
            # Process the text and generate response
            response = self.text_processor.generate_response(user_input)
        
        # Learn from the interaction
        if self.learning_mode:
            self.text_processor.learn_pattern(user_input, response)
        
        # Store the response
        response_experience = {
            'type': 'ai_response',
            'input': user_input,
            'output': response,
            'context': 'chat'
        }
        self.memory.add_experience(response_experience)
        
        return response
    
    def _simulate_pc_control(self, command: str) -> str:
        """Simulate PC control actions for demo"""
        cmd = command.lower()
        
        if "click" in cmd:
            return "🖱️ Simulated mouse click - would click on screen"
        elif "type" in cmd:
            text = cmd.replace("type", "").strip()
            return f"⌨️ Simulated typing: '{text}'"
        elif "open" in cmd:
            app = cmd.replace("open", "").strip()
            return f"🚀 Simulated opening: {app}"
        elif "screenshot" in cmd:
            return "📸 Simulated screenshot taken"
        elif "browse" in cmd:
            return "🌐 Simulated browser navigation"
        else:
            return f"🤖 PC Control: {command} (simulated)"
    
    def start_demo_streaming(self):
        """Demo streaming mode"""
        print("🎥 Starting demo streaming mode...")
        print("🎤 AI Commentary: Welcome to my stream!")
        
        # Simulate streaming commentary
        commentary_thread = threading.Thread(target=self._demo_commentary)
        commentary_thread.daemon = True
        commentary_thread.start()
        
        return "Demo streaming started!"
    
    def _demo_commentary(self):
        """Generate demo commentary"""
        comments = [
            "🎮 This is really exciting!",
            "💬 Thanks for watching everyone!",
            "🔥 Let me know what you think in chat!",
            "🎯 This AI system is learning in real-time!",
            "🚀 Next, I'll show you the PC control features!"
        ]
        
        for i, comment in enumerate(comments):
            time.sleep(5)
            print(f"🎤 AI Commentary: {comment}")
            if i >= 4:  # Stop after 5 comments
                break
    
    def save_state(self):
        """Save the AI's current state"""
        self.memory.save_memory('ai_memory.json')
        print("💾 AI state saved successfully!")
    
    def get_stats(self):
        """Get AI system statistics"""
        return {
            'memory_stats': {
                'short_term_count': len(self.memory.short_term_memory),
                'long_term_count': len(self.memory.long_term_memory),
                'knowledge_base_size': len(self.memory.knowledge_base)
            },
            'vocabulary_size': len(self.text_processor.vocabulary),
            'learning_mode': self.learning_mode
        }

def main():
    ai = DemoAI()
    print("\n🎯 Available Commands:")
    print("  'chat' - Talk with AI")
    print("  'stream' - Demo streaming mode") 
    print("  'stats' - View AI statistics")
    print("  'save' - Save AI state")
    print("  'quit' - Exit")
    
    while True:
        command = input("\n🤖 Enter command: ").strip().lower()
        
        if command == 'quit':
            ai.save_state()
            print("👋 AI shutting down...")
            break
        elif command == 'chat':
            print("💬 Chat mode (type 'exit' to return)")
            print("Try: 'click on screen', 'type hello', 'open browser'")
            while True:
                user_input = input("You: ")
                if user_input.lower() == 'exit':
                    break
                response = ai.process_input(user_input)
                print(f"🤖 AI: {response}")
        elif command == 'stream':
            result = ai.start_demo_streaming()
            print(f"📺 {result}")
            print("🎥 Watch the commentary above...")
        elif command == 'stats':
            stats = ai.get_stats()
            print("📊 AI System Stats:")
            for category, data in stats.items():
                print(f"  {category}: {data}")
        elif command == 'save':
            ai.save_state()
        else:
            print("❌ Unknown command. Try: chat, stream, stats, save, quit")

if __name__ == "__main__":
    main()