#!/usr/bin/env python3
"""
Pocket TTS - Enhanced API Server with OpenAI Compatibility
Provides TTS endpoints and voice chat functionality with LLM integration
"""

import os
import sys
import json
import base64
import asyncio
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import tempfile
import io
import subprocess

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
import scipy.io.wavfile
import numpy as np

# Try to import audio conversion
try:
    from pydub import AudioSegment

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("[WARNING] pydub not installed. Install with: pip install pydub")

# Try to import pocket_tts
try:
    from pocket_tts import TTSModel
    from pocket_tts import export_model_state

    POCKET_TTS_AVAILABLE = True
    print("[INFO] pocket_tts imported successfully")
except ImportError as e:
    POCKET_TTS_AVAILABLE = False
    print(f"[WARNING] pocket_tts not installed: {e}")
    print("[INFO] Run: pip install pocket-tts")


# Load configuration
def load_config():
    config_path = Path("config.json")
    default_config = {
        "server": {"host": "localhost", "port": 8000},
        "paths": {"voices_dir": "voices-celebrities", "output_dir": "output"},
        "llm": {
            "enabled": False,
            "api_url": "http://localhost:8080/v1/chat/completions",
            "api_key": "",
            "model": "llama-3",
            "system_prompt": "You are a helpful AI assistant. Keep your responses concise and natural.",
        },
    }

    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                loaded_config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in loaded_config:
                        loaded_config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in loaded_config[key]:
                                loaded_config[key][subkey] = subvalue
                return loaded_config
        except Exception as e:
            print(f"[WARNING] Failed to load config: {e}")

    # Save default config
    try:
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        print(f"[INFO] Created default config at {config_path}")
    except Exception as e:
        print(f"[WARNING] Failed to save config: {e}")

    return default_config


config = load_config()

# Initialize TTS Model
tts_model = None
voice_states = {}  # Cache voice states

if POCKET_TTS_AVAILABLE:
    try:
        print("[INFO] Loading TTS model...")
        tts_model = TTSModel.load_model()
        print(
            f"[INFO] TTS model loaded successfully (sample rate: {tts_model.sample_rate}Hz)"
        )
    except Exception as e:
        print(f"[WARNING] Failed to load TTS model: {e}")
        import traceback

        traceback.print_exc()
        tts_model = None
else:
    print("[INFO] TTS not available - voice generation disabled")

# Voice cache
available_voices = {}


def scan_voices():
    """Scan voice files and auto-convert MP3/OGG/FLAC to WAV with archiving"""
    voices = []
    voices_dir = Path(config["paths"]["voices_dir"])

    # Create archive directory for original files
    archive_dir = voices_dir.parent / f"{voices_dir.name}-archive"

    if voices_dir.exists():
        # First, auto-convert any non-WAV files
        if PYDUB_AVAILABLE:
            for ext in ["*.mp3", "*.ogg", "*.flac"]:
                for voice_file in voices_dir.glob(ext):
                    try:
                        print(f"[INFO] Auto-converting voice file: {voice_file.name}")
                        converted_path = convert_to_wav(
                            str(voice_file),
                            voices_dir=voices_dir,
                            archive_dir=archive_dir,
                        )
                        print(f"[INFO] Conversion complete: {converted_path}")
                    except Exception as e:
                        print(f"[ERROR] Failed to convert {voice_file.name}: {e}")
        else:
            print(
                "[WARNING] pydub not available. Non-WAV voice files will not be converted."
            )

        # Now scan only WAV files
        for voice_file in voices_dir.glob("*.wav"):
            voice_id = voice_file.stem.lower().replace(" ", "-").replace("_", "-")
            voices.append(
                {
                    "voice_id": voice_id,
                    "name": voice_file.stem,
                    "file": str(voice_file),
                    "preview": f"/voices/{voice_id}/preview",
                    "type": "custom",
                }
            )
            print(f"[INFO] Found voice: {voice_id}")

    return voices


def get_voice_state(voice_id):
    """Get or load voice state on-demand"""
    if voice_id in voice_states:
        return voice_states[voice_id]

    if voice_id in available_voices and tts_model:
        voice_file = available_voices[voice_id]["file"]
        try:
            print(f"[INFO] Loading voice state for: {voice_id}")

            # Convert to WAV if needed (for MP3/OGG/FLAC)
            wav_file = convert_to_wav(voice_file)

            voice_states[voice_id] = tts_model.get_state_for_audio_prompt(wav_file)
            print(f"[INFO] Voice state loaded for: {voice_id}")
            return voice_states[voice_id]
        except Exception as e:
            print(f"[WARNING] Failed to load voice state for {voice_id}: {e}")
            import traceback

            traceback.print_exc()

    return None


def convert_to_wav(
    audio_path, voices_dir=None, archive_dir=None, max_duration_ms=20000
):
    """
    Convert audio file to WAV format (24kHz mono) if needed.
    If voices_dir and archive_dir are provided, will archive the original MP3
    and keep only WAV in the voices directory.

    Args:
        audio_path: Path to audio file
        voices_dir: Directory to save converted WAV file
        archive_dir: Directory to archive original files
        max_duration_ms: Maximum duration in milliseconds (default 20 seconds)
    """
    import tempfile
    import shutil
    from pathlib import Path

    audio_path = Path(audio_path)

    # If already WAV, check if it needs trimming
    if audio_path.suffix.lower() == ".wav":
        # Check duration and trim if too long
        if PYDUB_AVAILABLE:
            try:
                audio = AudioSegment.from_file(str(audio_path))
                duration_ms = len(audio)
                if duration_ms > max_duration_ms:
                    print(
                        f"[INFO] Trimming WAV from {duration_ms / 1000:.1f}s to {max_duration_ms / 1000:.1f}s: {audio_path.name}"
                    )
                    audio = audio[:max_duration_ms]

                    # Create archive dir if needed
                    if archive_dir:
                        archive_dir = Path(archive_dir)
                        archive_dir.mkdir(parents=True, exist_ok=True)
                        # Archive original long file
                        archive_path = archive_dir / (
                            audio_path.stem + "_original_long.wav"
                        )
                        shutil.copy2(str(audio_path), str(archive_path))
                        print(f"[INFO] Archived original long WAV to: {archive_path}")

                    # Overwrite with trimmed version
                    audio.export(str(audio_path), format="wav")
                    print(f"[INFO] Trimmed and saved: {audio_path.name}")
            except Exception as e:
                print(f"[WARNING] Failed to trim WAV file: {e}")
        return str(audio_path)

    if not PYDUB_AVAILABLE:
        raise ImportError(
            "pydub is required for audio conversion. Install: pip install pydub"
        )

    # Create temp WAV file
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_wav.close()

    try:
        print(f"[INFO] Converting {audio_path.suffix} to WAV: {audio_path.name}")

        # Load audio
        audio = AudioSegment.from_file(str(audio_path))

        # Trim to max duration if too long
        duration_ms = len(audio)
        if duration_ms > max_duration_ms:
            print(
                f"[INFO] Trimming audio from {duration_ms / 1000:.1f}s to {max_duration_ms / 1000:.1f}s"
            )
            audio = audio[:max_duration_ms]

        # Convert to mono
        if audio.channels > 1:
            audio = audio.set_channels(1)
            print(f"[INFO] Converted to mono")

        # Set sample rate to 24kHz (required by pocket_tts)
        audio = audio.set_frame_rate(24000)
        audio = audio.set_sample_width(2)  # 16-bit

        # Export as WAV
        audio.export(temp_wav.name, format="wav")
        print(f"[INFO] Converted to 24kHz WAV format")

        # If voices_dir and archive_dir provided, archive original and move WAV
        if voices_dir and archive_dir:
            voices_dir = Path(voices_dir)
            archive_dir = Path(archive_dir)

            # Ensure archive directory exists
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Archive the original MP3
            archive_path = archive_dir / audio_path.name
            shutil.move(str(audio_path), str(archive_path))
            print(f"[INFO] Archived original MP3 to: {archive_path}")

            # Move converted WAV to voices directory
            wav_name = audio_path.stem + ".wav"
            final_wav_path = voices_dir / wav_name
            shutil.move(temp_wav.name, str(final_wav_path))
            print(f"[INFO] Saved WAV to voices directory: {final_wav_path}")

            return str(final_wav_path)

        return temp_wav.name

    except Exception as e:
        # Clean up temp file on error
        try:
            os.unlink(temp_wav.name)
        except:
            pass
        raise Exception(f"Failed to convert audio: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    global available_voices
    available_voices = {v["voice_id"]: v for v in scan_voices()}
    print(f"[INFO] Found {len(available_voices)} voices (loaded on-demand)")
    yield
    print("[INFO] Server shutting down...")


app = FastAPI(
    title="Pocket TTS API",
    description="OpenAI-compatible Text-to-Speech API with voice cloning and LLM integration",
    version="2.3.0",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== OpenAI Compatible Endpoints ==============


class OpenAITTSRequest(BaseModel):
    model: str = "tts-1"
    input: str
    voice: str = "alloy"
    response_format: str = "mp3"
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


@app.post("/v1/audio/speech")
async def create_speech(request: OpenAITTSRequest):
    """
    OpenAI-compatible TTS endpoint
    """
    if not tts_model:
        raise HTTPException(
            status_code=503,
            detail="TTS service not available. Please install pocket_tts: pip install pocket-tts",
        )

    try:
        # Get voice state
        voice_state = None
        if request.voice in voice_states:
            voice_state = voice_states[request.voice]
        elif request.voice in available_voices:
            # Load voice state on demand
            voice_file = available_voices[request.voice]["file"]
            try:
                voice_state = tts_model.get_state_for_audio_prompt(voice_file)
                voice_states[request.voice] = voice_state
            except Exception as e:
                print(f"[WARNING] Failed to load voice state: {e}")

        if not voice_state:
            # Use default voice if available
            if "default" in voice_states:
                voice_state = voice_states["default"]
            else:
                raise HTTPException(
                    status_code=400, detail=f"Voice '{request.voice}' not found"
                )

        # Generate audio
        audio = tts_model.generate_audio(voice_state, request.input)

        # Convert to WAV
        audio_np = audio.numpy()

        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        scipy.io.wavfile.write(wav_buffer, tts_model.sample_rate, audio_np)
        wav_buffer.seek(0)
        audio_data = wav_buffer.read()

        # Convert to requested format if needed
        if request.response_format == "mp3":
            try:
                from pydub import AudioSegment

                # Load WAV from memory
                audio = AudioSegment.from_wav(io.BytesIO(audio_data))
                mp3_buffer = io.BytesIO()
                audio.export(mp3_buffer, format="mp3")
                mp3_buffer.seek(0)
                audio_data = mp3_buffer.read()
            except ImportError:
                pass

        return StreamingResponse(
            iter([audio_data]),
            media_type=f"audio/{request.response_format}",
            headers={
                "Content-Disposition": f"attachment; filename=speech.{request.response_format}"
            },
        )

    except Exception as e:
        import traceback

        print(f"[ERROR] TTS generation failed: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.get("/v1/audio/voices")
async def list_voices():
    """
    OpenAI-compatible voices list endpoint
    """
    voices = []
    for voice_id, voice_info in available_voices.items():
        voices.append(
            {
                "voice_id": voice_id,
                "name": voice_info.get("name", voice_id),
                "preview_url": voice_info.get("preview", ""),
                "type": voice_info.get("type", "custom"),
            }
        )
    return {"voices": voices}


# ============== LLM Integration ==============


def call_llm(messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any]:
    """Call external LLM API"""
    llm_config = config.get("llm", {})

    if not llm_config.get("enabled", False):
        # Fallback: echo mode
        last_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break

        return {
            "id": f"chatcmpl-{datetime.now().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": "echo-mode",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Echo: {last_message}"
                        if last_message
                        else "No message received.",
                    },
                    "finish_reason": "stop",
                }
            ],
        }

    try:
        api_url = llm_config.get("api_url", "http://localhost:8080/v1/chat/completions")
        api_key = llm_config.get("api_key", "")
        model = llm_config.get("model", "llama-3")
        system_prompt = llm_config.get(
            "system_prompt", "You are a helpful AI assistant."
        )

        # Prepare messages with system prompt
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "messages": full_messages,
            "stream": stream,
            "max_tokens": 4000,
            "temperature": 0.7,
        }

        print(f"[INFO] Calling LLM at {api_url}")
        response = requests.post(api_url, json=payload, headers=headers, timeout=180)
        response.raise_for_status()

        # Debug: print response content if it's not JSON
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(f"[ERROR] LLM returned invalid JSON: {e}")
            print(f"[ERROR] Response content: {response.text[:500]}")
            raise

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to LLM at {api_url}")
        return {
            "id": f"chatcmpl-{datetime.now().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": "error",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Error: Cannot connect to LLM server at {api_url}. Please check your llama.cpp server is running.",
                    },
                    "finish_reason": "stop",
                }
            ],
        }
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return {
            "id": f"chatcmpl-{datetime.now().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": "error",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Error calling LLM: {str(e)}",
                    },
                    "finish_reason": "stop",
                }
            ],
        }


# ============== Voice Chat Endpoints ==============


class VoiceChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    voice: str = "barack-obama"
    stream: bool = False


class VoiceUploadRequest(BaseModel):
    voice_name: str


# ============== Streaming Chat Endpoints ==============


def split_into_sentences(text):
    """Split text into sentences for chunked TTS generation"""
    import re

    # Split on sentence endings but keep the punctuation
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    # Filter out empty sentences
    return [s.strip() for s in sentences if s.strip()]


def generate_sentence_audio_sync(voice_state, sentence):
    """Generate audio for a single sentence (synchronous version for thread pool)"""
    try:
        audio = tts_model.generate_audio(voice_state, sentence)
        audio_np = audio.numpy()

        # Convert to WAV
        wav_buffer = io.BytesIO()
        scipy.io.wavfile.write(wav_buffer, tts_model.sample_rate, audio_np)
        wav_buffer.seek(0)
        audio_bytes = wav_buffer.read()

        return base64.b64encode(audio_bytes).decode()
    except Exception as e:
        print(f"[WARNING] Failed to generate audio for sentence: {e}")
        return None


async def stream_chat_response(request: VoiceChatRequest):
    """
    Generator for streaming chat completions with real-time text AND chunked audio streaming.
    This generates audio sentence-by-sentence for faster first-audio delivery.
    """
    try:
        print(f"[INFO] Starting stream_chat_response with voice: {request.voice}")

        # Call LLM WITHOUT streaming - we'll handle streaming ourselves
        llm_response = call_llm(request.messages, stream=False)

        # Extract response text
        if "choices" in llm_response and len(llm_response["choices"]) > 0:
            response_text = llm_response["choices"][0]["message"]["content"]
        else:
            response_text = "Sorry, I couldn't generate a response."

        print(f"[INFO] LLM response received: {len(response_text)} chars")

        # Get voice state (load once for entire response)
        voice_state = None
        if tts_model:
            print(
                f"[INFO] TTS model available, getting voice state for: {request.voice}"
            )
            if request.voice in voice_states:
                voice_state = voice_states[request.voice]
                print(f"[INFO] Using cached voice state")
            elif request.voice in available_voices:
                voice_file = available_voices[request.voice]["file"]
                print(f"[INFO] Loading voice state from file: {voice_file}")
                try:
                    voice_state = tts_model.get_state_for_audio_prompt(voice_file)
                    voice_states[request.voice] = voice_state
                    print(f"[INFO] Voice state loaded successfully")
                except Exception as e:
                    print(f"[WARNING] Failed to load voice state: {e}")
                    import traceback

                    traceback.print_exc()
            else:
                print(f"[WARNING] Voice not found: {request.voice}")
                print(f"[INFO] Available voices: {list(available_voices.keys())}")
        else:
            print(f"[WARNING] TTS model not available")

        # Split text into sentences for chunked generation
        sentences = split_into_sentences(response_text)
        print(f"[INFO] Split into {len(sentences)} sentences")
        print(f"[INFO] Total text length: {len(response_text)} chars")

        # Process each sentence - stream text then audio for each sentence
        for sentence_idx, sentence in enumerate(sentences):
            sentence_words = sentence.split()
            print(
                f"[INFO] Processing sentence {sentence_idx}: '{sentence[:50]}...' ({len(sentence_words)} words)"
            )

            # Stream this sentence's text word by word
            for word in sentence_words:
                # Add space after each word except the last
                content = word + " "
                yield f"data: {json.dumps({'type': 'text', 'content': content})}\n\n"

            # Small delay to let text render before audio starts
            await asyncio.sleep(0.05)

            # Generate and stream audio for this sentence immediately after its text
            if voice_state and sentence.strip():
                print(f"[INFO] Generating audio for sentence {sentence_idx}")
                try:
                    # Run TTS generation in thread pool to not block
                    loop = asyncio.get_event_loop()
                    audio_data = await loop.run_in_executor(
                        None, generate_sentence_audio_sync, voice_state, sentence
                    )

                    if audio_data:
                        print(
                            f"[INFO] Audio generated for sentence {sentence_idx}: {len(audio_data)} bytes"
                        )
                        yield f"data: {json.dumps({'type': 'audio', 'data': audio_data, 'format': 'wav', 'chunk': sentence_idx})}\n\n"
                        print(f"[INFO] Audio data sent for sentence {sentence_idx}")
                    else:
                        print(
                            f"[WARNING] No audio data generated for sentence {sentence_idx}"
                        )
                except Exception as e:
                    print(
                        f"[ERROR] TTS generation failed for sentence {sentence_idx}: {e}"
                    )
                    import traceback

                    traceback.print_exc()
            else:
                if not voice_state:
                    print(f"[WARNING] No voice state available for TTS")
                if not sentence.strip():
                    print(f"[WARNING] Empty sentence, skipping audio")

        print(f"[INFO] Streaming complete, sending done signal")
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        import traceback

        print(f"[ERROR] Chat streaming failed: {e}")
        print(traceback.format_exc())
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.post("/v1/chat/completions/stream")
async def chat_completions_stream(request: VoiceChatRequest):
    """
    Streaming chat completions endpoint - returns SSE stream
    """
    return StreamingResponse(
        stream_chat_response(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.post("/v1/chat/completions")
async def chat_completions(request: VoiceChatRequest):
    """
    OpenAI-compatible chat completions with voice output
    """
    try:
        # Call LLM
        llm_response = call_llm(request.messages, request.stream)

        # Extract response text
        if "choices" in llm_response and len(llm_response["choices"]) > 0:
            response_text = llm_response["choices"][0]["message"]["content"]
        else:
            response_text = "Sorry, I couldn't generate a response."

        # Generate TTS for the response
        audio_data = None
        if tts_model:
            voice_state = None
            if request.voice in voice_states:
                voice_state = voice_states[request.voice]
            elif request.voice in available_voices:
                voice_file = available_voices[request.voice]["file"]
                try:
                    voice_state = tts_model.get_state_for_audio_prompt(voice_file)
                    voice_states[request.voice] = voice_state
                except Exception as e:
                    print(f"[WARNING] Failed to load voice state: {e}")

            if voice_state:
                try:
                    audio = tts_model.generate_audio(voice_state, response_text)
                    audio_np = audio.numpy()

                    # Convert to WAV in memory
                    wav_buffer = io.BytesIO()
                    scipy.io.wavfile.write(wav_buffer, tts_model.sample_rate, audio_np)
                    wav_buffer.seek(0)
                    audio_bytes = wav_buffer.read()

                    # Encode to base64
                    audio_data = base64.b64encode(audio_bytes).decode()
                except Exception as e:
                    print(f"[WARNING] TTS generation failed: {e}")

        return {
            "id": llm_response.get("id", f"chatcmpl-{datetime.now().timestamp()}"),
            "object": "chat.completion",
            "created": llm_response.get("created", int(datetime.now().timestamp())),
            "model": llm_response.get("model", "pocket-tts-chat"),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": response_text},
                    "finish_reason": "stop",
                }
            ],
            "audio": {"data": audio_data, "format": "wav"} if audio_data else None,
        }

    except Exception as e:
        import traceback

        print(f"[ERROR] Chat completion failed: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ============== Configuration Endpoint ==============


@app.get("/api/config")
async def get_config():
    """Get current configuration (excluding sensitive data)"""
    safe_config = config.copy()
    if "llm" in safe_config:
        safe_config["llm"] = safe_config["llm"].copy()
        safe_config["llm"]["api_key"] = (
            "***" if safe_config["llm"].get("api_key") else ""
        )
    return safe_config


@app.post("/api/config")
async def update_config(new_config: Dict[str, Any]):
    """Update configuration"""
    global config
    config.update(new_config)

    # Save to file
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {e}")


# ============== Web Interface ==============


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    html_path = Path("templates/index.html")
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return HTMLResponse(
            content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pocket TTS - Error</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 50px; text-align: center; }
                .error { color: #dc3545; }
                .info { background: #f8f9fa; padding: 20px; margin: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <h1 class="error">Template Not Found</h1>
            <div class="info">
                <p>The web interface template was not found.</p>
                <p>Please ensure templates/index.html exists.</p>
            </div>
        </body>
        </html>
        """
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "tts_available": tts_model is not None,
        "voices_loaded": len(available_voices),
        "timestamp": datetime.now().isoformat(),
    }


# ============== Voice Upload Endpoint ==============


@app.post("/api/voices/upload")
async def upload_voice(
    file: UploadFile = File(...),
    voice_name: str = Form(...),
):
    """Upload a new voice file (WAV or MP3) - converts to WAV format"""
    try:
        # Validate file type
        allowed_extensions = {".wav", ".mp3", ".ogg", ".flac"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}",
            )

        # Create voices directory if not exists
        voices_dir = Path(config["paths"]["voices_dir"])
        voices_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize voice name
        safe_name = "".join(c for c in voice_name if c.isalnum() or c in "-_ ").strip()
        if not safe_name:
            raise HTTPException(status_code=400, detail="Invalid voice name")

        # Save file
        voice_id = safe_name.lower().replace(" ", "-")

        # Always save as WAV for consistency
        target_path = voices_dir / f"{voice_id}.wav"

        # Check if file already exists
        if target_path.exists():
            raise HTTPException(
                status_code=400, detail=f"Voice '{safe_name}' already exists"
            )

        # Read uploaded content
        content = await file.read()

        # Convert to WAV format
        if file_ext == ".wav":
            # Already WAV, just save
            with open(target_path, "wb") as f:
                f.write(content)
            print(f"[INFO] Voice uploaded (WAV): {voice_id}")
        else:
            # Convert to WAV
            if not PYDUB_AVAILABLE:
                raise HTTPException(
                    status_code=400,
                    detail="pydub is required for audio conversion. Install with: pip install pydub",
                )

            # Save to temp file first
            temp_file = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
            temp_file.write(content)
            temp_file.close()

            try:
                # Convert to WAV
                audio = AudioSegment.from_file(temp_file.name)

                # Convert to mono if stereo
                if audio.channels > 1:
                    audio = audio.set_channels(1)

                # Set sample rate to 24kHz
                audio = audio.set_frame_rate(24000)
                audio = audio.set_sample_width(2)  # 16-bit

                # Export as WAV
                audio.export(str(target_path), format="wav")
                print(f"[INFO] Voice uploaded and converted to WAV: {voice_id}")

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass

        # Add to available voices
        available_voices[voice_id] = {
            "voice_id": voice_id,
            "name": safe_name,
            "file": str(target_path),
            "preview": f"/voices/{voice_id}/preview",
            "type": "custom",
        }

        return {
            "status": "success",
            "voice_id": voice_id,
            "name": safe_name,
            "message": f"Voice '{safe_name}' uploaded and converted to WAV format",
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Voice upload failed: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to upload voice: {str(e)}")


# ============== Static Files ==============

output_dir = Path(config["paths"]["output_dir"])
output_dir.mkdir(parents=True, exist_ok=True)

try:
    app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")
except:
    pass

if __name__ == "__main__":
    host = config["server"]["host"]
    port = config["server"]["port"]

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    Pocket TTS Server v2.3                    ║
╠══════════════════════════════════════════════════════════════╣
║  Web Interface: http://{host}:{port:<4}                     ║
║  API Docs:     http://{host}:{port:<4}/docs                  ║
║  Health:       http://{host}:{port:<4}/health               ║
╠══════════════════════════════════════════════════════════════╣
║  OpenAI Endpoints:                                           ║
║    POST /v1/audio/speech        - Text to Speech            ║
║    GET  /v1/audio/voices        - List Voices               ║
║    POST /v1/chat/completions    - Voice Chat with LLM       ║
╠══════════════════════════════════════════════════════════════╣
║  TTS Available: {"Yes" if tts_model else "No - Install: pip install pocket-tts":<42}║
║  Voices Loaded: {len(available_voices):<42}║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host=host, port=port)
