#  Import library

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import wave
import simpleaudio as sa
import os

from PIL import Image

if hasattr(Image, 'Resampling'):
    resample_method = Image.Resampling.LANCZOS
else:
    resample_method = Image.ANTIALIAS


# Main application class
class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LSB Steganography Tool")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Variables to store file paths and options
        self.payload_path = tk.StringVar()
        self.cover_path = tk.StringVar()
        self.stego_path = tk.StringVar()
        self.num_lsbs = tk.IntVar(value=1)
        self.file_type = tk.StringVar()

        # List to keep references to images
        self.image_refs = []

        # Create the landing page
        self.create_landing_page()

    def create_landing_page(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title Label
        title_label = tk.Label(self.root, text="LSB Steganography Tool", font=("Helvetica", 24))
        title_label.pack(pady=40)

        # Description Label
        desc_label = tk.Label(self.root, text="Choose an option to proceed:", font=("Helvetica", 14))
        desc_label.pack(pady=20)

        # Encode Button
        encode_button = tk.Button(self.root, text="Encode (Embed)", font=("Helvetica", 16),
                                  width=20, command=self.create_encode_page)
        encode_button.pack(pady=10)

        # Decode Button
        decode_button = tk.Button(self.root, text="Decode (Extract)", font=("Helvetica", 16),
                                  width=20, command=self.create_decode_page)
        decode_button.pack(pady=10)

    def create_encode_page(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Back Button
        back_button = tk.Button(self.root, text="Back", command=self.create_landing_page)
        back_button.pack(anchor='nw', padx=10, pady=10)

        # Title Label
        title_label = tk.Label(self.root, text="Encode (Embed Payload)", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # Frame for input selections
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        # Payload Selection
        payload_label = tk.Label(input_frame, text="Select Payload (Text File):")
        payload_label.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        payload_entry = tk.Entry(input_frame, textvariable=self.payload_path, width=50)
        payload_entry.grid(row=0, column=1, padx=5, pady=5)
        payload_button = tk.Button(input_frame, text="Browse", command=self.select_payload)
        payload_button.grid(row=0, column=2, padx=5, pady=5)

        # Cover Object Selection
        cover_label = tk.Label(input_frame, text="Select Cover Object (Image File):")
        cover_label.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        cover_entry = tk.Entry(input_frame, textvariable=self.cover_path, width=50)
        cover_entry.grid(row=1, column=1, padx=5, pady=5)
        cover_button = tk.Button(input_frame, text="Browse", command=self.select_cover)
        cover_button.grid(row=1, column=2, padx=5, pady=5)

        # Number of LSBs Selection
        lsb_label = tk.Label(input_frame, text="Number of LSBs to Use (1-8):")
        lsb_label.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        lsb_spinbox = tk.Spinbox(input_frame, from_=1, to=8, textvariable=self.num_lsbs, width=5)
        lsb_spinbox.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Embed Button
        embed_button = tk.Button(self.root, text="Embed and Save Stego Object", font=("Helvetica", 14),
                                 command=self.embed_payload)
        embed_button.pack(pady=20)

    def select_payload(self):
        file_path = filedialog.askopenfilename(title="Select Payload (Text File)",
                                               filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.payload_path.set(file_path)

    def select_cover(self):
        file_path = filedialog.askopenfilename(title="Select Cover Object (Image File)",
                                               filetypes=[("BMP Files", "*.bmp"), ("PNG Files", "*.png"), ("GIF Files", "*.gif")]
)
        if file_path:
            self.cover_path.set(file_path)
            self.file_type.set('image')  # Currently supporting images only

    def embed_payload(self):
        payload_path = self.payload_path.get()
        cover_path = self.cover_path.get()
        num_lsbs = self.num_lsbs.get()

        # Validate inputs
        if not payload_path or not cover_path:
            messagebox.showerror("Input Error", "Please select both a payload and a cover object.")
            return

        # Check capacity
        can_embed = self.check_capacity(cover_path, payload_path, num_lsbs)
        if not can_embed:
            return

        # Embed the payload
        stego_image = self.embed_into_image(cover_path, payload_path, num_lsbs)
        if stego_image:
            # Save stego object
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG Files", "*.png")],
                                                     title="Save Stego Object As")
            if save_path:
                stego_image.save(save_path)
                self.stego_path.set(save_path)
                messagebox.showinfo("Success", "Stego object saved successfully.")
                # Display the payload, cover, and stego images
                self.display_analysis(payload_path, cover_path, save_path)
            else:
                messagebox.showwarning("Cancelled", "Save operation cancelled.")
        else:
            messagebox.showerror("Embedding Error", "An error occurred during embedding.")

    def check_capacity(self, cover_path, payload_path, num_lsbs):
        # Calculate the capacity of the cover image
        try:
            cover_image = Image.open(cover_path)
            width, height = cover_image.size
            num_channels = len(cover_image.getbands())  # e.g., 3 for RGB
            max_capacity = width * height * num_channels * num_lsbs // 8  # in bytes

            # Get payload size
            payload_size = os.path.getsize(payload_path)  # in bytes

            if payload_size > max_capacity:
                messagebox.showerror("Capacity Error",
                                     f"The payload is too large to embed using {num_lsbs} LSB(s).\n"
                                     f"Maximum Capacity: {max_capacity} bytes\n"
                                     f"Payload Size: {payload_size} bytes")
                return False
            else:
                return True
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while checking capacity:\n{str(e)}")
            return False

    def embed_into_image(self, cover_path, payload_path, num_lsbs):
        try:
            cover_image = Image.open(cover_path)
            cover_pixels = cover_image.load()

            # Read payload data
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
            messagebox.showerror("Image Loading Error", f"Failed to load images:\n{str(e)}")
            return

        width, height = cover_image.size
        diff_image = Image.new('RGB', (width, height))

        for x in range(width):
            for y in range(height):
                cover_pixel = cover_image.getpixel((x, y))
                stego_pixel = stego_image.getpixel((x, y))
                diff_pixel = tuple(
                    min(abs(c - s) * 10, 255) for c, s in zip(cover_pixel, stego_pixel))  # Amplify difference
                diff_image.putpixel((x, y), diff_pixel)

        diff_image = diff_image.resize((200, 200), Image.LANCZOS)
        diff_photo = ImageTk.PhotoImage(diff_image)
        diff_label = tk.Label(parent_frame, image=diff_photo)
        diff_label.pack(pady=10)

        # Keep a reference to prevent garbage collection
        self.image_refs.append(diff_photo)

    def create_decode_page(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Back Button
        back_button = tk.Button(self.root, text="Back", command=self.create_landing_page)
        back_button.pack(anchor='nw', padx=10, pady=10)

        # Title Label
        title_label = tk.Label(self.root, text="Decode (Extract Payload)", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # Frame for input selections
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        # Stego Object Selection
        stego_label = tk.Label(input_frame, text="Select Stego Object (Image File):")
        stego_label.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        stego_entry = tk.Entry(input_frame, textvariable=self.stego_path, width=50)
        stego_entry.grid(row=0, column=1, padx=5, pady=5)
        stego_button = tk.Button(input_frame, text="Browse", command=self.select_stego)
        stego_button.grid(row=0, column=2, padx=5, pady=5)

        # Number of LSBs Selection
        lsb_label = tk.Label(input_frame, text="Number of LSBs Used (1-8):")
        lsb_label.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        lsb_spinbox = tk.Spinbox(input_frame, from_=1, to=8, textvariable=self.num_lsbs, width=5)
        lsb_spinbox.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # Extract Button
        extract_button = tk.Button(self.root, text="Extract Payload", font=("Helvetica", 14),
                                   command=self.extract_payload)
        extract_button.pack(pady=20)

    def select_stego(self):
        file_path = filedialog.askopenfilename(title="Select Stego Object (Image File)",
                                               filetypes=[("BMP Files", "*.bmp"), ("PNG Files", "*.png"), ("GIF Files", "*.gif")])
        if file_path:
            self.stego_path.set(file_path)
            self.file_type.set('image')  # Currently supporting images only

    def extract_payload(self):
        stego_path = self.stego_path.get()
        num_lsbs = self.num_lsbs.get()

        # Validate inputs
        if not stego_path:
            messagebox.showerror("Input Error", "Please select a stego object.")
            return

        # Extract the payload
        decoded_data = self.extract_from_image(stego_path, num_lsbs)
        if decoded_data:
            # Save decoded message
            save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text Files", "*.txt")],
                                                     title="Save Decoded Payload As")
            if save_path:
                with open(save_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(decoded_data)
                messagebox.showinfo("Success", "Payload extracted and saved successfully.")
                # Display the decoded message
                self.display_decoded_message(decoded_data)
            else:
                messagebox.showwarning("Cancelled", "Save operation cancelled.")
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
