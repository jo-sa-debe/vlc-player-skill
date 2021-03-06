from mycroft import MycroftSkill, intent_file_handler, intent_handler
from mycroft.messagebus import Message
from mycroft.skills.audioservice import AudioService
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.skills.common_query_skill import CommonQuerySkill, CQSMatchLevel
#from mycroft.audio.services import vlc
import vlc
import random
import os
from pathlib import Path



class VlcPlayerTrackAttribute():

    allowed_attribute_names = (
        'artist',
        'title',
        'album',
        'playlist',
        'duration',
        'tracknumber',
        'trackid',
        'genre',
        'type'
    )

    def __init__(self, attribute_name):
        # name
        self.attribute_name = attribute_name
        self.attribute_value = ''

        # vocabs
        self.vocabs = []

    def get_allowed_attribute_names(self):
        return self.allowed_attribute_names

    def attribute_name_is_allowed(self, attribute_name):
        if attribute_name in self.get_allowed_attribute_names():
            return True
        else:
            return False

    def get_name(self):
        return self.attribute_name
    
    def set_value(self, value):
        self.attribute_value = value

    def get_value(self):
        return self.attribute_value

    def add_vocab(self, vocab):
        if vocab not in self.vocabs:
            self.vocabs.append(vocab)

    def get_vocabs(self):
        return self.vocabs






class VlcPlayerTrackAttributeFactory():
    
    @staticmethod
    def create_attribute(attribute_name):
        attribute = VlcPlayerTrackAttribute(attribute_name)
        if attribute.attribute_name_is_allowed(attribute_name):
            method_name = '__create_attribute_' + attribute_name
            method = getattr(VlcPlayerTrackAttributeFactory(), method_name, False)
            if method != False:
                attribute = method(attribute)    
            return attribute

    @staticmethod
    def create_attribute_with_value(attribute_name, attribute_value):
        attribute = VlcPlayerTrackAttributeFactory.create_attribute(attribute_name)
        if attribute:
            attribute.set_value(attribute_value)
            return attribute

    @staticmethod
    def __create_attribute_artist(attribute):
        attribute.add_vocab('name.artist')
        return attribute

    @staticmethod
    def __create_attribute_playlist(attribute):
        attribute.add_vocab('name.playlist')
        return attribute

    @staticmethod
    def __create_attribute_album(attribute):
        attribute.add_vocab('name.album')
        return attribute

    @staticmethod
    def __create_attribute_title(self, attribute):
        attribute.add_vocab('name.title')
        return attribute





class VlcPlayerTrack():
    def __init__(self, track):
        self.track = track
        self.track_attributes = {}

    def set_track_attribute(self, track_attribute):
        self.track_attributes[track_attribute.get_name()] = track_attribute

    def get_track_attributes(self):
        return self.track_attributes



class VlcPlayerPlaylist():
    def __init__(self):
        self.tracks = []
        pass
    
    def add_tracks_from_local_folder(self, folder, recursive):
        pass

    def add_track(self):
        pass

    def get_tracks(self):
        pass

class VlcPlayerPlaylistFactory():
    standard_playlists = [
        '_audio',
        '_video',
        '_cd',
        '_dvd',
        '_search'
        '_playlist'
    ]

    @staticmethod
    def create_playlist():
        pass
    
    @staticmethod
    def create_standard_playlists():
        lists = []

    @staticmethod
    def __create_playlist__audio():
        pass
        



class VlcPlayer(CommonPlaySkill, CommonQuerySkill):
    def __init__(self):
        super().__init__(name="vlc-player")

    def initialize(self): 
        super().initialize()
        self.instance = vlc.Instance()
        self.current_list = ''

        # vlc settings
        self.vlc_parse_flag = vlc.MediaParseFlag.local
        self.vlc_parse_timeout = -1 # = default vlc settings
        # media attributes
        self.media_attributes = {}
        self.init_media_attributes()
        # configurations
        self.list_config = {}
        self.init_lists_config()

        # list player
        self.list_player = self.instance.media_list_player_new()
        # player
        self.player = self.instance.media_player_new()
        self.list_player.set_media_player(self.player)
        # add standard lists & set default list
        self.track_lists = {}
        self.add_standard_lists()
        self.vlc_set_default_list()
        
        # vocabs
        self.vocabs = {}
        self.init_vocabs()
        # entities
        self.register_entities()
        # skill intents
        self.register_intents()
        # vlc events
        self.register_vlc_player_events()
        self.register_vlc_list_player_events()        
        # mycroft events
        self.register_mycroft_player_control_events()
        self.register_mycroft_other_events()

    def init_vocabs(self):
        self.vocabs['name.skill'] = 'name.skill'
        self.vocabs['name.artist'] = 'name.artist'
        self.vocabs['name.playlist'] = 'name.playlist'
        self.vocabs['name.title'] = 'name.title'

    def register_entities(self):
        pass

    def register_intents(self):
        # also cover intents like 'vlc play' 'vlc next' 'vlc stop' ...
        self.register_intent_file('player.vlc.play.intent', self.handler_skill_vlc_play)
        self.enable_intent('player.vlc.play.intent')
        #self.register_intent_file('player.vlc.stop.intent', self.handler_skill_vlc_stop)
        #self.register_intent_file('player.vlc.next.intent', self.handler_skill_vlc_next)
        #self.register_intent_file('player.vlc.prev.intent', self.handler_skill_vlc_prev)
        #self.register_intent_file('player.vlc.pause.intent', self.handler_skill_vlc_pause)
        #self.register_intent_file('player.vlc.resume.intent', self.handler_skill_vlc_resume)
        #self.register_intent_file('player.trackinfo.intent', self.handler_skill_vlc_track_info)
        pass

    def register_mycroft_player_control_events(self):
        self.add_event('mycroft.stop', self.skill_stop)
        self.add_event('mycroft.audio.service.play', self.handler_mycroft_vlc_play)
        self.add_event('mycroft.audio.service.next', self.handler_mycroft_vlc_next)
        self.add_event('mycroft.audio.service.prev', self.handler_mycroft_vlc_prev)
        self.add_event('mycroft.audio.service.pause', self.handler_mycroft_vlc_pause)
        self.add_event('mycroft.audio.service.resume', self.handler_mycroft_vlc_resume)
        self.add_event('mycroft.audio.service.stop', self.handler_mycroft_vlc_stop)
        self.add_event('mycroft.audio.service.track_info', self.handler_mycroft_vlc_track_info)

    def register_mycroft_other_events(self):
        #self.add_event('question:query', self.handler_mycroft_question_query)
        pass

    def register_vlc_list_player_events(self):
        self.vlc_list_events = self.list_player.event_manager()
        self.vlc_list_events.event_attach(vlc.EventType.MediaListPlayerPlayed, self.vlc_queue_ended, 0)
        self.vlc_list_events.event_attach(vlc.EventType.MediaListEndReached, self.vlc_track_list_ended, 0)
        pass

    def register_vlc_player_events(self):
        self.vlc_events = self.player.event_manager()
        self.vlc_events.event_attach(vlc.EventType.MediaPlayerPlaying, self.vlc_start_track, 1)
        self.vlc_events.event_attach(vlc.EventType.MediaPlayerMediaChanged, self.vlc_track_changed, 0)
        pass

    def init_lists_config(self):
        # standard track lists : standard track list names start with "_"
        
        # default all list
        self.list_config["all"] = { 
            'list': '_all',
            'path_setting': 'dvd_path'
        }
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
        # default search list
        self.list_config["search"] = { 
            'list': '_search',
            'path_setting': ''
        }

    def init_media_attributes(self):
        self.media_attributes = {
            'artist': 'artist',
            'album': 'album',
            'title': 'title',
            'trackid': 'trackid',
            'tracknumber': 'tracknumber',
            'tracktotal': 'tracktotal',
            'genre': 'genre',
            'duration': 'duration',
            'type': 'type',
            'playlist': 'playlist'
        }



    # List tools
    #--------------------------------------------
    def add_standard_lists(self):
        for config_name in self.list_config:
            self.track_lists = self.vlc_add_list_to_lists(self.track_lists, self.list_config[config_name]['list'])
            
            if self.list_config[config_name]['path_setting'] in self.settings:
                location = Path(str(self.settings[self.list_config[config_name]['path_setting']]))
                self.track_lists = self.vlc_add_local_folder_to_list(location, self.track_lists, self.list_config[config_name]['list'])

    
    def vlc_get_list_from_lists(self, list_name):
        if list_name in self.track_lists:
            return self.track_lists.get(list_name)
        else:
            return False
    
    def vlc_set_current_playlist(self, list_name):
        if list_name in self.track_lists:
            self.list_player.set_media_list(self.track_lists[list_name])
            self.current_list = list_name
        return self.current_list

    def vlc_get_current_playlist(self):
        return self.current_list

    def vlc_set_default_list(self):
        self.vlc_set_current_playlist(self.list_config['audio']['list'])     

    def vlc_add_list_to_lists(self, lists, list_name):
        lists[list_name] = self.instance.media_list_new()
        return lists

    def vlc_add_local_folder_to_list(self, folder, lists, list_name):
        
        if list_name in lists: 
            for dirpath, dirnames, filenames in os.walk(folder):
                for file in filenames:
                    track_path = Path(dirpath)
                    track_path = track_path / file
                    lists = self.vlc_add_trackpath_to_list(str(track_path.resolve()), lists, list_name)    
        return lists


    def vlc_add_trackpath_to_list(self, track_path, lists, list_name):
        if list_name in lists:
            media_track = self.instance.media_new(track_path)
            media_info = self.vlc_get_track_info(media_track)
            lists[list_name].add_media(media_track)
        return lists

    def vlc_add_mediatrack_to_list(self, media_track, lists, list_name):
        if list_name in lists:
            media_info = self.vlc_get_track_info(media_track)
            lists[list_name].add_media(media_track)
        return lists

    def vlc_remove_track_from_list(self, track, list):
        pass

    
    # SKILL event handlers
    #--------------------------------------------
    def handler_skill_vlc_play(self, message):
        
        self.speak("Skill play intent : " + str(message.data))

    # General control
    #--------------------------------------------

    def skill_stop(self, message):
        self.handler_mycroft_vlc_stop(message)
        self.stop()

    # VLC events
    #--------------------------------------------

    def vlc_track_changed(self, data, other):
        context = {}
        self.send_mycroft_track_info_message(data, context)

    def vlc_start_track(self, data, other):
        pass

    def vlc_queue_ended(self, data, other):
        pass

    def vlc_track_list_ended(self, data, other):
        pass

    def send_mycroft_track_info_message(self, data, context):
        context = {}
        context['source'] = self.name
        context['destination'] = self.name
        data = {}
        self.bus.emit(Message('mycroft.audio.service.track_info', data, context))

    # Playback control - Mycroft events
    #--------------------------------------------

    def handler_mycroft_vlc_play(self, message):
        player_state = self.list_player.get_state()
        if player_state == vlc.State.Paused:
            self.handler_mycroft_vlc_resume(message)
        elif player_state == vlc.State.Stopped:
            self.speak("Playing playlist : " + self.vlc_get_current_playlist())
        self.list_player.play()
        pass

    def handler_mycroft_vlc_stop(self, message):
        if self.player.is_playing():
            self.list_player.stop()
        pass

    def handler_mycroft_vlc_next(self, message):
        if self.player.is_playing():
            self.list_player.next()
        pass

    def handler_mycroft_vlc_prev(self, message):
        if self.player.is_playing():
            self.list_player.previous()
        pass

    def handler_mycroft_vlc_pause(self, message):
        if self.player.is_playing():
            self.list_player.pause()    
        pass


    def handler_mycroft_vlc_resume(self, message):
        """
        resume playback

          Args:
                none
        """
        if not self.player.is_playing():
            self.list_player.play()
            self.bus.emit(Message('mycroft.audio.service.track_info'))
        pass

    def handler_mycroft_vlc_seek_forward(self, seconds=1):
        """
        skip X seconds

          Args:
                seconds (int): number of seconds to seek, if negative rewind
        """
        seconds = seconds * 1000
        new_time = self.player.get_time() + seconds
        duration = self.player.get_length()
        if new_time > duration:
            new_time = duration
        self.player.set_time(new_time)

    def handler_mycroft_vlc_seek_backward(self, seconds=1):
        """
        rewind X seconds

          Args:
                seconds (int): number of seconds to seek, if negative rewind
        """
        seconds = seconds * 1000
        new_time = self.player.get_time() - seconds
        if new_time < 0:
            new_time = 0
        self.player.set_time(new_time)

    # Other - Mycroft events
    #--------------------------------------------
    # def handler_mycroft_question_query(self, message):
    #     #message.data.get('phrase')
    #     self.speak('question query : ' + str(message.data.get('phrase')))
    #     self.speak(str(message))

        

    # Track info
    #-------------------------------------------- 
    def vlc_get_track_info(self, track):
        track_info = {}
        meta = vlc.Meta
        if track:
            track.parse_with_options(self.vlc_parse_flag)
            # set artist
            
            # TO-DO: check , value currently as None
            attribute = VlcPlayerTrackAttributeFactory.create_attribute_with_value('artist', track.get_meta(meta.Artist))
            

            track_info[self.media_attributes['album']] = track.get_meta(meta.Album) 
            track_info[self.media_attributes['artist']] = track.get_meta(meta.Artist) 
            track_info[self.media_attributes['title']] = track.get_meta(meta.Title) 
            track_info[self.media_attributes['trackid']] = track.get_meta(meta.TrackID) 
            track_info[self.media_attributes['tracknumber']] = track.get_meta(meta.TrackNumber) 
            track_info[self.media_attributes['tracktotal']] = track.get_meta(meta.TrackTotal) 
            track_info[self.media_attributes['genre']] = track.get_meta(meta.Genre) 
            track_info[self.media_attributes['duration']] = track.get_duration()
            track_info[self.media_attributes['type']] = track.get_type()
        return track_info

    def handler_mycroft_vlc_track_info(self, message):
        context = message.context
        if context:
            if context.get('source') == self.name and context.get('destination') == self.name:
                self.speak("track info - source: " + str(message.context.get('source')) + " - dest : " + str(message.context.get('destination') ))
                current_track = self.player.get_media()
                if current_track:
                    track_info = self.vlc_get_track_info(current_track)
                    if track_info.get('title'):
                        self.speak("Title : " + track_info.get('title'))
                    if track_info.get('artist'):
                        self.speak("Artist : " + track_info.get('artist'))

            #return track_info


    # Search tools
    #-------------------------------------------- 

    def vlc_search(self, data):
        # keep the current playlist to be able to go back
        current_playlist = self.vlc_get_current_playlist()
        

        
        # if no playlist, search current first
        if not data[self.media_attributes['playlist']]:
            data[self.media_attributes['playlist']] = self.vlc_get_current_playlist()

        track_score = self.vlc_search_list_by_meta(self.track_lists[data[self.media_attributes['playlist']]], data )
        for track in track_score:
            if track_score[track] > 0.0:
                #self.speak(str(self.track_lists[data[self.media_attributes['playlist']]][track]) + ' score : ' + str(track_score[track]))
                # use 'search' playlist to store found tracks
                self.vlc_add_mediatrack_to_list(track, self.track_lists, self.list_config['search']['list'])

        self.vlc_set_current_playlist(self.list_config['search']['list'])
        self.list_player.play()        

        # if not found search all playlist

        # if not found forward to other skills

    def vlc_search_list_by_meta(self, track_list, attribute_value_list):
        score_increment = 1 / len( attribute_value_list )
        track_score = {}

        for track in track_list:
            track_score[track] = 0.00

            track_info = self.vlc_get_track_info(track)
            for attribute in attribute_value_list:
                # TODO: this needs to be changed to fuzzy search
                if attribute in track_info:
                    if track_info[attribute] == attribute_value_list[attribute]:
                        track_score[track] = track_score[track] + score_increment

        return track_score


    # Common Playback Skill methods
    #--------------------------------------------  
    def CPS_match_query_phrase(self, phrase):
        self.speak('CPS Query : ' + str(phrase))
        level = CPSMatchLevel.GENERIC
        if self.voc_match(phrase, self.vocabs['name.skill']):
            self.speak("phrase : " + str(phrase) + " by vlc-player")
        return (phrase, level)

    def CPS_start(self, message, data):
        self.speak("CPS start : " + str(message) + " - data : "+ str(data))
        self.handler_mycroft_vlc_play(message)
        pass

    # Common Query Skill methods
    #-------------------------------------------- 
    def CQS_match_query_phrase(self, phrase):
        self.speak('CQS Query : ' + str(phrase))
        level = CQSMatchLevel.GENERAL
        if self.voc_match(phrase, self.vocabs['name.skill']):
            self.speak("phrase : " + str(phrase) + " by vlc-player")
            self.parse_common_skill_query(phrase)

        

    def CQS_action(self, phrase, data):
        self.speak('CQS Action : ' + str(phrase) + ' - ' +str(data))


    # Query parsing
    #-------------------------------------------- 

    def parse_common_skill_query(self, phrase):
        # check for key words - vocab
        # - artist / group / band / from / by ...
        # - title / track / song / video 
        # - genre
        # - playlist
        # - commands ( e.g. : random/shuffle/any (music | song) )

        # returns  (match, CPSMatchLevel[, callback_data]) or None: 
            # example
            # "match_text", CPSMatchLevel.MULTI_KEY, {"artist": 'artist_name', "song": 'song_name'})

        data = {}
        data = {
            self.media_attributes['playlist'] : '_audio',
            self.media_attributes['artist'] : 'dEUS',
        }
        self.vlc_search(data)
        pass

def create_skill():
    return VlcPlayer()

