import pyaudio
import numpy as np
from scipy.io.wavfile import write
from scipy.fftpack import fft

# Capture Audio from Microphone
def capture_audio(seconds=3, rate=44100):
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=1024)
    except IOError as e:
        print("Error opening audio stream. Make sure your microphone is connected and working properly.")
        print("Error message:", str(e))
        p.terminate()
        return None, None   
    print("Recording...")
    frames = []
    for i in range(0, int(rate / 1024 * seconds)):
        data = stream.read(1024)
        frames.append(np.frombuffer(data, dtype=np.int16))
    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    return np.concatenate(frames), rate

# Basic Pitch Detection
def detect_pitch(audio, rate):
    if audio is None:
        return None
    spectrum = np.abs(fft(audio))
    frequencies = np.linspace(0, rate, len(spectrum))
    peak = np.argmax(spectrum)
    detected_frequency = frequencies[peak]
    if detected_frequency < 20:  # You can adjust this threshold as needed
        print("Detected frequency is too low. Make sure you are not recording silence.")
        return None
    return detected_frequency


# Map Frequency to Piano Note
def frequency_to_note(frequency):
    A4 = 440
    C0 = A4 * pow(2, -4.75)
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    h = round(12 * np.log2(frequency / C0))
    octave = h // 12
    note = h % 12
    return note_names[note] + str(octave)

# Main Program
def main():
    audio, rate = capture_audio()
    if audio is None or rate is None:
        return
    frequency = detect_pitch(audio, rate)
    if frequency is None:
        return
    note = frequency_to_note(frequency)
    print("Detected note:", note)

if __name__ == "__main__":
    main()