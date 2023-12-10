import librosa
import pretty_midi
import numpy as np

# Load an audio file
file_path = 'E:\.Dev\chopin\Python\Files\Input\demo.wav'
y, sr = librosa.load(file_path, sr=None)

# Extract pitches and magnitudes from the audio
pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)

# Create a PrettyMIDI object
midi = pretty_midi.PrettyMIDI()
instrument = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program('Acoustic Grand Piano'))

# Process pitches
prev_pitch = 0
for t in range(pitches.shape[1]):
    index = magnitudes[:, t].argmax()
    pitch = pitches[index, t]

    # Only add notes with a pitch
    if pitch > 0 and np.abs(pitch - prev_pitch) > 0.1:
        note_number = pretty_midi.hz_to_note_number(pitch)
        note = pretty_midi.Note(
            velocity=100, pitch=int(note_number), start=t/100.0, end=(t+1)/100.0)
        instrument.notes.append(note)
        prev_pitch = pitch

# Add the instrument to the PrettyMIDI object
midi.instruments.append(instrument)

# Save as MIDI file
midi.write('E:\.Dev\chopin\Python\Files\Output/output.mid')

