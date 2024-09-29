from media_handlers.audio_steganography.audio_handler import audio_to_bytes, bytes_to_audio
from media_handlers.image_steganography.image_handler import image_to_bytes, bytes_to_image
from common.bit_manipulation import embed_payload_into_bytes, extract_payload_from_bytes
from common.file_utils import convert_payload_to_bits

def embed_payload(cover_path, payload_path, num_lsbs, file_type):
    """Embed the payload into the cover object (audio or image)."""
    
    # Convert the payload into a bit stream
    payload_bits = convert_payload_to_bits(payload_path)

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

def extract_payload(stego_path, num_lsbs, file_type):
    """Extract the payload from the stego object (audio or image)."""
    
    # Extract based on file type (image or audio)
    if file_type == 'image':
        # Convert the image file to bytes
        stego_bytes, _, _ = image_to_bytes(stego_path)

        # Extract the payload from the image bytes
        extracted_data = extract_payload_from_bytes(stego_bytes, num_lsbs)
        return extracted_data

    elif file_type == 'audio':
        # Convert the audio file to bytes
        stego_bytes, _ = audio_to_bytes(stego_path)

        # Extract the payload from the audio bytes
        extracted_data = extract_payload_from_bytes(stego_bytes, num_lsbs)
        return extracted_data
