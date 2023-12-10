import tkinter as tk
from tkinter import filedialog
import chopin  # Import your chopin.py script

def create_main_window():
    window = tk.Tk()
    window.title("Audio Processing Application")
    window.geometry("800x540")  # Set the size of the window

    # Function to handle recording toggle
    def toggle_recording():
        if not chopin.is_recording():
            chopin.start_recording(recording_length.get())
            record_button.config(text="Stop Recording", bg="red")
        else:
            audio_data = chopin.stop_recording()
            record_button.config(text="Record", bg="SystemButtonFace")
            save_file(audio_data)

    # Function to save the recorded file
    def save_file(audio_data):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav",
                                                 filetypes=[("WAV files", "*.wav"), ("All Files", "*.*")])
        if file_path:
            chopin.save_audio_file(audio_data, file_path)

    # Frame to hold buttons and input fields
    control_frame = tk.Frame(window)
    control_frame.pack(expand=True)

    # Record button
    record_button = tk.Button(control_frame, text="Record", command=toggle_recording, height=3, width=10)
    record_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Open file button
    open_file_button = tk.Button(control_frame, text="Open File", command=chopin.open_file, height=3, width=10)
    open_file_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Label for recording length
    length_label = tk.Label(control_frame, text="Recording Length (seconds):")
    length_label.pack(side=tk.LEFT, padx=10, pady=10)

    # Spinbox for recording length
    recording_length = tk.Spinbox(control_frame, from_=1, to=60, width=5)
    recording_length.delete(0, tk.END)
    recording_length.insert(0, 15)  # Default value of 15 seconds
    recording_length.pack(side=tk.LEFT, padx=10, pady=10)

    return window

def main():
    main_window = create_main_window()
    main_window.mainloop()

if __name__ == "__main__":
    main()
