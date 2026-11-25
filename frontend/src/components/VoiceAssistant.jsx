import {
  startRingingSound,
  stopRingingSound,
  playConnectedSound,
  playEndCallSound,
} from "../utils/callSounds";
import { useEffect, useRef, useState } from "react";

import {
  PipecatClientAudio,
  PipecatClientProvider,
} from "@pipecat-ai/client-react";

import { useVoiceAssistant } from "../hooks/useVoiceAssistant";
import "../App.css";

function formatDuration(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function VoiceAssistantUI({
  bookingConfirmation,
  status,
  error,
  connect,
  disconnect,
  isConnected,
  transcript,
  isMuted,
  toggleMute,
  isSpeaking,
  localAudioLevel,
  remoteAudioLevel,
}) {
  const [isCallOpen, setIsCallOpen] = useState(false);
  const [callSeconds, setCallSeconds] = useState(0);

  const transcriptContainerRef = useRef(null);

  const isConnecting = status === "connecting";
  const isActive = isConnected;
  const isAssistantReady = status === "ready";

  const safeLocalLevel = Math.min(1, Math.max(0, Number(localAudioLevel) || 0));

  const safeRemoteLevel = Math.min(
    1,
    Math.max(0, Number(remoteAudioLevel) || 0),
  );

  const audioLevel = Math.max(safeLocalLevel, safeRemoteLevel);

  const waveformIsActive = isActive && audioLevel > 0.015;
  useEffect(() => {
    if (status === "ready") {
      stopRingingSound();
      playConnectedSound();
    }

    if (status === "disconnected") {
      stopRingingSound();
    }
  }, [status]);

  useEffect(() => {
    const container = transcriptContainerRef.current;

    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [transcript, isCallOpen]);

  useEffect(() => {
    if (!isActive) {
      setCallSeconds(0);
      return;
    }

    const interval = setInterval(() => {
      setCallSeconds((previous) => previous + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [isActive]);

  const handleStartCall = async () => {
    setCallSeconds(0);
    setIsCallOpen(true);

    startRingingSound();

    try {
      await connect();
    } catch (err) {
      console.error("Failed to connect voice assistant:", err);
      stopRingingSound();
    }
  };

  const handleEndCall = async () => {
    stopRingingSound();

    try {
      await disconnect();
    } finally {
      playEndCallSound();
      setIsCallOpen(false);
      setCallSeconds(0);
    }
  };

  const getStatusText = () => {
    if (error) return "Connection issue";

    switch (status) {
      case "connecting":
        return "Connecting to CareConnect...";
      case "connected":
        return "Call connected";
      case "ready":
        return isSpeaking ? "Assistant is speaking" : "Listening to you";
      default:
        return "Call ended";
    }
  };

  return (
    <>
      <div className="assistant-container">
        <div className="voice-launcher-card">
          <div className="voice-launcher-top">
            <div className="voice-launcher-icon">✚</div>

            <div>
              <h2>CareConnect Voice</h2>
              <p>Your personal appointment assistant</p>
            </div>
          </div>

          <div className="voice-launcher-description">
            Book appointments, check doctor availability, or cancel an existing
            appointment through a natural voice conversation.
          </div>

          <div className="voice-launcher-features">
            <span>● Voice enabled</span>
            <span>● Live transcript</span>
          </div>

          <button
            type="button"
            className="voice-start-button voice-launcher-button"
            onClick={handleStartCall}
            disabled={isConnecting || isActive}
          >
            <span className="voice-button-icon">☎</span>
            {isConnecting ? "Connecting..." : "Try Call"}
          </button>

          {error && (
            <div className="voice-error">
              <span>!</span>
              <p>{error}</p>
            </div>
          )}
        </div>
      </div>

      {isCallOpen && (
        <div
          className="phone-call-overlay"
          role="dialog"
          aria-modal="true"
          aria-label="CareConnect voice call"
        >
          <div
            className={`phone-call-window phone-split-window ${
              isConnecting ? "call-connecting" : ""
            } ${isActive ? "call-active" : ""} ${
              waveformIsActive ? "call-speaking" : ""
            }`}
          >
            <div className="phone-call-header phone-split-header">
              <div className="phone-header-brand">
                <div className="phone-header-logo">✚</div>
                <div>
                  <span className="phone-call-label">CARECONNECT AI</span>
                  <p>Your healthcare companion</p>
                </div>
              </div>

              <div className="phone-header-right">
                <span className="phone-secure-label">
                  <span className="phone-state-dot" />
                  SECURE VOICE SESSION
                </span>

                <button
                  type="button"
                  className="phone-close-button"
                  onClick={handleEndCall}
                  aria-label="End call and close"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="phone-split-body">
              <section className="phone-call-left">
                <div className="phone-caller-area">
                  <div
                    className={`phone-avatar-ring ${
                      waveformIsActive ? "speaking" : ""
                    } ${isConnecting ? "connecting" : ""}`}
                  >
                    <div className="phone-caller-avatar">
                      <span>✚</span>
                    </div>
                  </div>

                  <div className="phone-assistant-tag">
                    <span className="phone-assistant-tag-dot" />
                    AI HEALTHCARE ASSISTANT
                  </div>

                  <h2>CareConnect Assistant</h2>

                  <p className="phone-caller-subtitle">
                    Doctor Appointment Support
                  </p>

                  <div className={`phone-call-state ${status}`}>
                    <span className="phone-state-dot" />
                    {getStatusText()}
                  </div>

                  {isActive && (
                    <div className="phone-call-timer">
                      {formatDuration(callSeconds)}
                    </div>
                  )}

                  {isConnecting && (
                    <div className="phone-connecting-text">
                      Preparing your secure voice connection...
                    </div>
                  )}
                </div>

                <div className="phone-wave-area">
                  <div
                    className={`phone-waveform ${
                      waveformIsActive ? "active" : ""
                    }`}
                    aria-label={
                      waveformIsActive
                        ? "Live voice activity"
                        : "Waiting for speech"
                    }
                    role="img"
                  >
                    {Array.from({ length: 35 }, (_, index) => {
                      const center = 1 - Math.abs(index - 17) / 17;

                      const variation =
                        0.65 + Math.abs(Math.sin(index * 0.8)) * 0.35;

                      const pulse =
                        0.88 + Math.abs(Math.sin(index * 1.7)) * 0.24;

                      const height =
                        5 + audioLevel * center * variation * pulse * 99;

                      return (
                        <span
                          key={index}
                          style={{
                            height: `${Math.max(5, height)}px`,
                            opacity: 0.55 + center * 0.45,
                          }}
                        />
                      );
                    })}
                  </div>

                  {/* <p className="phone-wave-caption">
                    {isConnecting
                      ? "Establishing your connection"
                      : !isActive
                        ? "Waiting for connection"
                        : isMuted
                          ? "Your microphone is muted"
                          : waveformIsActive
                            ? "Voice activity detected"
                            : ""}
                  </p> */}
                </div>

                {bookingConfirmation && (
  <div className="phone-booking-confirmation">
    <div className="phone-confirmation-icon">
      {bookingConfirmation.type === "cancelled" ? "✓" : "✓"}
    </div>

    <div className="phone-confirmation-details">
      <strong>
        {bookingConfirmation.type === "cancelled"
          ? "Appointment cancelled!"
          : "Appointment confirmed!"}
      </strong>

      <p>
        <b>Appointment ID:</b> #{bookingConfirmation.appointmentId}
      </p>

      <p><b>Doctor:</b> {bookingConfirmation.doctorName}</p>
      <p><b>Speciality:</b> {bookingConfirmation.speciality}</p>
      <p><b>Date:</b> {bookingConfirmation.date}</p>
      <p><b>Time:</b> {bookingConfirmation.time}</p>

      <span className="phone-confirmation-status">
        {bookingConfirmation.type === "cancelled"
          ? "CANCELLATION SUCCESSFUL"
          : "BOOKING SUCCESSFUL"}
      </span>
    </div>
  </div>
)}

                <div className="phone-call-controls phone-split-controls">
                  <button
                    type="button"
                    className={`phone-control-button ${isMuted ? "muted" : ""}`}
                    onClick={toggleMute}
                    disabled={!isActive}
                    aria-label={
                      isMuted ? "Unmute microphone" : "Mute microphone"
                    }
                  >
                    <span>{isMuted ? "🔇" : "🎙"}</span>
                    <small>{isMuted ? "Unmute" : "Mute"}</small>
                  </button>

                  <button
                    type="button"
                    className="phone-end-button"
                    onClick={handleEndCall}
                    disabled={!isActive && !isConnecting}
                    aria-label="End call"
                  >
                    <span className="phone-end-icon">☎</span>
                    <small>End call</small>
                  </button>
                </div>

                {error && <div className="phone-call-error">{error}</div>}
              </section>

              <section className="phone-call-right">
                <div className="phone-transcript">
                  <div className="phone-transcript-header">
                    <div>
                      <h3>Live conversation</h3>
                      <p>Real-time conversation transcript</p>
                    </div>

                    <span className="phone-live-indicator">
                      <span />
                      LIVE
                    </span>
                  </div>

                  <div
                    className="phone-transcript-messages"
                    ref={transcriptContainerRef}
                    aria-live="polite"
                    aria-relevant="additions text"
                  >
                    {!transcript || transcript.length === 0 ? (
                      <div className="phone-transcript-empty">
                        <span className="phone-transcript-empty-icon">◉</span>
                        <p>Your conversation will appear here.</p>
                        <span>
                          Start speaking when your assistant is ready.
                        </span>
                      </div>
                    ) : (
                      transcript.map((message) => (
                        <div
                          key={message.id}
                          className={`phone-message ${
                            message.speaker === "You"
                              ? "phone-message-user"
                              : "phone-message-assistant"
                          }`}
                        >
                          <span>
                            {message.speaker === "You" ? "YOU" : "CARECONNECT"}
                          </span>
                          <p>{message.text}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </section>
            </div>

            <div className="phone-call-footer phone-split-footer">
              <span>✚</span>
              Healthcare, made simpler.
              <span>POWERED BY CARECONNECT AI</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function VoiceAssistant({ bookingConfirmation }) {
  const {
    client,
    status,
    error,
    connect,
    disconnect,
    isConnected,
    transcript,
    isMuted,
    toggleMute,
    isSpeaking,
    localAudioLevel,
    remoteAudioLevel,
  } = useVoiceAssistant();

  return (
    <>
      <VoiceAssistantUI
        bookingConfirmation={bookingConfirmation}
        status={status}
        error={error}
        connect={connect}
        disconnect={disconnect}
        isConnected={isConnected}
        transcript={transcript}
        isMuted={isMuted}
        toggleMute={toggleMute}
        isSpeaking={isSpeaking}
        localAudioLevel={localAudioLevel}
        remoteAudioLevel={remoteAudioLevel}
      />

      {client && (
        <PipecatClientProvider client={client}>
          <PipecatClientAudio />
        </PipecatClientProvider>
      )}
    </>
  );
}

export default VoiceAssistant;
