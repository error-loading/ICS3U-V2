import pygame
from utils.support import import_csv, import_sprite_sheet
from utils.tiles.terrain import Terrain
from utils.tiles.spikes import Spikes
from utils.tiles.fruits import Apple, Banana, Cherry, Stawberry, Pineapple
from utils.tiles.falling_trap import FallingTrap
from utils.tiles.saw_trap import Saw_Trap
from utils.particles import Particles
from utils.teleport import Teleport, Portal, TeleportAway
from utils.player import Player
from utils.tiles.limits import Limit
from constants import *

# keep creating new instances of this class for different levels


class Level:
    def __init__(self, screen, data):
        # general info
        self.screen = screen
        self.data = data
        self.shiftX = 0
        self.shiftY = 0
        self.fruit_count = 0
        self.player_died = False
        self.lvl_completed = False
        self.player_cnt = 0

        # background
        self.background_img = pygame.image.load(f"assets/bg/{self.data['bg_col']}.png").convert_alpha()
        self.background_img = pygame.transform.scale(self.background_img, (WIDTH, HEIGHT))
        self.background_img2 = pygame.image.load(f"assets/bg/{self.data['bg_col']}.png").convert_alpha()
        self.background_img2 = pygame.transform.scale(self.background_img, (WIDTH, HEIGHT))
        self.bg_y = 0

        # terrain
        self.terrain = import_csv(self.data["terrain"])
        self.terrain_sprite_sheet = import_sprite_sheet(
            "assets/terrain/terrain.png", (16, 16))
        self.terrain_sprites = self.create_group("terrain")

        # limits
        self.limits = import_csv(self.data["limits"])
        self.limits_sprites = self.create_group(type = "limit")

        # teleport
        self.teleport_sprite = pygame.sprite.GroupSingle()
        self.portal_sprite_end = pygame.sprite.GroupSingle()
        self.portal_sprite = pygame.sprite.GroupSingle()
        self.teleport_sprite_end = pygame.sprite.GroupSingle()

        # player
        self.player = import_csv(self.data["player"])
        self.player_sprite = self.create_group("player")

        # traps
        self.traps = import_csv(self.data["traps"])

        self.falling_trap_sprites = self.create_group("traps", "0")
        self.saw_trap_sprites = self.create_group("traps", "3")
        self.spike_sprites = self.create_group("traps", "5")

        # fruits
        self.fruits = import_csv(self.data["fruits"])
        self.fruits_sprites = self.create_group("fruits")

        # particle
        self.dust_sprite = pygame.sprite.GroupSingle()


    # creating the tiles for terrains and collectables
    def create_group(self, type, trap_type = "-1"):
        group = pygame.sprite.Group()

        for x, row in enumerate(self.terrain):
            for y, val in enumerate(row):
                posX = y * TILESIZE
                posY = x * TILESIZE
                # this class creates groups for multiple types of tilesets

                if type == "player" and self.player[x][y] == "1":
                    group = pygame.sprite.GroupSingle()

                    self.start_pos = (posX, posY)
                    player = Player((posX, posY), self.screen, self.create_particles)
                    group.add(player)

                    portal = Portal(posX, posY)
                    self.portal_sprite.add(portal)

                    teleport = Teleport(posX, posY, portal)

                    self.player_sprite = group
                    self.teleport_sprite.add(teleport)


                
                if type == "player" and self.player[x][y] == "2":
                    portal = Portal(posX, posY)
                    self.portal_sprite_end.add(portal)

                    teleport = TeleportAway(posX, posY, self.portal_sprite_end, self.player_sprite)
                    self.teleport_sprite_end.add(teleport)

                # limits
                if type == "limit" and self.limits[x][y] == "0":
                    sprite = Limit(posX, posY, self.screen)
                    group.add(sprite)
                    



                # terrain tileset and the value is not -1
                if type == "terrain" and val != "-1":
                    sprite = Terrain(
                        posX, posY, self.terrain_sprite_sheet, int(val))
                    group.add(sprite)

                # traps tilesets
                if type == "traps":
                    # falling trap
                    if self.traps[x][y] == "0" and trap_type == "0":
                        sprite = FallingTrap(posX, posY)
                        group.add(sprite)

                    # saw trap
                    if self.traps[x][y] == "3" and trap_type == "3":
                        sprite = Saw_Trap(posX, posY, x, y, self.terrain, self.limits_sprites)
                        group.add(sprite)

                    # spikes
                    if self.traps[x][y] == "5" and trap_type == "5":
                        sprite = Spikes(posX, posY)
                        group.add(sprite)

                # fruit tilesets
                if type == "fruits":
                    # Apple
                    if self.fruits[x][y] == "1":
                        sprite = Apple(posX, posY)
                        group.add(sprite)

                    # Banana
                    elif self.fruits[x][y] == "2":
                        sprite = Banana(posX, posY)
                        group.add(sprite)

                    # Cherry
                    elif self.fruits[x][y] == "3":
                        sprite = Cherry(posX, posY)
                        group.add(sprite)

                    # Stawberry
                    elif self.fruits[x][y] == "4":
                        sprite = Stawberry(posX, posY)
                        group.add(sprite)

                    # Pineapple
                    elif self.fruits[x][y] == "6":
                        sprite = Pineapple(posX, posY)
                        group.add(sprite)

        return group

    # creating the player
    def create_player(self):
        pass

    # creating particles
    def create_particles(self, pos):
        sprite = Particles(pos)
        self.dust_sprite.add(sprite)


    # method is called to check if game is over
    def check_game_over(self):
        if self.teleport_sprite_end.sprite.check_collision():
            self.lvl_completed = True

    # fruit collision
    def fruit_collide(self):
        fruits_hit = pygame.sprite.spritecollide(self.player_sprite.sprite, self.fruits_sprites, True, pygame.sprite.collide_mask)

        for fruit in fruits_hit:
            self.fruit_count += 1

    # check for horizontal collision
    def horizonal_collide(self):
        player = self.player_sprite.sprite

        player.rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                player.in_air = False
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left

        for sprite in self.falling_trap_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                player.in_air = False
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left

                sprite.dead = True

    # call function to reset the level
    def reset(self):
        pass

    # saw trap collide
    def saw_trap_collide(self):
        for sprite in self.limits_sprites:
            for saw in self.saw_trap_sprites:
                if pygame.sprite.collide_mask(sprite, saw):
                    saw.switch()

        dead = pygame.sprite.spritecollide(self.player_sprite.sprite, self.saw_trap_sprites, False, pygame.sprite.collide_mask)

        for i in dead:
            self.player_died = True
            self.player_sprite.sprite.dead()
            self.reset()

    def scrolling_background(self):
        self.screen.blit(self.background_img, (0, self.bg_y))
        self.screen.blit(self.background_img2, (0, self.bg_y - HEIGHT))
        self.bg_y += 1

        if self.bg_y > HEIGHT:
            self.bg_y = 0
    # scrolling function
    def scrollX(self):
        player = self.player_sprite.sprite
        posX = player.rect.x
        
        if 700 < posX < WIDTH and player.direction.x > 0:
            player.speed = 0
            self.shiftX = -5
        
        elif 0 < posX < 300 and player.direction.x < 0:
            player.speed = 0
            self.shiftX = 5

        else:
            self.shiftX = 0
            player.speed = 5
    
    def scrollY(self):
        pass
        # player = self.player_sprite.sprite
        # self.shiftY = player.direction.y
    
    # spiek collide
    def spike_collide(self):
        dead = pygame.sprite.spritecollide(self.player_sprite.sprite, self.spike_sprites, False, pygame.sprite.collide_mask)

        for i in dead:
            self.player_died = True
            self.player_sprite.sprite.dead()
            self.reset()
        
    # function for teleporting
    def teleport(self):
        pass

    # check for vertical collision
    def vertical_collide(self):
        player = self.player_sprite.sprite 

        if self.player_cnt > 60:
            player.get_gravity()

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                player.in_air = False
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

        for sprite in self.falling_trap_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                player.in_air = False
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

                sprite.dead = True

    # this method will be called by the main function, all the stuff that will be going in the while loop will be called here
    def run(self):
        self.scrolling_background()
        # limits sprites 
        self.limits_sprites.draw(self.screen)
        self.limits_sprites.update(self.shiftX, self.shiftY)

        # dust sprites draw and update
        self.dust_sprite.draw(self.screen)
        self.dust_sprite.update(self.shiftX)

        # WOW, this is a portal sprite, prolly not what u expected !! this is def not being written by Kevin Lu
        self.portal_sprite.draw(self.screen)
        self.portal_sprite.update(self.shiftX)

        # portal_sprite_end
        self.portal_sprite_end.draw(self.screen)
        self.portal_sprite_end.update(self.shiftX)

        # teleport draw and update
        self.teleport_sprite.draw(self.screen)
        self.teleport_sprite.update(self.shiftX)

        # teleport_sprite_end
        self.teleport_sprite_end.draw(self.screen)
        self.teleport_sprite_end.update(self.shiftX)

        # saw trap draw and update
        self.saw_trap_sprites.draw(self.screen)

        # terrain sprites draw and update
        self.terrain_sprites.draw(self.screen)
        self.terrain_sprites.update(self.shiftX, self.shiftY)


        # falling trap sprites draw and update
        self.falling_trap_sprites.draw(self.screen)
        self.falling_trap_sprites.update(self.shiftX, self.shiftY)

        # spike strap sprites draw and update
        self.spike_sprites.draw(self.screen)
        self.spike_sprites.update(self.shiftX, self.shiftY)

        # player sprites draw and update
        if self.player_cnt > 60:
            self.player_sprite.draw(self.screen)
            self.player_sprite.update()

        # fruit sprites draw and update
        self.fruits_sprites.draw(self.screen)
        self.fruits_sprites.update(self.shiftX, self.shiftY)


 

        # call other stuff
        if not self.player_died:
            self.vertical_collide()
            self.horizonal_collide()
            self.spike_collide()
            self.saw_trap_collide()
            self.saw_trap_sprites.update(self.shiftX, self.shiftY)

        self.fruit_collide()
        self.scrollX()
        self.scrollY()
        self.player_cnt += 1