from tool_language_video_translate.types import TimedLine, Segment
from typing import List



def estimator_speech_seconds(text: str, lang: str = None) -> float:
    """
    Simple estimator of speech time share by second. 
    """
    chars_per_sec = 15.0 # - pt/en/es: ~15 chars/seg (inclui espaços)
    lenght = max(1, len(text))
    return lenght / chars_per_sec


def compute_rate(original_dur: float, estimated_dur: float, clamp: tuple = (0.75, 1.25)) -> int:
    """
    Compute the playback rate percentage based on original and estimated durations.
    """
    # rate_factor > 1 => falar mais rápido; < 1 => mais devagar.
    rate_factor = estimated_dur / original_dur
    rate_factor = max(clamp[0], min(clamp[1], rate_factor))
    pct = int(round(rate_factor * 100))
    return pct


def build_timed_lines(segments: List[Segment], translated: List[str], 
                        lang_tgt=str) -> List[TimedLine]:
    lines: List[TimedLine] = []
    for s, t in zip(segments, translated):
        original_dur = s.end - s.start
        est = estimator_speech_seconds(t)
        pct = compute_rate(original_dur, est)
        lines.append(TimedLine(start=s.start, end=s.end, text_translated=t, rate_pct=pct))
    return lines


