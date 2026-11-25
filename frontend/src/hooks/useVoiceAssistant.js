
import { useCallback, useRef, useState } from "react";
import { PipecatClient } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";

const BACKEND_URL = "http://localhost:7860";
const START_ENDPOINT = `${BACKEND_URL}/start`;

export function useVoiceAssistant() {
  const clientRef = useRef(null);
  const [client, setClient] = useState(null);

  const [status, setStatus] = useState("disconnected");
  const [error, setError] = useState("");
  const [transcript, setTranscript] = useState([]);
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [localAudioLevel, setLocalAudioLevel] = useState(0);
  const [remoteAudioLevel, setRemoteAudioLevel] = useState(0);

  const connect = useCallback(async () => {
    if (clientRef.current) return;

    setStatus("connecting");
    setError("");
    setTranscript([]);
    setIsMuted(false);
    setIsSpeaking(false);

    setLocalAudioLevel(0);
  setRemoteAudioLevel(0);

    const transport = new SmallWebRTCTransport();

    const client = new PipecatClient({
      transport,
      enableMic: true,
      enableCam: false,

      callbacks: {
        onConnected: () => {
          console.log("Connected to Pipecat backend");
          setStatus("connected");
        },

        onLocalAudioLevel: (level) => {
  setLocalAudioLevel(level);
},

onRemoteAudioLevel: (level) => {
  setRemoteAudioLevel(level);
},

        onBotReady: () => {
          console.log("Voice assistant is ready");
          setStatus("ready");
        },

        onDisconnected: () => {
          console.log("Disconnected from Pipecat backend");

          clientRef.current = null;
          setClient(null);
          setStatus("disconnected");
          setIsMuted(false);
          setIsSpeaking(false);
          setLocalAudioLevel(0);
setRemoteAudioLevel(0);
        },

        onUserStartedSpeaking: () => {
          setIsSpeaking(true);
        },

        onUserStoppedSpeaking: () => {
          setIsSpeaking(false);
        },

        onBotStartedSpeaking: () => {
          setIsSpeaking(true);
        },

        onBotStoppedSpeaking: () => {
          setIsSpeaking(false);
        },

        onUserInput: (data) => {
          console.log("USER INPUT EVENT:", data);

          if (data?.final && data?.text?.trim()) {
            setTranscript((previous) => [
              ...previous,
              {
                id: Date.now() + Math.random(),
                speaker: "You",
                text: data.text.trim(),
              },
            ]);
          }
        },

        onBotOutput: (data) => {
          console.log("BOT OUTPUT:", data);

          const text = data?.text?.trim();

          if (!text) return;

          // Only add a new spoken segment once.
          if (data.spoken_status !== "new") return;

          setTranscript((previous) => {
            const alreadyExists = previous.some(
              (message) =>
                message.speaker === "Assistant" &&
                message.segmentId === data.segment_id
            );

            if (alreadyExists) return previous;

            return [
              ...previous,
              {
                id: `${data.segment_id}-${Date.now()}`,
                segmentId: data.segment_id,
                speaker: "Assistant",
                text,
              },
            ];
          });
        },

        onTransportStateChanged: (state) => {
          console.log("Transport state:", state);
        },

        onError: (err) => {
          console.error("Pipecat error:", err);

          setError(
            err?.message || "A voice connection error occurred."
          );
        },
      },
    });

    clientRef.current = client;
    setClient(client);

    try {
      await client.initDevices();

      await client.startBotAndConnect({
        endpoint: START_ENDPOINT,
        requestData: {
          transport: "webrtc",
          enableDefaultIceServers: true,
        },
      });
    } catch (err) {
      console.error("Connection failed:", err);

      setError(
        err?.message || "Unable to connect to the assistant."
      );

      try {
        await client.disconnect();
      } catch (disconnectError) {
        console.error("Cleanup failed:", disconnectError);
      }

      clientRef.current = null;
      setClient(null); 
      setStatus("disconnected");
      setIsMuted(false);
      setIsSpeaking(false);
    }
  }, []);

  const disconnect = useCallback(async () => {
    const client = clientRef.current;

    if (!client) {
      setStatus("disconnected");
      return;
    }

    try {
      await client.disconnect();
    } catch (err) {
      console.error("Disconnection failed:", err);

      setError(
        err?.message || "Unable to disconnect cleanly."
      );
    } finally {
      clientRef.current = null;
      setClient(null); 
      setStatus("disconnected");
      setIsMuted(false);
      setIsSpeaking(false);
    }
  }, []);

  const toggleMute = useCallback(() => {
    const client = clientRef.current;

    if (!client) return;

    const nextMutedState = !client.isMicEnabled;

    client.enableMic(nextMutedState);
    setIsMuted(!nextMutedState);
  }, []);

  return {
    client,
    status,
    error,
    transcript,
    connect,
    disconnect,
    isConnected:
      status === "connected" || status === "ready",
    isMuted,
    toggleMute,
    isSpeaking,
    localAudioLevel,
    remoteAudioLevel,
  };
}
