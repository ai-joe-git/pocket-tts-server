# Intel Arc mit Pocket TTS Server nutzen

Ab PyTorch 2.5 unterstützt PyTorch **Intel Arc** (und andere Intel GPUs) unter Windows über das Gerät **XPU**. So nutzt du deine Intel Arc GPU für die TTS-Inferenz.

---

## Voraussetzungen

- **Windows 10/11** (empfohlen: Windows 11)
- **Intel Arc** Grafikkarte (A-Series, B-Series Battlemage usw.) oder Intel Core Ultra mit integrierter Arc-Grafik
- **Aktueller Intel-Grafiktreiber**  
  [Intel Grafiktreiber](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html) (Version 32.0.101.6078 oder neuer)
- **Resizable BAR** in BIOS aktivieren (für Arc dGPU empfohlen)

---

## Schritte

### 1. PyTorch mit Intel XPU installieren

Der Standard-Installer (`install_pocket_tts.bat`) installiert PyTorch nur für **CPU**. Für Intel Arc musst du PyTorch mit XPU nachinstallieren.

**In der Projekt-venv:**

```powershell
cd c:\Users\pw\git\pocket-tts-server
.\venv\Scripts\activate
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu
```

**XPU verfügbar prüfen:**

```powershell
python -c "import torch; print('XPU available:', torch.xpu.is_available())"
```

Wenn `True` ausgegeben wird, ist die Intel GPU für PyTorch nutzbar.

---

### 2. Gerät in der Konfiguration setzen

In **`config.json`** die TTS-Geräte-Option auf `xpu` setzen:

```json
{
  "tts": {
    "device": "xpu"
  }
}
```

Falls der Abschnitt `tts` noch fehlt, einfach an beliebiger Stelle (z.B. nach `"paths"`) einfügen.

---

### 3. Server starten

Wie gewohnt:

```powershell
.\run_pocket_tts.bat
```

bzw. `python pocket_tts_api.py`

In der Konsole solltest du beim Start etwas wie:

```text
[INFO] Loading TTS model (device: xpu)...
[INFO] TTS model loaded successfully (sample rate: 24000Hz, device: xpu)
```

sehen. Dann läuft das TTS-Modell auf der Intel Arc GPU.

---

## Hinweise

- **pocket-tts** ist standardmäßig CPU-orientiert. Ob und wie stark es von XPU profitiert, hängt von der Bibliothek (Geräte-Nutzung) ab. Mit `device: xpu` wird das Gerät an die Bibliothek übergeben; falls sie es nicht unterstützt, fällt der Server intern auf CPU zurück (mit entsprechender Meldung).
- **Treiber:** Bei Problemen (z.B. `XPU available: False`) zuerst den [Intel Arc Treiber](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html) aktualisieren und ggf. Resizable BAR in BIOS aktivieren.
- **Zurück auf CPU:** In `config.json` wieder `"device": "cpu"` setzen.

---

## Referenzen

- [PyTorch – Getting Started on Intel GPU (XPU)](https://pytorch.org/docs/main/notes/get_start_xpu.html)
- [Intel GPU Support in PyTorch 2.5 (Blog)](https://pytorch.org/blog/intel-gpu-support-pytorch-2-5/)
