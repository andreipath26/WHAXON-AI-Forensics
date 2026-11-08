# Voice control design

Voice is an optional input/output interface for WHAXON, not an autonomous permission channel.

MVP: opt-in push-to-talk, visible microphone state, local STT (benchmark whisper.cpp/faster-whisper), optional local TTS (Piper), live editable transcription, explicit typed intents, accessible text-only fallback. Later: wake-word opt-in, VAD, barge-in, streaming transcription, multilingual support and configurable voices.

Read-only navigation/status commands may execute using the authenticated session's existing view permissions. Security actions become reviewable proposals. Sensitive changes or active security execution require WHAXON's actual approval mechanisms; spoken 'yes' alone does not authorize consequential actions.

Testing: acoustic confusion, spoof/replay/prompt injection, silence/noise, multilingual input, denied microphone permissions, device disconnect, accessibility, model failure, CPU/RAM use, interruption and persistent job reconciliation.
