import pygame
from GameObjects.enemy import Enemy
from GameObjects.player import Player
from GameObjects.tile import Tile
from GameObjects.wepon import Weapon
from GameObjects.particles import AnimationPlayer
from GameObjects.spell import MagicPlayer
from settings import *
from ui import UI
from utils import import_csv_map, import_folder
from random import choice, randint
from debug import debug
from upgrade_menu import UpgradeMenu

class Level:
    def __init__(self):

        self.display_surface = pygame.display.get_surface()
        
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        
        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.generate_map()

        # user interface
        self.ui = UI()
        self.game_pause = False
        self.upgrade_menu = UpgradeMenu(self.player)

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)
    
    def generate_map(self):

        layouts = {
            'boundary': import_csv_map("./Assets/map/map_FloorBlocks.csv"),
            'grass': import_csv_map("./Assets/map/map_Grass.csv"),
            'object': import_csv_map("./Assets/map/map_Objects.csv"),
            'entities': import_csv_map("./Assets/map/map_Entities.csv")
        }

        graphics = {
            'grass': import_folder("./Assets/graphics/grass"),
            'objects': import_folder("./Assets/graphics/objects")
        }

        for style, layout in layouts.items():
            for rowIndex, row in enumerate(layout):
                for colIndex, col in enumerate(row):
                    if col != '-1':
                        x = colIndex * TILESIZE
                        y = rowIndex * TILESIZE
                        if style == 'boundary':
                                Tile((x, y), [self.obstacle_sprites], 'invisible')
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'grass', random_grass_image)
                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)
                        if style == 'entities':
                            if col == '394':
                                self.player = Player(
                                    (x, y), 
                                    [self.visible_sprites], 
                                    self.obstacle_sprites, 
                                    self.create_attack, 
                                    self.destroy_attack, 
                                    self.create_magic
                                )
                            else:
                                monster_name = ''
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name = 'raccoon'
                                else: monster_name = 'squid'

                                Enemy([self.visible_sprites, self.attackable_sprites], monster_name, (x, y), self.obstacle_sprites, self.attack_player, self.trigger_death_effects, self.add_xp)

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                for target in collision_sprites:
                    if target.sprite_type == 'grass':
                        pos = target.rect.center
                        offset = pygame.math.Vector2(0, 75)
                        for leaf in range(randint(3, 5)):
                            self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                        target.kill()
                    else:
                        target.get_dmg(self.player, attack_sprite.sprite_type)

    def attack_player(self, damage, attack_type):
        if self.player.vulnerable:
            self.player.health -= damage  
            self.player.vulnerable_time = pygame.time.get_ticks()
            self.player.vulnerable = False

            # particles
            self.animation_player.generate_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    def trigger_death_effects(self, pos, particle_type):
        self.animation_player.generate_particles(particle_type, pos, [self.visible_sprites])

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player, strength, cost, [self.visible_sprites, self.attack_sprites])

    def add_xp(self, xp):
        self.player.exp += xp

    def toggle_menue(self):
        self.game_pause = not self.game_pause
        
    def run(self):

        self.visible_sprites.Draw(self.player)
        self.ui.display(self.player)

        if self.game_pause:
            self.upgrade_menu.display()
        else:
            self.player_attack_logic()
            self.visible_sprites.update()
            self.visible_sprites.update_enemies(self.player)
            
        




class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.half_width = pygame.display.get_window_size()[0] // 2
        self.half_height = pygame.display.get_window_size()[1] // 2

        self.offset = pygame.math.Vector2() 

        # creating the floor 
        self.floor_surf = pygame.image.load('./Assets/graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def Draw(self, player):

        self.offset.x =  player.rect.centerx - self.half_width 
        self.offset.y =  player.rect.centery - self.half_height 

        # drawing the floor
        floor_offset = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset)

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):  
            self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)

    def update_enemies(self, player):
        enemy_sprites = [
            sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy'
        ]

        for enemy in enemy_sprites:
            enemy.update_enemies(player)