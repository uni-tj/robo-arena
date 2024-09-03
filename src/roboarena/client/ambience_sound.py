import random
import time

from pygame import mixer

from roboarena.client.master_mixer import MasterMixer
from roboarena.shared.constants import (
    AmbienceSoundConstants,
    MusicPaths,
    MusicVolume,
    SoundPath,
    SoundVolume,
)


class AmbienceSound:
    _master_mixer: MasterMixer
    _ambience_sounds: list[mixer.Sound]
    _last_time_played: float
    _last_music_played: int
    """Index of last played music in AMBIENCE_MUSIC_PATHS"""

    def __init__(self, master_mixer: MasterMixer) -> None:
        self._master_mixer = master_mixer
        self._ambience_sounds = [
            self._master_mixer.load_sound(p) for p in SoundPath.AMBIENCE_SOUND
        ]
        self._last_time_played = time.time()
        self._last_music_played = AmbienceSoundConstants.AMBIENCE_MUSIC_NUM - 1

        self.switch_music()
        self._master_mixer.set_music_volume(MusicVolume.AMBIENCE_MUSIC)

    def tick(self) -> None:
        if (
            time.time() - self._last_time_played
            > AmbienceSoundConstants.DELTA_TIME_BETWEEN_AMBIENCE_SOUNDS
        ):
            self._last_time_played = time.time()
            self.play_random_ambience_sound()

    def play_random_ambience_sound(self) -> None:
        if random.random() < AmbienceSoundConstants.PROBABILITY_AMBIENCE_SOUND:
            return
        sound = random.choice(self._ambience_sounds)
        self._master_mixer.set_sound_volume(sound, SoundVolume.AMBIENCE_SOUND)
        self._master_mixer.fade_in_sound(sound, SoundVolume.AMBIENCE_SOUND_FADE)

    def switch_music(self) -> None:
        self._last_music_played = (
            self._last_music_played + 1
        ) % AmbienceSoundConstants.AMBIENCE_MUSIC_NUM
        self._master_mixer.play_music(
            MusicPaths.AMBIENCE_MUSIC[self._last_music_played]
        )

    def stop(self) -> None:
        self._master_mixer.stop_music()
