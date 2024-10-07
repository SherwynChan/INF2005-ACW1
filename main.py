import streamlit as st
import os
from steganography_core import embed_payload, embed_zip_payload, extract_payload, extract_zip_payload
import matplotlib.pyplot as plt
import numpy as np
import wave

# Streamlit app title
st.title("LSB Steganography Tool")

# Sidebar for navigation between Encode and Decode
app_mode = st.sidebar.selectbox("Choose the mode", ["Encode (Embed)", "Decode (Extract)"])

# Initialize session state variables for embedded file
if "embedded_stego_file" not in st.session_state:
    st.session_state.embedded_stego_file = None
if "embedded_file_type" not in st.session_state:
    st.session_state.embedded_file_type = None

# For Encode Mode
if app_mode == "Encode (Embed)":
    st.header("Encode (Embed Payload)")

    # File upload for payload (text)
    payload_file = st.file_uploader("Upload Payload (Text File)", type=["txt"])
    zip_file = st.file_uploader("Upload Payload - Only for Video-Metadata (ZIP)", type=["ZIP"])

    # File upload for cover file (Image or Audio)
    cover_file = st.file_uploader("Upload Cover Object (Image/Audio/Video)", type=["bmp", "png", "gif", "wav", "mp4"])

    # Number of LSBs to use
    num_lsbs = st.slider("Number of LSBs to Use", min_value=1, max_value=8, value=1)

    # Select File Type (Image or Audio)
    file_type = st.selectbox("File Type", ["image", "audio", "video", "video-metadata"])

    # Display preview of the uploaded media
    if cover_file:
        
        # Image
        if cover_file.type.startswith("image"): 
            st.image(cover_file, caption="Cover Image", use_column_width=True)
        
        # Video
        elif cover_file.type.startswith("video"):
            print(f"Cover_file: {cover_file}")
            st.video(cover_file)

    # Embed Button
    if st.button("Embed"):
        if (payload_file or zip_file) and cover_file:
            
            if payload_file:
                # Write the uploaded files to temporary paths
                with open("temp_payload.txt", "wb") as f:
                    f.write(payload_file.read())
                
            with open("temp_cover." + cover_file.name.split(".")[-1], "wb") as f:
                f.write(cover_file.read())

            # Call the core embedding function
            
            # Set correct success message
            if file_type != 'video':
                message = "Payload successfully embedded! See the result below."
            else:
                message = "Payload successfully embedded! Videos formatted in MKV are not able to be previewed via streamlit"
            
            if file_type == "image":
                file_extension = "png"
                
            elif file_type == "audio":
                file_extension = "wav"
            else:
                file_extension = "mp4"
                           
            if file_type == 'video-metadata':
                print("ViDEO_METADATA")
                stego_file = embed_zip_payload("temp_cover." + cover_file.name.split(".")[-1], zip_file)
            else:
                stego_file = embed_payload("temp_cover." + cover_file.name.split(".")[-1], "temp_payload.txt", num_lsbs, file_type)
           
            print(f"Stego_file path: {stego_file}")

            # Store the stego file path in session state for the next step
            st.session_state.embedded_stego_file = stego_file
            st.session_state.embedded_file_type = file_extension

            st.success(message)

            # Display the embedded image/audio/video immediately
            if file_type == "image":
                st.image(stego_file, caption="Embedded Stego Image", use_column_width=True)
            elif file_type == "audio":
                st.audio(stego_file, format='audio/wav')
            elif file_type == "video":
                if 'mkv' in stego_file: # Only preview video file if not in MKV format
                    pass
            elif file_type == "video-metadata":
                video_file = open(stego_file, "rb")
                video_bytes = video_file.read()
                st.video(video_bytes)
            else:
                 st.error("Unsupported")
        else:
            st.error("Please upload both a payload and a cover object!")

    # If an embedded file exists, show the option to save it
    if st.session_state.embedded_stego_file:
        st.subheader("Save the Embedded Stego File")
        
        # Ask the user for a filename
        output_filename = st.text_input("Enter the filename (without extension):", value="stego_file")

        # Save Button
        if st.button("Save Stego File"):
            # Ensure output folder exists
            if not os.path.exists("output"):
                os.makedirs("output")

            # Create the final output path
            if file_type == "video":
                final_output_path = f"output/{output_filename}.mkv"
            else:
                final_output_path = f"output/{output_filename}.{st.session_state.embedded_file_type}"

            # Move or copy the embedded file to the desired location
            os.rename(st.session_state.embedded_stego_file, final_output_path)

            st.success(f"Stego object saved as: {final_output_path}")
            # Clear the session state to reset for new embeddings
            st.session_state.embedded_stego_file = None
            st.session_state.embedded_file_type = None


def plot_waveform(audio_file, downsample_factor=10, smooth=False):
    """Generate and display a clean waveform of an audio file with optional smoothing and downsampling."""
    
    # Open the audio file using wave
    with wave.open(audio_file, 'rb') as wave_file:
        # Extract raw audio from the file
        signal_data = wave_file.readframes(-1)
        signal_data = np.frombuffer(signal_data, dtype=np.int16)
        
        # Get the frame rate (samples per second)
        framerate = wave_file.getframerate()
        
        # Downsample the audio for better visibility (reduce data points)
        signal_data = signal_data[::downsample_factor]
        time = np.linspace(0, len(signal_data) / framerate, num=len(signal_data))
        
        # Optional: Apply smoothing with a rolling average (can help with dense data)
        if smooth:
            signal_data = np.convolve(signal_data, np.ones(100)/100, mode='same')

    # Create a waveform plot with larger width for better visibility
    plt.figure(figsize=(14, 6))  # Make the figure wider
    plt.plot(time, signal_data, color='black')
    plt.title("Audio Waveform")
    plt.ylabel("Amplitude")
    plt.xlabel("Time (seconds)")
    plt.grid(False)  # Turn off the grid for a cleaner look
    plt.tight_layout()  # Ensure everything fits in the plot area
    st.pyplot(plt)

def is_valid_wav(file_path):
    """Check if the file at file_path is a valid WAV file."""
    try:
        with wave.open(file_path, 'rb') as wave_file:
            wave_file.getnframes()  # Try to read the number of frames
        return True  # No exceptions means it's a valid WAV file
    except (wave.Error, EOFError) as e:
        return False  # Not a valid or complete WAV file

# Decode Mode
if app_mode == "Decode (Extract)":
    st.header("Decode (Extract Payload)")

    # File upload for stego object (Image/Audio/Video)
    stego_file = st.file_uploader("Upload Stego Object", type=["bmp", "png", "gif", "wav", "mp4", "mkv"])

    # Number of LSBs used
    num_lsbs = st.slider("Number of LSBs Used", min_value=1, max_value=8, value=1)

    # Select File Type (Image, Audio, or Video)
    file_type = st.selectbox("File Type", ["image", "audio", "video", "video-zip"])

    if stego_file:
        # Write the uploaded file to a temporary path
        temp_file_path = "temp_stego." + stego_file.name.split(".")[-1]
        with open(temp_file_path, "wb") as f:
            f.write(stego_file.read())

        # Handle image display
        if file_type == "image" and stego_file.type.startswith("image"):
            st.image(stego_file, caption="Cover Image", use_column_width=True)

        # Handle audio play and waveform display
        elif file_type == "audio" and stego_file.type == "audio/wav":
            # Play the audio
            st.audio(stego_file, format="audio/wav")

            # Check if the uploaded file is a valid WAV file
            if is_valid_wav(temp_file_path):
                # Proceed to extract the payload if valid
                st.write("Valid WAV file, ready for payload extraction.")
                # Plot waveform or any other processing
                plot_waveform(temp_file_path)
            else:
                st.error("Invalid or corrupted WAV file. Please upload a valid WAV file.")

        # Handle video display
        elif file_type == "video":
            st.video(stego_file)
            
        elif file_type == "video-zip":
            st.video(stego_file)

    # Extract Button
    if st.button("Extract Payload"):
        if stego_file:
            # Check file type and handle extraction
            if file_type == "audio" and is_valid_wav(temp_file_path):
                extracted_data = extract_payload(temp_file_path, num_lsbs, file_type)
                st.text_area("Extracted Payload", extracted_data, height=500)
            elif file_type == "image":
                extracted_data = extract_payload(temp_file_path, num_lsbs, file_type)
                st.text_area("Extracted Payload", extracted_data, height=500)
            elif file_type == "video":
                extracted_data = extract_payload(temp_file_path, num_lsbs, file_type)
                print("extracted_data returned")
                st.text_area("Extracted Payload", extracted_data, height=500)
            elif file_type == "video-zip":
                extracted_data = extract_zip_payload(temp_file_path)
                if extracted_data:
                    
                    st.success("File has been successfully extracted")
                    
                    with open("./output/extract.zip", 'rb') as file:
                        file_data = file.read()
                    
                    st.download_button(
                            label="Download ZIP File",
                            data=file_data,  # The byte data to download
                            file_name="extract.zip",  # The name of the file to download
                            mime='application/zip')  # The MIME type for ZIP files
                        
                    
                else:
                    st.error("No zip file found")
                
            else:
                st.error("Unsupported file type or invalid audio file. Please check the file and try again.")
        else:
            st.error("Please upload a stego object!")