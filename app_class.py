import pygame, sys
from settings import * # custom settings file
from player_class import *
from enemy_class import *
from blinky import *
from inky import *
from pinky import *
from clyde import *
import neat
import visualize

pygame.init()
vec = pygame.math.Vector2

class App:
	def __init__(self):
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		self.clock = pygame.time.Clock()
		self.state = 'playing'
		self.running = True
		self.cell_width = MAZE_WIDTH//28 # init grid
		self.cell_height = MAZE_HEIGHT//30 # init grid
		self.walls = []
		self.map = [] # 2d array for ghosts to use to find path to pacman

	def run(self, genomes, config):

		# NEAT Neural Network
		for _, g in genomes:
			self.running = True
			self.hit_by_ghost = False
			self.coins = []
			self.players = []
			self.enemies = []
			self.player_pos = None # player position
			self.enemy_pos = [] # enemy position
			self.game_start_time = 0 # keep track of when player starts the game
			self.load() # load game

			self.net = neat.nn.FeedForwardNetwork.create(g, config)
			self.player = Player(self, vec(13,23))
			self.enemies = self.make_enemies(self.player)
			g.fitness = 0

			while self.running:
				if self.state == 'playing':
					self.playing_update()
					self.playing_draw()
					if self.hit_by_ghost:
						g.fitness = self.player.current_score
						self.running = False

				elif self.state == 'player_won':
					self.player_won()

				self.clock.tick(FPS) # 60, FPS in settings file


######################## HELPER FUNCTIONS ##############################

	def draw_text(self, words, screen, pos, size, color, font_name, centered=False):
		font = pygame.font.SysFont(font_name, size)
		text = font.render(words, False, color)
		text_size = text.get_size()
		if centered:
			pos[0] = pos[0] - text_size[0] // 2
			pos[1] = pos[1] - text_size[1] // 2
		screen.blit(text, pos)

	# Load images and walls on init
	def load(self):
		self.background = pygame.image.load('imgs/background.png')
		self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT)) # Scale background to correct size
		self.game_start_time = pygame.time.get_ticks()

		with open('walls.txt', 'r') as file: # read in walls file and create walls list for wall coordinates
			for yindex, line in enumerate(file): # enumerate to get coordinates
				for xindex, char in enumerate(line):
					if char == '1': # if wall,  set coordinate to boundary
						self.walls.append(vec(xindex, yindex))
					elif char == 'C': # if coin, set coordinate to coin
						self.coins.append(vec(xindex, yindex))
					elif char in ['2','3','4','5']:
						self.enemy_pos.append(vec(xindex, yindex))
					elif char == 'G': # gate for ghost house
						pygame.draw.rect(self.background, BLACK, (xindex*self.cell_width, yindex*self.cell_height, self.cell_width, self.cell_height))

				self.map.append([char for char in line]) # create 2d map for ghosts


	def make_enemies(self, player_obj):
		# each enemy is their own object, inheriting from enemy_class
		enemies = []
		for index, position in enumerate(self.enemy_pos):
			if index == 0:
				blinky_obj = Blinky(self, position, player_obj)
				enemies.append(blinky_obj)	
			elif index == 1:
				enemies.append(Pinky(self, position, player_obj))
			elif index == 2:
				enemies.append(Inky(self, position, player_obj, blinky_obj))
			else:
				enemies.append(Clyde(self, position, player_obj))

		return enemies


######################## PLAYING FUNCTIONS ##############################

	def playing_update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
				pygame.quit()
				sys.exit()

		coin_right = 0
		coin_left = 0
		coin_below = 0
		coin_above = 0

		if self.map[int(self.player.grid_pos.x+1)][int(self.player.grid_pos.y)] == 'C':
			coin_right = 1
		if self.map[int(self.player.grid_pos.x-1)][int(self.player.grid_pos.y)] == 'C':
			coin_left = 1
		if self.map[int(self.player.grid_pos.x)][int(self.player.grid_pos.y)+1] == 'C':
			coin_below = 1			
		if self.map[int(self.player.grid_pos.x+1)][int(self.player.grid_pos.y)-1] == 'C':
			coin_above = 1

		# activate neural network with inputs = player_pos, blinky_pos, pinky_pos, inky_pos, clyde_pos, all_coins_pos 
		output = self.net.activate((
			self.player.grid_pos.x,
			self.player.grid_pos.y, 
			self.enemies[0].grid_pos.x,
			self.enemies[0].grid_pos.y, 
			self.enemies[1].grid_pos.x,
			self.enemies[1].grid_pos.y, 
			self.enemies[2].grid_pos.x,
			self.enemies[2].grid_pos.y, 
			self.enemies[3].grid_pos.x,
			self.enemies[3].grid_pos.y,
			coin_right,
			coin_left,
			coin_below,
			coin_above
			))

		direction = output.index(max(output))

		if direction == 0:
			self.player.move(RIGHT)
		elif direction == 1:
			self.player.move(LEFT)
		elif direction == 2:
			self.player.move(UP)
		elif direction == 3:
			self.player.move(DOWN)

		self.player.update() # update player
		for enemy in self.enemies: # update enemy
			enemy.update()
			if self.player.grid_pos.x == enemy.grid_pos.x and self.player.grid_pos.y == enemy.grid_pos.y:
				self.hit_by_ghost = True

		if len(self.coins) == 0:
			self.state = 'player_won'


	def playing_draw(self):
		self.screen.fill(BLACK)
		self.screen.blit(self.background, (TOP_BOTTOM_BUFFER//2, TOP_BOTTOM_BUFFER//2))
		self.draw_coins()
		self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score), self.screen, [60, 2], START_TEXT_SIZE, WHITE, START_FONT)
		self.player.draw() # draw player
		for enemy in self.enemies: # draw enemies
			enemy.draw()

		pygame.display.update()

	def draw_coins(self):
		for coin in self.coins:
			pygame.draw.circle(self.screen, (124,123,7), 
				((int(coin.x*self.cell_width)+self.cell_width//2)+TOP_BOTTOM_BUFFER//2, 
					(int(coin.y*self.cell_height)+self.cell_height//2)+TOP_BOTTOM_BUFFER//2), 3)

######################## PLAYER WON ##############################

	def player_won(self):
		self.draw_text('YOU WON!', self.screen, [WIDTH//2, HEIGHT//2 - 100], 36, (170, 132, 58), START_FONT, centered=True) # PUSH SPACE BAR text
		self.draw_text('PUSH SPACE BAR TO PLAY AGAIN', self.screen, [WIDTH//2, HEIGHT//2 + 100], 28, (44, 167, 198), START_FONT, centered=True) # PUSH SPACE BAR text
		pygame.display.update()

######################## PLAYER LOST ##############################

	def player_lost(self):
		self.__init__()

