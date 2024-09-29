import ttkbootstrap as ttkb
from ttkbootstrap.constants import *  # Import constants for styling
from tkinter import filedialog, messagebox  # Import dialog boxes from Tkinter

from file_dialogs import select_payload, select_cover, select_stego
from steganography_utils import embed_payload, extract_payload

# Main application class
class SteganographyApp:
    def __init__(self, root):
        # Initialize the main window and variables
        self.style = ttkb.Style("flatly")  # Set the style theme for ttkbootstrap
        self.root = root
        self.root.title("LSB Steganography Tool")  # Set window title
        self.root.geometry("1700x750")  # Set window size
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
        """ Helper function to create file selection widgets. """
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
        self.create_file_selection(input_frame, "Select Payload (Text File):", self.payload_path, lambda: select_payload(self.payload_path), 0)
        self.create_file_selection(input_frame, "Select Cover Object (Image File):", self.cover_path, lambda: select_cover(self.cover_path, self.file_type), 1)

        # Spinbox for selecting the number of LSBs to use (1-8)
        ttkb.Label(input_frame, text="Number of LSBs to Use (1-8):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        ttkb.Spinbox(input_frame, from_=1, to=8, textvariable=self.num_lsbs, width=5).grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Button to start embedding the payload
        ttkb.Button(
            self.root,
            text="Embed & Save Stego Object",
            bootstyle="primary",
            width=20, 
            command=lambda: embed_payload(self, self.payload_path.get(), self.cover_path.get(), self.num_lsbs.get())
            ).pack(pady=20)

    def create_decode_page(self):
        """ Create the page for extracting payload from the stego image. """
        self.clear_window()  # Clear previous page widgets
        self.create_back_button()  # Create back button

        # Title Label
        ttkb.Label(self.root, text="Decode (Extract Payload)", font=("Helvetica", 20)).pack(pady=10)

        # Frame for input selections
        input_frame = ttkb.Frame(self.root)
        input_frame.pack(pady=10)

        # Stego Object Selection
        self.create_file_selection(input_frame, "Select Stego Object (Image File):", self.stego_path, lambda: select_stego(self.stego_path), 0)

        # Number of LSBs Selection Label and Spinbox
        ttkb.Label(input_frame, text="Number of LSBs Used (1-8):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        ttkb.Spinbox(input_frame, from_=1, to=8, textvariable=self.num_lsbs, width=5).grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # Extract Button to extract payload from stego object
        ttkb.Button(
            self.root, 
            text="Extract Payload",
            bootstyle="primary",
            width=20,
            command=lambda: extract_payload(self, self.stego_path.get(), self.num_lsbs.get())  # Call the extract payload function when clicked
        ).pack(pady=20)

        # Apply a style to make the button text larger
        #self.style.configure('Large.TButton', font=("Helvetica", 14))  # Larger font for better visibility
        #extract_button.configure(style='Large.TButton')
