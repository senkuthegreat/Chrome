using System;
using System.Collections.Concurrent;
using System.IO;
using System.Net.Http;
using System.Speech.Recognition;
using System.Speech.Synthesis;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

class Program
{
    // State management
    static bool isListening = false;
    static ConcurrentQueue<string> speechQueue = new ConcurrentQueue<string>();
    static bool isSpeaking = false;
    static bool isProcessingResponse = false;
    
    // Speech engines
    static SpeechRecognitionEngine speechRecognizer = new SpeechRecognitionEngine();
    static SpeechSynthesizer tts = new SpeechSynthesizer();

    // Response buffer for instant start
    static StringBuilder responseBuffer = new StringBuilder();
    static DateTime lastTokenTime = DateTime.MinValue;

    static async Task Main(string[] args)
    {
        // Initialize TTS
        try
        {
            tts.SelectVoiceByHints(VoiceGender.Female, VoiceAge.Adult);
            tts.SetOutputToDefaultAudioDevice();
            tts.Rate = 1; // Slightly faster speech
        }
        catch (Exception ex)
        {
            Console.WriteLine($"⚠️ TTS initialization error: {ex.Message}");
        }
        
        Console.WriteLine("🤖 Welcome to Mecha-Senku!");
        Console.WriteLine("Choose mode:");
        Console.WriteLine("1. Voice Mode (Say 'Hey Senku')");
        Console.WriteLine("2. Chat Mode (Type messages)");
        Console.Write("Enter choice (1 or 2): ");
        
        var choice = Console.ReadLine();
        
        if (choice == "2")
        {
            Console.Write("Enable AI voice responses? (y/n): ");
            bool enableVoice = Console.ReadLine()?.ToLower().StartsWith("y") == true;
            await StartChatMode(enableVoice);
        }
        else
        {
            Console.WriteLine("🎙️ Voice mode activated... Say 'Hey Senku'");
            SetupWakeWordRecognition();
            await Task.Delay(-1);
        }
    }

    // ======================== //
    //  VOICE MODE IMPLEMENTATION
    // ======================== //
    static void SetupWakeWordRecognition()
    {
        speechRecognizer.SetInputToDefaultAudioDevice();

        // Create wake word grammar
        var wakeGrammarBuilder = new GrammarBuilder();
        wakeGrammarBuilder.Append("hey senku");
        var wakeGrammar = new Grammar(wakeGrammarBuilder);
        
        // Create command grammar
        var commandGrammarBuilder = new GrammarBuilder();
        commandGrammarBuilder.AppendWildcard();
        var commandGrammar = new Grammar(commandGrammarBuilder);
        
        speechRecognizer.LoadGrammar(wakeGrammar);
        speechRecognizer.LoadGrammar(commandGrammar);

        speechRecognizer.SpeechRecognized += async (sender, e) =>
        {
            if (e.Result.Text.ToLower().Contains("hey senku") && !isListening)
            {
                isListening = true;
                Console.WriteLine("\n✅ Wake word detected! Listening...");
            }
            else if (isListening)
            {
                string command = e.Result.Text;
                Console.WriteLine($"\n🗣️ You: {command}");
                await HandleAIResponse(command);
                isListening = false;
                Console.WriteLine("\n🎙️ Ready for wake word...");
            }
        };
        
        speechRecognizer.RecognizeAsync(RecognizeMode.Multiple);
    }

    static async Task HandleAIResponse(string input)
    {
        try
        {
            Console.Write("🤖 Mecha-Senku: ");
            await ProcessAIResponse(input, true);
            Console.WriteLine();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error: {ex.Message}");
        }
    }

    // ======================== //
    //  CHAT MODE IMPLEMENTATION
    // ======================== //
    static async Task StartChatMode(bool enableVoice)
    {
        Console.WriteLine("\n💬 Chat mode activated! Type 'exit' to quit");
        while (true)
        {
            Console.Write("\nYou: ");
            string input = Console.ReadLine()?.Trim() ?? "";
            
            if (string.IsNullOrWhiteSpace(input) || input.Equals("exit", StringComparison.OrdinalIgnoreCase))
                break;
                
            await HandleChatResponse(input, enableVoice);
        }
    }
    
    static async Task HandleChatResponse(string input, bool enableVoice)
    {
        try
        {
            Console.Write("🤖 Mecha-Senku: ");
            await ProcessAIResponse(input, enableVoice);
            Console.WriteLine();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error: {ex.Message}");
        }
    }

    // ======================== //
    //  CORE AI RESPONSE HANDLING (OPTIMIZED)
    // ======================== //
    static async Task ProcessAIResponse(string input, bool useVoice)
    {
        isProcessingResponse = true;
        responseBuffer.Clear();
        lastTokenTime = DateTime.Now;
        
        using var client = new HttpClient();
        
        // Optimized prompt format for faster response
        string optimizedPrompt = $"User: {input}\nAssistant:";
        
        var body = new
        {
            model = "mistral",
            stream = true,
            prompt = optimizedPrompt,
            options = new {
                num_gpu_layers = 20,
                temperature = 0.7,  // More focused responses
                num_predict = 80,    // Shorter responses
                top_k = 40,          // Faster sampling
                top_p = 0.9
            }
        };

        var request = new HttpRequestMessage(HttpMethod.Post, "http://localhost:11434/api/generate")
        {
            Content = new StringContent(JsonSerializer.Serialize(body), Encoding.UTF8, "application/json")
        };

        // Start TTS processing immediately
        if (useVoice && !isSpeaking)
        {
            _ = Task.Run(ProcessSpeechQueue);
        }

        // Start timing for instant response
        var responseTask = client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);
        var startTime = DateTime.Now;
        
        // Show "thinking" indicator after 500ms if no response
        _ = Task.Run(async () => {
            await Task.Delay(500);
            if (isProcessingResponse && responseBuffer.Length == 0)
            {
                Console.Write("(thinking)");
            }
        });

        using var response = await responseTask;
        using var stream = await response.Content.ReadAsStreamAsync();
        using var reader = new StreamReader(stream);

        string line;
        while ((line = await reader.ReadLineAsync()) != null)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;

            try
            {
                var doc = JsonDocument.Parse(line);
                if (doc.RootElement.TryGetProperty("response", out var token))
                {
                    string text = token.GetString();
                    Console.Write(text);
                    lastTokenTime = DateTime.Now;
                    
                    // Add to response buffer
                    responseBuffer.Append(text);
                    
                    // Send to TTS immediately if voice enabled
                    if (useVoice)
                    {
                        // Process immediately without waiting for chunks
                        speechQueue.Enqueue(text);
                    }
                }
            }
            catch (JsonException)
            {
                // Skip invalid JSON lines
            }
        }
        
        isProcessingResponse = false;
    }

    // ======================== //
    //  SPEECH QUEUE PROCESSING (OPTIMIZED)
    // ======================== //
    static async Task ProcessSpeechQueue()
    {
        isSpeaking = true;
        StringBuilder ttsBuffer = new StringBuilder();
        
        while (isProcessingResponse || !speechQueue.IsEmpty || ttsBuffer.Length > 0)
        {
            // Process speech queue
            if (speechQueue.TryDequeue(out string text))
            {
                ttsBuffer.Append(text);
            }
            
            // Speak when we have enough content or pause detected
            if (ttsBuffer.Length > 0 && ShouldSpeakChunk(ttsBuffer.ToString()))
            {
                string chunk = ttsBuffer.ToString();
                ttsBuffer.Clear();
                
                if (!string.IsNullOrWhiteSpace(chunk))
                {
                    // Speak without waiting for completion
                    tts.SpeakAsync(chunk);
                }
            }
            
            // Small delay to prevent CPU hogging
            await Task.Delay(10);
        }
        isSpeaking = false;
    }

    static bool ShouldSpeakChunk(string text)
    {
        // Speak immediately on punctuation or after 15 characters
        return text.EndsWith(".") || text.EndsWith("?") || text.EndsWith("!") || 
               text.EndsWith(",") || text.EndsWith(";") || text.EndsWith(":") || 
               text.Length > 15;
    }
}