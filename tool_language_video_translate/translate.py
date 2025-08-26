# translate.py
import deepl
import os
from dotenv import load_dotenv
#from config import DEEP_API_KEY

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

