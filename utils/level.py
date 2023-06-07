import pygame
from utils.support import import_csv, import_sprite_sheet
from utils.tiles.terrain import Terrain
from utils.tiles.spikes import Spikes
from constants import *

# keep creating new instances of this class for different levels
class Level:
    def __init__(self, screen, data):
        # general info
        self.screen = screen
        self.data = data
        self.shiftX = -1
        self.shiftY = 0

        # terrain
        self.terrain = import_csv(self.data["terrain"])
        self.terrain_sprite_sheet = import_sprite_sheet(self.data["terrain"], (16, 16))
        self.terrain_sprites = self.create_group("terrain")

        # traps
        self.traps = import_csv(self.data["traps"])
        self.traps_sprites = self.create_group("traps")
    
    # creating the tiles for terrains and collectables
    def create_group(self, type):
        group = pygame.sprite.Group()

        for x, row in enumerate(self.terrain):
            for y, val in enumerate(row):
                posX = y * TILESIZE
                posY = x * TILESIZE

                # this class creates groups for multiple types of tilesets

                # terrain tileset and the value is not -1
                if type == "terrain" and val != "-1":
                    sprite = Terrain(posX, posY, self.terrain_sprite_sheet, int(val))
                    group.add(sprite)

                # traps tilesets
                if type == "traps":
                    # falling trap
                    if self.traps[x][y] == "0":
                        pass

                    # saw trap
                    if self.traps[x][y] == "3":
                        pass

                    # spikes
                    if self.traps[x][y] == "5":
                        sprite = Spikes(posX, posY)
                        group.add(sprite)

        
        return group

    # creating the player
    def create_player(self):
        pass

    # method is called to check if game is over
    def check_game_over(self):
        pass

    # fruit collision
    def fruit_collide(self):
        pass

    # check for horizontal collision
    def horizonal_collide(self):
        pass

    # call function to reset the level
    def reset(self):
        pass

    # function for teleporting 
    def teleport(self):
        pass

    # check for vertical collision
    def vertical_collide(self):
        pass

    # this method will be called by the main function, all the stuff that will be going in the while loop will be called here
    def run(self):
        self.terrain_sprites.draw(self.screen)
        self.terrain_sprites.update(self.shiftX, self.shiftY)

        self.traps_sprites.draw(self.screen)
        self.traps_sprites.update(self.shiftX, self.shiftY)