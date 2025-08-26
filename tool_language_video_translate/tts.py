# tts.py
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

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