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
        self.turning_right = False
        
        # Camera
        self.camera = None
        self.gui_camera = None
        
        # Map
        self.tile_map = None
        
    def on_update(self, delta_time):
        # Physics engine update related properties
        self.physics_engine.update()
        # Center camera to player
        self.camera.position = self.player_sprite.position
        
        # Continue turning based on attributes
        # If still turning left, turn sprite left
        if self.turning_left:
            self.player_sprite.angle -= TURN_SPEED
            # Update movement to ensure moving forwards/backwards reflects the new angle
            self.update_movement()
        
        # If still turning right, turn sprite right
        if self.turning_right:
            self.player_sprite.angle += TURN_SPEED
            # Update movement to ensure moving forwards/backwards reflects the new angle
            self.update_movement()