import pygame
from settings import *
from GameObjects.entity import Entity
from utils import import_folder

class Enemy(Entity):
    
    def __init__(self, groups, monster_name, position, obstacle_sprites, attack_player, death_effects, add_xp):
        super().__init__(groups)


        self.sprite_type = 'enemy'

        # graphics 
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][int(self.frame_index)]
        self.death_effects = death_effects

        # movement
        self.rect = self.image.get_rect(topleft = position)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']
        self.sound = pygame.mixer.Sound(monster_info['attack_sound'])
        
        # player interaction
        self.can_attack = True
        self.attack_cooldown = 500
        self.attack_time = None
        self.attack_player = attack_player
        self.add_xp = add_xp

        # invincibility timer
        self.vulnerable = True
        self.vulnerable_time = None
        self.vulnerable_cooldown = monster_data[self.monster_name]['invincibility']

    def import_graphics(self, name):

        self.animations = {
            'idle': {},
            'move': {},
            'attack': {}
        }

        path = f'./Assets/graphics/monsters/{name}/'

        for animation in self.animations.keys():
            self.animations[animation] = import_folder(path + animation)

    def get_player_dist_and_dir(self, player):
        enemy_vector = pygame.math.Vector2(self.rect.center)
        player_vector = pygame.math.Vector2(player.rect.center)
        distance = (player_vector - enemy_vector).magnitude()

        if distance != 0:
            direction = (player_vector - enemy_vector).normalize()
        else: direction = pygame.math.Vector2()

        return (distance, direction)

    def get_status(self, player):

        distance = self.get_player_dist_and_dir(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.attack_player(self.attack_damage, self.attack_type)
            self.sound.play()
        elif self.status == 'move':
            self.direction = self.get_player_dist_and_dir(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):

        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        if not self.vulnerable:
            alpha = self.get_wave()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.can_attack == False:
                if current_time - self.attack_time >= self.attack_cooldown:
                    self.can_attack = True

        if not self.vulnerable:
                if current_time - self.vulnerable_time >= self.vulnerable_cooldown:
                    self.vulnerable = True

    def get_dmg(self, player, attack_type):
        if self.vulnerable:
            self.direction = self.get_player_dist_and_dir(player)[1]
            if attack_type == 'weapon':
                self.health -= player.get_weapon_dmg()
            else:
                self.health -= player.get_magic_dmg()
            
            self.vulnerable_time = pygame.time.get_ticks()
            self.vulnerable = False
        
    def check_death(self):
        if self.health <= 0:
            self.death_effects(self.rect.center, self.monster_name)
            self.add_xp(self.exp)
            self.kill()

    def show_resistance(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def update(self):
        self.show_resistance()
        self.move(self.speed)
        self.check_death()
        self.animate()
        self.cooldowns()

    def update_enemies(self, player):
        self.get_status(player)
        self.actions(player)