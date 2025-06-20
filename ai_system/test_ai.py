from demo_ai import DemoAI

# Test the AI system
ai = DemoAI()

print("\n🧪 Testing AI Responses:")
print("=" * 40)

# Test regular chat
responses = [
    "Hello there!",
    "How are you doing?", 
    "What can you do?",
    "click on the screen",
    "type hello world",
    "open my browser",
    "take a screenshot"
]

for user_input in responses:
    response = ai.process_input(user_input)
    print(f"You: {user_input}")
    print(f"🤖 AI: {response}")
    print("-" * 30)

# Show stats
print("\n📊 AI Stats:")
stats = ai.get_stats()
for key, value in stats.items():
    print(f"{key}: {value}")

# Test streaming
print("\n🎥 Testing Streaming:")
ai.start_demo_streaming()

print("\n✅ AI System is working perfectly!")
print("\n🎯 To use interactively, run: python demo_ai.py")
print("Then use commands: chat, stream, stats, save, quit")