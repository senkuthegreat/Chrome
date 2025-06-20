import time
import threading
from core.neural_network import SimpleNeuralNetwork
from memory.memory_system import MemorySystem
from nlp.text_processor import TextProcessor
from streaming.youtube_streamer import YouTubeStreamer
from control.ai_actions import AIActions

class MainAI:
    def __init__(self):
        self.neural_network = SimpleNeuralNetwork(input_size=100, hidden_size=50, output_size=10)
        self.memory = MemorySystem()
        self.text_processor = TextProcessor()
        self.streamer = YouTubeStreamer()
        self.pc_control = AIActions()
        
        self.is_running = False
        self.learning_mode = True
        self.autonomous_mode = False
        
        # Load existing memory if available
        self.memory.load_memory('ai_memory.json')
        
    def process_input(self, user_input: str) -> str:
        # Store the interaction in memory
        experience = {
            'type': 'user_interaction',
            'input': user_input,
            'context': 'chat'
        }
        self.memory.add_experience(experience)
        
        # Check if it's a PC control command
        control_keywords = ['click', 'type', 'open', 'move', 'press', 'scroll', 'screenshot', 'browse']
        if any(keyword in user_input.lower() for keyword in control_keywords):
            pc_result = self.pc_control.interpret_command(user_input)
            response = f"PC Action: {pc_result}"
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
    
    def start_streaming(self, stream_key: str = None):
        """Start YouTube streaming with AI commentary"""
        if stream_key:
            self.streamer.stream_key = stream_key
        
        result = self.streamer.start_stream()
        
        if "started" in result:
            # Start commentary thread
            commentary_thread = threading.Thread(target=self._commentary_loop)
            commentary_thread.daemon = True
            commentary_thread.start()
            
            # Start chat monitoring thread
            chat_thread = threading.Thread(target=self._chat_monitor_loop)
            chat_thread.daemon = True
            chat_thread.start()
        
        return result
    
    def _commentary_loop(self):
        """Generate periodic commentary during streaming"""
        while self.streamer.is_streaming:
            # Generate commentary every 30-60 seconds
            time.sleep(30 + (time.time() % 30))
            
            if self.streamer.is_streaming:
                commentary = self.streamer.generate_commentary('general', 
                                                             self.streamer.chat_messages[-3:])
                self.streamer.add_commentary(commentary)
                print(f"AI Commentary: {commentary}")
    
    def _chat_monitor_loop(self):
        """Monitor and respond to chat messages"""
        while self.streamer.is_streaming:
            time.sleep(5)  # Check every 5 seconds
            
            new_message = self.streamer.simulate_chat_interaction()
            if new_message:
                # Generate AI response to chat
                ai_response = self.process_input(new_message)
                self.streamer.add_commentary(f"Responding to chat: {ai_response}")
                print(f"Chat: {new_message}")
                print(f"AI Response: {ai_response}")
    
    def learn_from_feedback(self, input_text: str, correct_response: str):
        """Learn from user corrections"""
        self.text_processor.learn_pattern(input_text, correct_response)
        
        learning_experience = {
            'type': 'learning',
            'input': input_text,
            'correct_response': correct_response,
            'context': 'feedback'
        }
        self.memory.add_experience(learning_experience)
    
    def save_state(self):
        """Save the AI's current state"""
        self.memory.save_memory('ai_memory.json')
        print("AI state saved successfully!")
    
    def start_autonomous_mode(self):
        """Start autonomous PC control"""
        self.autonomous_mode = True
        autonomous_thread = threading.Thread(target=self._autonomous_loop)
        autonomous_thread.daemon = True
        autonomous_thread.start()
        return "Autonomous mode started - AI now has full PC control"
    
    def _autonomous_loop(self):
        """Autonomous AI behavior loop"""
        while self.autonomous_mode:
            time.sleep(10)  # Wait 10 seconds between actions
            
            # AI decides what to do
            actions = [
                "take screenshot",
                "browse internet",
                "open terminal",
                "scroll down",
                "move mouse 400 300"
            ]
            
            import random
            action = random.choice(actions)
            result = self.pc_control.interpret_command(action)
            print(f"Autonomous Action: {action} -> {result}")
    
    def get_stats(self):
        """Get AI system statistics"""
        return {
            'memory_stats': {
                'short_term_count': len(self.memory.short_term_memory),
                'long_term_count': len(self.memory.long_term_memory),
                'knowledge_base_size': len(self.memory.knowledge_base)
            },
            'vocabulary_size': len(self.text_processor.vocabulary),
            'streaming_stats': self.streamer.get_stream_stats(),
            'pc_control_history': self.pc_control.get_action_history(),
            'autonomous_mode': self.autonomous_mode
        }

def main():
    ai = MainAI()
    print("AI System initialized with PC Control!")
    print("Commands: 'chat', 'stream', 'control', 'autonomous', 'stats', 'save', 'quit'")
    
    while True:
        command = input("\nEnter command: ").strip().lower()
        
        if command == 'quit':
            ai.save_state()
            break
        elif command == 'chat':
            print("Chat mode (type 'exit' to return to main menu)")
            while True:
                user_input = input("You: ")
                if user_input.lower() == 'exit':
                    break
                response = ai.process_input(user_input)
                print(f"AI: {response}")
        elif command == 'stream':
            stream_key = input("Enter YouTube stream key (or press Enter to use placeholder): ")
            if not stream_key:
                stream_key = "<your_stream_key>"
            result = ai.start_streaming(stream_key)
            print(result)
        elif command == 'control':
            print("PC Control mode (type 'exit' to return)")
            print("Examples: 'click 100 200', 'type hello', 'open firefox', 'screenshot'")
            while True:
                pc_input = input("PC Command: ")
                if pc_input.lower() == 'exit':
                    break
                result = ai.pc_control.interpret_command(pc_input)
                print(f"Result: {result}")
        elif command == 'autonomous':
            result = ai.start_autonomous_mode()
            print(result)
            print("AI is now controlling your PC autonomously. Type 'quit' to stop.")
        elif command == 'stats':
            stats = ai.get_stats()
            print("AI System Stats:")
            for category, data in stats.items():
                print(f"  {category}: {data}")
        elif command == 'save':
            ai.save_state()
        else:
            print("Unknown command. Available: chat, stream, control, autonomous, stats, save, quit")

if __name__ == "__main__":
    main()