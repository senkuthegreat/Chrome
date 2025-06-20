# 🤖 Mecha-Senku(Meku/M-Senku): Your Local AI Assistant

**Mecha-Senku** is a personal AI assistant that runs entirely offline on your PC using [Ollama](https://ollama.com/) and large language models like `gemma:2b` or `llama2:7b-chat`. Inspired by Ultron from Avengers and Senku from Dr. Stone, this assistant can:

- 💬 Chat intelligently with real-time text and voice
- 🎙️ Speak responses using neural voice synthesis
- 🎤 Listen for your voice ("Hey Senku") to trigger commands
- 🧠 Run on your PC without relying on cloud APIs

---

## 🛠 Features

- ✅ Offline AI responses with [Ollama](https://ollama.com/)
- 🎙️ Voice output using `Edge TTS` (Neural Microsoft voices)
- 🎤 Wake-word-based voice input using your microphone
- 💻 Built with **C# + .NET Framework 4.8**
- 🚀 Designed to evolve into a full Ultron-like OS companion

---

## 📦 Requirements

- Windows 10/11
- [.NET Framework 4.8](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net48)
- [Ollama](https://ollama.com/) installed and configured
- A model pulled (e.g. `gemma:2b`)

```bash
ollama pull gemma:2b
ollama run gemma:2b
