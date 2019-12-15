import pygame
from settings import *

vec = pygame.math.Vector2

class Enemy(object):
	def __init__(self, app, pos, player_obj, img):
		self.app = app
		self.grid_pos = pos
		self.pix_pos = self.get_pix_pos()
		self.direction = vec(0,0)
		self.img = img
		self.speed = 1
		self.player = player_obj
		self.in_ghost_house = True

	def draw(self):
		#pygame.draw.circle(self.app.screen, self.color, (int(self.pix_pos.x), int(self.pix_pos.y)), self.app.cell_width//2-2)
		self.img = pygame.transform.scale(self.img, (self.app.cell_width, self.app.cell_height))
		self.app.screen.blit(self.img, (int(self.pix_pos.x-self.app.cell_width//2), int(self.pix_pos.y-self.app.cell_height//2)))


	def time_to_move(self):
		if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
			if self.direction == vec(1,0) or self.direction == vec(-1, 0):
				return True

		if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:					
			if self.direction == vec(0,1) or self.direction == vec(0,-1):
				return True

		# else
		return False

	def get_pix_pos(self):
		return vec((self.grid_pos.x*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2, 
			(self.grid_pos.y*self.app.cell_height)+TOP_BOTTOM_BUFFER//2+self.app.cell_height//2) # so enemy moves by pixel, not grid (using 2d vector)


		