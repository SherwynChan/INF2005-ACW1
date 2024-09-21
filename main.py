import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import os
import wave
from PIL import Image

if hasattr(Image, 'Resampling'):
    resample_method = Image.Resampling.LANCZOS
else:
    resample_method = Image.ANTIALIAS

#test=
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

       # Cover Object Selection (Image or Audio)
        cover_label = tk.Label(input_frame, text="Select Cover Object (Image or Audio File):")
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
        file_path = filedialog.askopenfilename(title="Select Cover Object (Image or Audio File)",
                                               filetypes=[("BMP Files", "*.bmp"), ("PNG Files", "*.png"), ("GIF Files", "*.gif"),("Audio Files", "*.wav")])
        if file_path:
            self.cover_path.set(file_path)
            if file_path.lower().endswith('wav'):
                self.file_type.set('audio') # wav audio file
            else:
                self.file_type.set('image')  # Currently supporting images only

    def embed_payload(self):
        payload_path = self.payload_path.get()
        cover_path = self.cover_path.get()
        num_lsbs = self.num_lsbs.get()

        # Validate inputs
        if not payload_path or not cover_path:
            messagebox.showerror("Input Error", "Please select both a payload and a cover object.")
            return

        # Check capacity(image or audio)
        can_embed = self.check_capacity(cover_path, payload_path, num_lsbs)
        if not can_embed:
            return

        # Embed based on file type
        if self.file_type.get() == 'image':
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
        elif self.file_type.get() == 'audio':
            stego_audio = self.embed_payload_audio(cover_path, payload_path, num_lsbs)
            if stego_audio:
                #save stego object
                save_path = filedialog.asksaveasfilename(defaultextension=".wav",filetypes=[("WAV Files", "*.wav")],title="Save Stego Object As")
                if save_path:
                    os.rename(stego_audio, save_path)
                    self.stego_path.set(save_path)
                    messagebox.showinfo("Success", "Stego object saved successfully.")
                else: 
                    messagebox.showwarning("Cancelled", "Save operation cancelled.")
            else:
                messagebox.showerror("Embedding Error", "An error occurred during embedding.")
    def check_capacity(self, cover_path, payload_path, num_lsbs):
        # Calculate the capacity of the cover image
        try:
            #check file type before calculation
            if self.file_type.get() == 'image':
                cover_image = Image.open(cover_path)
                width, height = cover_image.size
                num_channels = len(cover_image.getbands())  # e.g., 3 for RGB
                max_capacity = width * height * num_channels * num_lsbs // 8  # in bytes
            elif self.file_type.get() == 'audio':
                #For audio files, the capacity is calculated in bits
                with wave.open(cover_path, 'rb') as audio_file:
                    num_frames = audio_file.getnframes()
                    num_channels = audio_file.getnchannels()
                    sample_width = audio_file.getsampwidth()  # in bytes (e.g., 2 bytes for 16-bit)
                    max_capacity = num_frames * num_channels * num_lsbs // 8  # in bytes               
           
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

            # Convert payload to binary string
            payload_bits = ''.join([format(byte, '08b') for byte in payload_data])
            payload_length = len(payload_bits)

            # Add a delimiter to indicate the end of the payload
            delimiter = '1111111111111110'  # 16-bit delimiter
            payload_bits += delimiter

            # Embed payload bits into the image
            width, height = cover_image.size
            num_channels = len(cover_image.getbands())  # e.g., 3 for RGB
            max_capacity = width * height * num_channels * num_lsbs

            if len(payload_bits) > max_capacity:
                messagebox.showerror("Embedding Error", "Payload is too large to embed.")
                return None

            bit_index = 0
            for y in range(height):
                for x in range(width):
                    pixel = list(cover_pixels[x, y])
                    for n in range(num_channels):
                        if bit_index < len(payload_bits):
                            # Modify the LSBs of each color channel
                            pixel[n] = self.set_lsbs(pixel[n], num_lsbs, payload_bits[bit_index:bit_index+num_lsbs])
                            bit_index += num_lsbs
                    cover_pixels[x, y] = tuple(pixel)
                    if bit_index >= len(payload_bits):
                        break
                if bit_index >= len(payload_bits):
                    break

            return cover_image
        except Exception as e:
            messagebox.showerror("Embedding Error", f"An error occurred during embedding:\n{str(e)}")
            return None
    
    def embed_payload_audio(self, cover_audio_path, payload_path, num_lsbs):
        try:
            # Open the audio file
            with wave.open(cover_audio_path, 'rb') as audio:
                frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

            # Read the payload data
            with open(payload_path, 'r') as f:
                payload_data = f.read()

            # Convert payload to binary string
            payload_bits = ''.join([format(ord(i), '08b') for i in payload_data])
            payload_bits += '1111111111111110'  # 16-bit delimiter to mark the end

            # Check capacity
            if len(payload_bits) > len(frame_bytes) * num_lsbs:
                messagebox.showerror("Capacity Error", "Payload is too large for the selected audio file.")
                return None

            # Embed the payload into the LSBs of the audio samples
            bit_index = 0
            for i in range(len(frame_bytes)):
                if bit_index < len(payload_bits):
                    frame_bytes[i] = (frame_bytes[i] & 254) | int(payload_bits[bit_index])
                    bit_index += 1

            # Write the modified frames to a new audio file
            output_audio = "stego_audio.wav"
            with wave.open(output_audio, 'wb') as stego_audio:
                stego_audio.setparams(audio.getparams())
                stego_audio.writeframes(bytes(frame_bytes))

            return output_audio

        except Exception as e:
            messagebox.showerror("Embedding Error", f"An error occurred during embedding:\n{str(e)}")
            return None
    def set_lsbs(self, value, num_lsbs, bits):
        # Set the num_lsbs least significant bits of value to bits
        bits = bits.ljust(num_lsbs, '0')  # Pad bits if less than num_lsbs
        value_bin = format(value, '08b')
        new_value_bin = value_bin[:-num_lsbs] + bits
        return int(new_value_bin, 2)

    def display_analysis(self, payload_path, cover_path, stego_path):
        # Clear image references to prevent memory leak
        self.image_refs.clear()

        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Back Button
        back_button = tk.Button(self.root, text="Back to Main Menu", command=self.create_landing_page)
        back_button.pack(anchor='nw', padx=10, pady=10)

        # Title Label
        title_label = tk.Label(self.root, text="Embedding Analysis", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # Frames for display
        display_frame = tk.Frame(self.root)
        display_frame.pack(pady=10)

        # Display Payload
        payload_frame = tk.Frame(display_frame)
        payload_frame.grid(row=0, column=0, padx=10)
        tk.Label(payload_frame, text="Payload (Text):", font=("Helvetica", 14)).pack()
        self.display_payload_text(payload_path, payload_frame)

        # Display Images
        images_frame = tk.Frame(display_frame)
        images_frame.grid(row=0, column=1, padx=10)
        tk.Label(images_frame, text="Cover and Stego Images:", font=("Helvetica", 14)).pack()
        self.display_images(cover_path, stego_path, images_frame)

        # Display Difference Image
        diff_frame = tk.Frame(display_frame)
        diff_frame.grid(row=0, column=2, padx=10)
        tk.Label(diff_frame, text="Difference Image:", font=("Helvetica", 14)).pack()
        self.display_difference_image(cover_path, stego_path, diff_frame)

    def display_payload_text(self, payload_path, parent_frame):
        with open(payload_path, 'r', encoding='utf-8', errors='replace') as file:
            payload_text = file.read()

        text_widget = tk.Text(parent_frame, wrap='word', width=40, height=20)
        text_widget.insert('1.0', payload_text)
        text_widget.config(state='disabled')  # Make the text read-only
        text_widget.pack(pady=10)

    def display_images(self, cover_path, stego_path, parent_frame):
        try:
            cover_image = Image.open(cover_path).resize((200, 200), Image.LANCZOS)
            stego_image = Image.open(stego_path).resize((200, 200), Image.LANCZOS)
        except Exception as e:
            messagebox.showerror("Image Loading Error", f"Failed to load images:\n{str(e)}")
            return

        cover_photo = ImageTk.PhotoImage(cover_image)
        stego_photo = ImageTk.PhotoImage(stego_image)

        cover_label = tk.Label(parent_frame, image=cover_photo)
        cover_label.pack(side='left', padx=5)

        stego_label = tk.Label(parent_frame, image=stego_photo)
        stego_label.pack(side='left', padx=5)

        # Keep references to prevent garbage collection
        self.image_refs.append(cover_photo)
        self.image_refs.append(stego_photo)

    def display_difference_image(self, cover_path, stego_path, parent_frame):
        try:
            cover_image = Image.open(cover_path).convert('RGB')
            stego_image = Image.open(stego_path).convert('RGB')
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
            if file_path.lower().endswith('wav'):
                self.file_type.set('audio') # wav audio file
            else:
                self.file_type.set('image')  # Currently supporting images only

    def extract_payload(self):
        stego_path = self.stego_path.get()
        num_lsbs = self.num_lsbs.get()

        # Validate inputs
        if not stego_path:
            messagebox.showerror("Input Error", "Please select a stego object.")
            return

        file_type = self.file_type.get()
        if file_type == 'audio':
            decoded_data = self.extract_from_audio(stego_path, num_lsbs)
        elif file_type == 'image':
            decoded_data = self.extract_from_image(stego_path, num_lsbs)
        else:
            messagebox.showerror("Input Error", "Unknown file type. Please select a valid stego object.")
            return
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
            messagebox.showerror("Extraction Error", "An error occurred during extraction.")

    def extract_from_image(self, stego_path, num_lsbs):
        try:
            stego_image = Image.open(stego_path)
            stego_pixels = stego_image.load()

            width, height = stego_image.size
            num_channels = len(stego_image.getbands())  # e.g., 3 for RGB

            bits = ''
            for y in range(height):
                for x in range(width):
                    pixel = stego_pixels[x, y]
                    for n in range(num_channels):
                        bits += self.get_lsbs(pixel[n], num_lsbs)
                        # Check for delimiter
                        if bits.endswith('1111111111111110'):
                            # Remove the delimiter before decoding
                            bits = bits[:-16]
                            # Convert bits to bytes
                            payload_bytes = int(bits, 2).to_bytes(len(bits) // 8, byteorder='big')
                            # Decode bytes to string
                            decoded_data = payload_bytes.decode('utf-8', errors='replace')
                            return decoded_data
            # If delimiter not found
            messagebox.showwarning("Extraction Warning", "Delimiter not found. Payload may be incomplete.")
            return None
        except Exception as e:
            messagebox.showerror("Extraction Error", f"An error occurred during extraction:\n{str(e)}")
            return None
    
    def extract_from_audio(self, stego_path, num_lsbs):
        try:
            with wave.open(stego_path, 'rb') as wav_file:
                num_frames = wav_file.getnframes()
                frames = wav_file.readframes(num_frames)
        
            bits = ''
            for byte in frames:
                bits += self.get_lsbs(byte, num_lsbs)
                # Check for delimiter
                if bits.endswith('1111111111111110'):
                    bits = bits[:-16]  # Remove the delimiter
                    # Convert bits to bytes
                    payload_bytes = int(bits, 2).to_bytes(len(bits) // 8, byteorder='big')
                    # Decode bytes to string
                    decoded_data = payload_bytes.decode('utf-8', errors='replace')
                    return decoded_data

            # If delimiter not found
            messagebox.showwarning("Extraction Warning", "Delimiter not found. Payload may be incomplete.")
            return None
        except Exception as e:
            messagebox.showerror("Extraction Error", f"An error occurred during extraction:\n{str(e)}")
            return None

    def get_lsbs(self, value, num_lsbs):
        value_bin = format(value, '08b')
        return value_bin[-num_lsbs:]

    def display_decoded_message(self, decoded_data):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Back Button
        back_button = tk.Button(self.root, text="Back to Main Menu", command=self.create_landing_page)
        back_button.pack(anchor='nw', padx=10, pady=10)

        # Title Label
        title_label = tk.Label(self.root, text="Decoded Payload", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # Display the decoded message
        text_widget = tk.Text(self.root, wrap='word', width=80, height=25)
        text_widget.insert('1.0', decoded_data)
        text_widget.config(state='disabled')  # Make the text read-only
        text_widget.pack(pady=10)

# Create the main window
root = tk.Tk()
app = SteganographyApp(root)
root.mainloop()