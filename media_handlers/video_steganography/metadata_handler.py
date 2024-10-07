from mutagen.mp4 import MP4
import streamlit as st

def file_to_bits(uploaded_file):
    file_content = uploaded_file.read()  # Read the file content from the UploadFile object
    bit_stream = ''.join(f'{byte:08b}' for byte in file_content)  # Convert each byte to 8-bit binary
    return bit_stream

def bits_to_file(bit_stream, output_filepath):
    byte_chunks = [bit_stream[i:i+8] for i in range(0, len(bit_stream), 8)]
    byte_data = bytearray([int(byte_chunk, 2) for byte_chunk in byte_chunks])
    with open(output_filepath, 'wb') as file:
        file.write(byte_data)
    
    print(f"File reconstructed successfully at {output_filepath}.")
    
def load_metadata(mp4_filepath, category):
    video = MP4(mp4_filepath)
    
    if category in video:
        # Retrieve the bitstream stored in the category
        bitstream = video[category][0]  # Assuming it's stored as a string or single entry
        print("Metadata loaded successfully.")
        return bitstream
    else:
        print(f"No metadata found for category '{category}'.")
        return None

def add_metadata(mp4_filepath, category, payload):
    video = MP4(mp4_filepath)
    video[category] = payload
    video.save(mp4_filepath)
    print("Metadata added successfully.")
    

def save_zip_from_metadata(mp4_filepath, category, output_zip_filepath):
    # Load the MP4 file
    video = MP4(mp4_filepath)
    
    # Check if the category exists in the video metadata
    if category in video:
        # Retrieve the bitstream stored in the category
        bitstream = video[category][0]
        
        # Split bitstream into chunks of 8 bits (each byte)
        byte_chunks = [bitstream[i:i+8] for i in range(0, len(bitstream), 8)]
        
        # Convert the 8-bit chunks back to byte format
        byte_data = bytearray([int(byte_chunk, 2) for byte_chunk in byte_chunks])
        
        # Write the bytes to a ZIP file
        with open(output_zip_filepath, 'wb') as zip_file:
            zip_file.write(byte_data)
        
        print(f"ZIP file saved successfully at {output_zip_filepath}.")
    else:
        print(f"No metadata found for category '{category}'.")
