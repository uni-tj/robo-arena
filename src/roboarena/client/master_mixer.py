import logging

import pygame
from pygame import mixer

from roboarena.shared.util import debounce, sound_path

MUSIC_DONE = pygame.USEREVENT + 1

logger = logging.getLogger(__file__)


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

    def play_sound(self, sound: mixer.Sound, overlap: bool = False):
        if not overlap and self.is_sound_playing(sound):
            return
        if self.muted:
            return
        sound.play()

    def play_sound_loop(self, sound: mixer.Sound):
        if self.muted or self.is_sound_playing(sound):
            return
        sound.play(loops=-1)

    def fade_in_sound(self, sound: mixer.Sound, time: int):
        if self.muted:
            return
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

    def set_music_volume(self, volume: float):
        self._last_set_music_volume = volume
        if not self.muted:
            mixer.music.set_volume(volume)

    def set_sound_volume(self, sound: mixer.Sound, volume: float):
        sound.set_volume(volume)

    def mute(self):
        self.muted = True
        mixer.music.set_volume(0)

    def unmute(self):
        self.muted = False
        mixer.music.set_volume(self._last_set_music_volume)

    def is_music_playing(self) -> bool:
        return mixer.music.get_busy()

    def is_sound_playing(self, sound: mixer.Sound) -> bool:
        return sound.get_num_channels() > 0


ENEMY_HOVER_SOUND_PATH = sound_path("enemy/enemy-hover.mp3")
ENEMY_SHOOTING_SOUND_PATH = sound_path("enemy/enemy-shot.mp3")
ENEMY_HIT_SOUND_PATH = sound_path("enemy/enemy-hit.mp3")
ENEMY_DYING_SOUND_PATH = sound_path("enemy/enemy-dying.mp3")


class EnemySounds:
    _master_mixer: MasterMixer
    _hover_sound: mixer.Sound
    _shooting_sound: mixer.Sound
    _hit_sound: mixer.Sound
    _dying_sound: mixer.Sound

    def __init__(self, master_mixer: MasterMixer) -> None:
        self._master_mixer = master_mixer
        self._hover_sound = self._master_mixer.load_sound(ENEMY_HOVER_SOUND_PATH)
        self._shooting_sound = self._master_mixer.load_sound(ENEMY_SHOOTING_SOUND_PATH)
        self._hit_sound = self._master_mixer.load_sound(ENEMY_HIT_SOUND_PATH)
        self._dying_sound = self._master_mixer.load_sound(ENEMY_DYING_SOUND_PATH)

    def enemy_hovering(self) -> None:
        self._master_mixer.set_sound_volume(self._hover_sound, 0.2)
        self._master_mixer.play_sound_loop(self._hover_sound)

    def enemy_shooting(self) -> None:
        self._master_mixer.play_sound(self._shooting_sound, True)

    def enemy_hit(self) -> None:
        self._master_mixer.set_sound_volume(self._hit_sound, 0.5)
        self._master_mixer.play_sound(self._hit_sound, True)

    def enemy_dying(self) -> None:
        self._master_mixer.stop_sound(self._hover_sound)
        self._master_mixer.play_sound(self._dying_sound)


DOOR_SOUND_PATH = sound_path("door/door.mp3")


class DoorSounds:
    _master_mixer: MasterMixer
    _door_sound: mixer.Sound

    def __init__(self, master_mixer: MasterMixer):
        self._master_mixer = master_mixer
        self._door_sound = master_mixer.load_sound(DOOR_SOUND_PATH)

    @debounce(1)
    def door_moving(self):
        self._master_mixer.play_sound(self._door_sound)


PLAYER_WALKING_SOUND_PATH = sound_path("player/player-moving.mp3")
PLAYER_SHOOTING_SOUND_PATH = sound_path("player/laser-gun.mp3")
PLAYER_HIT_SOUND_PATH = sound_path("player/player-hit.mp3")
PLAYER_DYING_SOUND_PATH = sound_path("player/player-dying.mp3")


class PlayerSounds:
    _master_mixer: MasterMixer
    _moving_sound: mixer.Sound
    _shooting_sound: mixer.Sound
    _hit_sound: mixer.Sound
    _dying_sound: mixer.Sound
    _player_moving_flag: bool

    def __init__(self, master_mixer: MasterMixer) -> None:
        self._master_mixer = master_mixer
        self._moving_sound = self._master_mixer.load_sound(PLAYER_WALKING_SOUND_PATH)
        self._shooting_sound = self._master_mixer.load_sound(PLAYER_SHOOTING_SOUND_PATH)
        self._hit_sound = self._master_mixer.load_sound(PLAYER_HIT_SOUND_PATH)
        self._dying_sound = self._master_mixer.load_sound(PLAYER_DYING_SOUND_PATH)
        self._player_moving_flag = False

    def player_moving(self) -> None:
        self._player_moving_flag = True

    def update(self) -> None:
        if self._player_moving_flag:
            self._master_mixer.play_sound_loop(self._moving_sound)
        else:
            self._master_mixer.stop_sound(self._moving_sound)

        self._player_moving_flag = False

    def player_shooting(self) -> None:
        self._master_mixer.set_sound_volume(self._shooting_sound, 0.2)
        self._master_mixer.play_sound(self._shooting_sound)

    def player_hit(self) -> None:
        self._master_mixer.play_sound(self._hit_sound)

    def player_dying(self) -> None:
        self._master_mixer.play_sound(self._dying_sound)
