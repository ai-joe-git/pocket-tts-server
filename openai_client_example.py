#!/usr/bin/env python3
"""
Pocket TTS - OpenAI Client Example
Shows how to use the OpenAI-compatible API
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def list_voices():
    """List all available voices"""
    response = requests.get(f"{BASE_URL}/v1/audio/voices")
    if response.status_code == 200:
        voices = response.json()
        print("\nAvailable Voices:")
        print("-" * 50)
        for voice in voices.get("voices", []):
            print(
                f"  ID: {voice['voice_id']:<20} Name: {voice['name']:<20} Type: {voice['type']}"
            )
        return voices.get("voices", [])
    else:
        print(f"Error: {response.status_code}")
        return []


def generate_speech(text, voice="barack-obama", output_file="output.mp3"):
    """Generate speech from text"""
    data = {"model": "tts-1", "input": text, "voice": voice, "response_format": "mp3"}

    print(f"\nGenerating speech with voice: {voice}")
    print(f"Text: {text[:50]}...")

    response = requests.post(f"{BASE_URL}/v1/audio/speech", json=data)

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✓ Saved to: {output_file}")
        return output_file
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        return None


def voice_chat(message, voice="elon-musk"):
    """Chat with voice output"""
    data = {"messages": [{"role": "user", "content": message}], "voice": voice}

    print(f"\n🎤 Chatting with {voice} voice...")

    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"🤖 Response: {result['choices'][0]['message']['content']}")

        # Save audio if available
        if result.get("audio") and result["audio"].get("data"):
            audio_data = result["audio"]["data"]
            output_file = f"chat_response_{voice}.wav"
            with open(output_file, "wb") as f:
                import base64

                f.write(base64.b64decode(audio_data))
            print(f"🎵 Audio saved to: {output_file}")

        return result
    else:
        print(f"✗ Error: {response.status_code}")
        return None


def batch_generate(texts, voice="barack-obama"):
    """Generate speech for multiple texts"""
    print(f"\nBatch processing {len(texts)} texts...")

    for i, text in enumerate(texts, 1):
        output_file = f"batch_{i:03d}_{voice}.mp3"
        generate_speech(text, voice, output_file)

    print(f"\n✓ Batch complete! Generated {len(texts)} files.")


def main():
    """Interactive demo"""
    print("=" * 60)
    print("Pocket TTS - OpenAI API Client Demo")
    print("=" * 60)

    # Check server
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"\n✓ Server is running")
            print(f"  Status: {health.get('status')}")
            print(f"  Voices loaded: {health.get('voices_loaded')}")
            print(f"  TTS Available: {health.get('tts_available')}")
        else:
            print("✗ Server not responding properly")
            return
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print("  Make sure to run: run_pocket_tts.bat")
        return

    # List voices
    voices = list_voices()

    if not voices:
        print("\nNo voices available. Add .wav files to voices-celebrities/ folder")
        return

    # Demo menu
    while True:
        print("\n" + "=" * 60)
        print("Options:")
        print("  1. Generate speech")
        print("  2. Voice chat")
        print("  3. Batch generate")
        print("  4. List voices")
        print("  5. Health check")
        print("  0. Exit")
        print("=" * 60)

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            text = input("Enter text to convert: ")
            if text:
                print("\nAvailable voices:")
                for i, voice in enumerate(voices[:5], 1):
                    print(f"  {i}. {voice['name']}")
                voice_choice = input("Select voice (or enter voice_id): ").strip()

                try:
                    voice_idx = int(voice_choice) - 1
                    voice = voices[voice_idx]["voice_id"]
                except:
                    voice = voice_choice if voice_choice else voices[0]["voice_id"]

                generate_speech(text, voice)

        elif choice == "2":
            message = input("Enter your message: ")
            if message:
                print("\nAvailable voices:")
                for i, voice in enumerate(voices[:5], 1):
                    print(f"  {i}. {voice['name']}")
                voice_choice = input("Select voice: ").strip()

                try:
                    voice_idx = int(voice_choice) - 1
                    voice = voices[voice_idx]["voice_id"]
                except:
                    voice = voice_choice if voice_choice else voices[0]["voice_id"]

                voice_chat(message, voice)

        elif choice == "3":
            print("\nEnter texts (one per line, empty line to finish):")
            texts = []
            while True:
                text = input("> ").strip()
                if not text:
                    break
                texts.append(text)

            if texts:
                voice_choice = input("Select voice: ").strip()
                try:
                    voice_idx = int(voice_choice) - 1
                    voice = voices[voice_idx]["voice_id"]
                except:
                    voice = voice_choice if voice_choice else voices[0]["voice_id"]

                batch_generate(texts, voice)

        elif choice == "4":
            list_voices()

        elif choice == "5":
            try:
                response = requests.get(f"{BASE_URL}/health")
                if response.status_code == 200:
                    health = response.json()
                    print(f"\n✓ Server Status: {health.get('status')}")
                    print(f"  TTS Available: {health.get('tts_available')}")
                    print(f"  Voices Loaded: {health.get('voices_loaded')}")
                    print(f"  Timestamp: {health.get('timestamp')}")
            except Exception as e:
                print(f"✗ Error: {e}")

        elif choice == "0":
            print("\nGoodbye!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
