import pygame
#import math
from queue import PriorityQueue

WIDTH = 800     #Window Dimensions
WIN = pygame.display.set_mode((WIDTH, WIDTH)) #setting up a window
pygame.display.set_caption("A* Maze Solver") #Title

#Color Codes
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

#main visualization tool
#Spot is a node
class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width #tracking coordinates
		self.y = col * width
		self.color = WHITE   #intial and reset color
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
    #setting up nodes with status using colors
	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win): #drawing a spot/node
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):  #making the spots in grid as nodes in graph
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):  #lessthan - comparing 2 spot objects
		return False


#heuristic function: h-value
#manhattan distance- taxi can distance
#no diagonal traverse
def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):  #Path existed, so reconstructing using tracked data
	while current in came_from:
		current = came_from[current]
		current.make_path()       #PURPLE
		draw()


def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue() #to Get smallest element(heap sort) - min F-VALUE
	open_set.put((0, count, start))    #add start node to open set with f-score as 0
	came_from = {} #keep track where we came from
	g_score = {spot: float("inf") for row in grid for spot in row} #g-value
	g_score[start] = 0     #always g-value for start node=0
	f_score = {spot: float("inf") for row in grid for spot in row} #f-value
	f_score[start] = h(start.get_pos(), end.get_pos())     #always h-value for start node is heuristic

	open_set_hash = {start}    #To check item in Priority Queue, bcoz PQ doesn't say us directly

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:    #reached destination
			reconstruct_path(came_from, end, draw)
			end.make_end()   #so that END node doesn't become purple
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1  

			if temp_g_score < g_score[neighbor]: #found a better way to reach node
				came_from[neighbor] = current    #update 
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()   #open on screen, exploring - GREEN

		draw() #open set is explored completely, path exists

		if current != start:
			current.make_closed()    #visited - RED

	return False


def make_grid(rows, width):
	grid = []  #list holds all spots
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows) #creating a spot
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap)) #horizontal lines
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

#draws everything
def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win) 

	draw_grid(win, rows, width)  #call draw_grid
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	ROWS = 40   #Make dynamic by varying value
	grid = make_grid(ROWS, width)      #2d-array of spot generated

	start = None
	end = None

	run = True
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():  #loops through all the events happened
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT button is pressed
				pos = pygame.mouse.get_pos()  #get position
				row, col = get_clicked_pos(pos, ROWS, width)  
				spot = grid[row][col]         #get the spot from grid
                
                #setting up nodes/spots status using methods defined
				if not start and spot != end:
					start = spot
					start.make_start()     #orange node/spot

				elif not end and spot != start:
					end = spot
					end.make_end()         #torquoise node/spot

				elif spot != end and spot != start:
					spot.make_barrier()    #black node/spot

			elif pygame.mouse.get_pressed()[2]: # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
                #right click used to reset the spot status
                
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.KEYDOWN: #anykey...pressed ?
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c:     #clear screen, get started again
					start = None
					end = None
					grid = make_grid(ROWS, width)

	pygame.quit()  #quits window

main(WIN, WIDTH)