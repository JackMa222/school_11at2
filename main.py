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
            
    def setup(self):
        # Inital/reset code
        layer_options = {
            "Walls": {
                "use_spatial_hash": True
            }
        }
        
        # Load in tile map from file (the map that the car drives on)
        self.tile_map = arcade.load_tilemap("map.json", scaling=TILE_SCALING, layer_options=layer_options)
        
        # Create scene from tilemap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        
        # Add player on top sprite list and add player texture
        self.scene.add_sprite_list_after("Player", "Walls")
        self.player_texture = arcade.load_texture("Resources/Car_1_01.png")
        
        # Designate player size
        original_height = self.player_texture.height
        desired_height = 128
        scale = desired_height / original_height

        # Create/position player sprite (car)
        self.player_sprite = arcade.Sprite(self.player_texture, scale=scale)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)
    
        # Create camera
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        #self.score_text = arcade.Text(f"Score : {self.score}", x=0, y=0)
        
        # Set background color to racetrack gray
        self.background_color = arcade.types.Color(187, 187, 187, 255)
        
        # Create physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, walls=self.scene["Walls"]
        )
        
    def on_draw(self):
        # TODO add comments
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()
    
def main():
    window = GameView()
    window.setup()
    arcade.run()
        
if __name__ == "__main__":
    main()
        