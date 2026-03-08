# Using Intel Arc with Pocket TTS Server

As of PyTorch 2.5, PyTorch supports **Intel Arc** (and other Intel GPUs) on Windows via the **XPU** device. This guide explains how to use your Intel Arc GPU for TTS inference.

---

## Prerequisites

- **Windows 10/11** (Windows 11 recommended)
- **Intel Arc** graphics (A-Series, B-Series Battlemage, etc.) or Intel Core Ultra with integrated Arc graphics
- **Up-to-date Intel graphics driver**  
  [Intel Graphics Drivers](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html) (version 32.0.101.6078 or newer)
- **Resizable BAR** enabled in BIOS (recommended for Arc dGPU)

---

## Steps

### 1. Install PyTorch with Intel XPU

The default installer (`install_pocket_tts.bat`) installs PyTorch for **CPU** only. For Intel Arc, install the XPU build of PyTorch.

**Inside the project venv:**

```powershell
cd C:\path\to\pocket-tts-server
.\venv\Scripts\activate
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu
```

**Verify XPU is available:**

```powershell
python -c "import torch; print('XPU available:', torch.xpu.is_available())"
```

Or run the included check script:

```powershell
python check_gpu.py
```

If you see `True` or "XPU (Intel Arc): available", the Intel GPU is ready for PyTorch.

---

### 2. Set the device in configuration

In **`config.json`**, set the TTS device option to `xpu`:

```json
{
  "tts": {
    "device": "xpu"
  }
}
```

If the `tts` section is missing, add it (e.g. after `"paths"`).

---

### 3. Start the server

As usual:

```powershell
.\run_pocket_tts.bat
```

or `python pocket_tts_api.py`

On startup you should see something like:

```
[INFO] Loading TTS model (device: xpu)...
[INFO] TTS model loaded successfully (sample rate: 24000Hz, device: xpu)
```

The TTS model is then running on the Intel Arc GPU.

---

## Notes

- **pocket-tts** is primarily CPU-oriented. Whether and how much it benefits from XPU depends on the library’s device handling. With `device: xpu` the server passes the device to the library; if the library does not support it, the server falls back to CPU (with a warning).
- **Drivers:** If you see `XPU available: False`, update the [Intel Arc driver](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html) and ensure Resizable BAR is enabled in BIOS if applicable.
- **Back to CPU:** Set `"device": "cpu"` in `config.json`.

---

## References

- [PyTorch – Getting Started on Intel GPU (XPU)](https://pytorch.org/docs/main/notes/get_start_xpu.html)
- [Intel GPU Support in PyTorch 2.5 (Blog)](https://pytorch.org/blog/intel-gpu-support-pytorch-2-5/)
