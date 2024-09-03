from roboarena.shared.util import load_graphic, sound_path
from roboarena.shared.utils.vector import Vector

CLIENT_TIMESTEP = 1 / 60
SERVER_TIMESTEP = 1 / 20
SERVER_FRAMES_PER_TIMESTEP = 3
SERVER_IP = 0x00000000
VSYNC = True


class PlayerConstants:

    # Movement
    ACCELEARTE = 0.6
    DECELERATE = 0.1

    # Health
    MAX_HEALTH = 10


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


class MusicPaths:

    # Menue
    MENU_MUSIC = sound_path("menu/menu-music.mp3")


class SoundPath:

    # Buttons
    BUTTON_HOVER_SOUND = sound_path("menu/button-hover.mp3")
    BUTTON_CLICK_SOUND = sound_path("menu/button-click.mp3")


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


class Colors:

    # Menue
    BACKGROUND_GRADIENT = ((80, 80, 80), (140, 140, 140))

    # Text
    TEXT_COLOR = (0, 0, 0)


class TextureSize:

    BUTTON_HEIGHT = 1.3
    TEXT_WIDTH = 15


class MusicVolume:

    # MainMenu
    MAIN_MENU = 1.0


class SoundVolume:

    # Buttons
    BUTTON_HOVER = 1.0
    BUTTON_CLICK = 1.0
