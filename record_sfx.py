import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(filename, duration=3, fs=44100):
    print(f"Recording for {duration} seconds...")
    # Record audio data
    # channels=1 for mono, channels=2 for stereo
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    write(filename, fs, myrecording)  # Save as WAV file
    print(f"Finished! Saved to {filename}")

if __name__ == "__main__":
    # Usage: python record_sfx.py
    # Requires: paru -S python-sounddevice python-scipy
    try:
        record_audio("new_sfx.wav")
    except Exception as e:
        print(f"Error: {e}. Make sure your mic is connected.")