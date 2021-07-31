import json, math
import pygame as pg
from collision import *

from settings import *

class TiledMap:
    def __init__(self, game, path):
        self.game = game
        self.spawner_tiles = {
            "player": 49,
            "enemy": 50, 
            # Power ups
            "disguise": 41,
            "shotgun": 42, 
            "armour": 43,
            # Traps
            "laser_h": 33,
            "laser_v": 34,
        }

        self.load_tilemap(path)
        self.load_tileset()
        self.load_polygons()
        self.load_tiles()

    def load_tilemap(self, path):
        f = open(rs_dir + path)
        self.data = json.load(f)

    def load_tileset(self):
        img = pg.image.load(rs_dir + "/tilesheet.png").convert_alpha()
        img_width, img_height = img.get_size()
        tile_width, tile_height = self.data["tilewidth"], self.data["tileheight"]
        self.tileset = []
        for tile_y in range(math.floor(img_height / tile_height)):
            img_y = tile_y * tile_height
            for tile_x in range(math.floor(img_width / tile_width)):
                img_x = tile_x * tile_width
                rect = (img_x, img_y, tile_width, tile_height)
                self.tileset.append(img.subsurface(rect))

    # All polygons must be convex
    def load_polygons(self):
        v = Vector
        self.polygons = {}
        for layer in self.data["layers"]:
            if layer["type"] == "objectgroup":
                polys = []
                for obj in layer["objects"]:
                    if "polygon" in obj:
                        points = []
                        for p in obj["polygon"]:
                            points.append(v(p["x"], p["y"]))
                        polys.append(Poly(v(obj["x"], obj["y"]), points))
                if polys:
                    self.polygons[layer["name"]] = polys

    def load_tiles(self):
        self.spawners = {}
        self.tiles = []
        self.tilewidth = self.data["tilewidth"]
        self.tileheight = self.data["tileheight"]
        for layer in self.data["layers"]:
            if layer["type"] == "tilelayer":
                for chunk in layer["chunks"]:
                    cw = chunk["width"]
                    ch = chunk["height"]
                    cx = chunk["x"]
                    cy = chunk["y"]
                    tx = 0
                    ty = 0
                    for tile_id in chunk["data"]:
                        render_x = (cx + tx) * self.tilewidth 
                        render_y = (cy + ty) * self.tileheight
                        # means there is no tile
                        if tile_id != 0:
                            rect = (render_x, render_y, self.tilewidth, self.tileheight)
                            if layer["visible"]:
                                self.tiles.append({
                                    "img": self.tileset[tile_id-1], 
                                    "rect": rect,
                                    "tile_id": tile_id,
                                    "layer_name": layer["name"],
                                })
                            else:
                                for k, v in self.spawner_tiles.items():
                                    if tile_id == v:
                                        if k not in self.spawners:
                                            self.spawners[k] = []
                                        self.spawners[k].append(rect)
                        tx += 1
                        if tx == cw:
                            tx = 0
                            ty += 1

    def rect_collide(self, rect, target_layer_name=None):
        x1 = rect[0]
        y1 = rect[1]
        w1 = rect[2]
        h1 = rect[3]
        for layer in self.data["layers"]:
            if layer["type"] == "objectgroup":
                if not target_layer_name or target_layer_name == layer["name"]:
                    for obj in layer["objects"]:
                        # Check for intersection
                        x2 = obj["x"]
                        y2 = obj["y"]
                        w2 = obj["width"]
                        h2 = obj["height"]
                        if ((x1 < x2 and x1 + w1 > x2) or \
                            (x1 < x2 + w2 and x1 + w1 > x2 + w2) or \
                            (x1 > x2 and x1 + w1 < x2 + w2)) and \
                            ((y1 < y2 and y1 + h1 > y2) or \
                            (y1 < y2 + h2 and y1 + h1 > y2 + h2) or \
                            (y1 > y2 and y1 + h1 < y2 + h2)):
                            return True

    def poly_collide(self, p1, target_layer_name=None, capture_all=False):
        # Must capture all collisions for r.overlap_v to work, 
        # otherwise 'a' will tunnel into 'b' while responding collision with 'c'
        all_collisions = []
        for layer_name, items in self.polygons.items():
            if not target_layer_name or target_layer_name == layer_name:
                for p2 in items:
                    # Collision responses are only supported for convex polygons
                    r = Response()
                    if collide(p1, p2, response=r):
                        # Calculate the collision angle
                        # angle = round(math.atan2(*r.overlap_n)*180/math.pi)
                        if capture_all:
                            all_collisions.append(r.overlap_v)
                        else:
                            return r.overlap_v
        return all_collisions

    def get_tile(self, x1, y1, target_layer_name=None, capture_all=False):
        all_tiles = []
        for t in self.tiles:
            if not target_layer_name or target_layer_name == t["layer_name"]:
                x2, y2, w2, h2 = t["rect"]
                if (x1 == x2 and y1 == y2) or ((x1 > x2 and x1 < x2 + w2) and (y1 > y2 and y1 < y2 + h2)):
                    if capture_all:
                        all_tiles.append(t)
                    else:
                        return t
        return all_tiles

    def draw(self, screen):
        for t in self.tiles:
            rect = t["rect"]
            # Only render tile if it's within the viewport
            if (rect[0] + rect[2] > self.game.camera.pos.x and rect[0] < self.game.camera.pos.x + WORLD_SIZE[0]) \
                and (rect[1] + rect[3] > self.game.camera.pos.y and rect[1] < self.game.camera.pos.y + WORLD_SIZE[1]):
                screen.blit(t["img"], rect)



