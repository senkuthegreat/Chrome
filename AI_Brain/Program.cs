using System;
using System.Net.Http;
using System.Speech.Synthesis;
using System.Speech.Recognition;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

class Program
{
    static SpeechRecognitionEngine recognizer;
    static bool isListening = false;

    static async Task Main(string[] args)
    {
        var synth = new SpeechSynthesizer();
        synth.SelectVoiceByHints(VoiceGender.Neutral, VoiceAge.Teen);

        StartVoiceRecognition();

        Console.WriteLine("🤖 Say 'Hey Senku' or type your message (type 'exit' to quit):");

        while (true)
        {
            string input;

            if (isListening)
            {
                Console.Write("> You (speak): ");
                input = Console.ReadLine();  // Simulated speech text input
                isListening = false;
            }
            else
            {
                Console.Write("> You: ");
                input = Console.ReadLine();
            }

            if (string.IsNullOrWhiteSpace(input))
                continue;

            if (input.ToLower() == "exit")
                break;

            try
            {
                var reply = await AskOllama(input);
                Console.WriteLine($"\n🧠 AI: {reply}\n");
                synth.SpeakAsync(reply);
            }
            catch (Exception ex)
            {
                Console.WriteLine("❌ Error: " + ex.Message);
            }
        }
    }

    static void StartVoiceRecognition()
    {
        recognizer = new SpeechRecognitionEngine();
        recognizer.SetInputToDefaultAudioDevice();

        var choices = new Choices();
        choices.Add(new string[] { "hey senku", "stop listening" });

        var gb = new GrammarBuilder();
        gb.Append(choices);

        var grammar = new Grammar(gb);
        recognizer.LoadGrammar(grammar);

        recognizer.SpeechRecognized += (s, e) =>
        {
            var text = e.Result.Text.ToLower();
            Console.WriteLine($"\n🎤 Heard: {text}");

            if (text.Contains("hey senku"))
            {
                Console.WriteLine("👂 Listening... What do you want to ask?");
                isListening = true;
            }
            else if (text.Contains("stop listening"))
            {
                Console.WriteLine("🛑 Voice listening stopped.");
                isListening = false;
            }
        };

        recognizer.RecognizeAsync(RecognizeMode.Multiple);
    }

    static async Task<string> AskOllama(string prompt)
    {
        var client = new HttpClient();

        var requestData = new
        {
            model = "gemma:2b",
            prompt = prompt,
            stream = false
        };

        var content = new StringContent(JsonSerializer.Serialize(requestData), Encoding.UTF8, "application/json");

        var response = await client.PostAsync("http://localhost:11434/api/generate", content);

        if (!response.IsSuccessStatusCode)
        {
            Console.WriteLine($"Error: {response.StatusCode}");
            return "Failed to get response from local AI.";
        }

        var jsonString = await response.Content.ReadAsStringAsync();
        using var doc = JsonDocument.Parse(jsonString);
        var reply = doc.RootElement.GetProperty("response").GetString();
        return reply ?? "No response.";
    }
}
