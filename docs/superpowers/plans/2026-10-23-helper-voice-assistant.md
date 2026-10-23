# Helper Voice Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the current Russian Ollama CLI into Helper, a fully local voice-in/voice-out assistant.

**Architecture:** Keep the conversation loop in `main.py`. Capture microphone audio with `sounddevice`, write a temporary 16 kHz mono WAV, invoke the local `whisper-cli` executable with the configured Whisper model, send the transcript to Ollama, then speak the response through `pyttsx3`.

**Tech Stack:** Python, requests, sounddevice, pyttsx3, whisper.cpp CLI, Ollama.

**Spec:** `docs/superpowers/specs/2026-10-23-helper-voice-assistant-design.md`

## Global Constraints

- Keep the existing Ollama endpoint, `qwen2.5:3b` model, Russian persona, and conversational history.
- Capture speech from the default microphone, transcribe it locally with Whisper.cpp, and speak replies with a locally available system voice.
- Keep the interface in the existing terminal app: Enter starts and stops recording; typed `exit`, `quit`, or `выход` exits.
- Do not add cloud speech APIs or automatic model downloads.
- Keep audio processing sequential and show the transcript and answer in the terminal.
- Configure executable, Whisper model path, Ollama URL, and Ollama model using environment variables.

## Review Focus

- Missing Whisper executable or model path: show setup guidance and exit cleanly.
- Microphone unavailable or recording interrupted: show a useful error and return to the prompt.
- Empty or whitespace-only transcription: do not send an empty chat message.
- Whisper process failure: show stderr/exit details and continue the session.
- Ollama request failure: do not retain the failed user turn in history.

## File Structure

- Modify `main.py`: configuration, microphone capture, local transcription, TTS, and assistant loop.
- Create `requirements.txt`: Python runtime dependencies for microphone capture and offline speech.
- Create `README.md`: platform-neutral setup, local Whisper model/build setup, environment variables, and usage.

## Task 1: Implement the local voice loop

**Files:**
- Modify: `main.py`
- Create: `requirements.txt`
- Create: `README.md`

**Interfaces:**
- `record_audio() -> Path`: record from the default input device until Enter is pressed, save a temporary mono 16 kHz PCM WAV, and return its path.
- `transcribe_audio(audio_path: Path) -> str`: call the configured `WHISPER_CPP_PATH` executable with `-m WHISPER_MODEL_PATH -f <audio> -l ru -nt -np`; return stdout as the transcript and raise a useful error on failure.
- `speak(text: str) -> None`: use one initialized `pyttsx3` engine to speak text synchronously.
- `ask_ollama(prompt: str) -> str`: preserve the existing request format, history behavior, and timeout; only append the user turn when the request can be retained successfully.
- `main() -> None`: orchestrate recording, transcription, Ollama, and speech sequentially; support text-mode exit commands.

**Dependency choices:** `sounddevice` captures audio and `pyttsx3` speaks through an installed offline system voice. `whisper-cli` and the GGML model are installed separately and selected via environment variables.

- [ ] Add the declared Python dependencies to `requirements.txt`.
- [ ] Implement the functions and CLI flow in `main.py` with clear startup checks and actionable microphone, Whisper, TTS, and Ollama errors.
- [ ] Document installation of Python dependencies, `whisper-cli`, and a Russian-capable local Whisper model, then document default and environment-based configuration in `README.md`.
- [ ] Verify Python syntax with `python -m py_compile main.py` and review `git diff --check` when Git metadata is writable.
- [ ] Commit the feature as `feat: add local voice interaction to Helper` when Git metadata is writable.
