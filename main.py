import arcade
import math

from CONSTANTS import *

class GameView(arcade.Window):
    """"
    Main application class.
    """
    
    def __init__(self):
        # Set up window using paretn class
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        
        # Set up class variables
        # Player
        self.player_texture = None
        self.player_sprite = None
        
        # Player Movement
        self.player_movement_speed = PLAYER_MOVEMENT_SPEED
        self.moving_forward = False
        self.moving_backward = False
        self.turning_left = False
        self.turning_right
        
        # Camera
        self.camera = None
        self.gui_camera = None
        
        # Map
        self.tile_map = None