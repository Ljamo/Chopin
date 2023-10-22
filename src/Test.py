import numpy as np
import librosa
import os
import sounddevice as sd
from scipy.fft import fft
from midiutil import MIDIFile

def record_audio(duration, sr):
    print("Recording...")
    audio_data = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype='float32')
    sd.wait()
    print("Finished recording.")
    return audio_data.reshape(-1)

def frequency_to_midi(frequency):
    if frequency == 0:
        return None
    return 69 + 12 * np.log2(frequency / 440.0)

def extract_notes_fft(audio_data, sr, frame_size, hop_size):
    notes = []
    for i in range(0, len(audio_data) - frame_size, hop_size):
        frame = audio_data[i:i + frame_size]
        spectrum = np.abs(fft(frame))
        frequency = np.argmax(spectrum) * sr / frame_size
        if frequency > 20:  # Ignore frequencies lower than 20Hz
            midi_note = frequency_to_midi(frequency)
            notes.append((i / sr, midi_note))
    return notes

def write_notes_to_midi(notes, output_midi_path):
    midi_file = MIDIFile(1)
    track = 0
    time = 0
    channel = 0
    volume = 100
    
    midi_file.addTrackName(track, time, "Sample Track")
    midi_file.addTempo(track, time, 120)
    
    for note_time, note in notes:
        duration = 1  # You might want to calculate duration based on the time between notes
        if note is not None:
            midi_file.addNote(track, channel, int(note), note_time, duration, volume)
    
    with open(output_midi_path, 'wb') as output_file:
        midi_file.writeFile(output_file)
        print("MIDI file written successfully to", output_midi_path)

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    output_dir = os.path.join(current_dir, 'Files', 'Output')
    input_dir = os.path.join(current_dir, 'Files', 'Input')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    choice = input("Choose audio source (mic/wav): ").strip().lower()
    output_midi_path = os.path.join(output_dir, "output_midi.midi")
    
    if choice == 'mic':
        duration = float(input("Enter recording duration in seconds: "))
        sr = 44100  # Sample rate
        frame_size = 1024  # Change if necessary
        hop_size = 512  # Change if necessary
        audio_data = record_audio(duration, sr)
        notes = extract_notes_fft(audio_data, sr, frame_size, hop_size)
        write_notes_to_midi(notes, output_midi_path)
        
    elif choice == 'wav':
        audio_file_name = input("Enter the name of your WAV file (without extension): ")
        audio_path = os.path.join(input_dir, audio_file_name + ".wav")
        if os.path.exists(audio_path):
            audio_data, sr = librosa.load(audio_path, sr=None)
            frame_size = 1024  # Change if necessary
            hop_size = 512  # Change if necessary
            notes = extract_notes_fft(audio_data, sr, frame_size, hop_size)
            write_notes_to_midi(notes, output_midi_path)
        else:
            print(f"The file {audio_path} does not exist.")
        
    else:
        print("Invalid choice. Please enter 'mic' or 'wav'.")
