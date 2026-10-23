"""Local voice assistant that connects Whisper.cpp to Ollama."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any

import requests


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
WHISPER_CPP_PATH = os.getenv("WHISPER_CPP_PATH", "whisper-cli")
WHISPER_MODEL_PATH = os.getenv("WHISPER_MODEL_PATH", "")
SAMPLE_RATE = 16_000
EXIT_COMMANDS = {"exit", "quit", "выход"}

messages: list[dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "Ты Хелпер, персональный ИИ-ассистент. "
            "Общайся на русском, кратко и естественно. "
            "Помогай с Linux, DevOps и автоматизацией."
        ),
    }
]


def resolve_whisper_executable() -> str:
    """Find whisper-cli and give setup guidance when it is unavailable."""
    executable = shutil.which(WHISPER_CPP_PATH)
    if executable:
        return executable

    configured_path = Path(WHISPER_CPP_PATH).expanduser()
    if configured_path.is_file() and os.access(configured_path, os.X_OK):
        return str(configured_path)

    raise RuntimeError(
        "Не найден whisper-cli. Установите whisper.cpp или задайте путь "
        "в переменной WHISPER_CPP_PATH. Инструкция есть в README.md."
    )


def validate_setup() -> tuple[str, Path]:
    """Validate local Whisper configuration before opening the microphone."""
    executable = resolve_whisper_executable()
    if not WHISPER_MODEL_PATH:
        raise RuntimeError(
            "Не задана переменная WHISPER_MODEL_PATH. Укажите путь к локальной "
            "модели Whisper (например, ggml-base.bin)."
        )

    model_path = Path(WHISPER_MODEL_PATH).expanduser()
    if not model_path.is_file():
        raise RuntimeError(f"Файл модели Whisper не найден: {model_path}")
    return executable, model_path


def record_audio() -> Path:
    """Record mono 16 kHz audio from the default microphone until Enter."""
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError(
            "Не установлен пакет sounddevice. Выполните: pip install -r requirements.txt"
        ) from exc

    audio_chunks: list[bytes] = []

    def collect_audio(indata: Any, _frames: int, _time: Any, status: Any) -> None:
        if status:
            print(f"\nПредупреждение микрофона: {status}")
        audio_chunks.append(indata.copy().tobytes())

    print("Говорите. Нажмите Enter, когда закончите.")
    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            callback=collect_audio,
        ):
            input()
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(
            "Не удалось записать звук. Проверьте подключение и доступ к микрофону."
        ) from exc

    if not audio_chunks:
        raise RuntimeError("Микрофон не записал звук. Попробуйте ещё раз.")

    temp_file = tempfile.NamedTemporaryFile(prefix="helper-", suffix=".wav", delete=False)
    audio_path = Path(temp_file.name)
    temp_file.close()

    try:
        with wave.open(str(audio_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(b"".join(audio_chunks))
    except Exception:
        audio_path.unlink(missing_ok=True)
        raise
    return audio_path


def transcribe_audio(audio_path: Path, executable: str, model_path: Path) -> str:
    """Run local Whisper.cpp and return the Russian transcript."""
    command = [
        executable,
        "-m",
        str(model_path),
        "-f",
        str(audio_path),
        "-l",
        "ru",
        "-nt",
        "-np",
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        raise RuntimeError(f"Не удалось запустить whisper.cpp: {exc}") from exc

    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(
            "Whisper.cpp завершился с ошибкой"
            + (f":\n{details}" if details else ". Проверьте модель и WAV-файл.")
        )
    return result.stdout.strip()


def create_speech_engine() -> Any:
    """Initialize offline TTS and select a Russian system voice when available."""
    try:
        import pyttsx3
    except ImportError as exc:
        raise RuntimeError(
            "Не установлен пакет pyttsx3. Выполните: pip install -r requirements.txt"
        ) from exc

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices") or []
        for voice in voices:
            locale_values = []
            for language in getattr(voice, "languages", []) or []:
                if isinstance(language, bytes):
                    language = language.decode("utf-8", errors="ignore")
                locale_values.append(str(language).lower())
            voice_description = " ".join(
                [str(getattr(voice, "id", "")), str(getattr(voice, "name", ""))]
                + locale_values
            ).lower()
            russian_locale = any(
                language.strip("\x05").split("-", 1)[0].split("_", 1)[0] == "ru"
                for language in locale_values
            )
            if russian_locale or "russian" in voice_description:
                engine.setProperty("voice", voice.id)
                break
        return engine
    except Exception as exc:
        raise RuntimeError(
            "Не удалось запустить локальный синтез речи. Установите системный "
            "движок речи и русский голос (см. README.md)."
        ) from exc


def speak(engine: Any, text: str) -> None:
    """Speak a response synchronously using the local system voice."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        print(f"Не удалось озвучить ответ: {exc}")


def ask_ollama(prompt: str) -> str:
    """Send one turn to Ollama and preserve history only on success."""
    messages.append({"role": "user", "content": prompt})
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "messages": messages, "stream": False},
            timeout=300,
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"].strip()
        if not answer:
            raise ValueError("Ollama вернула пустой ответ")
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        messages.pop()
        raise RuntimeError(f"Ошибка при запросе к Ollama: {exc}") from exc

    messages.append({"role": "assistant", "content": answer})
    return answer


def main() -> int:
    try:
        whisper_executable, whisper_model = validate_setup()
        speech_engine = create_speech_engine()
    except RuntimeError as exc:
        print(f"Ошибка настройки Helper: {exc}")
        return 1

    print("Хелпер готов. Говорите по-русски или введите сообщение текстом.")
    print("Нажмите Enter для записи; введите exit, quit или выход для завершения.")

    while True:
        try:
            command = input("\nТы: ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nЗавершение работы.")
            break

        if command.lower() in EXIT_COMMANDS:
            break

        audio_path: Path | None = None
        try:
            if command:
                prompt = command
            else:
                audio_path = record_audio()
                print("Распознаю речь локально...")
                prompt = transcribe_audio(audio_path, whisper_executable, whisper_model)
                if prompt:
                    print(f"Ты (распознано): {prompt}")
                else:
                    print("Не удалось распознать речь. Попробуйте ещё раз.")
                    continue

            answer = ask_ollama(prompt)
            print(f"\nХелпер: {answer}")
            speak(speech_engine, answer)
        except RuntimeError as exc:
            print(f"\nОшибка: {exc}")
        finally:
            if audio_path is not None:
                audio_path.unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nЗавершение работы.")
