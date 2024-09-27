import ttkbootstrap as ttkb  # Import ttkbootstrap for themed Tkinter widgets
from ttkbootstrap.constants import *  # Import constants for styling
from tkinter import filedialog, messagebox  # Import dialog boxes from Tkinter
from PIL import Image, ImageTk  # Import Image handling from PIL (Pillow)
import os  # Import os for file system operations

from PIL import Image

if hasattr(Image, 'Resampling'):
    resample_method = Image.Resampling.LANCZOS
else:
    resample_method = Image.ANTIALIAS


# Main application class
class SteganographyApp:
    def __init__(self, root):
        # Initialize the main window and variables
        self.style = ttkb.Style("flatly")  # Set the style theme for ttkbootstrap
        self.root = root
        self.root.title("LSB Steganography Tool")  # Set window title
        self.root.geometry("800x600")  # Set window size
        self.root.resizable(False, False)  # Disable resizing

        # Variables to store file paths and settings
        self.payload_path = ttkb.StringVar()  # Path to the payload (text file)
        self.cover_path = ttkb.StringVar()  # Path to the cover image
        self.stego_path = ttkb.StringVar()  # Path to the output stego image
        self.num_lsbs = ttkb.IntVar(value=1)  # Number of least significant bits to use for embedding
        self.file_type = ttkb.StringVar()  # File type variable (optional)
        self.image_refs = []  # List to store image references for display (optional)

        self.create_landing_page()  # Create the landing page

    def clear_window(self):
        """ Clear all widgets in the main window. """
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_landing_page(self):
        """ Create the main landing page with options to encode or decode. """
        self.clear_window()  # Clear previous page widgets
        ttkb.Label(self.root, text="LSB Steganography Tool", font=("Helvetica", 24)).pack(pady=40)  # Title
        ttkb.Label(self.root, text="Choose an option to proceed:", font=("Helvetica", 14)).pack(pady=20)  # Subtext

        # Buttons to navigate to encoding or decoding pages
        ttkb.Button(self.root, text="Encode (Embed)", bootstyle="primary", width=20,
                    command=self.create_encode_page).pack(pady=10)
        ttkb.Button(self.root, text="Decode (Extract)", bootstyle="secondary", width=20,
                    command=self.create_decode_page).pack(pady=10)

    def create_back_button(self):
        """ Create a 'Back' button to return to the landing page. """
        ttkb.Button(self.root, text="Back", command=self.create_landing_page, bootstyle="danger").pack(anchor='nw', padx=10, pady=10)

    def create_file_selection(self, frame, label_text, var, command, row):
        """ 
        Helper function to create file selection widgets. 
        Args:
            frame: The parent frame where the widgets will be placed.
            label_text: Text for the label (e.g. 'Select Payload').
            var: The StringVar to hold the file path.
            command: The command to open the file dialog.
            row: The row position in the grid layout.
        """
        ttkb.Label(frame, text=label_text).grid(row=row, column=0, sticky='e', padx=5, pady=5)  # Label for file selection
        ttkb.Entry(frame, textvariable=var, width=50).grid(row=row, column=1, padx=5, pady=5)  # Entry widget for file path
        ttkb.Button(frame, text="Browse", command=command, bootstyle="success").grid(row=row, column=2, padx=5, pady=5)  # Browse button

    def create_encode_page(self):
        """ Create the page for embedding payload into the cover image. """
        self.clear_window()  # Clear previous page widgets
        self.create_back_button()  # Create back button
        ttkb.Label(self.root, text="Encode (Embed Payload)", font=("Helvetica", 20)).pack(pady=10)  # Page title

        input_frame = ttkb.Frame(self.root)  # Create a frame for input fields
        input_frame.pack(pady=10)

        # Use helper function to create file selection fields for payload and cover
        self.create_file_selection(input_frame, "Select Payload (Text File):", self.payload_path, self.select_payload, 0)
        self.create_file_selection(input_frame, "Select Cover Object (Image File):", self.cover_path, self.select_cover, 1)

        # Spinbox for selecting the number of LSBs to use (1-8)
        ttkb.Label(input_frame, text="Number of LSBs to Use (1-8):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        ttkb.Spinbox(input_frame, from_=1, to=8, textvariable=self.num_lsbs, width=5).grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Button to start embedding the payload
        ttkb.Button(self.root, text="Embed and Save Stego Object", bootstyle="primary", width=20, 
                    command=self.embed_payload).pack(pady=20)

    def select_payload(self):
        file_path = filedialog.askopenfilename(title="Select Payload (Text File)",
                                               filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.payload_path.set(file_path)

    def select_cover(self):
        file_path = filedialog.askopenfilename(
            title="Select Cover Object (Image File)",
            filetypes=[
                ("BMP Files", "*.bmp"),
                ("PNG Files", "*.png"),
                ("GIF Files", "*.gif"),
                ("JPEG Files", "*.jpeg;*.JPEG"),
                ("JPG Files", "*.jpg;*.JPG")
            ]
        )
        if file_path:
            print(f"Selected file: {file_path}")  # Debugging line to check the file path
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
        back_button = ttkb.Button(self.root, text="Back to Main Menu", command=self.create_landing_page)
        back_button.pack(anchor='nw', padx=10, pady=10)

        # Title Label
        title_label = ttkb.Label(self.root, text="Embedding Analysis", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # Frames for display
        display_frame = ttkb.Frame(self.root)
        display_frame.pack(pady=10)

        # Display Payload
        payload_frame = ttkb.Frame(display_frame)
        payload_frame.grid(row=0, column=0, padx=10)
        ttkb.Label(payload_frame, text="Payload (Text):", font=("Helvetica", 14)).pack()
        self.display_payload_text(payload_path, payload_frame)

        # Display Images
        images_frame = ttkb.Frame(display_frame)
        images_frame.grid(row=0, column=1, padx=10)
        ttkb.Label(images_frame, text="Cover and Stego Images:", font=("Helvetica", 14)).pack()
        self.display_images(cover_path, stego_path, images_frame)

        # Display Difference Image
        diff_frame = ttkb.Frame(display_frame)
        diff_frame.grid(row=0, column=2, padx=10)
        ttkb.Label(diff_frame, text="Difference Image:", font=("Helvetica", 14)).pack()
        self.display_difference_image(cover_path, stego_path, diff_frame)

    def display_payload_text(self, payload_path, parent_frame):
        with open(payload_path, 'r', encoding='utf-8', errors='replace') as file:
            payload_text = file.read()

        text_widget = ttkb.Text(parent_frame, wrap='word', width=40, height=20)
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

        cover_label = ttkb.Label(parent_frame, image=cover_photo)
        cover_label.pack(side='left', padx=5)

        stego_label = ttkb.Label(parent_frame, image=stego_photo)
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
        diff_label = ttkb.Label(parent_frame, image=diff_photo)
        diff_label.pack(pady=10)

        # Keep a reference to prevent garbage collection
        self.image_refs.append(diff_photo)

    def create_decode_page(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Back Button
        back_button = ttkb.Button(self.root, text="Back", command=self.create_landing_page)
        back_button.pack(anchor='nw', padx=10, pady=10)

        # Title Label
        title_label = ttkb.Label(self.root, text="Decode (Extract Payload)", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # Frame for input selections
        input_frame = ttkb.Frame(self.root)
        input_frame.pack(pady=10)

        # Stego Object Selection
        stego_label = ttkb.Label(input_frame, text="Select Stego Object (Image File):")
        stego_label.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        stego_entry = ttkb.Entry(input_frame, textvariable=self.stego_path, width=50)
        stego_entry.grid(row=0, column=1, padx=5, pady=5)
        stego_button = ttkb.Button(input_frame, text="Browse", command=self.select_stego)
        stego_button.grid(row=0, column=2, padx=5, pady=5)

        # Number of LSBs Selection
        lsb_label = ttkb.Label(input_frame, text="Number of LSBs Used (1-8):")
        lsb_label.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        lsb_spinbox = ttkb.Spinbox(input_frame, from_=1, to=8, textvariable=self.num_lsbs, width=5)
        lsb_spinbox.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # Extract Button
        extract_button = ttkb.Button(self.root, text="Extract Payload", font=("Helvetica", 14),
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

    def get_lsbs(self, value, num_lsbs):
        value_bin = format(value, '08b')
        return value_bin[-num_lsbs:]

    def display_decoded_message(self, decoded_data):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Back Button
        back_button = ttkb.Button(self.root, text="Back to Main Menu", command=self.create_landing_page)
        back_button.pack(anchor='nw', padx=10, pady=10)

        # Title Label
        title_label = ttkb.Label(self.root, text="Decoded Payload", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # Display the decoded message
        text_widget = ttkb.Text(self.root, wrap='word', width=80, height=25)
        text_widget.insert('1.0', decoded_data)
        text_widget.config(state='disabled')  # Make the text read-only
        text_widget.pack(pady=10)

# Create the main window
root = ttkb.Window(themename="flatly")  # Create the main window with 'flatly' theme
app = SteganographyApp(root)  # Create an instance of SteganographyApp
root.mainloop()  # Start the Tkinter event loop