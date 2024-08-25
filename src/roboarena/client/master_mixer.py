import pygame
from pygame import mixer

MUSIC_DONE = pygame.USEREVENT + 1


class MasterMixer:

    muted: bool = False
    _last_set_music_volume: float

    def __init__(self):
        mixer.init()
        self._last_set_music_volume = 1.0

    def load_sound(self, path: str) -> mixer.Sound:
        return mixer.Sound(path)

    def load_music(self, path: str) -> None:
        return mixer.music.load(path)

    def play_sound(self, sound: mixer.Sound):
        if self.muted:
            return
        sound.play()

    def fade_in_sound(self, sound: mixer.Sound, time: int):
        sound.play(fade_ms=time)

    def play_music(self, song_path: str):
        mixer.music.set_endevent(MUSIC_DONE)
        self.load_music(song_path)
        mixer.music.play()

    def play_music_loop(self, song_path: str):
        self.load_music(song_path)
        mixer.music.play(loops=-1)

    def stop_sound(self, sound: mixer.Sound):
        sound.stop()

    def stop_music(self):
        mixer.music.fadeout(500)
        mixer.music.unload()

    def stop_all(self):
        mixer.stop()
        mixer.music.unload()

    def set_music_volume(self, volume: float):
        if not self.muted:
            mixer.music.set_volume(volume)
            self._last_set_music_volume = volume

    def set_sound_volume(self, sound: mixer.Sound, volume: float):
        sound.set_volume(volume)

    def mute(self):
        mixer.music.set_volume(0)
        self.muted = True

    def unmute(self):
        self.muted = False
        self.set_music_volume(self._last_set_music_volume)
        print(self._last_set_music_volume)

    def is_music_playing(self) -> bool:
        return mixer.music.get_busy()

    def is_sound_playing(self, sound: mixer.Sound) -> bool:
        return sound.get_num_channels() > 0
