# Voice AI Doctor Appointment Assistant

A real-time voice-based doctor appointment assistant built with **Pipecat, React, ElevenLabs, Google Gemini, and SQLite**.

The assistant allows callers to check doctor availability, book appointments, and cancel existing appointments through natural voice conversations. A web dashboard provides access to the voice assistant, live transcript, doctors, available slots, and appointments.

## Features

### Voice Assistant
- Real-time voice interaction through the browser.
- Speech-to-text using ElevenLabs.
- LLM reasoning and function calling using Google Gemini.
- Text-to-speech using ElevenLabs.
- Doctor availability lookup.
- Appointment booking.
- Appointment cancellation.
- Caller identification using the phone number spoken during the call.
- Phone number readback and confirmation before booking or cancellation.
- Silero VAD for voice activity detection.

### Frontend Dashboard
- React and Vite dashboard.
- Start and end voice calls.
- Live conversation transcript.
- Doctors and available appointment slots.
- Appointments dashboard with automatic updates.
- Phone-style call interface.
- Call timer, mute and end-call controls.
- Live audio waveform.
- Booking confirmation card.
- Dashboard row highlighting after booking and cancellation.
- Call sounds and interface transitions.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python |
| Voice pipeline | Pipecat |
| Speech-to-text | ElevenLabs |
| Text-to-speech | ElevenLabs |
| LLM | Google Gemini |
| Database | SQLite |
| Voice activity detection | Silero VAD |
| Communication | WebRTC |

## Project Structure

```text
AI_appointment_assistant/
├── backend/
│   ├── app/
│   ├── data/
│   ├── .env.example
│   ├── pyproject.toml
│   └── ...
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

## Prerequisites

- Python
- uv package manager
- Node.js and npm
- ElevenLabs API credentials
- Google Gemini API key

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/bhargavmalasala/AI_appointment_assistant.git
cd AI_appointment_assistant
```

### 2. Configure the backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate the virtual environment and install dependencies using uv:

```bash
uv sync
```

Create a `.env` file using `.env.example` as a template.

Configure the following variables:

```env
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=

GEMINI_API_KEY=
GEMINI_MODEL=
```

Add your actual API credentials locally.

### 3. Start the backend

From the backend directory:

```bash
uv run python -m app.bot
```

The Pipecat voice backend runs on port 7860.

### 4. Configure and start the frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed by Vite, usually:

```text
http://localhost:5173
```

## How It Works

The application follows a real-time voice interaction pipeline:

1. The caller speaks through the browser microphone.
2. ElevenLabs converts speech into text.
3. Google Gemini processes the conversation and determines the appropriate action.
4. Gemini can invoke registered Pipecat tools to check availability, book appointments, or cancel appointments.
5. The backend interacts with the SQLite database.
6. ElevenLabs converts the assistant's response into speech.
7. The browser plays the generated audio and displays the conversation transcript.
8. The dashboard refreshes to reflect appointment and availability changes.

## Appointment Workflow

### Check Availability
The caller requests appointments by doctor speciality or date. The assistant retrieves available slots and communicates the results.

### Book Appointment
The caller provides a phone number. The assistant reads the number back and requests confirmation before booking the selected slot.

### Cancel Appointment
The caller provides their phone number. The assistant identifies the caller's appointment, confirms the phone number, and proceeds with cancellation after confirmation.

## Security

- API credentials are stored in local environment files.
- `.env` files and virtual environments should not be committed.
- `.env.example` provides the required environment variable names without exposing credentials.

## LLM Used

Google Gemini.

## Developer

Bhargav Malasala
