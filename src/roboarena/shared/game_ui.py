from typing import TYPE_CHECKING

from pygame import Surface, transform

from roboarena.shared.rendering.util import size_from_texture_height
from roboarena.shared.util import load_graphic
from roboarena.shared.utils.vector import Vector
from roboarena.shared.weapon import Weapon

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx


HEART_FULL_TEXTURE = load_graphic("game_ui/healthbar/heart-full.png")

HEART_EMPTY_TEXTURE = load_graphic("game_ui/healthbar/heart-empty.png")

HEART_HALF_TEXTURE = load_graphic("game_ui/healthbar/heart-half.png")

HEALTHBAR_BACKGROUND_TEXTURE = load_graphic(
    "game_ui/healthbar/healthbar-background.png"
)

WEAPON_UI_BACKGROUND_TEXTURE = load_graphic("game_ui/weaponui/weaponui-background.png")


class Healthbar:

    heart_full_texture: Surface = HEART_FULL_TEXTURE
    heart_empty_texture: Surface = HEART_EMPTY_TEXTURE
    heart_half_texture: Surface = HEART_HALF_TEXTURE
    background_texture: Surface = HEALTHBAR_BACKGROUND_TEXTURE

    max_health: int
    texture: Surface

    def __init__(self, max_health: int) -> None:
        self.max_health = max_health
        self.texture = self.render_healthbar(max_health)

    def render_healthbar(self, health: int) -> Surface:
        healthbar = self.background_texture.copy()
        for heart in range(0, self.max_health):
            if health >= 2:
                healthbar.blit(self.heart_full_texture, (12 + heart * 50, 13))
                health -= 2
            elif health == 1:
                healthbar.blit(self.heart_half_texture, (12 + heart * 50, 13))
                health -= 1
            else:
                healthbar.blit(self.heart_empty_texture, (12 + heart * 50, 13))
        return healthbar

    def update_healthbar(self, health: int) -> None:
        self.texture = self.render_healthbar(health)


class WeaponUI:

    background_texture = WEAPON_UI_BACKGROUND_TEXTURE
    texture: Surface

    def __init__(self, weapon: Weapon) -> None:
        self.texture = self.render_weapon_ui(weapon)

    def render_weapon_ui(self, weapon: Weapon) -> Surface:
        weapon_ui = self.background_texture.copy()
        scaled_weapon_texture = transform.scale(
            weapon.texture, (weapon_ui.get_height() * 0.6, weapon_ui.get_height() * 0.6)
        )
        weapon_pos = (
            Vector.from_tuple(weapon_ui.get_size()) / 2
            - Vector.from_tuple(scaled_weapon_texture.get_size()) / 2
        )

        weapon_ui.blit(scaled_weapon_texture, weapon_pos.to_tuple())
        return weapon_ui

    def update_weapon(self, weapon: Weapon) -> None:
        self.texture = self.render_weapon_ui(weapon)


class GameUI:

    healthbar: Healthbar
    weapon_ui: WeaponUI

    def __init__(self, current_weapon: Weapon, current_health: int) -> None:
        self.healthbar = Healthbar(current_health)
        self.weapon_ui = WeaponUI(current_weapon)

    def texture_size(self, texture: Surface) -> Vector[float]:
        """In game units"""
        return size_from_texture_height(texture, height=1.5)

    def render(self, ctx: "RenderCtx") -> None:
        scaled_healthbar = ctx.scale_gu(
            self.healthbar.texture, self.texture_size(self.healthbar.texture)
        )
        weapon_ui_scaled = ctx.scale_gu(
            self.weapon_ui.texture, self.texture_size(self.weapon_ui.texture)
        )
        weapon_ui_pos_px = Vector(
            ctx.screen_size_px.x - weapon_ui_scaled.get_width() - 10, 10
        )
        ctx.screen.blit(scaled_healthbar, (10, 10))
        ctx.screen.blit(weapon_ui_scaled, weapon_ui_pos_px.to_tuple())

    def update_health(self, health: int) -> None:
        self.healthbar.update_healthbar(health)

    def update_weapon(self, weapon: Weapon) -> None:
        self.weapon_ui.update_weapon(weapon)
