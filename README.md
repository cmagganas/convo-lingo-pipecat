# ConvoLingo - AI Language Learning Phone Bot

Learn how to connect your ConvoLingo AI language learning assistant to a phone number so users can call and practice languages through voice conversations. This example shows the complete setup for telephone-based AI language learning using Twilio's telephony services. At the end, you'll have a fully functional language learning assistant that users can call to practice languages, learn grammar, expand vocabulary, and explore cultures.

## Prerequisites

- Python 3.10+
- [ngrok](https://ngrok.com/docs/getting-started/) (for tunneling)
- [Twilio Account](https://www.twilio.com/login) and [phone number](https://help.twilio.com/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console)
- AI Service API keys for: [Deepgram](https://console.deepgram.com/signup), [OpenAI](https://auth.openai.com/create-account), and [Cartesia](https://play.cartesia.ai/sign-up)

## Setup

This example requires running both a server and ngrok tunnel in **two separate terminal windows**.

### Clone this repository

```bash
git clone https://github.com/pipecat-ai/pipecat-quickstart-phone-bot.git
cd pipecat-quickstart-phone-bot
```

### Terminal 1: Start ngrok and Configure Twilio

1. Start ngrok:

   In a new terminal, start ngrok to tunnel the local server:

   ```bash
   ngrok http 7860
   ```

   > Want a fixed ngrok URL? Use the `--subdomain` flag:
   > `ngrok http --subdomain=your_ngrok_name 7860`

2. Update the Twilio Webhook:

   - Go to your Twilio phone number's configuration page
   - Under "Voice Configuration", in the "A call comes in" section:
     - Select "Webhook" from the dropdown
     - Enter your ngrok URL: `https://your-ngrok-url.ngrok.io`
     - Ensure "HTTP POST" is selected
   - Click Save at the bottom of the page

3. Configure streams.xml:
   - Copy the template file to create your local version:
     ```bash
     cp templates/streams.xml.template templates/streams.xml
     ```
   - In `templates/streams.xml`, replace `<your_server_url>` with your ngrok URL (without `https://`)
   - The final URL should look like: `wss://abc123.ngrok.io/ws?language={{flow.variables.caller_language}}`
   - This template automatically passes the selected language from the Twilio Call Flow to the bot

### Terminal 2: Server Setup

1. Configure environment variables

   Create a `.env` file:

   ```bash
   cp env.example .env
   ```

   Then, add your API keys:

   ```
   DEEPGRAM_API_KEY=your_deepgram_api_key
   OPENAI_API_KEY=your_openai_api_key
   CARTESIA_API_KEY=your_cartesia_api_key
   ```

   > Optional: Add your `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` to enable auto-hangup.

2. Set up a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   > Using `uv`? Create your venv using: `uv sync`

3. Run the Application

   ```bash
   python bot.py --transport twilio --proxy your_ngrok.ngrok.io
   ```

   > Using `uv`? Run using: `uv run bot.py --transport twilio --proxy your_ngrok.ngrok.io`

   > 💡 First run note: The initial startup may take ~15 seconds as Pipecat downloads required models, like the Silero VAD model.

### Test Your Phone Bot

**Call your Twilio phone number** to start talking with your AI bot! 🚀

> 💡 **Tip**: Check your server terminal for debug logs showing Pipecat's internal workings.

## Troubleshooting

- **Call doesn't connect**: Verify your ngrok URL is correctly set in both Twilio webhook and `streams.xml`
- **No audio or bot doesn't respond**: Check that all API keys are correctly set in your `.env` file
- **Webhook errors**: Ensure your server is running and ngrok tunnel is active before making calls
- **ngrok tunnel issues**: Free ngrok URLs change each restart - remember to update both Twilio and `streams.xml`

## Understanding the Call Flow

1. **Incoming Call**: User dials your Twilio number
2. **Language Selection**: Twilio Call Flow prompts user to select their preferred language for learning (English, Spanish, German, Greek, or Japanese)
3. **Webhook**: Twilio sends call data to your ngrok URL
4. **WebSocket**: Your server establishes real-time audio connection via Websocket and exchanges Media Streams with Twilio
5. **Language Processing**: The bot receives the selected language and configures ConvoLingo to focus on that language
6. **Processing**: Audio flows through your Pipecat Pipeline with language learning system prompts
7. **Response**: ConvoLingo responds with language learning assistance in the selected language

## Language Learning Features

ConvoLingo is a comprehensive AI language learning assistant that helps students:

### **Conversation Practice**
- Engage in natural dialogue practice
- Role-play real-world scenarios
- Practice speaking with confidence

### **Grammar Learning**
- Get clear explanations of grammar rules
- Practice grammar in context
- Receive instant feedback on grammar usage

### **Vocabulary Building**
- Learn topic-specific vocabulary
- Understand word usage and context
- Practice new words in sentences

### **Cultural Insights**
- Learn about customs and traditions
- Explore cultural nuances
- Understand cultural context for language use

## Supported Languages

ConvoLingo supports learning in multiple languages:
- **English**: Practice English conversation, grammar, and vocabulary
- **Spanish**: Learn Spanish with cultural insights from Spanish-speaking countries
- **German**: Master German grammar and vocabulary with cultural context
- **Greek**: Explore Greek language and culture
- **Japanese**: Learn Japanese with cultural understanding

The language selection is passed from the Twilio Call Flow to ConvoLingo via the websocket URL parameters, allowing for personalized language learning experiences.

## Next Steps

- **Deploy to production**: Replace ngrok with a proper server deployment
- **Explore other telephony providers**: Try [Telnyx](https://github.com/pipecat-ai/pipecat-examples/tree/main/telnyx-chatbot) or [Plivo](https://github.com/pipecat-ai/pipecat-examples/tree/main/plivo-chatbot) examples
- **Advanced telephony features**: Check out [pipecat-examples](https://github.com/pipecat-ai/pipecat-examples) for call recording, transfer, and more
- **Join Discord**: Connect with other developers on [Discord](https://discord.gg/pipecat)
