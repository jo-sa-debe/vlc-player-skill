from mycroft import MycroftSkill, intent_file_handler, intent_handler
from mycroft.messagebus import Message
from mycroft.skills.audioservice import AudioService
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.audio.services import vlc
import random
import os
from pathlib import Path

class VlcPlayer(CommonPlaySkill):
    def __init__(self):
        super().__init__(name="vlc-player")

    def initialize(self): 
        super().initialize()

    def CPS_match_query_phrase(self, phrase):
        level = CPSMatchLevel.GENERIC
        if phrase == "vlc-player":
            self.speak("query phrase : handled by vlc-player")
        else:
            self.speak("query phrase : " + str(phrase))
        return phrase, level

    def CPS_start(self, phrase, data):
        pass


def create_skill():
    return VlcPlayer()

