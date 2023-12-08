import numpy as np
import sounddevice as sd
import librosa
from scipy.fft import fft
from midiutil import MIDIFile
import os
import tkinter as tk
from tkinter import filedialog

def open_file():
    # This function will be called when the "Open File" button is clicked
    root = tk.Tk()
    root.withdraw()  # Hide the extra tkinter window

    # Open a dialog to choose a file
    file_path = filedialog.askopenfilename()

    # Process the selected file
    if file_path:
        print(f"File selected: {file_path}")
        # Add your file processing code here

    root.destroy()  # Close the tkinter instance

is_currently_recording = False
audio_data = None

def start_recording(duration):
    global is_currently_recording
    is_currently_recording = True
    # Implement starting the recording process

def stop_recording():
    global is_currently_recording, audio_data
    is_currently_recording = False
    # Implement stopping the recording process and return the recorded data
    return audio_data

def is_recording():
    return is_currently_recording

def save_audio_file(audio_data, file_path):
    # Implement saving the audio_data to the specified file_path
    pass


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

def calculate_rms(frame):
    return np.sqrt(np.mean(np.square(frame)))

def extract_notes_fft(audio_data, sr, frame_size, hop_size):
    notes = []
    for i in range(0, len(audio_data) - frame_size, hop_size):
        frame = audio_data[i:i + frame_size]
        rms = calculate_rms(frame)
        volume = int(rms * 127)  # Scale RMS to MIDI velocity range (0-127)
        spectrum = np.abs(fft(frame))
        sorted_indices = np.argsort(spectrum)[::-1]  # Sort in descending order
        dominant_frequencies = sorted_indices[:5] * sr / frame_size
        midi_notes = [(frequency_to_midi(freq), volume) for freq in dominant_frequencies if freq > 20]  # Ignore frequencies lower than 20Hz
        notes.append((i / sr, midi_notes))

    filtered_notes = filter_short_notes(notes)
    return filtered_notes

def filter_short_notes(notes, min_duration=0.1):
    if len(notes) < 2:
        return notes

    filtered_notes = [notes[0]]
    for i in range(1, len(notes)):
        current_note_time, current_midi_notes = notes[i]
        prev_note_time, prev_midi_notes = filtered_notes[-1]

        # Debug print to show note information
        print(f"Prev Note: Time: {prev_note_time}, Notes: {prev_midi_notes}")
        print(f"Curr Note: Time: {current_note_time}, Notes: {current_midi_notes}")

        if prev_midi_notes == current_midi_notes and (current_note_time - prev_note_time) < min_duration:
            print("Removing short note")
            continue
        filtered_notes.append((current_note_time, current_midi_notes))

    return filtered_notes


def write_notes_to_midi(notes, output_midi_path, tempo):
    midi_file = MIDIFile(1)
    track = 0
    time = 0
    channel = 0
    
    midi_file.addTrackName(track, time, "Speech to Piano")
    midi_file.addTempo(track, time, tempo)
    
    for note_time, midi_notes in notes:
        for note, volume in midi_notes:
            if note is not None:
                duration = 0.5  # Adjust as needed
                midi_file.addNote(track, channel, int(note), note_time, duration, volume)
    
    with open(output_midi_path, 'wb') as output_file:
        midi_file.writeFile(output_file)
        print("MIDI file written successfully to", output_midi_path)

def boost_volume(audio_data, gain_factor):
    boosted_audio = audio_data * gain_factor
    np.clip(boosted_audio, -1, 1, out=boosted_audio)  # Ensure the values stay within the valid range
    return boosted_audio

def record_audio_wrapper(duration):
    # Use the provided duration for recording
    sr = 44100  # Sampling rate
    audio_data = record_audio(duration, sr)
    # Process the audio_data as needed


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    output_dir = os.path.join(current_dir, 'Files', 'Output')
    input_dir = os.path.join(current_dir, 'Files', 'Input')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    choice = input("Choose audio source (mic/wav): ").strip().lower()
    output_midi_path = os.path.join(output_dir, "speech_to_piano.mid")
    
    tempo_input = input("Enter the tempo (BPM) or press Enter to use the default (60 BPM): ").strip()
    tempo = 60 if tempo_input == "" else int(tempo_input)

    gain_input = input("Enter the volume gain factor or press Enter to use the default (1.0, no change): ").strip()
    gain_factor = 1.0 if gain_input == "" else float(gain_input)

    if choice == 'mic':
        duration = float(input("Enter recording duration in seconds: "))
        sr = 44100  # Sample rate
        frame_size = 1024  # Change if necessary
        hop_size = 512  # Change if necessary
        audio_data = record_audio(duration, sr)
        boosted_audio_data = boost_volume(audio_data, gain_factor)
        notes = extract_notes_fft(boosted_audio_data, sr, frame_size, hop_size)
        write_notes_to_midi(notes, output_midi_path, tempo)
        
    elif choice == 'wav':
        audio_file_name = input("Enter the name of your WAV file (without extension): ")
        audio_path = os.path.join(input_dir, audio_file_name + ".wav")
        if os.path.exists(audio_path):
            audio_data, sr = librosa.load(audio_path, sr=None)
            boosted_audio_data = boost_volume(audio_data, gain_factor)
            frame_size = 1024  # Change if necessary
            hop_size = 512  # Change if necessary
            notes = extract_notes_fft(boosted_audio_data, sr, frame_size, hop_size)
            write_notes_to_midi(notes, output_midi_path, tempo)
        else:
            print(f"The file {audio_path} does not exist.")
        
    else:
        print("Invalid choice. Please enter 'mic' or 'wav'.")
