import pygame
import collections
import math
from settings import *
from enemy_class import Enemy
from player_class import *
import pdb

vec = pygame.math.Vector2

class Pinky(Enemy):
	def __init__(self, app, pos, player_obj):
		self.color = 0xffc0cb
		self.img = pygame.image.load("imgs/pinky.png")
		super(Pinky, self).__init__(app, pos, player_obj, self.img)
		self.possible_directions = [[1,0],[-1,0],[0,1],[0,-1]] #right, left, down, up
		self.direction = vec(0,0)

	# Get position of pacman and find best possible route to 4 tiles ahead of him
	def update(self):
		if pygame.time.get_ticks() - self.app.game_start_time > 3000:

			self.pix_pos += self.direction*self.speed # move

			if self.in_ghost_house: # manually move left 2 and up 2
				if self.grid_pos.x == 16 and self.grid_pos.y == 13:
					self.direction = vec(-1,0)
				if self.grid_pos.x == 14 and self.grid_pos.y == 13:
					self.direction = vec(0,-1)
				if self.grid_pos.x == 14 and self.grid_pos.y == 11:
					self.in_ghost_house = False
			else:
				if self.time_to_move():
					find = self.find_next_tile(self.player.grid_pos, self.player.direction)
					self.direction = vec(find[0],find[1])

		# Setting grid position in reference to pix position
		self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER+self.app.cell_width//2)//self.app.cell_width+1 # grid position x-axis
		self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER+self.app.cell_height//2)//self.app.cell_height+1 # grid position y-axis


	def find_next_tile(self, player_pos, player_dir):
		# get minimum linear distance from enemy to pacman for all possible tiles
		direction_to_move = 0 # holds index of directions_allowed array
		min_distance = 0

		# target tile = pacman_pos + (pacman_direction * 4)
		target_tile = player_pos + (player_dir * 4)

		for index, direction in enumerate(self.possible_directions):
			if direction != self.direction*-1 and self.app.map[int(self.grid_pos.y+direction[1])][int(self.grid_pos.x+direction[0])] != '1' and self.app.map[int(self.grid_pos.y+direction[1])][int(self.grid_pos.x+direction[0])] != 'G':
				distance = math.sqrt(((self.grid_pos.x+direction[0])-target_tile.x)**2 + ((self.grid_pos.y+direction[1])-target_tile.y)**2)
				if distance < min_distance or min_distance == 0:
					min_distance = distance
					direction_to_move = index
				if distance < 5: # If pinky is within 5 tiles of pacman, make target tile pacman instead of 4 tiles ahead of him
					target_tile = player_pos
				else:
					target_tile = player_pos + (player_dir * 4)

		# return which direction to move
		if direction_to_move == 0:
			return [1,0]
		elif direction_to_move == 1:
			return [-1,0]
		elif direction_to_move == 2:
			return [0,1]
		elif direction_to_move == 3:
			return [0,-1]



		