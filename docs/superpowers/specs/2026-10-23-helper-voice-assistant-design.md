# Helper voice assistant design

## Intent

Turn the existing Russian Ollama text chat in `main.py` into a local voice assistant called Helper. The user speaks a prompt; Helper transcribes it, sends it to the configured local Ollama model, and speaks the reply.

## Goals

- Keep the existing Ollama endpoint, `qwen2.5:3b` model, Russian persona, and conversational history.
- Capture speech from the default microphone, transcribe it locally with Whisper.cpp, and speak replies with a locally available system voice.
- Keep the interface in the existing terminal app: Enter starts and stops recording; typed `exit`, `quit`, or `выход` exits.
- Explain setup requirements and configuration in a README, including where to obtain a Whisper.cpp executable and a local Whisper model.

## Non-goals

- No cloud speech recognition, cloud text-to-speech, web interface, wake word, or background listening.
- No automatic installation or download of speech models at runtime.

## Constraints and implementation calls

- The repository currently contains only `main.py`; preserve that entry point and build on its existing Ollama chat loop.
- Use Whisper.cpp through its command-line executable and a user-provided local model path. Capture microphone audio locally and pass a temporary WAV file to the executable.
- Use `sounddevice` for microphone capture and `pyttsx3` for offline speech synthesis. Report clear setup errors when the executable, model, microphone, or system voice engine is unavailable.
- Keep audio processing sequential: record, transcribe, call Ollama, then speak the response. Text output remains visible in the terminal.
- Allow executable, model, Ollama URL, and model name to be configured with environment variables while keeping current Ollama defaults.

## Approaches considered

1. **Whisper.cpp + sounddevice + pyttsx3 (chosen):** fully local voice pipeline, with a separate Whisper.cpp executable and model to set up. This matches the user's choice of Whisper.cpp and keeps the project in its existing Python CLI.
2. **Vosk + sounddevice + pyttsx3:** smaller and simpler speech model setup, but the user selected Whisper.cpp.
3. **Cloud speech APIs:** less local setup, but require internet and send audio to a service, contrary to the requested offline operation.

## Approval

This design is ready for user review. Implementation begins after approval.
