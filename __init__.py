from mycroft import MycroftSkill, intent_file_handler, intent_handler
from mycroft.messagebus import Message
from mycroft.skills.audioservice import AudioService
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
#from mycroft.audio.services import vlc
import vlc
import random
import os
from pathlib import Path

class VlcPlayer(CommonPlaySkill):
    def __init__(self):
        super().__init__(name="vlc-player")

    def initialize(self): 
        super().initialize()
        self.instance = vlc.Instance()
        # configurations
        self.list_config = {}
        self.init_config()

        # list player
        self.list_player = self.instance.media_list_player_new()
        # player
        self.player = self.instance.media_player_new()
        self.list_player.set_media_player(self.player)
        # add standard lists & set default list
        self.track_lists = {}
        self.add_standard_lists()
        self.set_default_list()
        

        # vlc events
        self.vlc_events = self.player.event_manager()
        self.vlc_list_events = self.list_player.event_manager()
        self.vlc_events.event_attach(vlc.EventType.MediaPlayerPlaying, self.vlc_start_track, 1)
        self.vlc_list_events.event_attach(vlc.EventType.MediaListPlayerPlayed, self.vlc_queue_ended, 0)
        # mycroft events
        self.add_event('mycroft.audio.service.next', self.vlc_next)
        self.add_event('mycroft.audio.service.prev', self.vlc_prev)
        self.add_event('mycroft.audio.service.pause', self.vlc_pause)
        self.add_event('mycroft.audio.service.resume', self.vlc_resume)
        self.add_event('mycroft.audio.service.stop', self.vlc_stop)
    
    def init_config(self):
        # default track lists
        # default audio list
        self.list_config["audio"] = { 
            'list': '_audio',
            'path_setting': 'audio_path'
        }
        # default video list
        self.list_config["video"] = { 
            'list': '_video',
            'path_setting': 'video_path'
        }
        # default playlist list
        self.list_config["playlist"] = { 
            'list': '_playlist',
            'path_setting': 'playlist_path'
        }
        # default cd list
        self.list_config["cd"] = { 
            'list': '_cd',
            'path_setting': 'cd_path'
        }
        # default dvd list
        self.list_config["dvd"] = { 
            'list': '_dvd',
            'path_setting': 'dvd_path'
        }

    def add_standard_lists(self):
        for config_name in self.list_config:
            self.track_lists = self.vlc_add_list_to_lists(self.track_lists, self.list_config[config_name]['list'])
            location = str(self.settings.get(self.list_config[config_name]['path_setting']))
            self.track_lists = self.vlc_add_local_folder_to_list(location, self.track_lists, self.list_config[config_name]['list'])

    def set_default_list(self):
        self.list_player.set_media_list(self.track_lists[self.list_config['audio']['list']])        

    def CPS_match_query_phrase(self, phrase):
        level = CPSMatchLevel.GENERIC
        if phrase == "vlc-player" or phrase == "vlc":
            self.speak("query phrase : handled by vlc-player")
        return (phrase, level)

    def CPS_start(self, phrase, data):
        self.speak("start phrase : " + str(phrase))
        self.vlc_play()
        pass

    def vlc_add_list_to_lists(self, lists, list_name):
        lists[list_name] = self.instance.media_list_new()
        return lists

    def vlc_add_local_folder_to_list(self, folder, lists, list_name):
          
        if list_name in lists:
            for dirpath, dirnames, filenames in os.walk(folder):
                for file in filenames:
                    track_path = Path(dirpath)
                    track_path = track_path / file
                    self.speak(track_path)  
                    lists = self.vlc_add_track_to_list(str(track_path.resolve()), lists, list_name)
                
        return lists

    def vlc_start_track(self, data, other):
        pass

    def vlc_queue_ended(self, data, other):
        pass

    def vlc_add_track_to_list(self, track, lists, list_name):
        if list_name in lists:
            lists[list_name].add_media(self.instance.media_new(track))
        return lists

    def vlc_remove_track_from_list(self, track, list):
        pass

    def vlc_play(self):
        self.speak(str(self.track_lists))
        self.list_player.play()
        pass

    def vlc_stop(self):
        if self.player.is_playing():
            self.list_player.stop()
        pass

    def vlc_next(self):
        if self.player.is_playing():
            self.list_player.next()
        pass

    def vlc_prev(self):
        if self.player.is_playing():
            self.list_player.prev()
        pass

    def vlc_pause(self):
        if self.player.is_playing():
            self.list_player.pause()
        pass


    def vlc_resume(self):
        if self.player.is_playing():
            self.list_player.resume()
        pass



def create_skill():
    return VlcPlayer()
