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
    
    def update_movement(self):
        radians_angle = math.radians(self.player_sprite.angle)
        if self.moving_forward:
            self.player_sprite.change_x = self.player_movement_speed * math.sin(radians_angle)
            self.player_sprite.change_y = self.player_movement_speed * math.cos(radians_angle)
        elif self.moving_backward:
            self.player_sprite.change_x = -self.player_movement_speed * math.sin(radians_angle)
            self.player_sprite.change_y = -self.player_movement_speed * math.cos(radians_angle)
        else:
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
        
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
            
    def on_key_press(self, key, modifiers):
        # Resets the game/level
        if key == arcade.key.ESCAPE:
            self.setup()
            
        # Adjusts the players (the cars) movement based on keyboard input from the user    
        if key == arcade.key.W or key == arcade.key.UP:
            # Move forward in the direction the car is facing
            self.moving_forward = True
            self.update_movement()
        if key == arcade.key.A or key == arcade.key.LEFT:
            # Rotate car left and update movement
            self.turning_left = True
            self.update_movement()
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            # Rotate car right and update movement
            self.turning_right = True
            self.update_movement()
        elif key == arcade.key.S or key == arcade.key.DOWN:
            # Move car backwards
            self.moving_backward = True
            self.update_movement()
        elif key == arcade.key.SPACE:
            # Ability to increase speed on space press
            if IS_TURBO:
                self.player_movement_speed = PLAYER_TURBO_MOVEMENT_SPEED
            self.update_movement()
            
    def on_key_release(self, key, modifers):
        # When keys are released the movement and/or turning also ceases
        if key == arcade.key.W or key == arcade.key.UP:
            # Stop moving forward when W or UP is released
            self.moving_forward = False
            self.update_movement()
        elif key == arcade.key.S or key == arcade.key.DOWN:
            # Stop moving backwards when S or DOWN is released
            self.moving_backward = False
            self.update_movement()
        elif key == arcade.key.A or key == arcade.key.LEFT:
            # Stop turning left when A or LEFT is released
            self.turning_left = False
            self.update_movement()
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            # Stop turning right when D or RIGHT is released
            self.turning_right = False
            self.update_movement()
        elif key == arcade.key.SPACE:
            # Revert player_movement speed to initial value once SPACE is released
            self.player_movement_speed = PLAYER_MOVEMENT_SPEED
            self.update_movement()