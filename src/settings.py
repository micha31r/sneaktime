import pygame as pg
from os import path
from pathlib import Path

pg.init()

BASE_DIR = Path(path.dirname(__file__))
WINDOW_SIZE = W_WIDTH, W_HEIGHT = 640, 480
WORLD_SIZE = (640*4, 480*4)

rs_dir = path.join(BASE_DIR.parent.parent, "resources") # Production
rs_dir = path.join(BASE_DIR, "resources") # Development

# Kenney Audio Assets (https://kenney.nl/assets?q=audio)
# Shapeforms Audio Assets (https://shapeforms.itch.io/shapeforms-audio-free-sfx)
# Mixkit Audio Assets (https://mixkit.co/)

pg.mixer.set_num_channels(16)

sound_effects = {
	"aura": pg.mixer.Sound(rs_dir + '/sounds/aura.wav'),
	"alarm": pg.mixer.Sound(rs_dir + '/sounds/alarm.wav'),
	"start_level": pg.mixer.Sound(rs_dir + '/sounds/start_level.wav'),
	"click": pg.mixer.Sound(rs_dir + '/sounds/click.ogg'),
	"confirm": pg.mixer.Sound(rs_dir + '/sounds/confirm.ogg'),
	"fail": pg.mixer.Sound(rs_dir + '/sounds/fail.ogg'),
	"footstep": pg.mixer.Sound(rs_dir + '/sounds/footstep.ogg'),
	"impact": pg.mixer.Sound(rs_dir + '/sounds/impact.ogg'),
	"laser": pg.mixer.Sound(rs_dir + '/sounds/laser.ogg'),
	"pickup_item": pg.mixer.Sound(rs_dir + '/sounds/pickup_item.ogg'),
	"pickup_powerup": pg.mixer.Sound(rs_dir + '/sounds/pickup_powerup.wav'),
	"shoot": pg.mixer.Sound(rs_dir + '/sounds/shoot.wav'),
	"success": pg.mixer.Sound(rs_dir + '/sounds/success.ogg'),
	"explode": pg.mixer.Sound(rs_dir + '/sounds/explode.wav'),
	"splatter": pg.mixer.Sound(rs_dir + '/sounds/splatter.wav'),
	"activate_forcefield": pg.mixer.Sound(rs_dir + '/sounds/activate_forcefield.wav'),
	"show_message": pg.mixer.Sound(rs_dir + '/sounds/show_message.wav'),
}
