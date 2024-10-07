import os
import cv2
from media_handlers.audio_steganography.audio_handler import audio_to_bytes, bytes_to_audio
from media_handlers.image_steganography.image_handler import image_to_bytes, bytes_to_image
from media_handlers.video_steganography.video_handler import get_total_frames, frame_to_bytes, extract_frame, extract_audio,replace_frame#, video_to_frames
from media_handlers.video_steganography.metadata_handler import add_metadata, file_to_bits, bits_to_file, load_metadata, save_zip_from_metadata
from common.bit_manipulation import embed_payload_into_bytes, extract_payload_from_bytes, extract_video_payload_from_bytes
from common.file_utils import convert_payload_to_bits

def embed_payload(cover_path, payload_path, num_lsbs, file_type):
    
    print(f"cover_path is: {cover_path}")
    
    """Embed the payload into the cover object (audio or image)."""
    
    # Convert the payload into a bit stream
    #payload_bits, total_bits_embedded = convert_payload_to_bits(payload_path, num_lsbs)
    #print(f"Total Bits to Embed: {total_bits_embedded}")
    # This lines of code has been moved to within the if-elif-else function

    # Embed based on file type (image or audio)
    if file_type == 'image':
        
        # For image file, reuse original convert function
        payload_bits, total_bits_embedded = convert_payload_to_bits(payload_path, num_lsbs)
        print(f"Total Bits to Embed: {total_bits_embedded}")
    
        # Convert the image file to bytes
        cover_bytes, mode, size = image_to_bytes(cover_path)

        # Embed the payload into the image bytes
        stego_bytes = embed_payload_into_bytes(cover_bytes, payload_bits, num_lsbs)

        # Convert the modified bytes back into an image and save
        output_image_path = "stego_image.png"
        bytes_to_image(output_image_path, stego_bytes, mode, size)
        return output_image_path

    elif file_type == 'audio':
        
        # For audio file, reuse original convert function
        payload_bits, total_bits_embedded = convert_payload_to_bits(payload_path, num_lsbs)
        print(f"Total Bits to Embed: {total_bits_embedded}")
    
        # Convert the audio file to bytes
        cover_bytes, params = audio_to_bytes(cover_path)

        # Embed the payload into the audio bytes
        stego_bytes = embed_payload_into_bytes(cover_bytes, payload_bits, num_lsbs)

        # Convert the modified bytes back into an audio file and save
        output_audio_path = "stego_audio.wav"
        bytes_to_audio(output_audio_path, stego_bytes, params)
        return output_audio_path
    
    elif file_type == 'video':
        # File type will be video here. The idea is to extract a single frame, and apply the same techniques as image.
        """ Workflow idea: 
            1: extract audio from video first
            2: choose reference and stego frame
            3: extract that stego frame and format it as PIL object so we can
               reuse the same working method as image stego (image_to_bytes/bytes_to_image)
            4: Replace the original frame with the stego frame

        """
        
        # Extract out audio component from video first
        extract_audio(cover_path, "temp_audio_only.wav")
        
        # Reuse function
        payload_bits, total_bits_embedded = convert_payload_to_bits(payload_path, num_lsbs)
        print(f"Total Bits to Embed: {total_bits_embedded}")
        
        # Get total number of frames from the video
        total_frames = get_total_frames(cover_path)
        
        reference_frame_number = None # stores where to find the stego frame
        stego_frame_number = 1 #TODO: write additional function that randomizes which frame
        
        # Ensure wanted stego frame is within the index of total frames
        if stego_frame_number > total_frames:
            raise ValueError(f"Wanted stego frame {stego_frame_number} is out of bounds of {total_frames}")
        
        # Get PIL object of stego frame
        stego_frame = extract_frame(cover_path, stego_frame_number, 'PIL')
        
        # Convert stego frame to bytes
        cover_bytes, mode, size = frame_to_bytes(stego_frame)
        
        # Embed the payload into the image bytes (Reuses method for image)
        stego_bytes = embed_payload_into_bytes(cover_bytes, payload_bits, num_lsbs)
        print("Embed Payload OK")
        
        # Convert the modified bytes back into an image and save (Reuses method for image)
        output_image_path = "single_frame_modified_from_input.png"
        bytes_to_image(output_image_path, stego_bytes, mode, size)

        # Replace the same frame with the stego'd frame
        output_video_path = "modified_frame_video.mkv" # Set MKV if using ffv1
        replace_frame(cover_path, output_image_path, stego_frame_number, output_video_path, "temp_audio_only.wav")
        print("Replace frame done")
        
        # VERIFICATION ----------------------------------------
        #extract_frame(output_video_path, stego_frame_number, 'PNG')
        
        return output_video_path
    
    else:
        pass
    
def embed_zip_payload(cover_path, zip_file):
    
    print(f"COVER PATH = {cover_path}")
    
    payload_bitstream = file_to_bits(zip_file)
    add_metadata(cover_path, 'zip', payload_bitstream)
    
    # Not a mistake, returns the original temp file because mutagen does not allow creating a new mp4
    return cover_path 
        
def extract_payload(stego_path, num_lsbs, file_type, delimiter='1111111111111110'):
    """Extract the payload from the stego object (audio or image)."""
    
    if file_type not in ['image', 'audio', 'video']:
        raise ValueError("Invalid file_type. Supported types are 'image', 'audio' or 'video'.")

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
    
    elif file_type == 'video':
        # Get PIL object of stego frame
        stego_frame_number = 1 #TODO: write additional function that randomizes which frame
        stego_frame = extract_frame(stego_path, stego_frame_number, 'PIL')
        
        # Convert stego frame to bytes
        stego_bytes, mode, size = frame_to_bytes(stego_frame)
        extracted_data = extract_payload_from_bytes(stego_bytes, num_lsbs, delimiter)
        
        return extracted_data
    
    elif file_type == 'video-metadata':
        pass
        #TODO
    
    else:
        raise ValueError("Unsupported file type.")
    
def extract_zip_payload(stego_path):
    
    save_zip_from_metadata(stego_path, 'zip\x00', "./output/extract.zip")
    #bitstream = load_metadata(stego_path, 'zip')
    #bits_to_file(bitstream, "./output/extracted_file.zip")
    return True
    
