#!/usr/bin/env python3
"""
Quick check: Is the GPU (Intel Arc XPU / NVIDIA CUDA) available for PyTorch?
Run from project root: python check_gpu.py
"""

import sys

def main():
    print("=" * 60)
    print("GPU/XPU availability check (PyTorch)")
    print("=" * 60)

    # PyTorch
    try:
        import torch
        print(f"\nPyTorch version: {torch.__version__}")
    except ImportError:
        print("\n[FAIL] PyTorch not installed.")
        return 1

    # CPU is always "available"
    print("  CPU: available")

    # CUDA (NVIDIA)
    cuda_ok = getattr(torch.cuda, "is_available", lambda: False)()
    print(f"  CUDA (NVIDIA): {'available' if cuda_ok else 'not available'}")
    if cuda_ok:
        print(f"    Device: {torch.cuda.get_device_name(0)}")

    # XPU (Intel Arc / Intel GPUs)
    xpu_ok = False
    if getattr(torch, "xpu", None) is not None:
        xpu_ok = getattr(torch.xpu, "is_available", lambda: False)()
    print(f"  XPU (Intel Arc): {'available' if xpu_ok else 'not available'}")
    if xpu_ok:
        try:
            n = torch.xpu.device_count()
            print(f"    Device count: {n}")
            for i in range(n):
                print(f"    Device {i}: {torch.xpu.get_device_name(i)}")
        except Exception as e:
            print(f"    (details: {e})")
    else:
        print("    -> Install PyTorch with XPU: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu")
        print("    -> Ensure Intel Arc drivers are installed and up to date.")

    # Config device
    print("\n" + "-" * 60)
    try:
        import json
        from pathlib import Path
        cfg_path = Path("config.json")
        if cfg_path.exists():
            with open(cfg_path, "r") as f:
                cfg = json.load(f)
            dev = cfg.get("tts", {}).get("device", "cpu")
            print(f"config.json tts.device = '{dev}'")
        else:
            print("config.json not found (tts.device defaults to 'cpu')")
    except Exception as e:
        print(f"Config read: {e}")

    # Quick tensor test on XPU
    if xpu_ok:
        print("\n" + "-" * 60)
        try:
            t = torch.randn(2, 2, device="xpu")
            print("  XPU tensor test: OK (randn on xpu succeeded)")
        except Exception as e:
            print(f"  XPU tensor test: FAIL - {e}")

    print("\n" + "=" * 60)
    if not xpu_ok and not cuda_ok:
        print("Only CPU is available. For Intel Arc, install PyTorch XPU wheels.")
    else:
        print("At least one GPU backend is available.")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
