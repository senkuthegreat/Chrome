using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Speech.Recognition;
using System.Speech.Synthesis;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
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

    // Performance optimizations
    static readonly HttpClient httpClient = new HttpClient() { Timeout = TimeSpan.FromSeconds(30) };
    static readonly Dictionary<string, string> responseCache = new Dictionary<string, string>();
    static readonly Dictionary<string, DateTime> cacheTimestamps = new Dictionary<string, DateTime>();

    // Emotion and personality system
    static string currentEmotion = "neutral";
    static readonly Dictionary<string, EmotionConfig> emotions = new Dictionary<string, EmotionConfig>
    {
        ["excited"] = new EmotionConfig { Rate = 2, Volume = 90, Pitch = "high", Prefix = "Oh wow! ", Suffix = "!" },
        ["happy"] = new EmotionConfig { Rate = 1, Volume = 85, Pitch = "medium-high", Prefix = "", Suffix = " 😊" },
        ["curious"] = new EmotionConfig { Rate = 0, Volume = 80, Pitch = "medium", Prefix = "Hmm, ", Suffix = "?" },
        ["confident"] = new EmotionConfig { Rate = 0, Volume = 85, Pitch = "medium", Prefix = "Absolutely! ", Suffix = "." },
        ["thoughtful"] = new EmotionConfig { Rate = -1, Volume = 75, Pitch = "medium-low", Prefix = "Let me think... ", Suffix = "..." },
        ["neutral"] = new EmotionConfig { Rate = 0, Volume = 80, Pitch = "medium", Prefix = "", Suffix = "" },
        ["empathetic"] = new EmotionConfig { Rate = -1, Volume = 75, Pitch = "medium-low", Prefix = "I understand, ", Suffix = "." }
    };

    // Instant response system
    static readonly Dictionary<string, string> quickResponses = new Dictionary<string, string>
    {
        ["hello"] = "Hey there! How can I help you today?",
        ["hi"] = "Hi! What's on your mind?",
        ["how are you"] = "I'm doing great, thanks for asking! How about you?",
        ["what's up"] = "Not much, just here ready to help! What's going on?",
        ["thanks"] = "You're absolutely welcome! Anything else I can do?",
        ["thank you"] = "My pleasure! Happy to help anytime!",
        ["bye"] = "See you later! Take care!",
        ["goodbye"] = "Goodbye! Have a wonderful day!"
    };

    public class EmotionConfig
    {
        public int Rate { get; set; }
        public int Volume { get; set; }
        public string Pitch { get; set; }
        public string Prefix { get; set; }
        public string Suffix { get; set; }
    }

    static async Task Main(string[] args)
    {
        // Initialize enhanced TTS with emotion support
        try
        {
            tts.SelectVoiceByHints(VoiceGender.Female, VoiceAge.Adult);
            tts.SetOutputToDefaultAudioDevice();
            ConfigureTTSForEmotion("neutral");

            // Warm up the TTS engine
            tts.SpeakAsync("System initialized");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"⚠️ TTS initialization error: {ex.Message}");
        }

        // Pre-warm the HTTP client
        _ = Task.Run(async () => {
            try
            {
                await httpClient.GetAsync("http://localhost:11434/api/tags");
            }
            catch { /* Ignore pre-warm errors */ }
        });

        Console.WriteLine("🤖 Welcome to Mecha-Senku! (Enhanced with Emotions & Instant Responses)");
        Console.WriteLine("✨ New Features: Emotional responses, instant replies, human-like speech!");
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

    static void ConfigureTTSForEmotion(string emotion)
    {
        if (emotions.TryGetValue(emotion, out var config))
        {
            tts.Rate = config.Rate;
            tts.Volume = config.Volume;
            currentEmotion = emotion;
        }
    }

    static string DetectEmotion(string input)
    {
        input = input.ToLower();

        // Excitement patterns
        if (input.Contains("wow") || input.Contains("amazing") || input.Contains("awesome") ||
            input.Contains("incredible") || input.EndsWith("!"))
            return "excited";

        // Question patterns
        if (input.Contains("?") || input.StartsWith("what") || input.StartsWith("how") ||
            input.StartsWith("why") || input.StartsWith("when") || input.StartsWith("where"))
            return "curious";

        // Positive patterns
        if (input.Contains("good") || input.Contains("great") || input.Contains("nice") ||
            input.Contains("love") || input.Contains("like"))
            return "happy";

        // Thinking patterns
        if (input.Contains("think") || input.Contains("consider") || input.Contains("analyze") ||
            input.Contains("explain") || input.Contains("complex"))
            return "thoughtful";

        // Sad/empathetic patterns
        if (input.Contains("sad") || input.Contains("sorry") || input.Contains("problem") ||
            input.Contains("help") || input.Contains("difficult"))
            return "empathetic";

        return "neutral";
    }

    static string GetInstantResponse(string input)
    {
        string normalizedInput = input.ToLower().Trim();

        // Check for exact matches first
        if (quickResponses.TryGetValue(normalizedInput, out string response))
        {
            return response;
        }

        // Check for partial matches
        foreach (var kvp in quickResponses)
        {
            if (normalizedInput.Contains(kvp.Key))
            {
                return kvp.Value;
            }
        }

        return null; // No instant response available
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
            var startTime = DateTime.Now;
            Console.Write("🤖 Mecha-Senku: ");
            await ProcessAIResponse(input, true);
            Console.WriteLine();
            LogResponseTime(startTime, "Voice");
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
            var startTime = DateTime.Now;
            Console.Write("🤖 Mecha-Senku: ");
            await ProcessAIResponse(input, enableVoice);
            Console.WriteLine();
            LogResponseTime(startTime, enableVoice ? "Chat+Voice" : "Chat");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error: {ex.Message}");
        }
    }

    // ======================== //
    //  CORE AI RESPONSE HANDLING (ULTRA-OPTIMIZED)
    // ======================== //
    static async Task ProcessAIResponse(string input, bool useVoice)
    {
        // Step 1: Check for instant responses first
        string instantResponse = GetInstantResponse(input);
        if (instantResponse != null)
        {
            // Detect emotion and configure TTS
            string emotion = DetectEmotion(input);
            if (useVoice) ConfigureTTSForEmotion(emotion);

            // Add emotional prefix/suffix
            if (emotions.TryGetValue(emotion, out var emotionConfig))
            {
                instantResponse = emotionConfig.Prefix + instantResponse + emotionConfig.Suffix;
            }

            // Output instantly (0ms response time!)
            Console.Write(instantResponse);
            if (useVoice)
            {
                _ = Task.Run(() => tts.SpeakAsync(instantResponse));
            }
            return;
        }

        // Step 2: Check cache for recent similar queries
        string cacheKey = input.ToLower().Trim();
        if (responseCache.TryGetValue(cacheKey, out string cachedResponse) &&
            cacheTimestamps.TryGetValue(cacheKey, out DateTime cacheTime) &&
            DateTime.Now - cacheTime < TimeSpan.FromMinutes(5))
        {
            Console.Write(cachedResponse);
            if (useVoice)
            {
                _ = Task.Run(() => tts.SpeakAsync(cachedResponse));
            }
            return;
        }

        // Step 3: Full AI processing with optimizations
        isProcessingResponse = true;
        responseBuffer.Clear();
        lastTokenTime = DateTime.Now;

        // Detect emotion for AI response
        string detectedEmotion = DetectEmotion(input);
        if (useVoice) ConfigureTTSForEmotion(detectedEmotion);

        // Enhanced prompt with personality and emotion
        string personalityPrompt = $@"You are Senku, a brilliant and enthusiastic AI assistant.
Respond with emotion: {detectedEmotion}. Be concise, engaging, and human-like.
Current mood: {detectedEmotion}

User: {input}
Senku:";

        var body = new
        {
            model = "mistral",
            stream = true,
            prompt = personalityPrompt,
            options = new {
                num_gpu_layers = 35,      // More GPU layers for speed
                temperature = 0.8,        // More personality
                num_predict = 120,        // Slightly longer for personality
                top_k = 30,              // Faster sampling
                top_p = 0.85,            // More focused
                repeat_penalty = 1.1,     // Avoid repetition
                num_ctx = 2048           // Smaller context for speed
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

        // Ultra-fast response timing
        var responseTask = httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);
        var startTime = DateTime.Now;

        // Show thinking indicator after just 200ms (faster feedback)
        _ = Task.Run(async () => {
            await Task.Delay(200);
            if (isProcessingResponse && responseBuffer.Length == 0)
            {
                Console.Write("💭");
            }
        });

        using var response = await responseTask;
        using var stream = await response.Content.ReadAsStreamAsync();
        using var reader = new StreamReader(stream);

        string fullResponse = "";
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
                    fullResponse += text;

                    // Send to TTS with emotion immediately if voice enabled
                    if (useVoice)
                    {
                        speechQueue.Enqueue(text);
                    }
                }
            }
            catch (JsonException)
            {
                // Skip invalid JSON lines
            }
        }

        // Cache the response for future instant replies
        if (!string.IsNullOrWhiteSpace(fullResponse))
        {
            responseCache[cacheKey] = fullResponse;
            cacheTimestamps[cacheKey] = DateTime.Now;

            // Clean old cache entries (keep only last 50)
            if (responseCache.Count > 50)
            {
                var oldestKey = cacheTimestamps.OrderBy(kvp => kvp.Value).First().Key;
                responseCache.Remove(oldestKey);
                cacheTimestamps.Remove(oldestKey);
            }
        }

        isProcessingResponse = false;
    }

    // ======================== //
    //  HUMAN-LIKE SPEECH PROCESSING (ULTRA-OPTIMIZED)
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

            // Speak when we have enough content or natural pause detected
            if (ttsBuffer.Length > 0 && ShouldSpeakChunk(ttsBuffer.ToString()))
            {
                string chunk = ttsBuffer.ToString();
                ttsBuffer.Clear();

                if (!string.IsNullOrWhiteSpace(chunk))
                {
                    // Process chunk for human-like speech
                    string processedChunk = ProcessForHumanSpeech(chunk);

                    // Speak with emotion-based timing
                    _ = Task.Run(async () => {
                        // Add natural pause before speaking (human-like)
                        if (chunk.StartsWith(".") || chunk.StartsWith("!") || chunk.StartsWith("?"))
                        {
                            await Task.Delay(300); // Pause after sentences
                        }

                        tts.SpeakAsync(processedChunk);
                    });
                }
            }

            // Minimal delay for ultra-responsiveness
            await Task.Delay(5);
        }
        isSpeaking = false;
    }

    static bool ShouldSpeakChunk(string text)
    {
        // More intelligent chunking for natural speech
        if (text.Length < 3) return false; // Don't speak tiny fragments

        // Immediate speech triggers (end of sentences)
        if (text.EndsWith(". ") || text.EndsWith("! ") || text.EndsWith("? "))
            return true;

        // Natural pause points
        if (text.EndsWith(", ") || text.EndsWith("; ") || text.EndsWith(": "))
            return true;

        // Longer chunks for better flow
        if (text.Length > 25) return true;

        // Word boundaries for natural breaks
        if (text.Length > 10 && (text.EndsWith(" and ") || text.EndsWith(" but ") ||
                                text.EndsWith(" so ") || text.EndsWith(" then ")))
            return true;

        return false;
    }

    static string ProcessForHumanSpeech(string text)
    {
        // Add natural pauses and emphasis for human-like speech
        text = text.Replace("...", "<break time='500ms'/>");
        text = text.Replace("—", "<break time='300ms'/>");
        text = text.Replace(" - ", " <break time='200ms'/> ");

        // Add emphasis based on emotion
        if (currentEmotion == "excited")
        {
            text = Regex.Replace(text, @"\b(amazing|wow|incredible|awesome)\b",
                                "<emphasis level='strong'>$1</emphasis>", RegexOptions.IgnoreCase);
        }
        else if (currentEmotion == "thoughtful")
        {
            text = Regex.Replace(text, @"\b(think|consider|perhaps|maybe)\b",
                                "<break time='200ms'/>$1<break time='100ms'/>", RegexOptions.IgnoreCase);
        }

        // Add natural breathing pauses for longer sentences
        if (text.Length > 50)
        {
            text = Regex.Replace(text, @"(\w+),\s+(\w+)", "$1,<break time='150ms'/> $2");
        }

        return text;
    }

    // ======================== //
    //  PERFORMANCE MONITORING
    // ======================== //
    static void LogResponseTime(DateTime startTime, string responseType)
    {
        var elapsed = DateTime.Now - startTime;
        Console.WriteLine($"\n⚡ {responseType} response time: {elapsed.TotalMilliseconds:F0}ms");
    }
}