import random
import time
from typing import List, Optional

from pygame import mixer

from roboarena.client.master_mixer import MasterMixer
from roboarena.shared.util import sound_path

DELTA_TIME_BETWEEN_AMBIENCE_SOUNDS = 20

MENU_MUSIC_1_PATH = sound_path("game_ambience/game-music_1.mp3")
MENU_MUSIC_2_PATH = sound_path("game_ambience/game-music_2.mp3")

BACKGROUND_AMBIENCE_SOUND_1_PATH = sound_path("game_ambience/background-ambience_1.mp3")
BACKGROUND_AMBIENCE_SOUND_2_PATH = sound_path("game_ambience/background-ambience_2.mp3")
BACKGROUND_AMBIENCE_SOUND_3_PATH = sound_path("game_ambience/background-ambience_3.mp3")
BACKGROUND_AMBIENCE_SOUND_4_PATH = sound_path("game_ambience/background-ambience_4.mp3")
BACKGROUND_AMBIENCE_SOUND_5_PATH = sound_path("game_ambience/background-ambience_5.mp3")
BACKGROUND_AMBIENCE_SOUND_6_PATH = sound_path("game_ambience/background-ambience_6.mp3")
BACKGROUND_AMBIENCE_SOUND_7_PATH = sound_path("game_ambience/background-ambience_7.mp3")
BACKGROUND_AMBIENCE_SOUND_8_PATH = sound_path("game_ambience/background-ambience_8.mp3")
BACKGROUND_AMBIENCE_SOUND_9_PATH = sound_path("game_ambience/background-ambience_9.mp3")
BACKGROUND_AMBIENCE_SOUND_10_PATH = sound_path(
    "game_ambience/background-ambience_10.mp3"
)


class AmbienceSound:
    _master_mixer: MasterMixer
    _background_ambience_sounds: List[Optional[mixer.Sound]]
    _last_time_played: float
    _toogle_music: bool

    def __init__(self, master_mixer: MasterMixer) -> None:
        self._master_mixer = master_mixer
        self.set_ambience_sound_list()
        self._last_time_played = time.time()
        self._master_mixer.play_music(MENU_MUSIC_1_PATH)
        self._toogle_music = True
        self._master_mixer.set_music_volume(0.15)

    def set_ambience_sound_list(self) -> None:
        self._background_ambience_sounds = [None]
        for i in range(1, 11):
            self._background_ambience_sounds.append(
                self._master_mixer.load_sound(
                    sound_path(f"game_ambience/background-ambience_{i}.mp3")
                )
            )

    def tick(self) -> None:
        if time.time() - self._last_time_played > DELTA_TIME_BETWEEN_AMBIENCE_SOUNDS:
            self._last_time_played = time.time()
            self.play_random_ambience_sound()

    def play_random_ambience_sound(self) -> None:
        random_sound: Optional[mixer.Sound] = random.choices(
            self._background_ambience_sounds, weights=[15, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        )[0]
        if random_sound is not None:
            self._master_mixer.set_sound_volume(random_sound, 0.1)
            self._master_mixer.fade_in_sound(random_sound, 1000)

    def switch_music(self) -> None:
        if self._toogle_music:
            self._master_mixer.play_music(MENU_MUSIC_2_PATH)
            self._toogle_music = False
        else:
            self._master_mixer.play_music(MENU_MUSIC_1_PATH)
            self._toogle_music = True

    def stop(self) -> None:
        self._master_mixer.stop_music()
