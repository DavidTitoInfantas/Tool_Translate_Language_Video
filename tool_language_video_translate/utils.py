# video_utils.py
import subprocess
from typing import List
import os
import tempfile
import math
from pydub import AudioSegment
from tool_language_video_translate.types import TimedLine

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


def run_ffmpeg(cmd_arg:List[str]):
    """
    Run a ffmpeg command with specific arguments.
    """
    cmd = ["ffmpeg", "-y", *cmd_arg]
    print("[ffmpeg]", 
        " ".join(cmd))
    subprocess.run(cmd, check=True)


def extra_audio_v2(video_path: str, out_wav: str, sr: int = 16000):
    """
    Extract the audio from a video file.v2
    """
    run_ffmpeg([
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", str(sr),
        out_wav
    ])


def build_timeline_audio(lines: List[TimedLine], seg_files: List[str], 
                        sr: int = 44100) -> AudioSegment:
    """
    Create a timeline audio segment from the given lines and segment files.
    """
    if len(lines) != len(seg_files):
        raise ValueError("lines e seg_files com tamanhos diferentes")

    # Duração total pela última marca de tempo
    total_ms = int(math.ceil(max(l.end for l in lines) * 1000)) + 500
    timeline = AudioSegment.silent(duration=total_ms, frame_rate=sr)

    for line, seg_path in zip(lines, seg_files):
        seg = AudioSegment.from_file(seg_path)
        start_ms = int(round(line.start * 1000))
        # Se o áudio sintetizado ficou maior que o slot, vamos cortar levemente a cauda
        slot_ms = int(round((line.end - line.start) * 1000))
        if len(seg) > slot_ms:
            seg = seg[:slot_ms]
        timeline = timeline.overlay(seg, position=start_ms)

    return timeline


def mux_with_video(temp_path: str, video_path: str, new_audio_path: str, out_video_path: str, mode: str = "dub", ducking_db: float = -18.0):
    """mode:
    - "dub": substitui 100% o áudio (dublagem)
    - "voiceover": mixa com o original reduzindo volume do original (ducking)
    """
    if mode == "dub":
        run_ffmpeg([
            "-i", video_path,
            "-i", new_audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            out_video_path,
            ])
    elif mode == "voiceover":
        # Extrai áudio original
        # with tempfile.TemporaryDirectory() as td:
        td = temp_path
        orig_wav = os.path.join(td, "orig.wav")
        print(orig_wav, video_path)
        run_ffmpeg(["-i", video_path, "-vn", orig_wav])
        # Aplica ducking no original e mixa
        mixed = os.path.join(td, "mixed.wav")
        run_ffmpeg([
            "-i", orig_wav,
            "-i", new_audio_path,
            "-filter_complex",
            f"[0:a]volume={10**(ducking_db/20):.6f}[bg];[bg][1:a]amix=inputs=2:dropout_transition=2, dynaudnorm",
            mixed,
        ])
        run_ffmpeg([
            "-i", video_path,
            "-i", mixed,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            out_video_path,
        ])
    else:
        raise ValueError("mode deve ser 'dub' ou 'voiceover'")