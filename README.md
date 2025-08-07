# ConvoLingo - AI Language Learning Phone Bot

Learn how to connect your ConvoLingo AI language learning assistant to a phone number so users can call and practice languages through voice conversations. This example shows the complete setup for telephone-based AI language learning using Twilio's telephony services. At the end, you'll have a fully functional language learning assistant that users can call to practice languages, learn grammar, expand vocabulary, and explore cultures.

## 🚀 **Deployment Options**

This project supports two deployment methods:

1. **Local Development** - Using ngrok for testing and development
2. **Pipecat Cloud** - Production deployment on Pipecat Cloud infrastructure

## Prerequisites

- Python 3.10+
- [Twilio Account](https://www.twilio.com/login) and [phone number](https://help.twilio.com/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console)
- AI Service API keys for: [Deepgram](https://console.deepgram.com/signup), [OpenAI](https://auth.openai.com/create-account), and [Cartesia](https://play.cartesia.ai/sign-up)

**For Local Development:**
- [ngrok](https://ngrok.com/docs/getting-started/) (for tunneling)

**For Pipecat Cloud:**
- [Pipecat Cloud Account](https://pipecat.daily.co/)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Hub Account](https://hub.docker.com/)

## 🏠 **Local Development Setup**

This method is perfect for testing and development.

### Clone this repository

```bash
git clone https://github.com/cmagganas/convo-lingo-pipecat.git
cd convo-lingo-pipecat
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

## ☁️ **Pipecat Cloud Deployment**

This method is ideal for production deployment with automatic scaling and management.

### Prerequisites Setup

1. **Install Pipecat Cloud CLI:**
   ```bash
   pip install pipecatcloud
   ```

2. **Authenticate with Pipecat Cloud:**
   ```bash
   pcc auth login
   ```

3. **Create Secrets Set:**
   ```bash
   # Create .env file with your API keys (see Local Development section)
   pcc secrets set convo-lingo-v0-secrets --file .env
   ```

### Build and Deploy

1. **Build Docker Image:**
   ```bash
   docker build --platform=linux/arm64 -t convo-lingo-v0:latest .
   ```

2. **Tag and Push to Docker Hub:**
   ```bash
   docker tag convo-lingo-v0:latest your-username/convo-lingo-v0:0.1
   docker push your-username/convo-lingo-v0:0.1
   ```

3. **Create Image Pull Secret:**
   ```bash
   pcc secrets image-pull-secret pull-secret https://index.docker.io/v1/
   ```

4. **Deploy to Pipecat Cloud:**
   ```bash
   pcc deploy convo-lingo-v0 your-username/convo-lingo-v0:0.1 --secrets convo-lingo-v0-secrets --credentials pull-secret
   ```

5. **Scale for Production:**
   ```bash
   pcc deploy convo-lingo-v0 your-username/convo-lingo-v0:0.1 --min-agents 1
   ```

### Configure Twilio for Pipecat Cloud

1. **Get Your Organization Name:**
   ```bash
   pcc organizations list
   ```

2. **Create TwiML Bin in Twilio Console:**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Response>
     <Connect>
       <Stream url="wss://api.pipecat.daily.co/ws/twilio">
         <Parameter name="_pipecatCloudServiceHost"
            value="convo-lingo-v0.YOUR_ORGANIZATION_NAME"/>
       </Stream>
     </Connect>
   </Response>
   ```

3. **Update Twilio Phone Number:**
   - Go to Phone Numbers in Twilio Console
   - Select your phone number
   - Under "Voice Configuration", set "A call comes in" to "TwiML Bin"
   - Select the TwiML Bin you created
   - Save changes

### Monitor Your Deployment

```bash
# Check deployment status
pcc agent status convo-lingo-v0

# View logs
pcc agent logs convo-lingo-v0
```

## 🎯 **Language Learning Features**

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

## 🌍 **Supported Languages**

ConvoLingo supports learning in multiple languages:
- **English**: Practice English conversation, grammar, and vocabulary
- **Spanish**: Learn Spanish with cultural insights from Spanish-speaking countries
- **German**: Master German grammar and vocabulary with cultural context
- **Greek**: Explore Greek language and culture
- **Japanese**: Learn Japanese with cultural understanding

The language selection is passed from the Twilio Call Flow to ConvoLingo via the websocket URL parameters, allowing for personalized language learning experiences.

## 🔧 **Troubleshooting**

### Local Development Issues
- **Call doesn't connect**: Verify your ngrok URL is correctly set in both Twilio webhook and `streams.xml`
- **No audio or bot doesn't respond**: Check that all API keys are correctly set in your `.env` file
- **Webhook errors**: Ensure your server is running and ngrok tunnel is active before making calls
- **ngrok tunnel issues**: Free ngrok URLs change each restart - remember to update both Twilio and `streams.xml`

### Pipecat Cloud Issues
- **Deployment fails**: Check that your Docker image builds successfully and is pushed to Docker Hub
- **Authentication errors**: Ensure you're logged into Pipecat Cloud and have valid API keys
- **Cold starts**: Scale to minimum 1 agent to avoid cold start delays
- **Connection issues**: Verify TwiML configuration matches your organization name

## 📈 **Project Status**

**✅ Successfully Deployed and Functional**

- Phone bot deployed to Pipecat Cloud
- Twilio WebSocket integration working
- Docker containerization with Daily's pipecat-base image
- Secrets management for API keys
- Cold start resolved
- Basic Spanish pronunciation practice functional

### Next Development Priorities:
1. **Voice Quality Enhancement** - Improve pronunciation accuracy
2. **Lesson Plan System** - Structured curriculum with progression
3. **User Progress Tracking** - Save learning progress and preferences
4. **Conversation Flow** - Smoother transitions and natural dialogue
5. **IVR Integration** - Proper language selection handling

## 📚 **Next Steps**

- **Explore other telephony providers**: Try [Telnyx](https://github.com/pipecat-ai/pipecat-examples/tree/main/telnyx-chatbot) or [Plivo](https://github.com/pipecat-ai/pipecat-examples/tree/main/plivo-chatbot) examples
- **Advanced telephony features**: Check out [pipecat-examples](https://github.com/pipecat-ai/pipecat-examples) for call recording, transfer, and more
- **Join Discord**: Connect with other developers on [Discord](https://discord.gg/pipecat)

## 📄 **License**

This project is licensed under the BSD 2-Clause License - see the LICENSE file for details.
