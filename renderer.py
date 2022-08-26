from typing import List
from .utils import get_characters
from .comment_bridge import CommentBridge
from .comment import Comment
from collections import Counter
from . import anim
from .constants import music_codes
import random
import os
import requests
import zipfile


def render_comment_list(comment_list: List[Comment], output_filename = 'hello.mp4', music_code = 'PWR'):
    counter = Counter()
    thread = []
    for comment in comment_list:
        counter.update({comment.effective_user_id: 1})
    characters = get_characters(comment_list)
    for comment in comment_list:
        comment.character = characters[comment.effective_user_id]
        thread.append(CommentBridge(comment))
    if (output_filename[-4:] != '.mp4'):
        output_filename += '.mp4'
    if (music_code == "RND"):
        music_code = random.choice(music_codes)
    return anim.comments_to_scene(thread, name_music = music_code, output_filename=output_filename)