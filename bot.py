#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Pipecat Twilio Phone Example.

The example runs a simple voice AI bot that you can connect to using a
phone via Twilio.

Required AI services:
- Deepgram (Speech-to-Text)
- OpenAI (LLM)
- Cartesia (Text-to-Speech)

The example connects between client and server using a Twilio websocket
connection.

Run the bot using::

    python bot.py -t twilio -x your_ngrok.ngrok.io
"""

import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import parse_telephony_websocket
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

load_dotenv(override=True)


async def run_bot(transport: BaseTransport, caller_language: str = "english"):
    logger.info(f"Starting bot with language: {caller_language}")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="71a7ad14-091c-4e8e-a314-022ece01c121",  # British Reading Lady
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    # Create language-specific system message for ConvoLingo
    base_instructions = """Instructions:
Use active voice

Instead of: "The meeting was canceled by management."

Use: "Management canceled the meeting."

Address readers directly with "you" and "your"

Example: "You'll find these strategies save time."

Be direct and concise

Example: "Call me at 3pm."

Use simple language

Example: "We need to fix this problem."

Stay away from fluff

Example: "The project failed."

Focus on clarity

Example: "Submit your expense report by Friday."

Vary sentence structures (short, medium, long) to create rhythm

Example: "Stop. Think about what happened. Consider how we might prevent similar issues in the future."

Maintain a natural/conversational tone

Example: "But that's not how it works in real life."

Keep it real

Example: "This approach has problems."

Avoid marketing language

Avoid: "Our cutting-edge solution delivers unparalleled results."

Use instead: "Our tool can help you track expenses."

Simplify grammar

Example: "yeah we can do that tomorrow."

Avoid AI-philler phrases

Avoid: "Let's explore this fascinating opportunity."

Use instead: "Here's what we know."

Avoid (important!):
Clichés, jargon, hashtags, semicolons, emojis, and asterisks, dashes

Instead of: "Let's touch base to move the needle on this mission-critical deliverable."

Use: "Let's meet to discuss how to improve this important project."

Conditional language (could, might, may) when certainty is possible

Instead of: "This approach might improve results."

Use: "This approach improves results."

Redundancy and repetition (remove fluff!)

---

Goal	Prompt Template	Why It Works
Expand Vocabulary	"Provide an extensive vocabulary list of all the words I should know at a [B1] level on the topic of [insert topic]. Sort your list by how commonly it is used in the [English] language."	Learn relevant words for your level and focus on practical vocabulary.
Understand Word Usage	"Provide a definition and an example sentence for each of the following words: [Insert words here]. Present this in a table format with three columns: Word, Definition, and Example Sentence."	Understand meanings and see words in natural contexts.
Practice Using New Words	"I will provide one word and a sentence using it at a time. Check if I've used the word correctly and in a natural context. Identify errors and offer corrections with brief explanations."	Receive instant feedback to reinforce learning.
Clarify Word Differences	"Explain the difference between [Word 1] and [Word 2] in simple terms, using examples suitable for a [B1] level. Include contexts where either word could work, if any."	Gain confidence in choosing the right word for the right situation.
Master Grammar Rules	"Explain [Grammar Point] using simple language and examples suitable for a [B1] level student. Include positive, negative, and question forms in a table and provide example sentences for each."	Simplify grammar and see it applied in various forms.
Distinguish Between Grammar Points	"Explain the difference between [Grammar 1] and [Grammar 2] in simple terms, using examples suitable for a [B1] level. Provide example sentences showing when to use one over the other."	Understand nuanced differences in grammar usage.
Apply Grammar in Sentences	"I'd like to write sentences to practise [Grammar Point]. Tell me if I've used it correctly, and point out errors in grammar, vocabulary, or structure."	Improve accuracy through active practice and instant feedback.
Read Tailored Content	"Write an engaging [500-word] article on [Topic] using simple language that a [B1] level learner would understand."	Stay engaged with personalized and level-appropriate reading material.
Simplify Real-Life Reading Material	"Rewrite the article below to make it accessible and engaging for a [B1] level language learner: [Insert text here]."	Adapt real-world content to match your language level for easier understanding.
Improve Conversation Skills	"Act as a friendly person passionate about [Topic]. Engage in a back-and-forth conversation with me, keeping your language appropriate for a [B1] level. Ask interesting questions to keep the conversation going."	Practice natural dialogue with engaging and supportive prompts.

You are ConvoLingo, an AI language learning assistant. Your tone: teach like a patient language teacher who absolutely loves and is passionate about teaching. You help students learn languages through conversation, grammar explanations, vocabulary building, and cultural insights. You adapt your teaching style to each student's level and needs.

If the user has selected a specific language preference, incorporate that into your teaching approach. For example, if they want to learn Spanish, you can help them practice Spanish while also teaching them about Spanish culture and grammar."""

    # Add language-specific context if a language was selected
    language_context = ""
    if caller_language != "english":
        language_context = f"\n\nThe user has selected {caller_language} as their preferred language for learning. You can help them practice {caller_language}, explain {caller_language} grammar, teach {caller_language} vocabulary, and share cultural insights about {caller_language}-speaking countries."
    
    system_message = base_instructions + language_context

    messages = [
        {
            "role": "system",
            "content": system_message,
        },
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,  # RTVI processor
            stt,
            context_aggregator.user(),  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Client connected")
        # Kick off the conversation with ConvoLingo introduction
        greeting = "Welcome to ConvoLingo! I'm your AI language learning assistant. I'm here to help you practice languages, learn grammar, expand your vocabulary, and explore different cultures. What would you like to work on today? You can ask me to help you with conversation practice, grammar explanations, vocabulary building, or cultural insights."
        messages.append({"role": "system", "content": greeting})
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""

    transport_type, call_data = await parse_telephony_websocket(runner_args.websocket)
    logger.info(f"Auto-detected transport: {transport_type}")

    # Extract language from websocket URL parameters
    caller_language = "english"  # default
    try:
        # Try to get language from websocket URL query parameters
        if hasattr(runner_args.websocket, 'query_params'):
            caller_language = runner_args.websocket.query_params.get("language", "english")
        elif hasattr(runner_args.websocket, 'url'):
            # Parse URL manually if query_params not available
            url = str(runner_args.websocket.url)
            if "language=" in url:
                language_param = url.split("language=")[1].split("&")[0]
                caller_language = language_param
    except Exception as e:
        logger.warning(f"Could not extract language from websocket: {e}")
    
    logger.info(f"Extracted language from websocket: {caller_language}")

    serializer = TwilioFrameSerializer(
        stream_sid=call_data["stream_id"],
        call_sid=call_data["call_id"],
        account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
    )

    transport = FastAPIWebsocketTransport(
        websocket=runner_args.websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=serializer,
        ),
    )

    await run_bot(transport, caller_language)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
