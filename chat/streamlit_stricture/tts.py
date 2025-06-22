import os
import sys
import torch
import soundfile as sf

base_path = r'C:\Users\User\Desktop\program lang\kokoro\tts\src\Kokoro-82M'
sys.path.append(base_path)

model_path = os.path.join(base_path, 'kokoro-v0_19.pth')

from models import build_model  # type: ignore

device = 'cuda' if torch.cuda.is_available() else 'cpu'

if device == 'cuda':
    print(f"GPU detected: {torch.cuda.get_device_name(0)}")
else:
    print("No GPU detected. Using CPU.")

from kokoro import generate  # type: ignore

def text_to_speech(text: str, speaker) -> bytes:
    MODEL = build_model(model_path, device)

    VOICE_NAME = [
        'af',  # Default voice is a 50-50 mix of Bella & Sarah
        'af_bella', 'af_sarah', 'am_adam', 'am_michael',
        'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
        'af_nicole', 'af_sky',
    ][speaker]

    VOICEPACK = torch.load(f'{base_path}/voices/{VOICE_NAME}.pt', map_location=device, weights_only=True).to(device)
    print(f'Loaded voice: {VOICE_NAME}')
    audio, _ = generate(MODEL, text, VOICEPACK, lang=VOICE_NAME[0])
    # Convert stereo to mono by averaging the two channels
    if audio.ndim == 2:
        audio = audio.mean(axis=1)

    # Convert audio to bytes
    sf.write('temp.wav', audio, samplerate=24000, format='WAV')
    audio_bytes = None
    with open('temp.wav', 'rb') as f:
        audio_bytes = f.read()

    # Clean up temporary file
    os.remove('temp.wav')

    return audio_bytes
