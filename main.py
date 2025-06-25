import arcade
from arcade.gui import UIManager, UIInputText
import math
import sqlite3
import time

from CONSTANTS import *

class LeaderboardManager:
    def __init__(self, database_path="database.db"):
        self.database_path = database_path
        
    def add_entry(self, username, score):
        with sqlite3.connect(self.database_path) as db:
            # UTILSES CODE FROM 11AT1 2025
            cursor = db.cursor()
            
            cursor.execute("INSERT INTO leaderboard (score, username) VALUES (?, ?)", (score, username))
            
            cursor.execute("SELECT COUNT(*) + 1 FROM leaderboard WHERE score > ?", (score,))  
            position = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) + 1 FROM leaderboard WHERE username = ? AND score > ?", (username, score))
            personal_position = cursor.fetchone()[0]
        
        return position, personal_position
            

class Leaderboard:
    def __init__(self, database_path="database.db"):
        self.database_path = database_path
    
    def get_connection(self):
        return sqlite3.connect(self.database_path)
    
    def get_top_scores(self, username=None):
        raise NotImplementedError("Must be overrided in subclass (polymorphism)")
    
    def get_scores_list(self, scores):
        ### DEBUG TOOL
        if not scores:
            print("No scores avaliable")
        scores_list = []
        for i, (score, username) in enumerate(scores, 1):
            scores_list.append(f"#{i}: {username} ({score})")
        return scores_list
            
class GlobalLeaderboard(Leaderboard):
    def get_top_scores(self, username=None):
        with self.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT score, username FROM leaderboard ORDER BY score DESC LIMIT 5")
            return cursor.fetchall()

class PersonalLeaderboard(Leaderboard):
    def get_top_scores(self, username):
        with self.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT score, username FROM leaderboard WHERE username = ? ORDER BY score DESC LIMIT 5", (username,))
            return cursor.fetchall()

class GameView(arcade.View):
    """"
    Main application class.
    """
    
    def __init__(self):
        # Set up window using parent class
        super().__init__()
        
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
        self.total_timer = 0
        
        # Boolean if map is running or not
        self.is_live = False
        
        self.timer_text = None
        
        # TODO add user input
        self.username = "Test1"
        self.leaderboard_manager = LeaderboardManager()
        self.finish_finished = False
        
    
    def update_movement(self, delta_time):
        radians_angle = math.radians(self.player_sprite.angle)
        if self.moving_forward:
            self.player_sprite.change_x = self.player_movement_speed * math.sin(radians_angle) * delta_time
            self.player_sprite.change_y = self.player_movement_speed  * math.cos(radians_angle) * delta_time
        elif self.moving_backward:
            self.player_sprite.change_x = -self.player_movement_speed * math.sin(radians_angle) * delta_time
            self.player_sprite.change_y = -self.player_movement_speed * math.cos(radians_angle) * delta_time
        else:
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
        
    def on_update(self, delta_time):
        # Physics engine update related properties
        self.physics_engine.update()
        # Center camera to player
        self.camera.position = self.player_sprite.position
        
        # Update movement
        self.update_movement(delta_time)
        
        # Continue turning based on attributes
        # If still turning left, turn sprite left
        if self.turning_left:
            self.player_sprite.angle -= TURN_SPEED
            # Update movement to ensure moving forwards/backwards reflects the new angle
            self.update_movement(delta_time)
        
        # If still turning right, turn sprite right
        if self.turning_right:
            self.player_sprite.angle += TURN_SPEED
            # Update movement to ensure moving forwards/backwards reflects the new angle
            self.update_movement(delta_time)
        
        # Check if player is 'going' in the map
        # If so update timer
        if self.is_live:
            self.timer = time.time() - self.start_time
            self.timer_text.text = f"Time: {round(self.timer, 2)}"
            self.total_timer_text.text = f"Total Time: {round(self.total_timer + self.timer, 2)}"
        
        if arcade.check_for_collision_with_list(self.player_sprite, self.finish_line_list):
            print("FINISH!", self.x)
            self.x += 1
            
            # End timer
            if not self.finish_finished:
                self.is_live = False
                self.total_timer += self.timer
            
            if self.level < self.max_level:
                self.level += 1
                self.setup()
            elif self.level == self.max_level and self.finish_finished is False:
                self.finish_finished = True
                final_score = round(self.total_timer, 2)
                
                position, personal_position = self.leaderboard_manager.add_entry(self.username, final_score)
                finish_view = FinishView(position, personal_position)
                self.window.show_view(finish_view)
            
    def on_key_press(self, key, modifiers):
        # Resets the game/level
        if key == arcade.key.ESCAPE:
            self.setup()
            
        # Adjusts the players (the cars) movement based on keyboard input from the user    
        if key == arcade.key.W or key == arcade.key.UP:
            # Move forward in the direction the car is facing
            self.moving_forward = True
        if key == arcade.key.A or key == arcade.key.LEFT:
            # Rotate car left and update movement
            self.turning_left = True
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            # Rotate car right and update movement
            self.turning_right = True
        elif key == arcade.key.S or key == arcade.key.DOWN:
            # Move car backwards
            self.moving_backward = True
        elif key == arcade.key.SPACE:
            # Ability to increase speed on space press
            if IS_TURBO:
                self.player_movement_speed = PLAYER_TURBO_MOVEMENT_SPEED
        elif key == arcade.key.N and LEVEL_DEBUG_SKIP:
            self.is_live = False            
            if self.level < self.max_level:
                self.level += 1
                self.setup()
        elif key == arcade.key.B and LEVEL_DEBUG_SKIP:
            self.is_live = False            
            if (self.level-1) > 0:
                self.level -= 1
                self.setup()
            
    def on_key_release(self, key, modifers):
        # When keys are released the movement and/or turning also ceases
        if key == arcade.key.W or key == arcade.key.UP:
            # Stop moving forward when W or UP is released
            self.moving_forward = False
        elif key == arcade.key.S or key == arcade.key.DOWN:
            # Stop moving backwards when S or DOWN is released
            self.moving_backward = False
        elif key == arcade.key.A or key == arcade.key.LEFT:
            # Stop turning left when A or LEFT is released
            self.turning_left = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            # Stop turning right when D or RIGHT is released
            self.turning_right = False
        elif key == arcade.key.SPACE:
            # Revert player_movement speed to initial value once SPACE is released
            self.player_movement_speed = PLAYER_MOVEMENT_SPEED
            
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
        self.tile_map = arcade.load_tilemap(f"maps/map_level_{self.level}.json", scaling=TILE_SCALING, layer_options=layer_options)
        
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
        self.player_sprite.center_x = 240
        self.player_sprite.center_y = 128
        if self.level in HORIZONTAL_START_LEVELS:
            self.player_sprite.angle = 90
            self.player_sprite.center_x = 96
            self.player_sprite.center_y = 240
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
        if COLLISION_DEBUG_BOXES:
            for sprite in self.scene["Walls"]:
                sprite.draw_hit_box(arcade.color.RED, line_thickness=2)
        
        # Set gui_camera        
        self.gui_camera.use()
        
        # Draw score, level text
        self.timer_text.draw()
        self.level_text.draw()
        self.total_timer_text.draw()
        
class InstructionView(arcade.View):
    def __init__(self):
        super().__init__()
        
        x_pos = self.window.width // 2
        y_pos = self.window.height // 2
        
        self.texts = [
            arcade.Text("Racing Game (11AT2)", x_pos, y_pos, arcade.color.WHITE, font_size=50, anchor_x="center"),
            arcade.Text("Use WASD or arrow keys for movement, space to speed up (turbo),", x_pos, y_pos - 50, arcade.color.WHITE, font_size=20, anchor_x="center"),
            arcade.Text("and escape to restart the level.", x_pos, y_pos - 80, arcade.color.WHITE, font_size=20, anchor_x="center"),
            arcade.Text("There are 10 levels to complete. Click on the screen to continue.", x_pos, y_pos - 110, arcade.color.WHITE, font_size=20, anchor_x="center")
        ]
        
    
    def on_show_view(self):
        self.window.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.window.default_camera.use()
        
    def on_draw(self):
        self.clear()
        for text in self.texts:
            text.draw()
        
    def on_mouse_press(self, x, y, button, modifers):
        if self.input_box.text:
            game_view = GameView()
            game_view.username = self.input_box.text
            game_view.setup()
            self.window.show_view(game_view)
            
class FinishView(arcade.View):
    def __init__(self, position, personal_position):
        super().__init__()
        self.position = position
        self.personal_position = personal_position
        
        self.ui_manager = UIManager()
        
        x_pos = self.window.width // 2
        y_pos = self.window.height // 2
        
        self.input_box = UIInputText(x=x_pos- 200, y=y_pos - 180, width=400, height=50, font_size=25)
        self.ui_manager.add(self.input_box)
        
        self.texts = [
            arcade.Text("Game over. Well done!", x_pos, y_pos, arcade.color.WHITE, font_size=50, anchor_x="center"),
            arcade.Text(f"Global position: {self.position}", x_pos, y_pos - 50, arcade.color.WHITE, font_size=20, anchor_x="center"),
            arcade.Text(f"Personal position: {self.personal_position}", x_pos, y_pos - 80, arcade.color.WHITE, font_size=20, anchor_x="center"),
            arcade.Text("There are 10 levels to complete. Click on the screen to continue.", x_pos, y_pos - 110, arcade.color.WHITE, font_size=20, anchor_x="center")
        ]
        
    
    def on_show_view(self):
        self.window.background_color = arcade.csscolor.LIGHT_GREEN
        self.window.default_camera.use()
        self.ui_manager.enable()
        
    def on_hide_view(self):
        self.ui_manager.disable()
        
    def on_draw(self):
        self.clear()
        for text in self.texts:
            text.draw()
        self.ui_manager.draw()
        
def main():
    # Create window object
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    
    # Run setup function for window
    #start_view.setup()
    
    # Run the game using arcade
    arcade.run()
        
if __name__ == "__main__":
    main()
        