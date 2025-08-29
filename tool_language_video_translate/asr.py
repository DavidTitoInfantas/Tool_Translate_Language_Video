# asr.py
import whisper
from dataclasses import dataclass
from typing import List
from faster_whisper import WhisperModel
from tqdm import tqdm
from tool_language_video_translate.types import Segment

def transcribe_audio(audio_path, model_size="small"):
    """
    Transcribe audio using whisper.
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"]


def transcribe_audio_with_segments(audio_path: str, lang_src: str = "auto",
                                model_size: str = "small", device: str = "auto") -> List[Segment]:
    """
    Transcribe audio and return segments with start and end times, ussing faster-whisper.
    """
    print(f"[transcribe] Carregando modelo faster-whisper: {model_size}")
    model = WhisperModel(model_size, device=device, compute_type="auto")

    print(f"[transcribe] Transcrevendo áudio: {audio_path} (lang: {lang_src})...")
    segments, info = model.transcribe(audio_path, language=lang_src if lang_src != "auto" else None,
                                        vad_filter=True, beam_size=5)
    result:List[Segment] = []
    for seg in tqdm(segments):
        result.append(Segment(start=float(seg.start), end=float(seg.end), text=seg.text.split()))
    print(f"[transcribe] {len(result)} segmentos.")
    return result


