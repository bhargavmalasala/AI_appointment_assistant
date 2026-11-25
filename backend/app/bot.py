# backend/app/bot.py

import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer

from pipecat.frames.frames import LLMRunFrame

from pipecat.pipeline.pipeline import Pipeline

from pipecat.pipeline.worker import (
    PipelineParams,
    PipelineWorker,
    ProcessorUnusablePolicy
)

from pipecat.processors.aggregators.llm_context import LLMContext

from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams
)

from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport

from pipecat.services.elevenlabs.stt import (
    ElevenLabsRealtimeSTTService
)

from pipecat.services.elevenlabs.tts import (
    ElevenLabsTTSService
)

from pipecat.services.google.llm import GoogleLLMService

from pipecat.transports.base_transport import (
    BaseTransport,
    TransportParams
)

from pipecat.workers.runner import WorkerRunner

from datetime import date


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


def validate_environment():

    required_variables = {
        "ELEVENLABS_API_KEY": ELEVENLABS_API_KEY,
        "ELEVENLABS_VOICE_ID": ELEVENLABS_VOICE_ID,
        "GEMINI_API_KEY": GEMINI_API_KEY
    }

    missing = [
        name
        for name, value in required_variables.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            f"Missing environment variables: {', '.join(missing)}"
        )


# ==========================================
# 2. CREATE VOICE SERVICES
# ==========================================

def create_voice_services():

    # Speech-to-Text
    stt = ElevenLabsRealtimeSTTService(
        api_key=ELEVENLABS_API_KEY
    )

    today = date.today().isoformat()
    # Language Model
    llm = GoogleLLMService(
        api_key=GEMINI_API_KEY,
        model=GEMINI_MODEL,
        system_instruction=f"""
        You are a professional AI doctor appointment assistant.

        Your responsibilities:

        1. Help callers find doctors.
        2. Check available appointment slots.
        3. Book appointments.
        4. Cancel existing appointments.

        CONVERSATION RULES:

        - Speak naturally and politely.
        - Keep responses short and suitable for voice.
        - Ask one question at a time.
        - Never invent doctor information or appointment slots.
        - Use the availability tool before offering appointment times.
        - Never claim an appointment is booked unless the booking
          tool returns success.
        - Never claim cancellation succeeded unless the cancellation
          tool returns success.
        - Ask for the caller's phone number when required.
        - Read the complete phone number back and obtain explicit
          confirmation before booking or cancelling.
        - Do not treat a phone number as verified merely because
          it was spoken.
        - Ask for clarification if information is missing.
        - Do not provide medical diagnosis or treatment advice.

        DATE RULES:

        - Today's date is {today}.
        - Use this date as the reference for today, tomorrow,
          and other relative dates.
        - Pass dates to tools in YYYY-MM-DD format.
        - NEVER invent or assume an appointment date.
        - If the caller does not specify a date, do not pass
          an appointment_date value. Leave it unset or null.
        - If the caller specifies an unclear date, ask for clarification.

        Always communicate the actual result returned by tools.
        """
    )

    # Text-to-Speech
    tts = ElevenLabsTTSService(
        api_key=ELEVENLABS_API_KEY,
        settings=ElevenLabsTTSService.Settings(
            voice=ELEVENLABS_VOICE_ID
        )
    )

    return stt, llm, tts


# ==========================================
# 3. CREATE CONVERSATION CONTEXT
# ==========================================

def create_conversation_context():

    from app.pipecat_tools import (
        check_doctor_availability,
        book_appointment,
        cancel_appointment
    )

    context = LLMContext(
        tools=[
            check_doctor_availability,
            book_appointment,
            cancel_appointment
        ]
    )

    return context


# ==========================================
# 4. BUILD THE PIPELINE
# ==========================================

async def run_bot(
    transport: BaseTransport,
    runner_args: RunnerArguments
):

    logger.info("Starting Doctor Appointment Assistant")

    # Validate credentials
    validate_environment()

    # Initialize AI services
    stt, llm, tts = create_voice_services()

    # Create conversation context
    context = create_conversation_context()

    # Create conversation aggregators
    user_aggregator, assistant_aggregator = (
        LLMContextAggregatorPair(
            context,
            user_params=LLMUserAggregatorParams(
                vad_analyzer=SileroVADAnalyzer()
            )
        )
    )

    # Define processing pipeline
    pipeline = Pipeline([

        transport.input(),

        stt,

        user_aggregator,

        llm,

        tts,

        transport.output(),

        assistant_aggregator

    ])

    # Configure pipeline worker
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True
        ),
        idle_timeout_secs=(
            runner_args.pipeline_idle_timeout_secs
        ),
        processor_unusable_policy=ProcessorUnusablePolicy.END
    )

    # Create runner
    runner = WorkerRunner(
        handle_sigint=runner_args.handle_sigint
    )

    await runner.add_workers(worker)

    # Handle browser connection
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):

        logger.info("Client connected")

        context.add_message({
            "role": "developer",
            "content": (
                "Greet the caller and introduce yourself "
                "as the doctor appointment assistant."
            )
        })

        await worker.queue_frames([
            LLMRunFrame()
        ])

    # Handle browser disconnection
    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):

        logger.info("Client disconnected")

        await runner.cancel()

    await runner.run()


# ==========================================
# 5. PIPECAT ENTRY POINT
# ==========================================

async def bot(runner_args: RunnerArguments):

    transport = await create_transport(
        runner_args,
        {
            "webrtc": lambda: TransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True
            )
        }
    )

    await run_bot(
        transport,
        runner_args
    )


# ==========================================
# 6. START APPLICATION
# ==========================================

if __name__ == "__main__":
    from app import dashboard_api
    from pipecat.runner.run import main

    main()