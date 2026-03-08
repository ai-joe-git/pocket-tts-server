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

3. **Put `.onnx` (and optional `.onnx.json`) files** in the Piper voices folder. Default folder: `voices-piper/` in the project root. You can place files directly in `voices-piper/` or inside subfolders.

   Example layout:
   ```
   voices-piper/
     en_US-lessac-medium.onnx
     en_US-lessac-medium.onnx.json
     de_DE-thorsten-low.onnx
     vits-piper-de_DE-thorsten-high/    ← subfolder supported
       model.onnx
       model.onnx.json
   ```
   The voice ID is the **folder name** when the `.onnx` is inside a subfolder, otherwise the **file name** (without extension). So `vits-piper-de_DE-thorsten-high` appears as one voice.

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

## CPU vs GPU

Piper runs on **CPU by default**. To use an **NVIDIA GPU** for Piper:

1. Install the GPU build of ONNX Runtime:  
   `pip install onnxruntime-gpu`
2. In `config.json` set:  
   `"tts": { "piper_use_cuda": true }`  
   (or add `"piper_use_cuda": true` under existing `"tts"`).
3. Restart the server.

**Intel Arc:** Piper uses ONNX Runtime; GPU support there is via CUDA (NVIDIA). Intel Arc is not supported by Piper’s built-in `use_cuda` option. So on Intel Arc, Piper will use CPU; Pocket TTS can still use XPU (see [INTEL_ARC.md](INTEL_ARC.md)).

## Compatibility

- **Pocket TTS**: clone-from-audio voices (WAV in `voices-celebrities/`), engine `pocket`.
- **Piper**: ONNX model voices in `voices-piper/`, engine `piper`.

Both use the same OpenAI-compatible endpoints. If `piper-tts` is not installed, only Pocket voices are available.
