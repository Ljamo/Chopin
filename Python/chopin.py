import numpy as np
import librosa
import os
import sounddevice as sd
from scipy.fft import fft
from scipy.signal import find_peaks
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

def extract_notes_stft(audio_data, sr, frame_size, hop_size):
    notes = []
    current_note = None
    note_start_time = None
    pitch_change_threshold = 0.5  # Reduced tolerance for pitch change

    # Perform STFT
    stft_result = np.abs(librosa.stft(audio_data, n_fft=frame_size, hop_length=hop_size))

    # Iterate over frames
    for i in range(stft_result.shape[1]):
        spectrum = stft_result[:, i]
        peaks, _ = find_peaks(spectrum, height=np.max(spectrum)/5)
        
        if len(peaks) > 0:
            freqs = librosa.fft_frequencies(sr=sr, n_fft=frame_size)
            peak_freq = freqs[peaks[0]]
            midi_note = librosa.hz_to_midi(peak_freq)

            if current_note is None:
                current_note = midi_note
                note_start_time = i * hop_size / sr
            elif np.abs(current_note - midi_note) > pitch_change_threshold:
                # Add the note
                duration = (i * hop_size / sr) - note_start_time
                notes.append((note_start_time, current_note, duration))
                current_note = midi_note
                note_start_time = i * hop_size / sr
        else:
            if current_note is not None:
                duration = (i * hop_size / sr) - note_start_time
                notes.append((note_start_time, current_note, duration))
                current_note = None
                note_start_time = None

    # Add the last note
    if current_note is not None:
        duration = (stft_result.shape[1] * hop_size / sr) - note_start_time
        notes.append((note_start_time, current_note, duration))

    return notes


def write_notes_to_midi(notes, output_midi_path):
    midi_file = MIDIFile(1)
    track = 0
    time = 0
    channel = 0
    volume = 127  # Maximum volume

    midi_file.addTrackName(track, time, "Sample Track")
    midi_file.addTempo(track, time, 60)  # Set the tempo to 60 BPM

    for note_time, note, duration in notes:
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
        notes = extract_notes_stft(audio_data, sr, frame_size, hop_size)
        write_notes_to_midi(notes, output_midi_path)

    elif choice == 'wav':
        audio_file_name = input("Enter the name of your WAV file (without extension): ")
        audio_path = os.path.join(input_dir, audio_file_name + ".wav")
        if os.path.exists(audio_path):
            audio_data, sr = librosa.load(audio_path, sr=None)
            frame_size = 1024  # Change if necessary
            hop_size = 512  # Change if necessary
            notes = extract_notes_stft(audio_data, sr, frame_size, hop_size)
            write_notes_to_midi(notes, output_midi_path)
        else:
            print(f"The file {audio_path} does not exist.")

    else:
        print("Invalid choice. Please enter 'mic' or 'wav'.")