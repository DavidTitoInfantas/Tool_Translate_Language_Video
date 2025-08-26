# video_utils.py
import subprocess

def extract_audio(video_path, audio_path="temp_audio.wav"):
    """
    Extract the audio from a video using ffmpeg
    """
    cmd = [
        "ffmpeg", "-i", video_path, 
        "-ar", "16000", "-ac", "1", "-f", "wav", audio_path, "-y"
    ]
    subprocess.run(cmd, check=True)
    return audio_path


def merge_audio_with_video(video_path, new_audio_path, output_path="output_video.mp4"):
    """
    Replace the original audio in a video with a new audio track.
    """
    cmd = [
        "ffmpeg", "-i", video_path, "-i", new_audio_path,
        "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0", 
        "-shortest", output_path, "-y"
    ]
    subprocess.run(cmd, check=True)
    return output_path