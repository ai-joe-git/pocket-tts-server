# 🎙️ Pocket TTS Server v1.0

[![GitHub](https://img.shields.io/badge/GitHub-ai--joe--git/pocket--tts--server-blue?logo=github)](https://github.com/ai-joe-git/pocket-tts-server)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

A lightweight, real-time voice cloning and chat server with OpenAI-compatible API. Clone any voice with just 20 seconds of audio and chat with AI using that voice instantly.

**[📥 Download](https://github.com/ai-joe-git/pocket-tts-server) | [🐛 Report Issue](https://github.com/ai-joe-git/pocket-tts-server/issues) | [⭐ Star](https://github.com/ai-joe-git/pocket-tts-server)**

---

## ✨ Screenshots

### Voice Chat Interface
![Voice Chat](screenshot-voice-chat.png)
*Real-time voice chat with streaming text and audio*

### Voice Library & Upload
![Voice Library](screenshot-voice-library.png)
*Upload voices via drag-and-drop or browse. Auto-converts MP3/OGG/FLAC to WAV.*

### LLM Configuration
![Settings](screenshot-settings.png)
*Easy configuration for any OpenAI-compatible LLM backend*

---

## 🚀 Quick Start (Windows - 3 Steps)

### Step 1: Install
Double-click **`install_pocket_tts.bat`**
- Installs Python (if needed)
- Creates virtual environment
- Installs all dependencies automatically
- Runs preflight checks — installs `ffmpeg` via `winget` if missing, and prompts for HuggingFace login (needed for the voice-cloning weights)

> **Before running:** create a free [HuggingFace account](https://huggingface.co/join). The installer will pause and ask you to accept the [`kyutai/pocket-tts` model terms](https://huggingface.co/kyutai/pocket-tts) and paste a [Read access token](https://huggingface.co/settings/tokens). Without this, custom voices return `Voice not found`.

### Step 2: Run
Double-click **`run_pocket_tts.bat`**
- Starts the server
- Opens browser automatically (or go to `http://localhost:8000`)

### Step 3: Chat
- Select a voice from the sidebar
- Go to **Voice Chat**
- Start typing!

**That's it!** No coding required.

---

## 🎭 Key Features

### 🗣️ Voice Cloning
- **Any voice** - Upload 15-20 seconds of clear audio
- **Auto-conversion** - MP3/OGG/FLAC → WAV automatically
- **Smart trimming** - Long audio auto-trimmed to 20s (prevents gibberish)
- **Archive system** - Originals saved to `voices-celebrities-archive/`

### 💬 Real-Time Voice Chat
- **Streaming text** - Words appear as LLM generates them
- **Streaming audio** - Audio plays sentence-by-sentence
- **No waiting** - First audio in 2-3 seconds
- **Sequential playback** - Sentences queue and play in order

### 🔌 OpenAI Compatible
- Drop-in replacement for OpenAI TTS API
- Works with OpenWebUI, SillyTavern, and other clients
- `/v1/audio/speech`, `/v1/chat/completions`, `/v1/audio/voices`

### ⚡ Performance
- 4000 token support for long responses
- 180-second timeout for slow LLMs
- CPU optimized (GPU optional)
- 76+ voices included (celebrities, characters, custom)

---

## 📋 Requirements

### Automatic (Windows)
Just run `install_pocket_tts.bat` - handles everything!

### Manual Installation
```bash
# 1. Clone repository
git clone https://github.com/ai-joe-git/pocket-tts-server.git
cd pocket-tts-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python pocket_tts_api.py
```

**System Requirements:**
- Windows 10/11 (Linux/Mac supported with manual setup)
- Python 3.8+
- 4GB+ RAM
- Audio: WAV, MP3, OGG, FLAC supported

---

## 🎤 Setting Up Voices

### Method 1: Web Upload (Easiest)
1. Open `http://localhost:8000`
2. Click **Voice Library** or current voice in sidebar
3. Drag & drop audio file or click to browse
4. Name your voice
5. Done! Ready in seconds

### Method 2: Manual Copy
1. Copy audio files to `voices-celebrities/`
2. Restart server
3. Files auto-convert to WAV format
4. Originals archived automatically

**Voice Quality Tips:**
- ✅ **Best length:** 15-20 seconds
- ✅ **Max length:** 20 seconds (longer files auto-trimmed)
- ✅ **Clear audio:** Single speaker, no background noise
- ✅ **Why trim?** Prevents gibberish from overly long samples

---

## 🤖 Connecting to LLM

### Recommended: llama.cpp

**1. Start LLM server:**
```bash
./server -m your-model.gguf -c 4096 --port 8080
```

**2. Configure Pocket TTS:**
- Open web interface
- Go to **Settings** tab
- Enable **LLM Integration**
- Set URL: `http://127.0.0.1:8080/v1/chat/completions`
- Save

**3. Start chatting:**
- Select **Voice Chat** tab
- Type message
- Watch text stream in real-time
- Hear voice respond immediately!

**Other LLM Options:**
- Ollama (`http://localhost:11434/v1/chat/completions`)
- text-generation-webui
- Any OpenAI-compatible API

---

## 📚 API Documentation

### Generate Speech
```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, this is a test!",
    "voice": "barack-obama",
    "response_format": "wav"
  }' \
  --output speech.wav
```

### List Voices
```bash
curl http://localhost:8000/v1/audio/voices
```

Response:
```json
{
  "voices": [
    {"voice_id": "barack-obama", "name": "Barack Obama"},
    {"voice_id": "donald-trump", "name": "Donald Trump"}
  ]
}
```

### Voice Chat (Non-Streaming)
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Tell me a joke"}],
    "voice": "elon-musk"
  }'
```

### Voice Chat (Streaming - Real-Time)
```bash
curl -X POST http://localhost:8000/v1/chat/completions/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "voice": "donald-trump"
  }'
```

**SSE Response Format:**
- `data: {"type": "text", "content": "word "}` - Streaming text
- `data: {"type": "audio", "data": "base64...", "chunk": 0}` - Audio per sentence  
- `data: {"type": "done"}` - Complete

---

## 🛠️ Configuration

Edit `config.json` or use Settings page:

```json
{
  "server": {
    "host": "localhost",
    "port": 8000
  },
  "llm": {
    "enabled": true,
    "api_url": "http://127.0.0.1:8080/v1/chat/completions",
    "api_key": "",
    "model": "llama-3",
    "system_prompt": "You are a helpful AI assistant."
  }
}
```

---

## 🔧 Troubleshooting

### ❌ No Audio Output
- [ ] Check voice selected in sidebar
- [ ] Verify files in `voices-celebrities/` folder
- [ ] Check browser console (F12) for errors
- [ ] Restart server after adding voices

### ❌ Text Gets Cut Off
- [ ] This was fixed in v1.0 (4000 token limit)
- [ ] Check if your LLM has its own token limit

### ❌ Audio Sounds Weird/Garbled  
- [ ] Voice sample too long - check `voices-celebrities-archive/`
- [ ] Re-upload 15-20 second clip
- [ ] Ensure single speaker, clear audio

### ❌ LLM Connection Fails
- [ ] Verify LLM server running on correct port
- [ ] Check API URL matches your LLM (Settings page)
- [ ] Timeout is 180s - increase if needed

### ❌ "Voice 'X' not found" / "Failed to load voice state"
HuggingFace authentication is missing or you haven't accepted the model terms.
- [ ] Visit https://huggingface.co/kyutai/pocket-tts and click "Agree and access repository" (one-time, browser only)
- [ ] From the activated venv, run `hf auth login` and paste a Read token from https://huggingface.co/settings/tokens
- [ ] Or rerun `fix_dependencies.bat` — the preflight walks you through both steps

### ❌ MP3/OGG upload fails with "pydub not installed"
The message is misleading; pydub itself is installed but can't load.
- [ ] **Python 3.13+:** rerun `fix_dependencies.bat` to install `audioop-lts` (the stdlib `audioop` module was removed by [PEP 594](https://peps.python.org/pep-0594/) and pydub still depends on it)
- [ ] **Missing ffmpeg:** the preflight installs it via `winget`; if winget is unavailable, grab a static build from https://www.gyan.dev/ffmpeg/builds/ and add the `bin` folder to PATH, then restart your shell

---

## 📁 Project Structure

```
pocket-tts-server/
├── pocket_tts_api.py           # Main server (FastAPI)
├── templates/
│   └── index.html              # Web interface
├── voices-celebrities/         # Active voices (WAV)
├── voices-celebrities-archive/ # Original MP3/OGG files
├── config.json                 # Settings
├── requirements.txt            # Python dependencies
├── install_pocket_tts.bat      # Windows installer
├── run_pocket_tts.bat          # Windows launcher
└── fix_dependencies.bat        # Repair tool
```

---

## 🎯 How It Works

### Streaming Architecture
1. **User sends message** → LLM starts generating
2. **Text streams** → Word-by-word as LLM generates
3. **Sentence complete** → TTS generates audio for that sentence
4. **Audio queues** → Plays sequentially (no overlap)
5. **Next sentence** → Continues while previous audio plays

### Voice Processing Pipeline
1. **Upload** → MP3/OGG/FLAC/WAV accepted
2. **Convert** → Auto-convert to WAV (24kHz, mono)
3. **Trim** → Cut to 20 seconds max (prevents gibberish)
4. **Archive** → Move original to archive folder
5. **Cache** → Load voice state for fast access

---

## 🤝 Contributing

Ideas for v1.1:
- 🎚️ Voice effects (pitch, speed, reverb)
- 🎭 Voice blending/mixing
- 🌐 Multi-language support
- 📱 Mobile app
- ⚡ WebRTC for ultra-low latency

**Open an issue** with feature requests or bugs!

---

## 📄 License

MIT License - Free for personal and commercial use.

---

## 🙏 Credits

- [pocket-tts](https://github.com/kyutai-labs/pocket-tts) - The TTS engine
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Recommended LLM backend

---

**Made with ❤️ by the AI community**

*Note: Not affiliated with OpenAI. API compatibility for convenience only.*

**[⬆️ Back to Top](#readme-top)**
