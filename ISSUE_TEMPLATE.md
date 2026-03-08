# Issue: Feature summary – Intel Arc, Piper, Edge TTS, Wyoming, Ruff, tests

## Title (for Issue)

**Feature summary: Intel Arc (XPU), Piper, Edge TTS, Wyoming (Home Assistant), Ruff, and tests**

---

## Description

Summary of the feature work on the **feature/wyoming** branch (or equivalent) for reference and documentation.

### Scope

| Area | Summary |
|------|--------|
| **Intel Arc (XPU)** | Optional GPU support for Intel Arc via `tts.device: "xpu"`. See `INTEL_ARC.md` and `check_gpu.py`. |
| **Piper** | Optional Piper ONNX voices in `voices-piper/` (subfolders supported). See `PIPER.md`. |
| **Edge TTS** | Optional free Microsoft TTS (70+ languages). Config: `tts.edge_tts_enabled`. See `EDGE_TTS.md`. |
| **Wyoming (HA)** | Optional TCP server for Home Assistant Wyoming TTS; per-voice languages. See `WYOMING.md`. |
| **Voices** | `voices-pockettts` for uploads and HF `kyutai/tts-voices` download; subfolder scanning. |
| **Ruff** | Linting and formatting in `pyproject.toml`; `ruff check` / `ruff format` in README. |
| **Tests** | pytest: Wyoming protocol, sentence splitting, API (health, voices, speech). See `tests/` and README. |

### Docs
- New/updated: `INTEL_ARC.md`, `PIPER.md`, `EDGE_TTS.md`, `WYOMING.md`, README (features, install, lint, test).
- Language note in Wyoming doc: Pocket TTS English-only; German via Piper de_DE or Edge TTS.

### For maintainers
- PR title/description can be taken from `PR_TEMPLATE.md` in this repo.
- Run `pytest` and `ruff check .` before merge.
