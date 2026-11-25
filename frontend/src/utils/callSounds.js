
let audioContext = null;
let ringingInterval = null;

function getAudioContext() {
  const AudioContextClass =
    window.AudioContext || window.webkitAudioContext;

  if (!AudioContextClass) return null;

  if (!audioContext) {
    audioContext = new AudioContextClass();
  }

  if (audioContext.state === "suspended") {
    audioContext.resume();
  }

  return audioContext;
}

function playTone(frequency, duration, volume = 0.20) {
  const context = getAudioContext();
  if (!context) return;

  const oscillator = context.createOscillator();
  const gain = context.createGain();

  oscillator.type = "sine";
  oscillator.frequency.setValueAtTime(
    frequency,
    context.currentTime
  );

  gain.gain.setValueAtTime(0.001, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(
    volume,
    context.currentTime + 0.03
  );
  gain.gain.exponentialRampToValueAtTime(
    0.001,
    context.currentTime + duration
  );

  oscillator.connect(gain);
  gain.connect(context.destination);

  oscillator.start();
  oscillator.stop(context.currentTime + duration + 0.05);
}

export function startRingingSound() {
  stopRingingSound();

  const playRing = () => {
    playTone(440, 0.45, 0.16);
    setTimeout(() => {
      playTone(480, 0.45, 0.16);
    }, 500);
  };

  playRing();
  ringingInterval = setInterval(playRing, 2200);
}

export function stopRingingSound() {
  if (ringingInterval) {
    clearInterval(ringingInterval);
    ringingInterval = null;
  }
}

export function playConnectedSound() {
  stopRingingSound();
  playTone(660, 0.12, 0.16);
  setTimeout(() => {
    playTone(880, 0.16, 0.16);
  }, 130);
}

export function playEndCallSound() {
  stopRingingSound();
  playTone(480, 0.18, 0.16);
  setTimeout(() => {
    playTone(360, 0.28, 0.16);
  }, 180);
}