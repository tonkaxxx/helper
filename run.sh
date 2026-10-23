#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

export WHISPER_CPP_PATH="${WHISPER_CPP_PATH:-$ROOT_DIR/.tools/whisper.cpp/build/bin/whisper-cli}"
export WHISPER_MODEL_PATH="${WHISPER_MODEL_PATH:-$ROOT_DIR/.tools/whisper.cpp/models/ggml-base.bin}"

if [ -d "$ROOT_DIR/.tools/portaudio/lib" ] && [ -d "$ROOT_DIR/.tools/espeak-ng/lib" ]; then
    export LD_LIBRARY_PATH="$ROOT_DIR/.tools/portaudio/lib:$ROOT_DIR/.tools/espeak-ng/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    export ESPEAK_DATA_PATH="$ROOT_DIR/.tools/espeak-ng/share/espeak-ng-data"
fi

exec "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/main.py" "$@"
