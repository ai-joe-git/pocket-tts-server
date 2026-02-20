# LLM Integration Guide

Pocket TTS now supports integration with local LLM servers for voice chat mode.

## Supported LLM Servers

### 1. llama.cpp Server

**Install llama.cpp:**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```

**Download a model:**
Download a GGUF model from Hugging Face (e.g., Llama-3, Mistral, etc.)

**Start the server:**
```bash
./server -m models/llama-3-8b-q4.gguf -c 4096 --host 0.0.0.0 --port 8080
```

**Configuration in Pocket TTS:**
- LLM API URL: `http://localhost:8080/v1/chat/completions`
- Model: `llama-3` (or whatever you named it)
- API Key: Leave empty

### 2. Ollama

**Install Ollama:**
Download from https://ollama.ai

**Pull a model:**
```bash
ollama pull llama3
```

**Start Ollama:**
```bash
ollama serve
```

**Configuration in Pocket TTS:**
- LLM API URL: `http://localhost:11434/v1/chat/completions`
- Model: `llama3`
- API Key: Leave empty

### 3. LM Studio

1. Download LM Studio from https://lmstudio.ai
2. Load a model and start the local server
3. Note the server URL (usually `http://localhost:1234/v1/chat/completions`)

**Configuration in Pocket TTS:**
- LLM API URL: `http://localhost:1234/v1/chat/completions`
- Model: (leave as default or model name)
- API Key: Leave empty

## Quick Setup

1. Start your LLM server (see instructions above)
2. Open Pocket TTS web interface
3. Go to "LLM Settings" tab
4. Enable "LLM Integration"
5. Enter your LLM server URL
6. Click "Test Connection" to verify
7. Start chatting in "Voice Chat" tab!

## Troubleshooting

**Connection Failed:**
- Verify LLM server is running: `curl http://localhost:8080/health`
- Check firewall settings
- Ensure correct port number

**No Response:**
- Check LLM server logs
- Verify model is loaded
- Try shorter messages

**Slow Responses:**
- Use a smaller model
- Enable GPU acceleration on your LLM server
- Adjust max_tokens in settings

## API Examples

### Chat with Voice
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Tell me a joke"}],
    "voice": "barack-obama"
  }'
```

The response will include both text and base64-encoded audio.