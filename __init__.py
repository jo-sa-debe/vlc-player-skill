from mycroft import MycroftSkill, intent_file_handler


class VlcPlayer(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('player.vlc.intent')
    def handle_player_vlc(self, message):
        self.speak_dialog('player.vlc')


def create_skill():
    return VlcPlayer()

