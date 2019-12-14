import pygame, sys
from settings import * # custom settings file
from player_class import *
from enemy_class import *
from blinky import *
from inky import *
from pinky import *
from clyde import *

pygame.init()
vec = pygame.math.Vector2

class App:
	def __init__(self):
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		self.clock = pygame.time.Clock()
		self.running = True
		self.state = 'start' # start at start screen
		self.cell_width = MAZE_WIDTH//28 # init grid
		self.cell_height = MAZE_HEIGHT//30 # init grid
		self.walls = []
		self.map = [] # 2d array for ghosts to use to find path to pacman
		self.coins = []
		self.enemies = []
		self.player_pos = None # player position
		self.enemy_pos = [] # enemy position
		self.game_start_time = 0 # keep track of when player starts the game

		self.load() # load game
		self.player = Player(self, self.player_pos) # init player
		self.make_enemies()

	def run(self):
		while self.running:
			if self.state == 'start':
				self.start_events()
				self.start_update()
				self.start_draw()
			elif self.state == 'playing':
				self.playing_events()
				self.playing_update()
				self.playing_draw()
			elif self.state == 'player_won':
				self.player_won()
			elif self.state == 'player_lost':
				self.player_lost()

			self.clock.tick(FPS) # 60, FPS in settings file

		pygame.quit()
		sys.exit()

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

		with open('walls.txt', 'r') as file: # read in walls file and create walls list for wall coordinates
			for yindex, line in enumerate(file): # enumerate to get coordinates
				for xindex, char in enumerate(line):
					if char == '1': # if wall,  set coordinate to boundary
						self.walls.append(vec(xindex, yindex))
					elif char == 'C': # if coin, set coordinate to coin
						self.coins.append(vec(xindex, yindex))
					elif char == 'P': # if player, set coordinate for player start
						self.player_pos = (vec(xindex, yindex))
					elif char in ['2','3','4','5']:
						self.enemy_pos.append(vec(xindex, yindex))
					elif char == 'G': # gate for ghost house
						pygame.draw.rect(self.background, BLACK, (xindex*self.cell_width, yindex*self.cell_height, self.cell_width, self.cell_height))

				self.map.append([char for char in line]) # create 2d map for ghosts


	def make_enemies(self):
		# each enemy is their own object, inheriting from enemy_class
		for index, position in enumerate(self.enemy_pos):
			if index == 0:
				blinky_obj = Blinky(self, position, self.player)
				self.enemies.append(blinky_obj)	
			elif index == 1:
				self.enemies.append(Pinky(self, position, self.player))
			elif index == 2:
				self.enemies.append(Inky(self, position, self.player, blinky_obj))
			else:
				self.enemies.append(Clyde(self, position, self.player))


######################## INTRO FUNCTIONS ##############################

	def start_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				self.state = 'playing'
				self.game_start_time = pygame.time.get_ticks()

	def start_update(self):
		pass

	def start_draw(self):
		self.draw_text('PUSH SPACE BAR', self.screen, [WIDTH//2, HEIGHT//2 - 50], START_TEXT_SIZE, (170, 132, 58), START_FONT, centered=True) # PUSH SPACE BAR text
		self.draw_text('1 PLAYER ONLY', self.screen, [WIDTH//2, HEIGHT//2 + 50], START_TEXT_SIZE, (44, 167, 198), START_FONT, centered=True) # 1 PLAYER ONLY text
		pygame.display.update()


######################## PLAYING FUNCTIONS ##############################

	def playing_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					self.player.move(vec(-1,0))
				if event.key == pygame.K_RIGHT:
					self.player.move(vec(1,0))
				if event.key == pygame.K_UP:
					self.player.move(vec(0,-1))
				if event.key == pygame.K_DOWN:
					self.player.move(vec(0,1))

	def playing_update(self):
		self.player.update() # update player
		for enemy in self.enemies: # update enemy
			enemy.update()
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

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				self.screen.fill(pygame.Color("black"))
				self.__init__()

######################## PLAYER LOST ##############################

	def player_lost(self):
		self.draw_text('YOU LOST :(', self.screen, [WIDTH//2, HEIGHT//2 - 100], 36, (170, 132, 58), START_FONT, centered=True) # PUSH SPACE BAR text
		self.draw_text('PUSH SPACE BAR TO PLAY AGAIN', self.screen, [WIDTH//2, HEIGHT//2 + 100], 28, (44, 167, 198), START_FONT, centered=True) # PUSH SPACE BAR text
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				self.screen.fill(pygame.Color("black"))
				self.__init__()




