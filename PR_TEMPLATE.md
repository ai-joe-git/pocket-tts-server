# Pull Request: Feature/wyoming – Intel Arc, Piper, Edge TTS, Wyoming, Ruff & tests

## Title (for PR)

**Add Intel Arc (XPU), Piper, Edge TTS, Wyoming (Home Assistant), Ruff, and tests**

Closes #1

---

## Description

This PR extends the pocket-tts-server with optional engines, Home Assistant integration, and developer tooling.

### Intel Arc (XPU) support
- Config: `tts.device` can be set to `"xpu"` for Intel Arc GPUs.
- Model loading and tensor handling use the XPU device when available; fallback to CPU if not.
- Documentation: `INTEL_ARC.md` (setup, drivers, `check_gpu.py`).

### Piper TTS
- Optional Piper voice models (ONNX) alongside Pocket TTS.
- Config: `paths.voices_piper_dir` (default `voices-piper`); supports subfolders.
- All Piper voices appear in `/v1/audio/voices`, Voice Chat, and Wyoming.
- Documentation: `PIPER.md`.

### Edge TTS (Microsoft, free)
- Optional [edge-tts](https://github.com/rany2/edge-tts) integration (70+ languages, 300+ voices).
- Config: `tts.edge_tts_enabled`; voices loaded at startup via `list_voices()`.
- WAV output via pydub (MP3→WAV). Works with API, Voice Chat, and Wyoming.
- Documentation: `EDGE_TTS.md`.

### Wyoming protocol (Home Assistant)
- Optional TCP server for [Home Assistant Wyoming](https://www.home-assistant.io/integrations/wyoming/) TTS.
- Config: `wyoming.enabled`, `wyoming.host`, `wyoming.port`.
- Protocol: `describe` → `info` (per-voice languages), `synthesize` → audio (PCM); wire format matches Wyoming package (data_length + payload).
- Per-voice language reporting so HA shows the right voices for the selected language (e.g. Piper de_DE / Edge TTS for German).
- Documentation: `WYOMING.md` (incl. language/German notes).

### Voices layout
- `voices-pockettts` for user uploads and optional [kyutai/tts-voices](https://huggingface.co/kyutai/tts-voices) download; subfolders scanned.
- README: Hugging Face model access, voice download command, and Method 3 for tts-voices.

### Linting & formatting (Ruff)
- `pyproject.toml`: `[tool.ruff]` and `[tool.ruff.format]` (line-length 100, py38).
- `requirements-dev.txt`: `ruff`.
- README: how to run `ruff check` / `ruff format`.

### Tests
- **pytest**: `tests/test_wyoming.py` (Wyoming protocol encoding, no server deps), `tests/test_sentences.py` (sentence splitting), `tests/test_api.py` (health, voices, speech validation).
- `wyoming_protocol.py`: encode helper used by server and tests.
- `conftest.py`: project root on `sys.path`, lazy `client` fixture.
- `requirements-dev.txt`: pytest, pytest-asyncio, httpx. README: run tests.
- Fix: `create_speech` re-raises `HTTPException` so invalid voice returns 400 instead of 500.

### Other
- README and docs in English; optional dev/test instructions.

---

## Checklist (optional)
- [ ] Config defaults and paths documented.
- [ ] New dependencies optional where possible (Piper, Edge TTS, Ruff, pytest in dev).
- [ ] Wyoming wire format compatible with HA client.
- [ ] Tests pass (`pytest`), Ruff passes (`ruff check .`).
