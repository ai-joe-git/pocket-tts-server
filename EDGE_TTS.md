# Edge TTS (Microsoft, kostenlos)

[Edge TTS](https://github.com/rany2/edge-tts) nutzt die **kostenlose** Microsoft-Text-to-Speech-API (wie die „Vorlesen“-Funktion im Edge-Browser). Kein Azure-Konto nötig. Über **70 Sprachen** und **300+ Stimmen**.

## Installation

```bash
pip install edge-tts
```

Für WAV-Ausgabe wird außerdem **pydub** benötigt (für MP3→WAV), das in der Regel schon für Pocket TTS installiert ist:

```bash
pip install pydub
```

## Aktivierung

In **`config.json`**:

```json
{
  "tts": {
    "edge_tts_enabled": true
  }
}
```

Server neu starten. Beim Start werden alle verfügbaren Edge-Stimmen abgefragt und erscheinen in der Stimmenliste (z. B. `de-DE-KatjaNeural`, `en-US-AriaNeural`).

## Stimmen

- Die **Voice-ID** entspricht dem Microsoft ShortName, z. B. `de-DE-KatjaNeural`, `en-US-GuyNeural`.
- Alle Stimmen erscheinen unter `/v1/audio/voices`, im Voice Chat und in **Wyoming** (Home Assistant).
- Für Wyoming wird die Sprache aus dem Locale abgeleitet (z. B. `de-DE` → Deutsch), sodass bei HA-Sprache „Deutsch“ die passenden Edge-Stimmen angeboten werden.

## Nutzung

- **API:** `POST /v1/audio/speech` mit `"voice": "de-DE-KatjaNeural"` (oder einer anderen Edge-Voice-ID).
- **Wyoming/Home Assistant:** Edge TTS erscheint zusammen mit Pocket- und Piper-Stimmen; Sprache wird automatisch zugeordnet.
- **Voice Chat:** Edge-Stimmen können wie alle anderen ausgewählt werden.

## Hinweise

- Die Synthese läuft über das Microsoft-Edge-TTS-API (Internetverbindung nötig).
- Es gelten die üblichen Nutzungsbedingungen von Microsoft; die Nutzung entspricht der des Browsers „Vorlesen“.
- Keine API-Keys oder Anmeldung erforderlich.

## Referenzen

- [edge-tts auf GitHub](https://github.com/rany2/edge-tts)
- [edge-tts auf PyPI](https://pypi.org/project/edge-tts/)
- Stimmenliste: `edge-tts --list-voices`
