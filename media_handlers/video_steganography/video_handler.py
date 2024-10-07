import cv2
import numpy as np
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip

###################################################################################################################################  
def frame_to_bytes(PIL_object):
    """Convert frame to bytes."""

    cover_bytes = bytearray(PIL_object.tobytes())
    mode = PIL_object.mode
    print(f"Image To Bytes: Mode is: {mode}")
    size = PIL_object.size
    return cover_bytes, mode, size

def get_total_frames(video_path):
    """Return the total number of frames in a video."""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    return total_frames

def extract_frame(video_path, frame_number, output_mode):
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Set the video to the desired frame number
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    # Read the frame
    ret, frame = cap.read()
    
    if ret:
        # Convert the frame (which is in BGR format) to RGB format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert the frame to a PIL image
        pil_image = Image.fromarray(frame_rgb)
        
        cap.release()
        if output_mode == 'PIL':
            return pil_image
        elif output_mode == 'PNG':
            pil_image.save('single_frame_extracted_from_output.png', format="PNG")
    else:
        cap.release()
        raise ValueError(f"Frame {frame_number} could not be extracted from {video_path}")
    
def replace_frame(video_path, image_path, frame_number, output_path, audio_path):
    """Replace a specific frame in a video with a PNG image using MoviePy and lossless MP4 encoding (crf=0)."""
    
    # Open the video file using OpenCV
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"REPLACE FRAME FPS: {fps}")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Check if the frame number is valid
    if frame_number >= total_frames or frame_number < 0:
        raise ValueError(f"Frame number {frame_number} is out of range. The video has {total_frames} frames.")
    
    # Load the replacement image and resize it to match the video frame size
    replacement_image = Image.open(image_path)
    replacement_image = replacement_image.resize((width, height))
    
    # Convert the PIL image to a NumPy array in BGR format (since OpenCV uses BGR)
    replacement_image_bgr = cv2.cvtColor(np.array(replacement_image), cv2.COLOR_RGB2BGR)
    
    # List to hold all video frames
    frames = []
    
    # Process the video and replace the specified frame
    current_frame = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Replace the specified frame
        if current_frame == frame_number:
            frame = replacement_image_bgr
        
        # Convert the frame from BGR (OpenCV format) to RGB (MoviePy format)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        
        # Append the frame to the list
        frames.append(frame_rgb)
        
        current_frame += 1
    
    # Release the OpenCV video capture object
    cap.release()
    
    # Load original audio
    audio_clip = AudioFileClip(audio_path)

    # Create a MoviePy video clip from the list of frames
    video_clip = ImageSequenceClip(frames, fps=fps)
    
    # Add original audio back to video
    video_clip = video_clip.set_audio(audio_clip)
    
    video_clip.write_videofile(
    output_path,
    codec="ffv1",
    audio_codec=None,
    preset="slow",
    fps=fps
)

    print(f"Frame {frame_number} has been replaced and the video has been saved to {output_path}.")

def extract_audio(input_video_path, output_audio_path):
    """
    Extracts audio from a video file and saves it as an audio file.

    Args:
        input_video_path (str): Path to the input video file.
        output_audio_path (str): Path where the extracted audio will be saved.
    """
    try:
        video = VideoFileClip(input_video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)
        print(f"Audio extracted and saved to {output_audio_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    