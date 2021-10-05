
"""
-------------------------------------------------
    Project: Sneaktime
    Standard: 91906 (AS3.7)
    School: Tauranga Boys' College
    Author: Michael Ren
    Date: 05 OCT 2021
    Python: 3.9.6
    License: MIT
-------------------------------------------------
"""

import pygame as pg
from collision import *
from settings import *
from scripts import *

class ItemManager:
    def __init__(self, game):
        self.game = game
        self.items = []

    def add(self, item):
        self.items.append(item)

    def update(self, dt):
        for i, item in reversed(list(enumerate(self.items))):
            item.update(dt)
            # Activate item and add to player's inventory after collision
            if collide(item.collision_obj, self.game.player.collision_obj):
                item.activated = True
                if item.type == "item":
                    sound_effects["pickup_item"].play()
                    self.game.player.inventory.add_item(item)
                    current = len(self.game.player.inventory.get_item("key")) # The amount the player has
                    total = self.game.level_manager.current_level_obj()["items"]["key"] # The total amount required
                    self.game.interface_manager.message(f"Collected {item.name} ({current}/{total})", typing_effect=False)
                    color = self.game.get_color("third")
                else:
                    sound_effects["pickup_powerup"].play()
                    self.game.player.inventory.add_powerup(item)
                    self.game.interface_manager.message(f"Applying powerup '{item.name}'", typing_effect=False)
                    color = self.game.get_color("primary")
                self.game.particle_manager.generate(*self.game.player.c_pos, color, (10,20))
                del self.items[i]

    def reset(self):
        self.items = []

    def draw(self, screen):
        for item in self.items:
            item.draw(screen)


class DisguisePowerUp:
    def __init__(self, game, x, y):
        self.game = game
        self.type = "powerup"
        self.pos = pg.Vector2(x, y)
        self.angle = 0 # in degrees
        self.name = "disguise"
        self.timer = 10
        self.activated = False

        self.load_sprite()
        self.img_w, self.img_h = self.img.get_size()

        v = Vector
        self.collision_obj = Poly(
            v(*self.pos),
            [v(0,0), v(self.img_w,0), v(self.img_w,self.img_h), v(0,self.img_h)]
        )

    def load_sprite(self):
        self.img = pg.image.load(self.game.get_themed_path("powerups", "disguise.png")).convert_alpha()

    def is_expired(self):
        if self.timer < 0:
            self.game.particle_manager.generate(*self.game.player.c_pos, self.game.get_color("primary"), (10,20))
            return True

    def update(self, dt):
        if self.activated:
            self.timer -= dt
        else:
            self.angle += 180 * dt
            if self.angle > 360:
                self.angle = 0

    def draw_status(self, screen, index):
        line_width = 500
        gap = 20
        y = 20 + index*(self.img_h/2 + 10) # This assumes all images are the same height
        ww, wh = self.game.window.get_size()
        scaled_img = pg.transform.scale(self.img, (int(self.img_w/2), int(self.img_h/2)))
        iw, ih = scaled_img.get_size()
        pos = pg.Vector2((ww - line_width - gap - iw) / 2, y) + self.game.camera.pos
        screen.blit(scaled_img, pos)
        pos.x += iw + gap
        pos.y += ih/2
        rect = (pos.x, pos.y - 2, line_width * self.timer / 10, 4)
        pg.draw.rect(screen, self.game.get_color("primary"), rect,
            border_top_left_radius=5,
            border_top_right_radius=5,
            border_bottom_left_radius=5,
            border_bottom_right_radius=5
        )

    def draw(self, screen):
        rotated_img = pg.transform.rotate(self.img, self.angle)
        new_rect = rotated_img.get_rect(center=center(*self.pos, self.img_w, self.img_h))
        screen.blit(rotated_img, new_rect)


class ShotgunPowerUp(DisguisePowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "shotgun"
        self.img_w, self.img_h = self.img.get_size()
        v = Vector
        self.collision_obj = Poly(
            v(*self.pos),
            [v(0,0), v(self.img_w,0), v(self.img_w,self.img_h), v(0,self.img_h)]
        )

    def load_sprite(self):
        self.img = pg.image.load(self.game.get_themed_path("powerups", "shotgun.png")).convert_alpha()
        

class ArmourPowerUp(DisguisePowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "armour"
        self.img_w, self.img_h = self.img.get_size()
        v = Vector
        self.collision_obj = Poly(
            v(*self.pos),
            [v(0,0), v(self.img_w,0), v(self.img_w,self.img_h), v(0,self.img_h)]
        )

    def load_sprite(self):
        self.img = pg.image.load(self.game.get_themed_path("powerups", "armour.png")).convert_alpha()

    def draw(self, screen):
        super().draw(screen)


class KeyItem(DisguisePowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.type = "item"
        self.name = "key"
        self.img_w, self.img_h = self.img.get_size()
        v = Vector
        self.collision_obj = Poly(
            v(*self.pos),
            [v(0,0), v(self.img_w,0), v(self.img_w,self.img_h), v(0,self.img_h)]
        )

    def load_sprite(self):
        self.img = pg.image.load(self.game.get_themed_path("items", "key.png")).convert_alpha()





