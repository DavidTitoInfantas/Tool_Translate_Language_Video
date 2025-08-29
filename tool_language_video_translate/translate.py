# translate.py
import deepl
import os
from dotenv import load_dotenv
#from config import DEEP_API_KEY

from dataclasses import dataclass
from transformers import MarianTokenizer, MarianMTModel
from typing import List
from tool_language_video_translate.types import Segment, TranslationModel

def translate_text(text, target_lang, context=None):
    """
    Translate text using DeepL
    """
    load_dotenv()
    DEEP_API_KEY = os.getenv("DEEP_API_KEY")
    print("chave: ", DEEP_API_KEY)
    translator = deepl.Translator(DEEP_API_KEY)


    result = translator.translate_text(text=text, 
                                        target_lang=target_lang, 
                                        context=context)
    return result.text


LANG_PAIR_TO_MODEL = {
    ("pt", "en"): "Helsinki-NLP/opus-mt-pt-en",
    ("en", "pt"): "Helsinki-NLP/opus-mt-tc-big-en-pt", #modelo ajustado
    ("es", "pt"): "Helsinki-NLP/opus-mt-es-pt",
    ("pt", "es"): "Helsinki-NLP/opus-mt-pt-es",
    ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
    ("en", "es"): "Helsinki-NLP/opus-mt-en-es"
}


def load_translation_model(lang_src: str, lang_tgt: str) -> TranslationModel:
    """
    Load the translation model for the given language pair.
    """
    key = (lang_src, lang_tgt)
    if key not in LANG_PAIR_TO_MODEL:
        raise ValueError(f"Pair of languages not supported: {lang_src} -> {lang_tgt}."
                        f"Add on the dictionary LANG_PAIR_TO_MODEL.")
    model_name = LANG_PAIR_TO_MODEL[key]
    print(f"[translate] Loading model {model_name}...")
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return TranslationModel(model_name=model_name, tokenizer=tokenizer, model=model)


def translate_segments(segments: List[Segment], tm: TranslationModel, batch_size: int = 8, 
                        target_lang: str = 'pt', context: str = None) -> List[str]:
    """
    Translate a list of segments using MarianMTModel.
    """
    texts = [" ".join(s.text) for s in segments]
    outputs = []

    for s in texts:
        translated = translate_text(text=s, target_lang=target_lang, context=context)
        outputs.append(translated)

    assert len(outputs) == len(texts)
    return outputs

    # for i in range(0, len(texts), batch_size):
    #     batch = texts[i:i+batch_size]
    #     enc = tm.tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
    #     gen = tm.model.generate(**enc, max_new_tokens=256)
    #     decoded = tm.tokenizer.batch_decode(gen, skip_special_tokens=True)
    #     outputs.extend([d.strip() for d in decoded])
    # assert len(outputs) == len(texts)
    # return outputs

