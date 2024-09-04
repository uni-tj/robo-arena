import os

import pygame

from roboarena.shared.utils.vector import Vector

type Acknoledgement = int
type Path = str


def resource_path(relative_path: str) -> str:
    """Get the absolute path to the resource"""
    base_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "resources")
    )

    return os.path.join(base_path, relative_path.replace("/", os.sep))


def graphic_path(path: str) -> str:
    return resource_path(os.path.join("graphics", path))


def sound_path(path: str) -> str:
    return resource_path(os.path.join("sounds", path))


def load_graphic(path: str) -> pygame.Surface:
    return pygame.image.load(graphic_path(path))


class Graphics:

    # Buttons
    # MainMenu
    START_BUTTON_UH = load_graphic("buttons/button-play-uh.png")
    START_BUTTON_H = load_graphic("buttons/button-play-h.png")
    SETTINGS_BUTTON_UH = load_graphic("buttons/button-settings-uh.png")
    SETTINGS_BUTTON_H = load_graphic("buttons/button-settings-h.png")
    BACK_BUTTON_UH = load_graphic("buttons/button-back-uh.png")
    # SettingMenu
    BACK_BUTTON_H = load_graphic("buttons/button-back-h.png")
    SOUND_BUTTON_MUTE = load_graphic("buttons/button-sound-mute.png")
    SOUND_BUTTON_UNMUTE = load_graphic("buttons/button-sound-unmute.png")
    UP_BUTTON_UH = load_graphic("buttons/button-upkey-uh.png")
    UP_BUTTON_H = load_graphic("buttons/button-upkey-h.png")
    DOWN_BUTTON_UH = load_graphic("buttons/button-downkey-uh.png")
    DOWN_BUTTON_H = load_graphic("buttons/button-downkey-h.png")
    LEFT_BUTTON_UH = load_graphic("buttons/button-leftkey-uh.png")
    LEFT_BUTTON_H = load_graphic("buttons/button-leftkey-h.png")
    RIGHT_BUTTON_UH = load_graphic("buttons/button-rightkey-uh.png")
    RIGHT_BUTTON_H = load_graphic("buttons/button-rightkey-h.png")

    # Text
    FONT = "font/ka1.ttf"

    # Level
    # Floor
    FLOOR_1 = load_graphic("floor/floor1.png")
    FLOOR_2 = load_graphic("floor/floor2.png")
    FLOOR_START = load_graphic("floor/floor-start.png")
    # Wall
    WALL = load_graphic("wall/wall.png")
    # Door
    DOOR_OPEN = load_graphic("doors/door-open.png")
    DOOR_CLOSED = load_graphic("doors/door-closed.png")
    # Void
    VOID = load_graphic("void/void.png")
    # Obstacles
    CRATE = load_graphic("objects/chest.png")

    # Bullets
    BULLET_FRIENDLY = load_graphic("bullets/bullet-player.png")
    BULLET_ENEMY = load_graphic("bullets/bullet-enemy.png")

    # Weapons
    LASER_GUN = load_graphic("weapons/laser-gun.png")

    # Player
    PLAYER_CENTRE = load_graphic("player/player-centre.png")
    PLAYER_LEFT = load_graphic("player/player-left.png")
    PLAYER_LEFT_HALF = load_graphic("player/player-left-half.png")
    PLAYER_RIGHT = load_graphic("player/player-right.png")
    PLAYER_RIGHT_HALF = load_graphic("player/player-right-half.png")

    # Enemy
    ENEMY_FRAME_1 = load_graphic("enemy/enemy-1.png")
    ENEMY_FRAME_2 = load_graphic("enemy/enemy-2.png")
    ENEMY_FRAME_3 = load_graphic("enemy/enemy-3.png")

    # GameUI
    HEART_FULL = load_graphic("game_ui/healthbar/heart-full.png")
    HEART_EMPTY = load_graphic("game_ui/healthbar/heart-empty.png")
    HEART_HALF = load_graphic("game_ui/healthbar/heart-half.png")
    HEALTHBAR_BACKGROUND = load_graphic("game_ui/healthbar/healthbar-background.png")
    WEAPON_UI_BACKGROUND = load_graphic("game_ui/weapon_ui/weapon_ui-background.png")


class ButtonPos:

    # MainMenu
    START_BUTTON = Vector(50, 50)
    SETTINGS_BUTTON = Vector(70, 70)

    # SettingsMenu
    MUTE_BUTTON = Vector(50, 25)
    BACK_BUTTON = Vector(20, 70)
    UP_BUTTON = Vector(50, 45)
    DOWN_BUTTON = Vector(50, 60)
    LEFT_BUTTON = Vector(50, 75)
    RIGHT_BUTTON = Vector(50, 90)


class TextPos:

    # MainMenu
    HEADER_MAIN_MENU = Vector(50, 10)

    # SettingsMenu
    HEADER_SETTINGS = Vector(50, 5)
    INFO_MUTE = Vector(50, 15)
    INFO_KEYS = Vector(50, 35)

    # Endscreen
    HEADER_ENDSCREEN = Vector(50, 10)
    SCORE = Vector(50, 50)


class TextSize:

    # MainMenu
    HEADER = 200

    # SettingsMenu
    STANDARD_SIZE = 100


class TextContent:

    # MainMenu
    HEADER_MAIN_MENU = "I N F I N I T U M"

    # SettingsMenu
    HEADER_SETTINGS = "          Settings          "
    INFO_MUTE = "              Toggle sound              "
    INFO_KEYS = "Click button and hit key to change key binding"

    # Endscreen
    HEADER_ENDSCREEN = "G A M E O V E R"


class Colors:

    # Menue
    BACKGROUND_GRADIENT = ((80, 80, 80), (140, 140, 140))

    # Text
    TEXT_COLOR = (0, 0, 0)


class TextureSize:

    BUTTON_HEIGHT = 1.3
    TEXT_WIDTH = 10
    BLOCK_WIDTH = 1.0
    BULLET_TEXTURE = Vector(0.3, 0.3)
    WEAPON_WIDTH = 0.75
    WEAPON_HEIGHT = 0.6
    PLAYER_WIDTH = 1.0
    ENEMY_WIDTH = 1.5
    GAME_UI_HEIGHT = 1.0


class MusicPaths:

    # Menue
    MENU_MUSIC = sound_path("menu/menu-music.mp3")

    # AmbienceMusic
    AMBIENCE_MUSIC: list[Path] = [
        sound_path("game_ambience/game-music_1.mp3"),
        sound_path("game_ambience/game-music_2.mp3"),
    ]


class SoundPath:

    # Buttons
    BUTTON_HOVER_SOUND = sound_path("menu/button-hover.mp3")
    BUTTON_CLICK_SOUND = sound_path("menu/button-click.mp3")
    KEY_SET_SOUND = sound_path("menu/button-key-set.mp3")

    # AmbienceSound
    AMBIENCE_SOUND: list[Path] = [
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

    # EnemySounds
    ENEMY_HOVER_SOUND = sound_path("enemy/enemy-hover.mp3")
    ENEMY_SHOOTING_SOUND = sound_path("enemy/enemy-shot.mp3")
    ENEMY_HIT_SOUND = sound_path("enemy/enemy-hit.mp3")
    ENEMY_DYING_SOUND = sound_path("enemy/enemy-dying.mp3")

    # DoorSounds
    DOOR_SOUND = sound_path("door/door.mp3")

    # PlayerSounds
    PLAYER_WALKING_SOUND = sound_path("player/player-moving.mp3")
    PLAYER_SHOOTING_SOUND = sound_path("player/laser-gun.mp3")
    PLAYER_HIT_SOUND = sound_path("player/player-hit.mp3")
    PLAYER_DYING_SOUND = sound_path("player/player-dying.mp3")


class MusicVolume:

    # MainMenu
    MAIN_MENU = 0.6

    # AmbienceMusic
    AMBIENCE_MUSIC = 0.2

    # MasterMixer
    START_VOLUME = 0.15
    MUSIC_FADE = 500


class SoundVolume:

    # Buttons
    BUTTON_HOVER = 0.8
    BUTTON_CLICK = 0.7
    KEY_SET = 0.9

    # AmbienceSound
    AMBIENCE_SOUND = 0.1
    AMBIENCE_SOUND_FADE = 1500

    # EnemySounds
    ENEMY_HOVER = 0.15
    ENEMY_SHOOTING = 0.4
    ENEMY_HIT = 0.4
    ENEMY_DYING = 0.6

    # DoorSounds
    DOOR = 0.5

    # PlayerSounds
    PLAYER_WALKING = 0.4
    PLAYER_SHOOTING = 0.2
    PLAYER_HIT = 0.4
    PLAYER_DYING = 0.7


class UserEvents:
    MUSIC_DONE = pygame.USEREVENT + 1


class PlayerConstants:

    # Movement
    ACCELEARTE = 0.5
    DECELERATE = 0.1

    # Health
    START_HEALTH = 10


class WeaponConstants:
    WEAPON_SPEED = 2
    BULLET_SPEED = 6
    BULLET_Strength = 2


class DIFFICULTY:
    Weapon_Mod = 3


class EnemyConstants:

    # Health
    START_HEALTH = 10


class AmbienceSoundConstants:

    DELTA_TIME_BETWEEN_AMBIENCE_SOUNDS = 20
    AMBIENCE_MUSIC_NUM = len(MusicPaths.AMBIENCE_MUSIC)
    PROBABILITY_AMBIENCE_SOUND = 0.6


class CameraPositionConstants:
    RESPONSIVENESS_FACTOR: float = 0.025
    """Regulates the responsiveness. [0.01, 0.05] works with reasonable speeds"""


class ClientConstants:
    START_SCREEN_SIZE = (1920, 1080)


class BlockConstants:
    STANDARD_BLOCK_SIZE_PX = 50


class AnimationConstants:
    PLAYER_LOOPS_PER_FRAME = 7
    ENEMY_LOOPS_PER_FRAME = 14


class GameUIConstants:
    HEART_OFFSET = 12
    HEART_SPACING = 50
    HEART_Y = 13
    HEALTHBAR_POS = (10, 10)
    WEAPON_UI_OFFSET = 10


class NetworkConstants:
    CLIENT_TIMESTEP = 1 / 60
    SERVER_TIMESTEP = 1 / 20
    SERVER_FRAMES_PER_TIMESTEP = 3
    SERVER_IP = 0x00000000
    VSYNC = True
    INITIAL_ACKNOLEDGEMENT: Acknoledgement = -1


class GraphicConstants:
    GU_PER_SCREEN = 20.0


class PerlinNoiseConstants:
    threshold = 0.650
    gridsize = 4
    num_octaves = 3
    offset = Vector.random_unif(0, 1000000).to_int()


class SettingPathConstants:
    SETTINGS_PATH: str = os.path.join(
        os.path.dirname(__file__), "../client/settings.yml"
    )
