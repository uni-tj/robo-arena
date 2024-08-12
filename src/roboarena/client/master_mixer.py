from pygame import mixer


class MasterMixer:

    _sound_volume: float = 1.0
    muted: bool = False

    def __init__(self):
        mixer.init()

    def load_sound(self, path: str) -> mixer.Sound:
        return mixer.Sound(path)

    def load_music(self, path: str) -> None:
        return mixer.music.load(path)

    def play_sound(self, sound: mixer.Sound):
        sound.set_volume(self._sound_volume)
        sound.play()

    def play_music(self, song_path: str):
        self.load_music(song_path)
        mixer.music.set_volume(self._sound_volume)
        mixer.music.play(loops=-1)

    def stop_sound(self, sound: mixer.Sound):
        sound.stop()

    def pause_music(self):
        mixer.music.pause()

    def unpause_music(self):
        mixer.music.set_volume(self._sound_volume)
        mixer.music.unpause()

    def stop_music(self):
        mixer.music.stop()
        mixer.music.unload()

    def stop_all(self):
        mixer.stop()
        mixer.music.unload()

    def mute(self):
        self._sound_volume = 0.0
        self.pause_music()
        self.unpause_music()
        self.muted = True

    def unmute(self):
        self._sound_volume = 1.0
        self.pause_music()
        self.unpause_music()
        self.muted = False

    def is_music_playing(self) -> bool:
        return mixer.music.get_busy()

    def is_sound_playing(self, sound: mixer.Sound) -> bool:
        return sound.get_num_channels() > 0
