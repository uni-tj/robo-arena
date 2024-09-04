from typing import TYPE_CHECKING

from pygame import Surface, transform

from roboarena.shared.constants import GameUIConstants, Graphics, TextureSize
from roboarena.shared.entity import SharedWeapon
from roboarena.shared.rendering.util import size_from_texture_height
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx


class Healthbar:
    """
    Healthbar renderer

    Exposes texture, which is the currently computed texture. This value is updated
    using `update_healthbar` and `render_healthbar` by the respective entity.
    """

    heart_full_texture: Surface = Graphics.HEART_FULL
    heart_empty_texture: Surface = Graphics.HEART_EMPTY
    heart_half_texture: Surface = Graphics.HEART_HALF
    background_texture: Surface = Graphics.HEALTHBAR_BACKGROUND

    max_health: int
    texture: Surface

    def __init__(self, max_health: int) -> None:
        self.max_health = max_health
        self.texture = self.render_healthbar(max_health)

    def render_healthbar(self, health: int) -> Surface:
        healthbar = self.background_texture.copy()
        for heart in range(0, self.max_health):
            if health >= 2:
                healthbar.blit(
                    self.heart_full_texture,
                    (
                        GameUIConstants.HEART_OFFSET
                        + heart * GameUIConstants.HEART_SPACING,
                        GameUIConstants.HEART_Y,
                    ),
                )
                health -= 2
            elif health == 1:
                healthbar.blit(
                    self.heart_half_texture,
                    (
                        GameUIConstants.HEART_OFFSET
                        + heart * GameUIConstants.HEART_SPACING,
                        GameUIConstants.HEART_Y,
                    ),
                )
                health -= 1
            else:
                healthbar.blit(
                    self.heart_empty_texture,
                    (
                        GameUIConstants.HEART_OFFSET
                        + heart * GameUIConstants.HEART_SPACING,
                        GameUIConstants.HEART_Y,
                    ),
                )
        return healthbar

    def update_healthbar(self, health: int) -> None:
        self.texture = self.render_healthbar(health)


class WeaponUI:
    """
    Weapon renderer

    Exposes texture, which is the currently computed texture. This value is updated
    using `update_weapon` and `render_weapon_ui` by the respective entity.
    """

    background_texture = Graphics.WEAPON_UI_BACKGROUND
    texture: Surface

    def __init__(self, weapon: SharedWeapon) -> None:
        self.texture = self.render_weapon_ui(weapon)

    def render_weapon_ui(self, weapon: SharedWeapon) -> Surface:
        weapon_ui = self.background_texture.copy()
        scaled_weapon_texture = transform.scale(
            weapon.texture,
            (
                weapon_ui.get_height() * TextureSize.WEAPON_HEIGHT,
                weapon_ui.get_height() * TextureSize.WEAPON_HEIGHT,
            ),
        )
        weapon_pos = (
            Vector.from_tuple(weapon_ui.get_size()) / 2
            - Vector.from_tuple(scaled_weapon_texture.get_size()) / 2
        )

        weapon_ui.blit(scaled_weapon_texture, weapon_pos.to_tuple())
        return weapon_ui

    def update_weapon(self, weapon: SharedWeapon) -> None:
        self.texture = self.render_weapon_ui(weapon)


class GameUI:
    """Game UI renderer"""

    healthbar: Healthbar
    weapon_ui: WeaponUI

    def __init__(self, current_weapon: SharedWeapon, current_health: int) -> None:
        self.healthbar = Healthbar(current_health)
        self.weapon_ui = WeaponUI(current_weapon)

    def texture_size(self, texture: Surface) -> Vector[float]:
        """In game units"""
        return size_from_texture_height(texture, height=TextureSize.GAME_UI_HEIGHT)

    def render(self, ctx: "RenderCtx") -> None:
        scaled_healthbar = ctx.scale_gu(
            self.healthbar.texture, self.texture_size(self.healthbar.texture)
        )
        weapon_ui_scaled = ctx.scale_gu(
            self.weapon_ui.texture, self.texture_size(self.weapon_ui.texture)
        )
        weapon_ui_pos_px = Vector(
            ctx.screen_size_px.x
            - weapon_ui_scaled.get_width()
            - GameUIConstants.WEAPON_UI_OFFSET,
            GameUIConstants.WEAPON_UI_OFFSET,
        )
        ctx.screen.blit(scaled_healthbar, GameUIConstants.HEALTHBAR_POS)
        ctx.screen.blit(weapon_ui_scaled, weapon_ui_pos_px.to_tuple())

    def update_health(self, health: int) -> None:
        self.healthbar.update_healthbar(health)

    def update_weapon(self, weapon: SharedWeapon) -> None:
        self.weapon_ui.update_weapon(weapon)
