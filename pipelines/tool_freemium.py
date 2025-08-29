from tool_language_video_translate.utils import extract_audio, build_timeline_audio, mux_with_video
from tool_language_video_translate.asr import transcribe_audio_with_segments
from tool_language_video_translate.translate import load_translation_model, translate_segments
from tool_language_video_translate.timespeech import build_timed_lines
from tool_language_video_translate.tts import synthesize_all

import asyncio
import yaml
import os
import shutil

# Parameters
# video_name = "Pep_Guardiola_explained_why_Chelsea_is_so_good"
# context = "This is a tactic football class video"

def main(video_name, context):

    video_path = f"./video_data/{video_name}.mp4"
    base_path =  f"./video_data/{video_name}"

    audio_path = os.path.join(base_path, f"origin_audio_{video_name}.wav")
    output_audio_path = os.path.join(base_path, f"tts_timeline_{video_name}.wav")
    output_video_path = os.path.join(base_path, f"translated_{video_name}.mp4")
    tmpdir = f"./temp/{video_name}"

    os.makedirs(base_path, exist_ok=True)
    os.makedirs(tmpdir, exist_ok=True)

    # video_name = "Pep_Guardiola_explained_why_Chelsea_is_so_good"
    # video_path = f"./video_data/{video_name}.mp4"
    # audio_path = f"./video_data/origin_audio_{video_name}.wav"
    # output_video_path = f"./video_data/{video_name}/translated_{video_name}.mp4"
    # base_path = f'./video_data/{video_name}/'
    # final_wav = os.path.join(base_path, "tts_timeline.wav")


    #     context = "This is a tactic football class video"
    target_lang="PT-BR"
    # Audio extract
    extract_audio(video_path=video_path, audio_path=audio_path)

    # Text convert
    #text = asr.transcribe_audio(audio_path)
    segmentos = transcribe_audio_with_segments(audio_path, lang_src="en", model_size="small", device="cpu")

    # Translate the text
    # text_translated = translate.translate_text(text, target_lang="PT-BR", 
    #                                        context=context)

    tm = load_translation_model(lang_src="en", lang_tgt="pt")
    translated = translate_segments(segments=segmentos, tm=tm, batch_size=8, target_lang=target_lang, context=context)

    # Build timeline
    lines = build_timed_lines(segmentos,translated)

    # Text to speech
    # tts.synthesize_speech(text_translated, output_audio_path)
    outfiles = asyncio.run(synthesize_all(lines, tmpdir=tmpdir))

    # Merge TTS segments into a single audio file
    timeline = build_timeline_audio(lines=lines, seg_files=outfiles, sr=44100)

    #save timeline
    timeline.export(output_audio_path, format="wav")

    # Merge audio with video
    # utils.merge_audio_with_video(video_path, output_audio_path, output_video_path)

    # Save the video
    mux_with_video(
        temp_path=base_path,    
        video_path=video_path,
        new_audio_path=output_audio_path,
        out_video_path=output_video_path,
        mode="dub" #"voiceover",
        )
    
    # save copy original video in base path 
    # tem ue ser copya não mover o arquivo

    original_video_copy = os.path.join(base_path, f"{video_name}.mp4")
    shutil.copyfile(video_path, original_video_copy)



if __name__ == "__main__":
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    video_name = config["video_parameters"]["video_name"]
    context = config["video_parameters"]["context"]
    main(video_name, context)
