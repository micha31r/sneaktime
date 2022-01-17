
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

class InventoryManager:
    def __init__(self, game):
        self.game = game
        self.items = []
        self.powerups = []

    def add_item(self, item):
        if self.game.player.alive:
            self.items.append(item)

    def add_powerup(self, p):
        if self.game.player.alive:
            self.powerups.append(p)
            self.game.player.powerup_count += 1

    def has_item(self, name):
        for item in self.items:
            if item.name == name:
                return True

    def has_powerup(self, name):
        for p in self.powerups:
            if p.name == name:
                return True

    def get_item(self, name):
        results = []
        for item in self.items:
            if item.name == name:
                results.append(item)
        return results

    def get_powerup(self, name):
        results = []
        for p in self.powerups:
            if p.name == name:
                results.append(p)
        return results

    def update(self, dt):
        for i, p in reversed(list(enumerate(self.powerups))):
            p.update(dt)
            if p.is_expired():
                del self.powerups[i]

    def draw(self, screen):
        for i, p in enumerate(self.powerups):
            p.draw_status(screen, i)
