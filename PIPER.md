# Piper voice support

You can use **Piper** voice models alongside Pocket TTS. Piper uses pre-trained ONNX models (one per voice); Pocket TTS clones from a short WAV. Both appear in the same voice list and API.

## Setup

1. **Install Piper (optional):**
   ```bash
   pip install piper-tts
   ```

2. **Download Piper voices** (e.g. from [Rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices)) or use the official downloader:
   ```bash
   python -m piper.download_voices en_US-lessac-medium
   ```

3. **Put `.onnx` (and optional `.onnx.json`) files** in the Piper voices folder. Default folder: `voices-piper/` in the project root.

   Example layout:
   ```
   voices-piper/
     en_US-lessac-medium.onnx
     en_US-lessac-medium.onnx.json
     de_DE-thorsten-low.onnx
     ...
   ```

4. **Restart the server.** Piper voices show up in `/v1/audio/voices` and work with `/v1/audio/speech` and Voice Chat like Pocket voices.

## Config

In `config.json` you can set the Piper directory:

```json
{
  "paths": {
    "voices_dir": "voices-celebrities",
    "voices_piper_dir": "voices-piper",
    "output_dir": "output"
  }
}
```

## Compatibility

- **Pocket TTS**: clone-from-audio voices (WAV in `voices-celebrities/`), engine `pocket`.
- **Piper**: ONNX model voices in `voices-piper/`, engine `piper`.

Both use the same OpenAI-compatible endpoints. If `piper-tts` is not installed, only Pocket voices are available.
