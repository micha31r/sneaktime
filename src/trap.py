import random, math
import pygame as pg
from collision import *

from settings import *
from scripts import *

class TrapManager:
    def __init__(self, game):
        self.game = game
        self.traps = []

    def add(self, t):
        self.traps.append(t)

    def update(self, dt):
        for t in self.traps:
            t.update(dt)

    def draw(self, screen):
        for t in self.traps:
            t.draw(screen)


class LaserTrap:
    end_tile_id = 17
    end_tile_layer_name = "Tile Layer 3"

    def __init__(self, game, x, y, direction):
        self.game = game
        self.pos = pg.Vector2(x, y)
        self.end_pos = pg.Vector2()
        self.direction = direction
        self.activated = False
        self.delay = random.randint(1,3)
        self.delay_timer = 0
        self.duration = random.randint(1,3)
        self.duration_timer = 0

        self.get_end_pos()

    def get_end_pos(self):
        game_map = self.game.level_manager.current_map()
        tw = game_map.tilewidth
        th = game_map.tileheight
        dx = 0
        dy = 0
        for i in range(32):
            if self.direction == "horizontal":
                dx += tw
            else:
                dy += th
            tile = game_map.get_tile(self.pos.x+dx, self.pos.y+dy, self.end_tile_layer_name) or game_map.get_tile(self.pos.x-dx, self.pos.y-dy, "Tile Layer 3")
            if tile and tile["tile_id"] == self.end_tile_id:
                v = Vector
                # Center pos
                self.pos = center(*self.pos, tw, th, False)
                self.end_pos = center(*tile["rect"], False)
                dv = self.end_pos - self.pos
                points = [
                    v(0,-1),
                    v(dv.x,-1),
                    v(dv.x,1),
                    v(0,1)
                ]
                if self.direction == "vertical":
                    points = [
                        v(-1,0),
                        v(-1,dv.y),
                        v(1,dv.y),
                        v(1,0)
                    ]
                self.collision_obj = Poly(self.pos, points)
                break

    def update(self, dt):
        if self.activated:
            self.duration_timer -= dt
            if self.duration_timer < 0:
                self.activated = False
                self.duration_timer = self.duration
            if collide(self.collision_obj, self.game.player.collision_obj):
                print("Laser collision")
        else:
            self.delay_timer -= dt
            if self.delay_timer < 0:
                self.activated = True
                self.delay_timer = self.delay

    def draw(self, screen):
        if self.activated:
            pg.draw.line(screen, (0,0,0), self.pos, self.end_pos, 3)


class NinjaStarTrap(LaserTrap):
    end_tile_id = 28
    end_tile_layer_name = "Tile Layer 3"

    def __init__(self, game, x, y, direction):
        super().__init__(game, x, y, direction)
        # Calculate the distance between start pos and end pos
        if self.direction == "horizontal":
            self.distance = (self.end_pos - self.pos).x
        else:
            self.distance = (self.end_pos - self.pos).y

        self.angle = 0 # degrees
        self.half_cycle_time = abs(3/self.distance) * 200 # The n of seconds it takes to complete half a cycle
        self.movement_counter = 0

        self.img = pg.image.load(rs_dir + "/traps/ninja_star.png").convert_alpha()
        self.img_w, self.img_h = self.img.get_size()

        v = Vector
        self.collision_obj = Circle(v(*self.pos), self.img_w/2)

    def update(self, dt):
        # Calculate displacement based on sin(movement_counter)
        self.movement_counter += self.half_cycle_time * dt
        self.displacement = (math.sin(self.movement_counter) + 1) * self.distance / 2
        
        # Set the render position to be origin + displacement
        self.render_pos = self.pos.copy()
        if self.direction == "horizontal":
            self.render_pos.x += self.displacement
        else:
            self.render_pos.y += self.displacement

        # Update collision object's position
        self.collision_obj.pos = self.render_pos

        self.angle -= 360 * dt
        if self.angle > 360:
            self.angle = 0

        if collide(self.collision_obj, self.game.player.collision_obj):
            print("Laser collision")

    def draw(self, screen):
        rotated_img = pg.transform.rotate(self.img, self.angle)
        new_rect = rotated_img.get_rect(center=self.render_pos)
        screen.blit(rotated_img, new_rect)
