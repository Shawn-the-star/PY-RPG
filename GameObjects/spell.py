import pygame
from settings import *
from random import randint

class MagicPlayer:
  def __init__(self, animation_player):

    self.animation_player = animation_player
    self.sound = {
      'heal': pygame.mixer.Sound('./Assets/audio/heal.wav'),
      'flame': pygame.mixer.Sound('./Assets/audio/Fire.wav')
    }

  def heal(self, player, strength, cost, groups):
    if player.energy >= cost:
      self.sound['heal'].play()
      player.health += strength
      player.energy -= cost
      if player.health >= player.stats['health']:
        player.health = player.stats['health']

      offset = pygame.math.Vector2(0, 60)
      self.animation_player.generate_particles('aura', player.rect.center, groups)
      self.animation_player.generate_particles('heal', player.rect.center - offset, groups)

  def flame(self, player, strength, cost, groups):
    if player.energy >= cost:
      self.sound['flame'].play()
      player.energy -= cost

      d = player.status.split('_')[0]
      if d == 'right':
        direction = pygame.math.Vector2(1, 0)
      elif d == 'left':
        direction = pygame.math.Vector2(-1, 0)
      elif d == 'down':
        direction = pygame.math.Vector2(0, 1)
      else:
        direction = pygame.math.Vector2(0, -1)
      
      for i in range(1, 6):
        if direction.x:
          for _ in range(2):
            offset = (direction.x * i) * TILESIZE
            x = player.rect.centerx + offset + randint(-TILESIZE // 3, TILESIZE // 3)
            y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)

            self.animation_player.generate_particles('flame', (x, y), groups)
        elif direction.y:
          for _ in range(2):
            offset = (direction.y * i) * TILESIZE
            y = player.rect.centery + offset + randint(-TILESIZE // 3, TILESIZE // 3)
            x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
            
            self.animation_player.generate_particles('flame', (x, y), groups)
        