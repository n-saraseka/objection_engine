polyglot_available = True
from translatepy import Translator
translator = Translator()
from textblob import TextBlob
from collections import Counter
import random
import os

class Analizer:
    def __init__(self):
        self.official_api = True
        self.language_counter = Counter()

    def get_sentiment(self, text):
        if len(os.getenv('oe_bypass_sentiment', '')) > 0:
            return 'N'
        try:
            return self.proccess_blob(text)
        except Exception as e:
            print(e)

    def proccess_blob(self, text):
        if len(text)>1:
            translated_text = translator.translate(text, "en").result
            blob = TextBlob(translated_text)
            if (blob.sentiment.polarity >= 0.35):
                return '+'
            if (blob.sentiment.polarity < -0.35):
                return '-'
        return 'N'