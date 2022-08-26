from enum import IntEnum
import random
import os
import configparser

# Classes
class Action(IntEnum):
    TEXT = 1
    SHAKE_EFFECT = 2
    OBJECTION = 3
    TEXT_SHAKE_EFFECT = 4

class Location(IntEnum):
    COURTROOM_LEFT = 1
    WITNESS_STAND = 2
    COURTROOM_RIGHT = 3
    CO_COUNCIL = 4
    JUDGE_STAND = 5
    COURT_HOUSE = 6
    def __str__(self):
        return str(self.name).capitalize()

# Single_constants
fps = 18
lag_frames = 25
lib_path = os.path.dirname(os.path.abspath(__file__))
pollys_gender = random.choice(['male', 'female'])
music_codes = ["AAI", "AAI2", "AJ", "DD", "JFA", "PWR", "SOJ", "T&T"]

config = configparser.RawConfigParser()
config.read(os.path.join(lib_path, 'render_config.cfg'))

# Config-related constants
ignore_gender = int(config.get('render-config', 'ignore-gender'))
hd_video = int(config.get('render-config', 'hd-video'))


character_roles_and_gender = {
    'PHOENIX': ['attorney', 'male'],
    'APOLLO': ['attorney', 'male'],
    'MIA': ['attorney', 'female'],
    'GREGORY': ['attorney', 'male'],
    'EDGEWORTH': ['prosecutor', 'male'],
    'GODOT': ['prosecutor', 'male'],
    'KARMA': ['prosecutor', 'male'],
    'FRANZISKA': ['prosecutor', 'female'],
    'KLAVIER': ['prosecutor', 'male'],
    'PAYNE': ['prosecutor', 'male'],
    'ROU': ['prosecutor', 'male'],
    'JUDGE': ['judge', 'male'],
    'GANT': ['witness', 'male'],
    'GROSSBERG': ['witness', 'male'],
    'GUMSHOE': ['witness', 'male'],
    'LARRY': ['witness', 'male'],
    'LOTTA': ['witness', 'female'],
    'MAGGEY': ['witness', 'female'],
    'PEARL': ['witness', 'female'],
    'SAHWIT': ['witness', 'male'],
    'SKYE': ['witness', 'female'],
    'TRUCY': ['witness', 'female'],
    'APRIL': ['witness', 'female'],
    'REDD': ['witness', 'male'],
    'YANNI': ['witness', 'male'],
    'CODY': ['witness', 'male'],
    'OLDBAG': ['witness', 'female'],
    'PENNY': ['witness', 'female'],
    'DEE': ['witness', 'female'],
    'LANA': ['witness', 'female'],
    'SAL': ['witness', 'male'],
    'MEEKINS': ['witness', 'male'],
    'WILL': ['witness', 'male'],
    'ACRO': ['witness', 'male'],
    'ADRIAN': ['witness', 'female'],
    'ANGEL': ['witness', 'female'],
    'BEN': ['witness', 'male'],
    'INI': ['witness', 'female'],
    'JAKE': ['witness', 'male'],
    'MAX': ['witness', 'male'],
    'MOE': ['witness', 'male'],
    'MORGAN': ['witness', 'female'],
    'REGINA': ['witness', 'female'],
    'WELLINGTON': ['witness', 'male'],
    'ALITA': ['witness', 'female'],
    'DARYAN': ['witness', 'male'],
    'LAMIROIR': ['witness', 'female'],
    'ELDOON': ['witness', 'male'],
    'VERA': ['witness', 'female'],
    'WOCKY': ['witness', 'male'],
    'VIOLA': ['witness', 'female'],
    'VICTOR': ['witness', 'male'],
    'TIGRE': ['witness', 'male'],
    'RON': ['witness', 'male'],
    'DESIREE': ['witness', 'female'],
    'DAHLIA': ['witness', 'female'],
    'ATMEY': ['witness', 'male'],
    'STICKLER': ['witness', 'male'],
    'KRISTOPH': ['witness', 'male'],
    'OLGA': ['witness', 'female'],
    'PLUM': ['witness', 'female'],
    'POLLY': ['witness', pollys_gender],
    'ARMSTRONG': ['witness', 'male'],
    'MATT': ['witness', 'male'],
    'BRUSHEL': ['witness', 'male'],
    'VALANT': ['witness', 'male'],
    'KILLER': ['witness', 'male'],
    'MAYA': ['assistant', 'female']
}

# Maps
locations = {
    'attorney': Location.COURTROOM_LEFT, 
    'prosecutor': Location.COURTROOM_RIGHT, 
    'judge': Location.JUDGE_STAND, 
    'witness': Location.WITNESS_STAND, 
    'assistant': Location.CO_COUNCIL
}

location_map = {
    Location.COURTROOM_LEFT: f"{lib_path}/assets/locations/defenseempty.png",
    Location.WITNESS_STAND: f"{lib_path}/assets/locations/witnessempty.png",
    Location.COURTROOM_RIGHT: f"{lib_path}/assets/locations/prosecutorempty.png",
    Location.CO_COUNCIL: f"{lib_path}/assets/locations/helperstand.png",
    Location.JUDGE_STAND: f"{lib_path}/assets/locations/judgestand.png",
    Location.COURT_HOUSE: f"{lib_path}/assets/locations/courtroomoverview.png",
}