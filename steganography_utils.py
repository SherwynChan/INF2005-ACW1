from PIL import Image
from tkinter import messagebox
from tkinter import filedialog
import os
from display_utils import display_analysis, display_decoded_message

def check_capacity(cover_path, payload_path, num_lsbs):
    """Check if the cover image has enough capacity to embed the payload."""
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

def embed_into_image(cover_path, payload_path, num_lsbs):
    """Embed the payload into the cover image using LSB steganography."""
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
        padded_delimiter = (delimiter * (num_lsbs // len(delimiter) + 1))[:num_lsbs]
        payload_bits += padded_delimiter

        # Embed payload bits into the image
        width, height = cover_image.size
        num_channels = len(cover_image.getbands())  # e.g., 3 for RGB
        max_capacity = width * height * num_channels * num_lsbs

        if payload_length > max_capacity:
            messagebox.showerror("Embedding Error", "Payload is too large to embed.")
            return None

        bit_index = 0
        for y in range(height):
            for x in range(width):
                pixel = list(cover_pixels[x, y])
                for n in range(num_channels):
                    if bit_index < len(payload_bits):
                        # Modify the LSBs of each color channel
                        pixel[n] = set_lsbs(pixel[n], num_lsbs, payload_bits[bit_index:bit_index+num_lsbs])
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


def extract_from_image(stego_path, num_lsbs):
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
                    bits += get_lsbs(pixel[n], num_lsbs)

        delimiter = '1111111111111110'  # 16-bit delimiter
        padded_delimiter = (delimiter * (num_lsbs // len(delimiter) + 1))[:num_lsbs]

        delimiter_pos = bits.find(padded_delimiter)
        if delimiter_pos == -1:
            messagebox.showwarning("Extraction Warning", "Delimiter not found. Payload may be incomplete.")
            return None
        else:
            bits = bits[:delimiter_pos]

        payload_bytes = int(bits, 2).to_bytes(len(bits) // 8, byteorder='big')
        decoded_data = payload_bytes.decode('utf-8', errors='replace')

        return decoded_data

    except Exception as e:
        messagebox.showerror("Extraction Error", f"An error occurred during extraction:\n{str(e)}")
        return None
    
def extract_payload(app, stego_path, num_lsbs):
    """ Extract the hidden payload from the stego image. """
    # Validate inputs
    if not stego_path:
        messagebox.showerror("Input Error", "Please select a stego object.")
        return

    # Extract the payload using the utility function
    decoded_data = extract_from_image(stego_path, num_lsbs)
    if decoded_data:
        # Save the decoded message
        save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text Files", "*.txt")],
                                                title="Save Decoded Payload As")
        if save_path:
            with open(save_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(decoded_data)
            messagebox.showinfo("Success", "Payload extracted and saved successfully.")
            # Display the decoded message
            display_decoded_message(app, decoded_data)
        else:
            messagebox.showwarning("Cancelled", "Save operation cancelled.")
    else:
        messagebox.showerror("Extraction Error", "An error occurred during extraction.")


def embed_payload(app, payload_path, cover_path, num_lsbs):
        """ Embed the payload into the cover image using LSB steganography. """
        # Validate inputs
        if not payload_path or not cover_path:
            messagebox.showerror("Input Error", "Please select both a payload and a cover object.")
            return

        # Check capacity
        can_embed = check_capacity(cover_path, payload_path, num_lsbs)
        if not can_embed:
            return

        # Embed the payload
        stego_image = embed_into_image(cover_path, payload_path, num_lsbs)
        if stego_image:
            # Save stego object
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                    filetypes=[("PNG Files", "*.png")],
                                                    title="Save Stego Object As")
            if save_path:
                stego_image.save(save_path)
                app.stego_path.set(save_path)
                messagebox.showinfo("Success", "Stego object saved successfully.")
                # Display the payload, cover, and stego images
                display_analysis(app, payload_path, cover_path, save_path)
            else:
                messagebox.showwarning("Cancelled", "Save operation cancelled.")
        else:
            messagebox.showerror("Embedding Error", "An error occurred during embedding.")


def set_lsbs(value, num_lsbs, bits):
    """Set the num_lsbs least significant bits of value to bits."""
    bits = bits.ljust(num_lsbs, '0')  # Pad bits if less than num_lsbs
    value_bin = format(value, '08b')
    new_value_bin = value_bin[:-num_lsbs] + bits
    return int(new_value_bin, 2)

def get_lsbs(value, num_lsbs):
    """Get the num_lsbs least significant bits of value."""
    value_bin = format(value, '08b')
    return value_bin[-num_lsbs:]
