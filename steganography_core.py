import os
from media_handlers.audio_steganography.audio_handler import audio_to_bytes, bytes_to_audio
from media_handlers.image_steganography.image_handler import image_to_bytes, bytes_to_image
from common.bit_manipulation import embed_payload_into_bytes, extract_payload_from_bytes
from common.file_utils import convert_payload_to_bits

def embed_payload(cover_path, payload_path, num_lsbs, file_type):
    """Embed the payload into the cover object (audio or image)."""
    
    # Convert the payload into a bit stream
    payload_bits, total_bits_embedded = convert_payload_to_bits(payload_path, num_lsbs)
    print(f"Total Bits to Embed: {total_bits_embedded}")

    # Embed based on file type (image or audio)
    if file_type == 'image':
        # Convert the image file to bytes
        cover_bytes, mode, size = image_to_bytes(cover_path)

        # Embed the payload into the image bytes
        stego_bytes = embed_payload_into_bytes(cover_bytes, payload_bits, num_lsbs)

        # Convert the modified bytes back into an image and save
        output_image_path = "stego_image.png"
        bytes_to_image(output_image_path, stego_bytes, mode, size)
        return output_image_path

    elif file_type == 'audio':
        # Convert the audio file to bytes
        cover_bytes, params = audio_to_bytes(cover_path)

        # Embed the payload into the audio bytes
        stego_bytes = embed_payload_into_bytes(cover_bytes, payload_bits, num_lsbs)

        # Convert the modified bytes back into an audio file and save
        output_audio_path = "stego_audio.wav"
        bytes_to_audio(output_audio_path, stego_bytes, params)
        return output_audio_path

def extract_payload(stego_path, num_lsbs, file_type, delimiter='1111111111111110'):
    """Extract the payload from the stego object (audio or image)."""
    
    if file_type not in ['image', 'audio']:
        raise ValueError("Invalid file_type. Supported types are 'image' or 'audio'.")

    # Validate file path
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego file not found: {stego_path}")
    
    # Extract based on file type (image or audio)
    if file_type == 'image':
        # Convert the image file to bytes
        stego_bytes, _, _ = image_to_bytes(stego_path)

        # Extract the payload from the image bytes
        extracted_data = extract_payload_from_bytes(stego_bytes, num_lsbs, delimiter)
        return extracted_data

    elif file_type == 'audio':
        # Convert the audio file to bytes
        stego_bytes, _ = audio_to_bytes(stego_path)

        # Extract the payload from the audio bytes
        extracted_data = extract_payload_from_bytes(stego_bytes, num_lsbs, delimiter)
        return extracted_data
