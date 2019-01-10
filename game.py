#!/usr/bin/python3
# -*- coding: utf-8 -*-   

"""
Swift Driver powered by Arcade.
Drive the car and collect coins while avoiding pedestrians.
Author: Michał Ptak
"""

import random
import arcade
import os

ENEMY_SPRITE_SIZE = 80
SPRITE_SCALING = 1.3
SPRITE_SCALING_COIN = 0.5

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600

# How many pixels to keep as a minimum margin between the car
# and the edge of the screen.
VIEWPORT_MARGIN = 800

MOVEMENT_SPEED = 5

# How long will the game be in term screen length.
GAME_LENGHT = 20

# These numbers represent "states" that the game can be in.
INSTRUCTIONS_PAGE = 0
GAME_RUNNING = 1
GAME_OVER = 2
GAME_FINISHED = 3

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """ Initializer """
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Background image will be stored in this variable
        self.background = None
        self.finishingLine = None
        self.finishBlock = None

        # Start 'state' will be showing the first page of instructions.
        self.current_state = INSTRUCTIONS_PAGE

        # Sprite lists
        self.player_list = None
        self.enemy_list = None
        self.coin_list = None
        self.wall_list = None

        # Don't show the mouse cursor
        self.set_mouse_visible(False)
        
        # Set up the player
        self.score = 0
        self.player_sprite = None
        self.physics_engine = None
        self.view_bottom = 0
        self.view_left = 0

        # Instruction screens
        self.instructions = []
        texture = arcade.load_texture("images/instructions.png")
        self.instructions.append(texture)

        # Sounds
        self.soundtrack = arcade.load_sound("sounds/8bitHeatleyBros.mp3")
        self.pedestrianHit = arcade.load_sound("sounds/ouch.mp3")
        self.coinScored = arcade.load_sound("sounds/scored.mp3")
        self.gameFinished = arcade.load_sound("sounds/won.wav")
        
    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite("images/car.png", SPRITE_SCALING)
        self.player_sprite.center_x = 74
        self.player_sprite.center_y = 270
        self.player_list.append(self.player_sprite)

        # Set up row of crates at the top
        for x in range(0, SCREEN_WIDTH * GAME_LENGHT, 65): 
            # Create the box instance   
            wall = arcade.Sprite("images/boxCrate_double.png", SPRITE_SCALING_COIN)

            # Position the box
            wall.center_x = x
            wall.center_y = SCREEN_HEIGHT - SCREEN_HEIGHT / 10

            # Add the box to the list
            self.wall_list.append(wall)

        # Set up the finish blockage
        self.finishBlockage = arcade.Sprite("images/finishBlock.png")
        self.finishBlockage.center_x = GAME_LENGHT * SCREEN_WIDTH + SCREEN_WIDTH // 7
        self.finishBlockage.center_y = SCREEN_HEIGHT // 2

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Load the background image. Do this in the setup so we don't keep reloading it all the time.
        # Image from:
        self.background = arcade.load_texture("images/way.png")
        self.finishingLine = arcade.load_texture("images/finishingLine.png")
        self.finishBlock = arcade.load_texture("images/finishBlock.png")

        # Set up coins randomly on the road.
        for k in range(GAME_LENGHT * 3):
            # Create the coin instance
            coin = arcade.Sprite("images/pwszCoin.png", SPRITE_SCALING_COIN)

            # Boolean variable if we successfully placed the coin.
            coin_placed_successfully = False

            while not coin_placed_successfully:
                # Position the coin
                coin.center_x = random.randrange(SCREEN_WIDTH, SCREEN_WIDTH * GAME_LENGHT)
                coin.center_y = random.randrange(60, SCREEN_HEIGHT - 130)

                # See if the coin is hitting another coin
                coin_hit_list = arcade.check_for_collision_with_list(coin, self.coin_list)

                if len(coin_hit_list) == 0:
                    coin_placed_successfully = True

            # Add the coin to the list
            self.coin_list.append(coin)

        # Create 'enemies' strolling on the road.
        for k in range(1, GAME_LENGHT+1):
            # Create the enemy instance
            enemy = arcade.Sprite("images/oldMan.png")

            # Position the enemy
            enemy.bottom = random.randrange(SCREEN_HEIGHT * 0.1, SCREEN_HEIGHT * 0.7)
            enemy.left = SCREEN_WIDTH * k

            # Set boundaries on the left/right the enemy can't cross.
            enemy.boundary_top = enemy.bottom + ENEMY_SPRITE_SIZE * 2
            enemy.boundary_bottom = enemy.bottom
            enemy.change_y = 1

            # Add the enemy to the list
            self.enemy_list.append(enemy)


        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

    def draw_instructions_page(self, page_number):
        """ 
        Draw an instruction page. Load the page as an image. 
        """
        page_texture = self.instructions[page_number]
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      page_texture.width,
                                      page_texture.height, page_texture, 0)

    def draw_game_over(self):
        """
        Draw "Game over" across the screen.
        """
        output = "Game Over"
        arcade.draw_text(output, self.view_left + 350, 440, arcade.color.WHITE, 54)

        output = "Press ENTER or SPACE to restart"
        arcade.draw_text(output, self.view_left + 300, 250, arcade.color.WHITE, 24)

    def draw_game_finished(self):
        """
        Draw "Congratulations" across the screen.
        """
        output = "Congratulations"
        arcade.draw_text(output, self.view_left + 300, 440, arcade.color.WHITE, 54)

        output = f"You scored: {self.score} points!"
        arcade.draw_text(output, self.view_left + 320, 340, arcade.color.WHITE, 34)

        output = "Press ENTER or SPACE to play again"
        arcade.draw_text(output, self.view_left + 290, 250, arcade.color.WHITE, 24)


    def draw_game(self):
        """
        Draw all the sprites, along with the score.
        """
        # Draw the background texture
        for k in range(172, SCREEN_WIDTH * GAME_LENGHT, 344):
            arcade.draw_texture_rectangle(k, SCREEN_HEIGHT // 2,
                                      344, SCREEN_HEIGHT, 
                                      self.background)

        # Draw the finishing line texture
        arcade.draw_texture_rectangle(GAME_LENGHT * SCREEN_WIDTH, SCREEN_HEIGHT // 2,
                                    344, SCREEN_HEIGHT, self.finishingLine)
        
        # Draw the finish blockage
        #arcade.draw_texture_rectangle(GAME_LENGHT * SCREEN_WIDTH + SCREEN_WIDTH // 7, 
         #                           SCREEN_HEIGHT // 2, 5, 
          #                          SCREEN_HEIGHT, self.finishBlock)

        # Draw all the sprites.
        self.player_list.draw()
        self.enemy_list.draw()
        #self.wall_list.draw()
        self.coin_list.draw()

        # Render the text
        arcade.draw_text(f"Score: {self.score}", self.view_left + 10, 15, arcade.color.WHITE, 14)

    def on_draw(self):
        """ Render the screen. """

        # This command has to happen before we start drawing
        arcade.start_render()

        if self.current_state == INSTRUCTIONS_PAGE:
            self.draw_instructions_page(0)
        elif self.current_state == GAME_RUNNING:
            self.draw_game()
        elif self.current_state == GAME_FINISHED:
            self.draw_game()
            self.draw_game_finished()
        else:
            self.draw_game()
            self.draw_game_over()

    def on_key_press(self, key, modifiers):
        """ Called whenever a key is pressed. """

        # Change states as needed.
        if self.current_state == INSTRUCTIONS_PAGE:
            if key == arcade.key.ENTER or key == arcade.key.SPACE:
                # Start the game
                self.setup()
                self.current_state = GAME_RUNNING
                # Play the soundtrack
                arcade.play_sound(self.soundtrack)
                    
        elif self.current_state == GAME_RUNNING:
            if key == arcade.key.UP:
                self.player_sprite.change_y = MOVEMENT_SPEED
            elif key == arcade.key.DOWN:
                self.player_sprite.change_y = -MOVEMENT_SPEED

        elif self.current_state == GAME_OVER or self.current_state == GAME_FINISHED:
            if key == arcade.key.ENTER or key == arcade.key.SPACE:
                # Restart the game.
                self.setup()
                self.current_state = GAME_RUNNING
                arcade.set_viewport(self.view_left,
                                    SCREEN_WIDTH + self.view_left,
                                    self.view_bottom,
                                    SCREEN_HEIGHT + self.view_bottom)

    def on_key_release(self, key, modifiers):
        """ Called when the user releases a key. """

        if self.current_state == GAME_RUNNING:
            if key == arcade.key.UP or key == arcade.key.DOWN:
                self.player_sprite.change_y = 0
            elif key == arcade.key.E:
                self.player_sprite.change_x = MOVEMENT_SPEED
                

    def update(self, delta_time):
        """ Movement and game logic """

        # Only move and do things if the game is running.
        if self.current_state == GAME_RUNNING:

            # Call update on the coin sprites
            self.coin_list.update()

            # Generate a list of all sprites that collided with the player.
            hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

            # Loop through each colliding sprite, remove it, and add to the score.
            for coin in hit_list:
                coin.kill()
                self.score += 1
                # Play the sound of picked up coin
                arcade.play_sound(self.coinScored)

            # --- Manage Scrolling ---

            # Track if we need to change the viewport
            changed = False

            # Scroll right
            right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN
            if self.player_sprite.right > right_bndry and \
            self.player_sprite.right < SCREEN_WIDTH * GAME_LENGHT - SCREEN_WIDTH // 1.6:
                self.view_left += self.player_sprite.right - right_bndry
                changed = True

            # Don't scroll down and prevent the sprite from leaving the screen.
            bottom_bndry = self.view_bottom + SCREEN_WIDTH / 20
            if self.player_sprite.bottom < bottom_bndry:
                self.player_sprite.bottom = bottom_bndry

            if changed:
                arcade.set_viewport(self.view_left,
                                    SCREEN_WIDTH + self.view_left,
                                    self.view_bottom,
                                    SCREEN_HEIGHT + self.view_bottom)

            # Move the enemies
            self.enemy_list.update()

            # Check each enemy
            for enemy in self.enemy_list:
                # If the enemy hit a wall, reverse
                if len(arcade.check_for_collision_with_list(enemy, self.wall_list)) > 0:
                    enemy.change_y *= -1
                # If the enemy hit the top boundary, reverse
                if enemy.boundary_top is not None and enemy.top > enemy.boundary_top:
                    enemy.change_y *= -1
                elif enemy.boundary_bottom is not None and enemy.bottom < enemy.boundary_bottom:
                    enemy.change_y *= -1

            # Call update on all sprites 
            self.physics_engine.update()

            # See if the player hit the enemy. If so, game over.
            if len(arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)) > 0:
                self.current_state = GAME_OVER
                # Change the sprite of hit enemy
                man = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)[0]
                man.texture = arcade.load_texture("images/oldManDown.png")
                # Play the sound
                arcade.play_sound(self.pedestrianHit)

            # Check if the player reached the finish line.
            if arcade.check_for_collision(self.player_sprite, self.finishBlockage):
                self.current_state = GAME_FINISHED
                # Play the celebratory sound
                arcade.play_sound(self.gameFinished)

def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, "Swift Driver")
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()