import pyaudio
import numpy as np
from scipy.io.wavfile import write
from scipy.fftpack import fft

# Capture Audio from Microphone
def capture_audio(seconds=3, rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=1024)
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
    spectrum = np.abs(fft(audio))
    frequencies = np.linspace(0, rate, len(spectrum))
    peak = np.argmax(spectrum)
    return frequencies[peak]

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
    frequency = detect_pitch(audio, rate)
    note = frequency_to_note(frequency)
    print("Detected note:", note)

if __name__ == "__main__":
    main()
