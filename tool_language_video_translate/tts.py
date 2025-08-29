# tts.py
from typing import List
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

import asyncio
import edge_tts
from tool_language_video_translate.types import TimedLine

def synthesize_speech(text:str, output_path:str, voice:str="pt-BR-MacerioMultilingualNeural"):
    """
    Convert text to speech
    """

    try:
        # Setting the auth
        load_dotenv()
        AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY")
        AZURE_REGION = os.getenv("AZURE_REGION")
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_TTS_KEY, region=AZURE_REGION)
        speech_config.speech_synthesis_voice_name = voice

        # Define the output
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

        # Create the synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Run synthesizer
        result = synthesizer.speak_text_async(text).get()

        # Check erro
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Audio in PT-BR created: {output_path}")
            return output_path
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            raise RuntimeError(f"Speech synthesis canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}")

    except Exception as e:
        raise RuntimeError(f"An error when synthesizing speech: {e}")
    

async def synthesize_segment_tts(text: str, rate_pct: int, outfile: str, voice: str ='pt-BR-MacerioMultilingualNeural'):
    """Gera áudio via edge-tts com SSML controlando 'rate'.
    rate_pct=100 -> normal; 120 -> +20% (mais rápido); 80 -> -20% (mais devagar)
    """
    # Edge TTS aceita rate em porcentagem com sinal: +20%, -15%, etc.
    delta = rate_pct - 100
    sign = "+" if delta >= 0 else ""
    rate_str = f"{sign}{delta}%"
    # ssml = f"""
    # <speak version='1.0' xml:lang='en-US'>
    #     <voice name='{voice}'>
    #         <prosody rate='{rate_str}'>
    #             {text}
    #         </prosody>
    #     </voice>
    # </speak>
    # """.strip()

    # communicate = edge_tts.Communicate(ssml=ssml, voice=voice)
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    await communicate.save(outfile)


async def synthesize_all(lines: List[TimedLine], tmpdir: str,
                        voice: str = 'pt-BR-MacerioMultilingualNeural') -> List[str]:
    """
    Run all TTS synthesis for the given lines.
    """
    tasks = []
    outfiles = []
    os.makedirs(tmpdir, exist_ok=True)
    for i, line in enumerate(lines):
        path = os.path.join(tmpdir, f"seg_{i:05d}.mp3")
        outfiles.append(path)
        tasks.append(synthesize_segment_tts(text=line.text_translated, 
                                            rate_pct=line.rate_pct, 
                                            outfile=path, voice=voice))
    await asyncio.gather(*tasks)
    return outfiles