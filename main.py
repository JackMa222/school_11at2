import arcade
import math
import time

from CONSTANTS import *

class GameView(arcade.Window):
    """"
    Main application class.
    """
    
    def __init__(self):
        # Set up window using paretn class
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        
        self.x = 0
        
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
        
        # Finish line
        self.finish_line_list = None
        
        # Camera
        self.camera = None
        self.gui_camera = None
        
        # Map
        self.tile_map = None
        
        # Levels
        self.level = STARTING_LEVEL
        self.max_level = LEVELS
        
        # Time map is started
        self.start_time = None
        # Timer that is update in on_update 
        self.timer = 0
        
        # Boolean if map is running or not
        self.is_live = False
        
        self.timer_text = None
    
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
        
        # Check if player is 'going' in the map
        # If so update timer
        if self.is_live:
            self.timer = time.time() - self.start_time
            self.timer_text.text = f"Time: {round(self.timer, 2)}"
            self.total_timer_text.text = f"Total Time: {round(self.timer, 2)}"
            print(round(self.timer,2))
        
        if arcade.check_for_collision_with_list(self.player_sprite, self.finish_line_list):
            print("FINISH!", self.x)
            self.x += 1
            
            # End timer
            self.is_live = False
            print(self.timer)
            
            if self.level < self.max_level:
                self.level += 1
                self.setup()
            
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
            },
            "FinishLine": {
                "use_spatial_hash": True
            }
        }
        
        # Load in tile map from file (the map that the car drives on)
        # Map file needs to be in directory
        self.tile_map = arcade.load_tilemap(f"map_level_{self.level}.json", scaling=TILE_SCALING, layer_options=layer_options)
        
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
        
        # Designate Finish Line
        self.finish_line_list = self.scene["FinishLine"]
    
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
        
        self.start_time = time.time()
        self.is_live = True
        
        # Score text
        self.timer_text = arcade.Text(f"Time: {round(self.timer, 2)}", x = 16, y = 16, font_size = 36, color = arcade.color.AMARANTH_PURPLE)
        
        # Map/Level Text
        self.level_text = arcade.Text(f"Level: {self.level}", x = 16+64*6, y = 16, font_size = 36, color = arcade.color.AMARANTH_PURPLE)
        
        # Total time text
        # TODO actually have total time
        self.total_timer_text = arcade.Text(f"Total Time: {round(self.timer, 2)}", x = 16+64*11, y = 16, font_size = 36, color = arcade.color.AMARANTH_PURPLE)
        
    def on_draw(self):
        # TODO add comments
        # Clears the window with the configured background color set
        self.clear()
        
        # Set camera as the camera to be used
        self.camera.use()
        
        # Draw the scene (that was created in setup)
        self.scene.draw()
               
        # Test code for colissions
        #for sprite in self.scene["FinishLine"]:
        #    sprite.draw_hit_box(arcade.color.RED, line_thickness=2)
        
        # Set gui_camera        
        self.gui_camera.use()
        
        # Draw score, level text
        self.timer_text.draw()
        self.level_text.draw()
        self.total_timer_text.draw()
    
def main():
    # Create window object
    window = GameView()
    
    # Run setup function for window
    window.setup()
    
    # Run the game using arcade
    arcade.run()
        
if __name__ == "__main__":
    main()
        