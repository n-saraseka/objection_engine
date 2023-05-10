from . import constants
import random
from typing import List
from .comment import Comment
from collections import Counter
from .constants import ignore_gender

def get_characters(comment_list: List[Comment]):
    counter = Counter()
    for comment in comment_list:
        counter.update({comment.effective_user_id: 1})

    users_to_characters = {}

    genders = {}
    characters = {}
    for i in comment_list:
        characters[f'user-{i.user_id}'] = i.character
        if ignore_gender==0:
            genders[f'user-{i.user_id}'] = i.gender
        else:
            genders[f'user-{i.user_id}'] = random.choice(['male', 'female'])
    
    most_common =  [t[0] for t in counter.most_common()]

    roles = constants.character_roles_and_gender
    rnd_attorneys = {'male': [], 'female': []}
    rnd_prosecutors = {'male': [], 'female': []}
    other_rnd_characters = {'male': [], 'female': []}
    for i in roles:
        if roles[i][0]=='attorney':
            rnd_attorneys[roles[i][1]].append(i)
        elif roles[i][0]=='prosecutor':
            rnd_prosecutors[roles[i][1]].append(i)
        else:
            other_rnd_characters[roles[i][1]].append(i)
    
    if len(most_common) > 0:
        print(characters[f'user-{most_common[0]}'])
        if (characters[f'user-{most_common[0]}']==None or (characters[f'user-{most_common[0]}'] not in roles)):
            rnd_attorney = random.choice(rnd_attorneys[genders[f'user-{most_common[0]}']])
            users_to_characters[most_common[0]] = rnd_attorney
        else:
            users_to_characters[most_common[0]] = characters[f'user-{most_common[0]}']
        if len(most_common) > 1:
            print(characters[f'user-{most_common[1]}'])
            if (characters[f'user-{most_common[1]}']==None or (characters[f'user-{most_common[1]}'] not in roles)):
                rnd_prosecutor = random.choice(rnd_prosecutors[genders[f'user-{most_common[1]}']])
                users_to_characters[most_common[1]] = rnd_prosecutor
            else:
                users_to_characters[most_common[1]] = characters[f'user-{most_common[1]}']
            for character in most_common[2:]:
                i = most_common.index(character)
                print(characters[f'user-{most_common[i]}'])
                if (characters[f'user-{most_common[i]}']==None or (characters[f'user-{most_common[i]}'] not in roles)):
                    rnd_character = random.choice(other_rnd_characters[genders[f'user-{most_common[i]}']])
                    other_rnd_characters[genders[f'user-{most_common[i]}']].remove(rnd_character)
                    users_to_characters[character] = rnd_character
                else:
                    users_to_characters[character] = characters[f'user-{most_common[i]}']
    return users_to_characters
