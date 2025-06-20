print("Starting AI System...")

try:
    import numpy as np
    print("[OK] numpy imported")
except ImportError:
    print("[FAIL] numpy failed")

try:
    from core.neural_network import SimpleNeuralNetwork
    print("[OK] neural network imported")
except ImportError as e:
    print(f"[FAIL] neural network failed: {e}")

try:
    from memory.memory_system import MemorySystem
    print("[OK] memory system imported")
except ImportError as e:
    print(f"[FAIL] memory system failed: {e}")

try:
    from nlp.text_processor import TextProcessor
    print("[OK] text processor imported")
except ImportError as e:
    print(f"[FAIL] text processor failed: {e}")

try:
    from streaming.youtube_streamer import YouTubeStreamer
    print("[OK] youtube streamer imported")
except ImportError as e:
    print(f"[FAIL] youtube streamer failed: {e}")

try:
    from control.ai_actions import AIActions
    print("[OK] ai actions imported")
except ImportError as e:
    print(f"[FAIL] ai actions failed: {e}")

print("Import test complete!")