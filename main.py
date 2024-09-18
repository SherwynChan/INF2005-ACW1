#  Import library

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import wave
import simpleaudio as sa
import os
import sys

# Define Helper Functions for Bit Manipulation
def bytes_to_bits(data):
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits

def bits_to_bytes(bits):
    bytes_data = bytearray()
    for b in range(0, len(bits), 8):
        byte = 0
        for i in range(8):
            if b + i < len(bits):
                byte = (byte << 1) | bits[b + i]
        bytes_data.append(byte)
    return bytes_data

def set_bits(byte_value, data_bits, num_lsb):
    mask = (1 << num_lsb) - 1  # Mask for num_lsb bits
    byte_value = (byte_value & ~mask) | (data_bits & mask)
    return byte_value

def get_bits(byte_value, num_lsb):
    mask = (1 << num_lsb) - 1
    return byte_value & mask

# Implement Image Steganography Functions

# Embedding Data into Image
def embed_data_into_image(cover_image_path, payload_path, num_lsb, output_path):
    img = Image.open(cover_image_path)
    pixels = img.load()
    width, height = img.size
    num_channels = len(pixels[0,0]) if isinstance(pixels[0,0], tuple) else 1

    # Read payload
    with open(payload_path, 'rb') as f:
        payload_data = f.read()

    # Add header for payload size
    payload_length = len(payload_data)
    header = payload_length.to_bytes(4, byteorder='big')
    payload_with_header = header + payload_data
    payload_bits = bytes_to_bits(payload_with_header)
    max_bits = width * height * num_channels * num_lsb

    if len(payload_bits) > max_bits:
        raise ValueError("Payload too large to fit in the cover image with the selected number of LSBs.")

    idx = 0
    for y in range(height):
        for x in range(width):
            pixel = list(pixels[x, y])
            for n in range(len(pixel)):
                if idx < len(payload_bits):
                    data_bits = 0
                    for b in range(num_lsb):
                        if idx < len(payload_bits):
                            data_bits = (data_bits << 1) | payload_bits[idx]
                            idx +=1
                        else:
                            data_bits = data_bits << 1
                    pixel[n] = set_bits(pixel[n], data_bits, num_lsb)
            pixels[x, y] = tuple(pixel)
            if idx >= len(payload_bits):
                break
        else:
            continue
        break

    img.save(output_path)

# Extracting Data from Image
def extract_data_from_image(stego_image_path, num_lsb, output_payload_path):
    img = Image.open(stego_image_path)
    pixels = img.load()
    width, height = img.size
    num_channels = len(pixels[0,0]) if isinstance(pixels[0,0], tuple) else 1

    total_pixels = width * height * num_channels
    max_bits = total_pixels * num_lsb

    extracted_bits = []
    idx = 0

    # First extract the header to find payload length
    header_bits = []
    header_size = 32  # 4 bytes * 8 bits
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            for n in range(len(pixel)):
                bits = get_bits(pixel[n], num_lsb)
                for b in range(num_lsb):
                    header_bits.append((bits >> (num_lsb - b - 1)) & 1)
                    idx +=1
                    if idx >= header_size:
                        break
                if idx >= header_size:
                    break
            if idx >= header_size:
                break
        if idx >= header_size:
            break

    header_bytes = bits_to_bytes(header_bits)
    payload_length = int.from_bytes(header_bytes, byteorder='big')
    payload_bits_length = payload_length * 8
    total_payload_bits = payload_bits_length

    payload_bits = []
    for y in range(height):
        for x in range(width):
            if idx >= header_size + payload_bits_length:
                break
            pixel = pixels[x, y]
            for n in range(len(pixel)):
                bits = get_bits(pixel[n], num_lsb)
                for b in range(num_lsb):
                    if idx >= header_size + payload_bits_length:
                        break
                    payload_bits.append((bits >> (num_lsb - b -1)) &1)
                    idx +=1
            if idx >= header_size + payload_bits_length:
                break
        if idx >= header_size + payload_bits_length:
            break

    payload_data = bits_to_bytes(payload_bits)
    with open(output_payload_path, 'wb') as f:
        f.write(payload_data)

# Implement Audio Steganography Functions

## Embedding Data into Audio
def embed_data_into_audio(cover_audio_path, payload_path, num_lsb, output_path):
    song = wave.open(cover_audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    # Read payload
    with open(payload_path, 'rb') as f:
        payload_data = f.read()

    # Add header for payload size
    payload_length = len(payload_data)
    header = payload_length.to_bytes(4, byteorder='big')
    payload_with_header = header + payload_data
    payload_bits = bytes_to_bits(payload_with_header)
    max_bits = len(frame_bytes) * num_lsb

    if len(payload_bits) > max_bits:
        raise ValueError("Payload too large to fit in the cover audio with the selected number of LSBs.")

    idx = 0
    for i in range(len(frame_bytes)):
        if idx < len(payload_bits):
            data_bits = 0
            for b in range(num_lsb):
                if idx < len(payload_bits):
                    data_bits = (data_bits <<1) | payload_bits[idx]
                    idx +=1
                else:
                    data_bits = data_bits <<1
            frame_bytes[i] = set_bits(frame_bytes[i], data_bits, num_lsb)
        else:
            break

    modified_frames = bytes(frame_bytes)

    with wave.open(output_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(modified_frames)
    song.close()

## Extracting Data from Audio
def extract_data_from_audio(stego_audio_path, num_lsb, output_payload_path):
    song = wave.open(stego_audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    extracted_bits = []
    idx = 0

    # First extract the header to find payload length
    header_bits = []
    header_size = 32  # 4 bytes * 8 bits
    for i in range(len(frame_bytes)):
        if idx >= header_size:
            break
        bits = get_bits(frame_bytes[i], num_lsb)
        for b in range(num_lsb):
            header_bits.append((bits >> (num_lsb - b - 1)) & 1)
            idx +=1
            if idx >= header_size:
                break

    header_bytes = bits_to_bytes(header_bits)
    payload_length = int.from_bytes(header_bytes, byteorder='big')
    payload_bits_length = payload_length *8
    total_payload_bits = payload_bits_length

    payload_bits = []
    for i in range(len(frame_bytes)):
        if idx >= header_size + payload_bits_length:
            break
        bits = get_bits(frame_bytes[i], num_lsb)
        for b in range(num_lsb):
            if idx >= header_size + payload_bits_length:
                break
            payload_bits.append((bits >> (num_lsb - b - 1)) & 1)
            idx +=1

    payload_data = bits_to_bytes(payload_bits)
    with open(output_payload_path, 'wb') as f:
        f.write(payload_data)
    song.close()

# Create the GUI Application
## Initialize the Main Window

class SteganographyApp:
    def __init__(self, master):
        self.master = master
        master.title("LSB Steganography and Steganalysis")

        self.cover_file_path = ''
        self.payload_file_path = ''
        self.output_file_path = ''
        self.num_lsb = tk.IntVar(value=1)
        self.mode = tk.StringVar(value='Image')

        self.create_widgets()


# Create GUI Widgets
    def create_widgets(self):
        # Mode selection (Image or Audio)
        tk.Label(self.master, text="Select Mode:").grid(row=0, column=0, sticky='e')
        tk.Radiobutton(self.master, text="Image", variable=self.mode, value='Image').grid(row=0, column=1, sticky='w')
        tk.Radiobutton(self.master, text="Audio", variable=self.mode, value='Audio').grid(row=0, column=2, sticky='w')

        # Cover file selection
        tk.Button(self.master, text="Select Cover File", command=self.select_cover_file).grid(row=1, column=0)
        self.cover_label = tk.Label(self.master, text="No file selected")
        self.cover_label.grid(row=1, column=1, columnspan=2)

        # Payload file selection
        tk.Button(self.master, text="Select Payload File", command=self.select_payload_file).grid(row=2, column=0)
        self.payload_label = tk.Label(self.master, text="No file selected")
        self.payload_label.grid(row=2, column=1, columnspan=2)

        # Number of LSBs selection
        tk.Label(self.master, text="Number of LSBs:").grid(row=3, column=0, sticky='e')
        self.lsb_scale = tk.Scale(self.master, from_=1, to=8, orient=tk.HORIZONTAL, variable=self.num_lsb)
        self.lsb_scale.grid(row=3, column=1, columnspan=2, sticky='w')

        # Output file name
        tk.Button(self.master, text="Select Output File", command=self.select_output_file).grid(row=4, column=0)
        self.output_label = tk.Label(self.master, text="No file selected")
        self.output_label.grid(row=4, column=1, columnspan=2)

        # Embed and Extract buttons
        tk.Button(self.master, text="Embed", command=self.embed_data).grid(row=5, column=0)
        tk.Button(self.master, text="Extract", command=self.extract_data).grid(row=5, column=1)

        # Display / Play buttons
        tk.Button(self.master, text="Display Cover", command=self.display_cover).grid(row=6, column=0)
        tk.Button(self.master, text="Display Stego", command=self.display_stego).grid(row=6, column=1)

# Implementing Button Commands
    def select_cover_file(self):
        if self.mode.get() == 'Image':
            filetypes = [("Image files", "*.bmp *.png *.gif"), ("All files", "*.*")]
        else:
            filetypes = [("Audio files", "*.wav"), ("All files", "*.*")]
        self.cover_file_path = filedialog.askopenfilename(title="Select Cover File", filetypes=filetypes)
        self.cover_label.config(text=os.path.basename(self.cover_file_path))

    def select_payload_file(self):
        self.payload_file_path = filedialog.askopenfilename(title="Select Payload File", filetypes=[("All files", "*.*")])
        self.payload_label.config(text=os.path.basename(self.payload_file_path))

    def select_output_file(self):
        if self.mode.get() == 'Image':
            filetypes = [("Image files", "*.bmp *.png"), ("All files", "*.*")]
        else:
            filetypes = [("Audio files", "*.wav"), ("All files", "*.*")]
        self.output_file_path = filedialog.asksaveasfilename(title="Select Output File", defaultextension=".bmp" if self.mode.get() == 'Image' else ".wav", filetypes=filetypes)
        self.output_label.config(text=os.path.basename(self.output_file_path))

    def embed_data(self):
        try:
            num_lsb = self.num_lsb.get()
            if self.mode.get() == 'Image':
                embed_data_into_image(self.cover_file_path, self.payload_file_path, num_lsb, self.output_file_path)
            else:
                embed_data_into_audio(self.cover_file_path, self.payload_file_path, num_lsb, self.output_file_path)
            messagebox.showinfo("Success", "Data embedded successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def extract_data(self):
        try:
            num_lsb = self.num_lsb.get()
            output_payload_path = filedialog.asksaveasfilename(title="Save Extracted Payload As", defaultextension=".txt", filetypes=[("All files", "*.*")])
            if self.mode.get() == 'Image':
                extract_data_from_image(self.cover_file_path, num_lsb, output_payload_path)
            else:
                extract_data_from_audio(self.cover_file_path, num_lsb, output_payload_path)
            messagebox.showinfo("Success", "Data extracted successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_cover(self):
        if self.mode.get() == 'Image':
            self.show_image(self.cover_file_path)
        else:
            self.play_audio(self.cover_file_path)

    def display_stego(self):
        if self.mode.get() == 'Image':
            self.show_image(self.output_file_path)
        else:
            self.play_audio(self.output_file_path)

# Helper Methods for Displaying Images and Playing Audio

    def show_image(self, image_path):
        try:
            img = Image.open(image_path)
            img.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def play_audio(self, audio_path):
        try:
            wave_obj = sa.WaveObject.from_wave_file(audio_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
