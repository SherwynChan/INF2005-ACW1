import wave

def audio_to_bytes(audio_path):
    """Convert audio file to bytes."""
    with wave.open(audio_path, 'rb') as audio_file:
        frame_bytes = bytearray(list(audio_file.readframes(audio_file.getnframes())))
        params = audio_file.getparams()  # Save the audio parameters (channels, frame rate, etc.)
    return frame_bytes, params

def bytes_to_audio(output_path, audio_bytes, params):
    """Convert bytes back to an audio file."""
    with wave.open(output_path, 'wb') as audio_file:
        audio_file.setparams(params)  # Restore the original audio parameters
        audio_file.writeframes(bytes(audio_bytes))
