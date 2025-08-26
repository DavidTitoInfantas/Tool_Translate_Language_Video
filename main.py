from tool_language_video_translate import utils, asr, translate, tts
import yaml

# Parameters
video_name = "Pep_Guardiola_explained_why_Chelsea_is_so_good"
context = "This is a tactic football class video"

def main(video_name, context):
    video_path = f"./video_data/{video_name}.mp4"
    audio_path = f"./video_data/origin_audio_{video_name}.wav"
    output_audio_path = f"./video_data/traslated_audio_{video_name}.wav"
    output_video_path = f"./video_data/translated_{video_name}.mp4"

    # Audio extract
    utils.extract_audio(video_path=video_path, audio_path=audio_path)

    # Text convert
    text = asr.transcribe_audio(audio_path)

    # Translate the text
    text_translated = translate.translate_text(text, target_lang="PT-BR", 
                                            context=context)

    # Text to speech
    tts.synthesize_speech(text_translated, output_audio_path)

    # Merge audio with video
    utils.merge_audio_with_video(video_path, output_audio_path, output_video_path)

if __name__ == "__main__":
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    video_name = config["video_parameters"]["video_name"]
    context = config["video_parameters"]["context"]
    main(video_name, context)
