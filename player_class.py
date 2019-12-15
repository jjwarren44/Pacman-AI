import pygame
from settings import *
vec = pygame.math.Vector2

class Player:
	def __init__(self, app, pos):
		self.app = app
		self.grid_pos = pos
		self.pix_pos = self.get_pix_pos()
		self.direction = vec(1,0)
		self.stored_direction = None
		self.able_to_move = True
		self.current_score = 0
		self.speed = 2

	def update(self):
		if self.able_to_move:
			self.pix_pos += self.direction*self.speed

		# Keep player on the grid, can't be on a line but has to be within the lines
		if self.time_to_move():
			if self.stored_direction != None:
				self.direction = self.stored_direction
			self.able_to_move = self.can_move()

		# Setting grid position in reference to pix position
		self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER+self.app.cell_width//2)//self.app.cell_width+1 # grid position x-axis
		self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER+self.app.cell_height//2)//self.app.cell_height+1 # grid position x-axis

		if self.on_coin():
			self.eat_coin()

	def draw(self):
		pygame.draw.circle(self.app.screen, PLAYER_COLOR, (int(self.pix_pos.x), int(self.pix_pos.y)), self.app.cell_width//2-2)

	def move(self, direction):
		self.stored_direction = direction

	def get_pix_pos(self):
		return vec((self.grid_pos.x*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2, 
			(self.grid_pos.y*self.app.cell_height)+TOP_BOTTOM_BUFFER//2+self.app.cell_height//2) # so player moves by pixel, not grid (using 2d vector)

	def get_grid_pos(self):
		return vec(self.grid_pos.x, self.grid_pos.y)

	# if pixel position is divisible (mod) by cell_width or cell_height, then we are within a cell. Allow movement
	def time_to_move(self):
		if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
			if self.direction == vec(1,0) or self.direction == vec(-1, 0):
				return True

		if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:					
			if self.direction == vec(0,1) or self.direction == vec(0,-1):
				return True

		# else
		#print('not time to move')
		return False

	# Function to handle whether or not there is a wall in the way
	def can_move(self):
		for wall in self.app.walls:
			if vec(self.grid_pos+self.direction) == wall: # if player hits wall, dont allow movement
				#print("wall there")
				return False
		return True

	# Function to check if player is on coin
	def on_coin(self):
		if self.grid_pos in self.app.coins: # if true, make sure player is on center of coin
			if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
				if self.direction == vec(1,0) or self.direction == vec(-1, 0):
					return True

			if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:					
				if self.direction == vec(0,1) or self.direction == vec(0,-1):
					return True

		return False

	def eat_coin(self):
		self.app.coins.remove(self.grid_pos) # remove coin
		self.current_score += 1





