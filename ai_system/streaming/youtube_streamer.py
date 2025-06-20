import subprocess
import threading
import time
from typing import Dict, List, Any

class YouTubeStreamer:
    def __init__(self, stream_key: str = "<your_stream_key>"):
        self.stream_key = stream_key
        self.is_streaming = False
        self.chat_messages = []
        self.commentary_queue = []
        
    def start_stream(self, rtmp_url: str = "rtmp://a.rtmp.youtube.com/live2/"):
        """Start streaming to YouTube using FFmpeg"""
        if self.is_streaming:
            return "Already streaming!"
        
        # FFmpeg command for streaming
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab',  # Screen capture on Linux
            '-s', '1920x1080',
            '-r', '30',
            '-i', ':0.0',
            '-f', 'alsa',  # Audio capture
            '-i', 'default',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-b:v', '2500k',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'flv',
            f'{rtmp_url}{self.stream_key}'
        ]
        
        try:
            self.stream_process = subprocess.Popen(ffmpeg_cmd, 
                                                 stdout=subprocess.PIPE, 
                                                 stderr=subprocess.PIPE)
            self.is_streaming = True
            print("Stream started successfully!")
            return "Stream started!"
        except Exception as e:
            return f"Failed to start stream: {str(e)}"
    
    def stop_stream(self):
        """Stop the current stream"""
        if hasattr(self, 'stream_process'):
            self.stream_process.terminate()
            self.is_streaming = False
            return "Stream stopped!"
        return "No active stream to stop."
    
    def add_commentary(self, text: str):
        """Add commentary to the queue"""
        self.commentary_queue.append({
            'text': text,
            'timestamp': time.time()
        })
    
    def generate_commentary(self, topic: str, chat_context: List[str] = None) -> str:
        """Generate commentary based on topic and chat"""
        commentary_templates = {
            'gaming': [
                "That was an incredible play!",
                "The strategy here is really interesting",
                "Let's see what happens next",
                "This is getting intense!"
            ],
            'general': [
                "What do you all think about this?",
                "This is really fascinating",
                "Thanks for joining the stream everyone!",
                "Let me know your thoughts in the chat"
            ],
            'educational': [
                "This is a great learning opportunity",
                "Let me explain what's happening here",
                "This concept is really important to understand",
                "Hope everyone is following along"
            ]
        }
        
        import random
        templates = commentary_templates.get(topic, commentary_templates['general'])
        base_commentary = random.choice(templates)
        
        # Add chat engagement if there are recent messages
        if chat_context and len(chat_context) > 0:
            base_commentary += f" I see {chat_context[-1]} in the chat - great point!"
        
        return base_commentary
    
    def simulate_chat_interaction(self):
        """Simulate reading and responding to chat messages"""
        # In a real implementation, this would connect to YouTube's chat API
        sample_messages = [
            "Great stream!",
            "Can you explain that again?",
            "This is awesome!",
            "What's next?",
            "Love the content!"
        ]
        
        import random
        if random.random() < 0.3:  # 30% chance of new message
            new_message = random.choice(sample_messages)
            self.chat_messages.append(new_message)
            return new_message
        return None
    
    def get_stream_stats(self) -> Dict[str, Any]:
        """Get current stream statistics"""
        return {
            'is_streaming': self.is_streaming,
            'chat_messages_count': len(self.chat_messages),
            'commentary_queue_size': len(self.commentary_queue),
            'uptime': time.time() if self.is_streaming else 0
        }