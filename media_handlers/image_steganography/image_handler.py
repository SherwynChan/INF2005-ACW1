from PIL import Image

def image_to_bytes(image_path):
    """Convert image file to bytes."""
    cover_image = Image.open(image_path)
    cover_bytes = bytearray(cover_image.tobytes())  # Convert image to byte array
    mode = cover_image.mode
    print(f"Image To Bytes: Mode is: {mode}")
    size = cover_image.size
    return cover_bytes, mode, size

def bytes_to_image(output_path, image_bytes, mode, size):
    """Convert bytes back to an image and save it."""
    stego_image = Image.frombytes(mode, size, bytes(image_bytes))
    stego_image.save(output_path)
