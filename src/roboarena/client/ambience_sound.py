import random
import time

from pygame import mixer

from roboarena.client.master_mixer import MasterMixer
from roboarena.shared.util import sound_path

DELTA_TIME_BETWEEN_AMBIENCE_SOUNDS = 20

type Path = str

AMBIENCE_SOUND_PATHS: list[Path] = [
    sound_path("game_ambience/background-ambience_1.mp3"),
    sound_path("game_ambience/background-ambience_2.mp3"),
    sound_path("game_ambience/background-ambience_3.mp3"),
    sound_path("game_ambience/background-ambience_4.mp3"),
    sound_path("game_ambience/background-ambience_5.mp3"),
    sound_path("game_ambience/background-ambience_6.mp3"),
    sound_path("game_ambience/background-ambience_7.mp3"),
    sound_path("game_ambience/background-ambience_8.mp3"),
    sound_path("game_ambience/background-ambience_9.mp3"),
    sound_path("game_ambience/background-ambience_10.mp3"),
    sound_path("game_ambience/background-ambience_1.mp3"),
]

AMBIENCE_MUSIC_PATHS: list[Path] = [
    sound_path("game_ambience/game-music_1.mp3"),
    sound_path("game_ambience/game-music_2.mp3"),
]
AMBIENCE_MUSIC_NUM = len(AMBIENCE_MUSIC_PATHS)


class AmbienceSound:
    _master_mixer: MasterMixer
    _ambience_sounds: list[mixer.Sound]
    _last_time_played: float
    _last_music_played: int
    """Index of last played music in AMBIENCE_MUSIC_PATHS"""

    def __init__(self, master_mixer: MasterMixer) -> None:
        self._master_mixer = master_mixer
        self._ambience_sounds = [
            self._master_mixer.load_sound(p) for p in AMBIENCE_SOUND_PATHS
        ]
        self._last_time_played = time.time()
        self._last_music_played = AMBIENCE_MUSIC_NUM - 1

        self.switch_music()
        self._master_mixer.set_music_volume(0.15)

    def tick(self) -> None:
        if time.time() - self._last_time_played > DELTA_TIME_BETWEEN_AMBIENCE_SOUNDS:
            self._last_time_played = time.time()
            self.play_random_ambience_sound()

    def play_random_ambience_sound(self) -> None:
        if random.random() < 0.6:
            return
        sound = random.choice(self._ambience_sounds)
        self._master_mixer.set_sound_volume(sound, 0.1)
        self._master_mixer.fade_in_sound(sound, 1000)

    def switch_music(self) -> None:
        self._last_music_played = (self._last_music_played + 1) % AMBIENCE_MUSIC_NUM
        self._master_mixer.play_music(AMBIENCE_MUSIC_PATHS[self._last_music_played])

    def stop(self) -> None:
        self._master_mixer.stop_music()
