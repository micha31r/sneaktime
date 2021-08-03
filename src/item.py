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
                    self.game.player.inventory.add_item(item)
                    self.game.interface_manager.message(f"Collected {item.name}", typing_effect=False)
                else:
                    self.game.player.inventory.add_powerup(item)
                    self.game.interface_manager.message(f"Applying powerup '{item.name}'", typing_effect=False)
                self.game.particle_manager.generate(*self.game.player.c_pos, (128,35,255), (10,20))
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

        self.img = pg.image.load(rs_dir + "/powerups/disguise.png").convert_alpha()
        self.img_w, self.img_h = self.img.get_size()

        v = Vector
        self.collision_obj = Poly(
            v(*self.pos),
            [v(0,0), v(self.img_w,0), v(self.img_w,self.img_h), v(0,self.img_h)]
        )

    def is_expired(self):
        if self.timer < 0:
            self.game.particle_manager.generate(*self.game.player.c_pos, (128,35,255), (10,20))
            return True

    def update(self, dt):
        if self.activated:
            self.timer -= dt
        else:
            self.angle += 180 * dt
            if self.angle > 360:
                self.angle = 0

    def draw(self, screen):
        rotated_img = pg.transform.rotate(self.img, self.angle)
        new_rect = rotated_img.get_rect(center=center(*self.pos, self.img_w, self.img_h))
        screen.blit(rotated_img, new_rect)


class ShotgunPowerUp(DisguisePowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "shotgun"
        self.img = pg.image.load(rs_dir + "/powerups/shotgun.png").convert_alpha()
        self.img_w, self.img_h = self.img.get_size()
        v = Vector
        self.collision_obj = Poly(
            v(*self.pos),
            [v(0,0), v(self.img_w,0), v(self.img_w,self.img_h), v(0,self.img_h)]
        )
        

class ArmourPowerUp(DisguisePowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "armour"
        self.img = pg.image.load(rs_dir + "/powerups/armour.png").convert_alpha()
        self.img_w, self.img_h = self.img.get_size()
        v = Vector
        self.collision_obj = Poly(
            v(*self.pos),
            [v(0,0), v(self.img_w,0), v(self.img_w,self.img_h), v(0,self.img_h)]
        )

    def draw(self, screen):
        super().draw(screen)


class KeyItem(DisguisePowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.type = "item"
        self.name = "key"
        self.img = pg.image.load(rs_dir + "/items/key.png").convert_alpha()
        self.img_w, self.img_h = self.img.get_size()
        v = Vector
        self.collision_obj = Poly(
            v(*self.pos),
            [v(0,0), v(self.img_w,0), v(self.img_w,self.img_h), v(0,self.img_h)]
        )




