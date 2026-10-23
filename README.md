# Хелпер — локальный голосовой ИИ-ассистент

Хелпер принимает вопросы через микрофон или текстом, распознаёт русскую речь локально с помощью Whisper.cpp, отправляет текст локальной модели в Ollama и озвучивает ответ системным голосом. Во время работы аудио не отправляется в облачные сервисы. Для первого запуска нужно отдельно установить программы и модели.

## Что понадобится

- Python 3.10 или новее.
- Ollama и загруженная модель `qwen2.5:3b`.
- Собранный исполняемый файл `whisper-cli` из [whisper.cpp](https://github.com/ggml-org/whisper.cpp) и мультиязычная модель Whisper, например `ggml-base.bin`.
- Микрофон, динамики или наушники, а также системный движок синтеза речи с русским голосом.

## Установка

### 1. Подготовьте Ollama

Установите Ollama для своей системы, запустите её и загрузите модель:

```bash
ollama pull qwen2.5:3b
```

По умолчанию Хелпер обращается к `http://127.0.0.1:11434/api/chat`. Перед запуском убедитесь, что Ollama работает локально.

### 2. Установите Python-зависимости

В корне репозитория создайте виртуальное окружение и установите пакеты:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

В Windows активируйте окружение командой `.venv\Scripts\activate`.

На Linux могут потребоваться системные аудиобиблиотеки. Например, в Debian или Ubuntu:

```bash
sudo apt install libportaudio2 portaudio19-dev espeak-ng
```

Для озвучивания установите или включите русский системный голос. В Linux с eSpeak NG обычно доступен голос `ru`; в macOS и Windows доступность голоса зависит от установленных системных голосов. Если русский голос не найден, Хелпер использует голос системы по умолчанию.

### 3. Соберите Whisper.cpp и подготовьте модель

Сборка из официального репозитория Whisper.cpp:

```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
cmake -B build
cmake --build build --config Release -j
sh ./models/download-ggml-model.sh base
```

Модель `base` мультиязычная и подходит для русского. Скачать модель нужно один раз во время установки; при обычной работе Хелпер использует локальный файл.

## Запуск

Из корня этого репозитория активируйте виртуальное окружение, задайте пути к Whisper.cpp и модели, затем запустите приложение:

```bash
export WHISPER_CPP_PATH="$HOME/whisper.cpp/build/bin/whisper-cli"
export WHISPER_MODEL_PATH="$HOME/whisper.cpp/models/ggml-base.bin"
python main.py
```

В PowerShell используйте:

```powershell
$env:WHISPER_CPP_PATH = "$HOME\whisper.cpp\build\bin\Release\whisper-cli.exe"
$env:WHISPER_MODEL_PATH = "$HOME\whisper.cpp\models\ggml-base.bin"
python main.py
```

Нажмите Enter в приглашении `Ты:`, чтобы начать запись, и нажмите Enter ещё раз, чтобы остановить её. Текст можно также ввести с клавиатуры. Для завершения введите `exit`, `quit` или `выход`.

## Настройки

| Переменная | Значение по умолчанию | Назначение |
| --- | --- | --- |
| `WHISPER_CPP_PATH` | `whisper-cli` из `PATH` | Путь к исполняемому файлу Whisper.cpp |
| `WHISPER_MODEL_PATH` | нет | Путь к локальной модели Whisper, например `ggml-base.bin` |
| `OLLAMA_URL` | `http://127.0.0.1:11434/api/chat` | Адрес локального API Ollama |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Имя установленной модели Ollama |

Если микрофон недоступен, проверьте права доступа приложения к микрофону и выбранное в системе устройство ввода. Для изменения системного голоса используйте настройки речи вашей операционной системы.
