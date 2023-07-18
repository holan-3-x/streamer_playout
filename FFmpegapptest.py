import subprocess
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading

# FFmpeg command options
ffmpeg_command = [
    'ffmpeg',
    '-hide_banner',
    '-i', '-',
    '-c:v', 'libx264',  # H.264 encoding
    # '-c:v', 'libx265',  # H.265 encoding
    '-crf', '23',  # Constant Rate Factor (CRF) for video quality
    '-preset', 'medium',  # Encoding preset
    '-c:a', 'copy',
    '-f', 'mpegts',
    'udp://127.0.0.1:1234'
]

# Global variable
stop_stream = False

def stream_video():
    input_file = input_entry.get()
    output_url = output_entry.get()
    output_format = format_var.get()
    additional_options = options_entry.get()

    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',  # H.264 encoding
        # '-c:v', 'libx265',  # H.265 encoding
        '-crf', '23',  # Constant Rate Factor (CRF) for video quality
        '-preset', 'medium',  # Encoding preset
        '-c:a', 'copy',
        '-f', output_format,
        output_url
    ]

    if additional_options:
        command += additional_options.split()

    subprocess.run(command)

def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[('Video Files', '*.*')])
    input_entry.delete(0, tk.END)
    input_entry.insert(tk.END, file_path)
    display_video(file_path)

def display_video(file_path):
    command = ['ffmpeg', '-i', file_path, '-vf', 'scale=640:480', '-f', 'image2pipe', '-pix_fmt', 'rgb24', '-vcodec', 'rawvideo', '-']

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

    while True:
        raw_image = pipe.stdout.read(640 * 480 * 3)
        if not raw_image:
            break
        image = Image.frombytes('RGB', (640, 480), raw_image)
        image = ImageTk.PhotoImage(image)

        # Display the image in the GUI
        image_label.configure(image=image)
        image_label.image = image

        # Update the GUI window
        window.update()

    pipe.terminate()

def start_stream():
    global stop_stream  # Declare stop_stream as a global variable
    stop_stream = False
    threading.Thread(target=stream_video).start()

def stop_stream():
    global stop_stream  # Declare stop_stream as a global variable
    stop_stream = True

# Create the main window
window = tk.Tk()
window.title('FFmpeg Video Streamer')

# Input file selection
input_label = tk.Label(window, text='Input File:')
input_label.pack()

input_entry = tk.Entry(window)
input_entry.pack()

input_button = tk.Button(window, text='Select', command=select_input_file)
input_button.pack()

# Output file selection
output_label = tk.Label(window, text='Output URL:')
output_label.pack()

output_entry = tk.Entry(window)
output_entry.pack()

# Output format selection
format_label = tk.Label(window, text='Output Format:')
format_label.pack()

format_var = tk.StringVar(value='mpegts')

r1 = tk.Radiobutton(window, text='MPEG-TS', variable=format_var, value='mpegts')
r1.pack()

r2 = tk.Radiobutton(window, text='RTP', variable=format_var, value='rtp')
r2.pack()

# Additional options
options_label = tk.Label(window, text='Additional FFmpeg Options:')
options_label.pack()

options_entry = tk.Entry(window)
options_entry.pack()

# Video display
video_frame = tk.Frame(window)
video_frame.pack()

image_label = tk.Label(video_frame)
image_label.pack()

# Stream buttons
start_stream_button = tk.Button(window, text='Start Stream', command=start_stream)
start_stream_button.pack()

stop_stream_button = tk.Button(window, text='Stop Stream', command=stop_stream)
stop_stream_button.pack()

# Start the GUI event loop
window.mainloop()
