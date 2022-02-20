import pygame, sys
from settings import *
from level import Level

class Game:
	def __init__(self): 
		  
		# general setup
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('Zelda')
		self.clock = pygame.time.Clock()
		self.main_sound = pygame.mixer.Sound('./Assets/audio/main.ogg')

		self.level = Level()
	
	def run(self):
		self.main_sound.play(True)
		while True:
			if self.level.player.health <= 0:
				pygame.quit()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_m:
						self.level.toggle_menue()

			self.screen.fill(WATER_COLOR)
			self.level.run()
			pygame.display.update()
			self.clock.tick(FPS)

if __name__ == '__main__':
	game = Game()
	game.run()	