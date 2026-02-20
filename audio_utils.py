# Audio Conversion Helper
import io
import os
import tempfile
from pathlib import Path

try:
    from pydub import AudioSegment

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print(
        "[WARNING] pydub not installed. MP3/OGG files won't be converted automatically."
    )
    print("[INFO] Install with: pip install pydub")


def ensure_wav_format(audio_path, target_sample_rate=24000):
    """
    Ensure audio file is in WAV format at the target sample rate.
    Converts MP3/OGG/FLAC to WAV if needed.

    Returns:
        str: Path to WAV file (either original or converted)
    """
    audio_path = Path(audio_path)

    # If already WAV, check sample rate
    if audio_path.suffix.lower() == ".wav":
        return str(audio_path)

    # Convert to WAV
    if not PYDUB_AVAILABLE:
        raise ImportError(
            "pydub is required to convert audio files. Install with: pip install pydub"
        )

    try:
        # Load audio file
        audio = AudioSegment.from_file(str(audio_path))

        # Convert to mono if stereo
        if audio.channels > 1:
            audio = audio.set_channels(1)

        # Set sample rate to target (24kHz for pocket_tts)
        if audio.frame_rate != target_sample_rate:
            audio = audio.set_frame_rate(target_sample_rate)

        # Create temp WAV file
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio.export(temp_wav.name, format="wav")
        temp_wav.close()

        print(f"[INFO] Converted {audio_path.name} to WAV format")
        return temp_wav.name

    except Exception as e:
        raise Exception(f"Failed to convert audio: {e}")


def convert_uploaded_audio(source_path, voice_name, voices_dir):
    """
    Convert uploaded audio to proper WAV format and save.

    Args:
        source_path: Path to uploaded file
        voice_name: Name for the voice
        voices_dir: Directory to save converted file

    Returns:
        Path: Path to converted WAV file
    """
    if not PYDUB_AVAILABLE:
        raise ImportError("pydub is required for audio conversion")

    # Load audio
    audio = AudioSegment.from_file(str(source_path))

    # Convert to mono
    if audio.channels > 1:
        audio = audio.set_channels(1)

    # Set to 24kHz
    if audio.frame_rate != 24000:
        audio = audio.set_frame_rate(24000)

    # Save as WAV
    output_path = Path(voices_dir) / f"{voice_name}.wav"
    audio.export(str(output_path), format="wav")

    return output_path
