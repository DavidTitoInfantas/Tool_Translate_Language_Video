from dataclasses import dataclass
from transformers import MarianTokenizer, MarianMTModel

@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class TranslationModel:
    model_name: str
    tokenizer: MarianTokenizer
    model: MarianMTModel

@dataclass
class TimedLine:
    start: float
    end: float
    text_translated: str
    rate_pct: int # ex.: 85 => "-15%" (mais devagar), 120 => "+20%" (mais rápido)