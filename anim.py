from .comment_bridge import CommentBridge
from PIL import Image, ImageDraw, ImageFont
from matplotlib.pyplot import imshow
import numpy as np
import cv2
from typing import List, Dict
import random
import os
import shutil
import random as r
from pydub import AudioSegment
import moviepy.editor as mpe
from enum import IntEnum
import ffmpeg
from collections import Counter
import random
from textwrap import wrap
import spacy
from .polarity_analysis import Analizer
analizer = Analizer()
from .img import AnimImg
from .text import AnimText
from .scene import AnimScene
from .video import AnimVideo
from .constants import lag_frames, fps, lib_path, character_roles_and_gender, hd_video
from PIL import Image, ImageDraw, ImageFont
from . import constants
import re
import subprocess

nlp = spacy.load("xx_ent_wiki_sm")
nlp.add_pipe(nlp.create_pipe('sentencizer'))

def split_str_into_newlines(text: str, max_line_count: int = 34):
    words = text.split(" ")
    new_text = ""
    for word in words:
        last_sentence = new_text.split("\n")[-1] + word + " "
        if len(last_sentence) >= max_line_count:
            new_text += "\n" + word + " "
        else:
            new_text += word + " "
    return new_text

def audio_duration(filename: str):
    duration = float(ffmpeg.probe(filename)['streams'][0]['duration'])
    return duration


# @profile
def do_video(config: List[Dict], output_filename):
    scenes = []
    sound_effects = []
    part = 0
    frames_since_video_start = 0
    audio_start_frame = 0
    for scene in config:
        # We pick up the images to be rendered
        bg = AnimImg(constants.location_map[scene["location"]])
        arrow = AnimImg(f"{lib_path}/assets/arrow.png", x=881, y=637, w=56, h=56, key_x=19)
        textbox = AnimImg(f"{lib_path}/assets/textbox4.png", w=bg.w)
        bench = None
        # constants.Location needs a more in-depth chose
        if scene["location"] == constants.Location.COURTROOM_LEFT:
            bench = AnimImg(f"{lib_path}/assets/locations/logo-left.png")
        elif scene["location"] == constants.Location.COURTROOM_RIGHT:
            bench = AnimImg(f"{lib_path}/assets/locations/logo-right.png")
        elif scene["location"] == constants.Location.WITNESS_STAND:
            bench = AnimImg(f"{lib_path}/assets/locations/witness_stand.png", w=bg.w)
            bench.y = bg.h - bench.h
        if "audio" in scene:
            audio_start_frame = frames_since_video_start
            audio_name = f'{lib_path}/assets/bgm/{scene["audio"]}.mp3'
            audio_length = int(audio_duration(audio_name)*fps)
            sound_effects.append({"_type": "bg", "length": audio_length, "src": audio_name, "start": audio_start_frame})
        current_frame = 0
        current_character_name = None
        text = None
        for obj in scene["scene"]:
            # First we check for evidences
            if "evidence" in obj and obj['evidence'] is not None:
                if scene["location"] == constants.Location.COURTROOM_RIGHT:
                    ev_bg = AnimImg(f'{lib_path}/assets/evidence-bg.gif', x=97, y=71, w=256, maxh=256)
                    evidence = AnimImg(obj["evidence"], x=111, y=85, w=232, maxh=232)
                    evidence = AnimImg(obj["evidence"], x=111, y=int(85+((228-evidence.h)/2)), w=232, h=evidence.h)
                else:
                    ev_bg = AnimImg(f'{lib_path}/assets/evidence-bg.gif', x=544, y=71, w=256, maxh=256)
                    evidence = AnimImg(obj["evidence"], x=558, y=85, w=232, maxh=232)
                    evidence = AnimImg(obj["evidence"], x=558, y=int(85+((228-evidence.h)/2)), w=232, h=evidence.h)
            else:
                ev_bg = None
                evidence = None
            if "character" in obj:
                _dir = f'{lib_path}/assets/characters/Sprites-{obj["character"]}'
                current_character_name = obj["character"]
                font_size = 30
                font_name = ImageFont.truetype(f'{lib_path}/assets/fonts/ace-name.ttf', size=font_size)
                temp = f'{lib_path}/assets/locations/defenseempty.png'
                img = Image.open(temp)
                draw = ImageDraw.Draw(img)
                w, h = draw.textsize(current_character_name, font_name)
                text_h = (30-h)/2
                if w>=367:
                    font_size = int(30*(367/w))
                    font_name = ImageFont.truetype(f'{lib_path}/assets/fonts/ace-name.ttf', size=font_size)
                    w, h = draw.textsize(current_character_name, font_name)
                    text_h = (30-h)/2
                character_name = AnimText(
                    current_character_name,
                    font_path=f'{lib_path}/assets/fonts/ace-name.ttf',
                    font_size=font_size,
                    x=int(16+(367-w)/2),
                    y=430+text_h,
                )
                default = f"neutral/{current_character_name.lower()}-normal" if "emotion" not in obj else obj["emotion"]
                default_path = (
                    f"{_dir}/{default}(a).gif"
                )
                if not os.path.isfile(default_path):
                    default_path = (
                        f"{_dir}/{default}.gif"
                    )
                if not os.path.isfile(
                        default_path
                        ):
                        default_path = (
                            f"{_dir}/neutral/{current_character_name.lower()}-normal(a).gif"
                        )
                assert os.path.isfile(
                    default_path
                ), f"{default_path} does not exist"
                default_character = AnimImg(default_path, half_speed=True)
                if "(a)" in default_path:
                    talking_character = AnimImg(
                        default_path.replace("(a)", "(b)"), half_speed=True
                    )
                else:
                    talking_character = AnimImg(default_path, half_speed=True)
            if "emotion" in obj:
                default = obj["emotion"]
                default_path = (
                    f"{_dir}/{default}(a).gif"
                )
                if not os.path.isfile(default_path):
                    default_path = (
                        f"{_dir}/{default}.gif"
                    )
                default_character = AnimImg(default_path, half_speed=True)
                if "(a)" in default_path:
                    talking_character = AnimImg(
                        default_path.replace("(a)", "(b)"), half_speed=True
                    )
                else:
                    talking_character = AnimImg(default_path, half_speed=True)
            if "action" in obj and (
                obj["action"] == constants.Action.TEXT
                or obj["action"] == constants.Action.TEXT_SHAKE_EFFECT
            ):
                character = talking_character
                _text = split_str_into_newlines(obj["text"])
                _colour = None if "colour" not in obj else obj["colour"]
                text = AnimText(
                    _text,
                    font_path=f"{lib_path}/assets/fonts/Igiari.ttf",
                    font_size=56,
                    x=19,
                    y=487,
                    typewriter_effect=True,
                    colour=_colour,
                )
                num_frames = len(_text) + lag_frames
                _character_name = character_name
                if "name" in obj:
                    font_size = 30
                    font_name = ImageFont.truetype(f'{lib_path}/assets/fonts/ace-name.ttf', size=font_size)
                    temp = f'{lib_path}/assets/locations/defenseempty.png'
                    img = Image.open(temp)
                    draw = ImageDraw.Draw(img)
                    w, h = draw.textsize(obj["name"], font_name)
                    text_h = (30-h)/2
                    if w>=427:
                        font_size = int(30*(427/w))
                        font_name = ImageFont.truetype(f'{lib_path}/assets/fonts/ace-name.ttf', size=font_size)
                        w, h = draw.textsize(obj["name"], font_name)
                        text_h = (30-h)/2
                    _character_name = AnimText(
                        obj["name"],
                        font_path=f"{lib_path}/assets/fonts/ace-name.ttf",
                        font_size=font_size,
                        x=int(16+(427-w)/2),
                        y=430+text_h,
                    )
                if obj["action"] == constants.Action.TEXT_SHAKE_EFFECT:
                    bg.shake_effect = True
                    character.shake_effect = True
                    if bench is not None:
                        bench.shake_effect = True
                    textbox.shake_effect = True
                scene_objs = list(
                    filter(
                        lambda x: x is not None,
                        [bg, character, bench, textbox, _character_name, text, ev_bg, evidence],
                    )
                )
                scenes.append(
                    AnimScene(scene_objs, len(_text) - 1, start_frame=current_frame)
                )
                sound_effects.append({"_type": "bip", "length": len(_text) - 1, "gender": character_roles_and_gender[obj["character"]][1]})
                if obj["action"] == constants.Action.TEXT_SHAKE_EFFECT:
                    bg.shake_effect = False
                    character.shake_effect = False
                    if bench is not None:
                        bench.shake_effect = False
                    textbox.shake_effect = False
                text.typewriter_effect = False
                character = default_character
                scene_objs = list(
                    filter(
                        lambda x: x is not None,
                        [bg, character, bench, textbox, _character_name, text, arrow, ev_bg, evidence],
                    )
                )
                scenes.append(
                    AnimScene(scene_objs, lag_frames, start_frame=len(_text) - 1)
                )
                current_frame += num_frames
                sound_effects.append({"_type": "silence", "length": lag_frames})
            elif "action" in obj and obj["action"] == constants.Action.SHAKE_EFFECT:
                bg.shake_effect = True
                character.shake_effect = True
                if bench is not None:
                    bench.shake_effect = True
                textbox.shake_effect = True
                character = default_character
                if text is not None:
                    scene_objs = list(
                        filter(
                            lambda x: x is not None,
                            [
                                bg,
                                character,
                                bench,
                                textbox,
                                character_name,
                                text,
                                arrow,
                                ev_bg,
                                evidence,
                            ],
                        )
                    )
                else:
                    scene_objs = [bg, character, bench]
                scenes.append(
                    AnimScene(scene_objs, lag_frames, start_frame=current_frame)
                )
                sound_effects.append({"_type": "shock", "length": lag_frames})
                current_frame += lag_frames
                bg.shake_effect = False
                character.shake_effect = False
                if bench is not None:
                    bench.shake_effect = False
                textbox.shake_effect = False
            elif "action" in obj and obj["action"] == constants.Action.OBJECTION:
                #                 bg.shake_effect = True
                #                 character.shake_effect = True
                #                 if bench is not None:
                #                     bench.shake_effect = True
                objection = AnimImg(f"{lib_path}/assets/objection.gif") if obj["character"] != 'ROU' else AnimImg(f"{lib_path}/assets/notsofast.gif")
                objection.shake_effect = True
                character = default_character
                scene_objs = list(
                    filter(lambda x: x is not None, [bg, character, bench, objection])
                )
                scenes.append(AnimScene(scene_objs, 11, start_frame=current_frame))
                bg.shake_effect = False
                if bench is not None:
                    bench.shake_effect = False
                character.shake_effect = False
                scene_objs = list(
                    filter(lambda x: x is not None, [bg, character, bench])
                )
                scenes.append(AnimScene(scene_objs, 11, start_frame=current_frame))
                sound_effects.append(
                    {
                        "_type": "objection",
                        "character": current_character_name.lower(),
                        "length": 22,
                    }
                )
                current_frame += 11
            else:
                # list(filter(lambda x: x is not None, scene_objs))
                character = default_character
                scene_objs = list(
                    filter(lambda x: x is not None, [bg, character, bench, ev_bg, evidence])
                )
                _length = lag_frames
                if "length" in obj:
                    _length = obj["length"]
                if "repeat" in obj:
                    character.repeat = obj["repeat"]
                scenes.append(AnimScene(scene_objs, _length, start_frame=current_frame))
                character.repeat = True
                sound_effects.append({"_type": "silence", "length": _length})
                current_frame += _length
            frames_since_video_start += current_frame
            if (len(scenes) > 50):
                video = AnimVideo(scenes, fps=fps)
                video.render(output_filename + '/' +str(part) + '.mp4')
                part+=1
                scenes = []
                
    if (len(scenes) > 0):
        video = AnimVideo(scenes, fps=fps)
        video.render(output_filename + '/' +str(part) + '.mp4')
    return [sound_effects, frames_since_video_start]

def do_audio(sound_effects: List[Dict], output_filename, video_end_frame):
    audio_se = AudioSegment.empty()
    music_se = AudioSegment.empty()
    blink = AudioSegment.from_wav(f"{lib_path}/assets/sfx general/sfx-blink.wav")
    blink -= 10
    badum = AudioSegment.from_wav(f"{lib_path}/assets/sfx general/sfx-fwashing.wav")
    spf = 1 / fps * 1000
    default_objection = AudioSegment.from_wav(f"{lib_path}/assets/sfx general/sfx-objection.wav")
    bgms = [x for i, x in enumerate(sound_effects) if x["_type"] == "bg"]
    cap = video_end_frame
    start = 0
    if len(bgms)>1:
        cap = bgms[1]["start"]
        l = cap
        if l>bgms[0]["length"]:
            music_se += AudioSegment.from_mp3(bgms[0]["src"])[:int((bgms[0]["length"]/fps)*1000)]
            start = bgms[0]["length"]
            l = cap-start
            bgms[0]["src"] = f'{bgms[0]["src"][:-4]}-loop.mp3'
            bgms[0]["length"] = int(audio_duration(bgms[0]["src"])*fps)
            while l>bgms[0]["length"]:
                music_se += AudioSegment.from_mp3(bgms[0]["src"])[:int((bgms[0]["length"]/fps)*1000)]
                l -= bgms[0]["length"]
            if l>0:
                music_se += AudioSegment.from_mp3(bgms[0]["src"])[:int((l/fps)*1000)]
        else:
            music_se+=AudioSegment.from_mp3(bgms[0]["src"])[:int((l/fps)*1000)]
        start = bgms[1]["start"]
        cap = video_end_frame
        l = cap - start
        if l>bgms[1]["length"]:
            music_se += AudioSegment.from_mp3(bgms[1]["src"])[:int((bgms[1]["length"]/fps)*1000)]
            start+=bgms[1]["length"]
            bgms[1]["src"] = f'{bgms[1]["src"][:-4]}-loop.mp3'
            bgms[1]["length"] = int(audio_duration(bgms[1]["src"])*fps)
            while l>bgms[1]["length"]:
                music_se += AudioSegment.from_mp3(bgms[1]["src"])[:int((bgms[1]["length"]/fps)*1000)]
                l -= bgms[1]["length"]
            if l>0:
                music_se += AudioSegment.from_mp3(bgms[1]["src"])[:int((l/fps)*1000)]
        else:
            music_se += AudioSegment.from_mp3(bgms[1]["src"])[:int((l/fps)*1000)]
    else:
        l = cap
        if l>bgms[0]["length"]:
            music_se += AudioSegment.from_mp3(bgms[0]["src"])[:int((bgms[0]["length"]/fps)*1000)]
            start = bgms[0]["length"]
            l = cap-start
            bgms[0]["src"] = f'{bgms[0]["src"][:-4]}-loop.mp3'
            bgms[0]["length"] = int(audio_duration(bgms[0]["src"])*fps)
            while l>bgms[0]["length"]:
                music_se += AudioSegment.from_mp3(bgms[0]["src"])[:int((bgms[0]["length"]/fps)*1000)]
                l -= bgms[0]["length"]
            if l>0:
                music_se += AudioSegment.from_mp3(bgms[0]["src"])[:int((l/fps)*1000)]
        else:
            music_se+=AudioSegment.from_mp3(bgms[0]["src"])[:int((l/fps)*1000)]
    for obj in sound_effects:
        if obj["_type"] == "silence":
            audio_se += AudioSegment.silent(duration=int(obj["length"] * spf))
        elif obj["_type"] == "bip":
            bip = bip = AudioSegment.from_wav(
                f"{lib_path}/assets/sfx general/sfx-blip{obj['gender']}.wav"
            ) + AudioSegment.silent(duration=50)
            long_bip = bip * 100
            long_bip -= 10
            audio_se += blink + long_bip[: max(int(obj["length"] * spf - len(blink)), 0)]
        elif obj["_type"] == "objection":
            if character_roles_and_gender[obj["character"].upper()][0] in ['attorney', 'prosecutor']:
                objection = AudioSegment.from_mp3(f'{lib_path}/assets/objections/objection ({obj["character"]}).mp3')
                audio_se += objection[: int(obj["length"] * spf)]
            else:
                audio_se += default_objection[: int(obj["length"] * spf)]
        elif obj["_type"] == "shock":
            audio_se += badum[: int(obj["length"] * spf)]
    final_se = music_se.overlay(audio_se)
    final_se.export(output_filename, format="mp3")

def ace_attorney_anim(config: List[Dict], output_filename: str = "output.mp4"):
    root_filename = output_filename[:-4]
    audio_filename = output_filename + '.audio.mp3'
    text_filename = root_filename + '.txt'
    if os.path.exists(root_filename):
        shutil.rmtree(root_filename)
    os.mkdir(root_filename)
    sound_effects = do_video(config, root_filename)
    do_audio(sound_effects[0], audio_filename, sound_effects[1])
    videos = []
    with open(text_filename, 'w') as txt:
        for file in os.listdir(root_filename):
            videos.append(file)
        videos.sort(key=lambda item : int(item[:-4]))
        for video in videos:
            txt.write('file ' + root_filename + '/' +video + '\n')
    textInput = ffmpeg.input(text_filename, format='concat')
    audio = ffmpeg.input(audio_filename)
    if os.path.exists(output_filename):
        os.remove(output_filename)
    out = ffmpeg.output(
        textInput,
        audio,
        output_filename,
        vcodec="copy",
        acodec="aac",
        strict="experimental",
        shortest=None
    )
    out.run()
    if hd_video==0:
        input_video = ffmpeg.input(output_filename)
        resized = ffmpeg.filter(input_video.video, "scale", w=256, h=192, sws_flags="neighbor")
        out = ffmpeg.output(
            resized,
            audio,
            f'{output_filename[:-4]}-resized.mp4',
            shortest=None
        )
        out.run()
        os.remove(output_filename)
        os.rename(f'{output_filename[:-4]}-resized.mp4', output_filename)
    if os.path.exists(root_filename):
        shutil.rmtree(root_filename)
    if os.path.exists(text_filename):
        os.remove(text_filename)
    if os.path.exists(audio_filename):
        os.remove(audio_filename)

def comments_to_scene(comments: List[CommentBridge], name_music = "PWR", **kwargs):
    scene = []
    for comment in comments:
        polarity = analizer.get_sentiment(comment.body)
        tokens = nlp(comment.body)
        sentences = [sent.string.strip() for sent in tokens.sents]
        joined_sentences = []
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            if len(sentence) > 85:
                text_chunks = [chunk for chunk in wrap(sentence, 85)]
                joined_sentences = [*joined_sentences, *text_chunks]
                i += 1
            else:
                if i + 1 < len(sentences) and len(f"{sentence} {sentences[i+1]}") <= 85: # Maybe we can join two different sentences
                    joined_sentences.append(sentence + " " + sentences[i+1])
                    i += 2
                else:
                    joined_sentences.append(sentence)
                    i += 1
        character_block = []
        character = comment.character
        character_folder = f'{lib_path}/assets/characters/Sprites-{character}'
        emotions = {}
        emotion_types = ['neutral', 'sad', 'happy']
        for i in range(len(emotion_types)):
            sprites = os.listdir(os.path.join(character_folder, emotion_types[i]))
            character_emotions = []
            for j in range(len(sprites)):
                character_emotion = f'{emotion_types[i]}/{sprites[j][:-7]}' if '(' in sprites[j] else f'{emotion_types[i]}/{sprites[j][:-4]}'
                if character_emotion not in character_emotions:
                    character_emotions.append(character_emotion)
            emotions[emotion_types[i]] = character_emotions
        main_emotion = random.choice(emotions['neutral'])
        if polarity == '-' or comment.score < 0:
            main_emotion = random.choice(emotions['sad'])
        elif polarity == '+':
            main_emotion = random.choice(emotions['happy'])
        # For each sentence we temporaly store it in character_block
        for idx, chunk in enumerate(joined_sentences):
            character_block.append(
                {
                    "character": character,
                    "name": comment.author.name,
                    "text": chunk,
                    "objection": (
                        polarity == '-'
                        or comment.score < 0
                        or re.search("objection", comment.body, re.IGNORECASE)
                        or (polarity == '+' and random.random() > 0.81)
                    )
                    and idx == 0,
                    "emotion": main_emotion,
                    "evidence": comment.evidence if hasattr(comment, "evidence") else None
                }
            )
        scene.append(character_block)
    formatted_scenes = []
    last_audio = f"trial/Trial ({name_music})"
    change_audio = True
    for character_block in scene:
        scene_objs = []
        if character_block[0]["objection"] == True:
            scene_objs.append(
                {
                    "character": character_block[0]["character"],
                    "action": constants.Action.OBJECTION,
                }
            )
            if last_audio != f"pursuit/Pursuit ({name_music})":
                last_audio = f"pursuit/Pursuit ({name_music})"
                change_audio = True
            
        for obj in character_block:
            # We insert the data in the character block in the definitive scene object
            scene_objs.append(
                {
                    "character": obj["character"],
                    "action": constants.Action.TEXT,
                    "emotion": obj["emotion"],
                    "text": obj["text"],
                    "name": obj["name"],
                    "evidence": obj["evidence"]
                }
            )
        # One scene may have several sub-scenes. I.e: A scene may have an objection followed by text
        formatted_scene = {
            "location": constants.locations[character_roles_and_gender[obj["character"]][0]],
            "scene": scene_objs,
        }
        if change_audio:
            formatted_scene["audio"] = last_audio
            change_audio = False
        formatted_scenes.append(formatted_scene)
    ace_attorney_anim(formatted_scenes, **kwargs)
