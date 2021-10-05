import pygame as pg
import math

from settings import *

class TutorialManager:
    def __init__(self, game):
        self.game = game
        self.timer = 1
        self.message = None
        self.tracker_counter = 0
        self.tracker_radius = 60
        self.tracker_index = 0

    def update(self, dt):
        keys = pg.key.get_pressed()
        
        # Tutorial
        if not self.game.player.completed_tutorial:
            self.timer -= dt
            if self.timer < 0:
                trackers = self.game.level_manager.current_map().trackers["tracker1"]
                if trackers:
                    self.tracker_counter += 10 * dt
                    tracker = trackers[self.tracker_index]
                    self.game.camera.track(tracker["rect"])
                    if self.message:
                        if self.message.retract:
                            if self.message.complete:
                                # Track the next object or set the tutorial as complete
                                self.message = None
                                if self.tracker_index < len(trackers)-1:
                                    self.tracker_index += 1
                                else:
                                    self.game.player.completed_tutorial = True
                                    self.game.interface_manager.message("You are on your own, good luck!", typing_effect=False)
                        elif keys[pg.K_SPACE] and self.message.text.index == len(self.message.text.text):
                            # Dismiss tutorial message
                            sound_effects["confirm"].play()
                            self.message.retract = True
                            self.message.retract_delay = -1
                    else:
                        # Show tutorial message if the camera has (almost) stopped moving
                        if self.game.camera.vel.x < 0.1 and self.game.camera.vel.y < 0.1:
                            messages = self.game.level_manager.tutorial_messages
                            for message in messages:
                                if tracker["spawner_id"] in message["tile_triggers"]:
                                    self.message = self.game.interface_manager.message(message["message"], False, typing_effect=False)
                                    break
                else:
                    self.game.player.completed_tutorial = True

    def draw(self, screen):
        # Draw tracker highlighter
        if not self.game.player.completed_tutorial:
            tracker = self.game.level_manager.current_map().trackers["tracker1"][self.tracker_index]
            change = (math.sin(self.tracker_counter) + 1) * 10
            _map = self.game.level_manager.current_map()
            pos = pg.Vector2(tracker["rect"][0] + _map.tilewidth/2, tracker["rect"][1] + _map.tileheight/2)
            pg.draw.circle(screen, self.game.get_color("primary"), pos, self.tracker_radius + change, 2)



