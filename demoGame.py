import math
import pygame
import random
import sys

# COLORS
BLACK = 0, 0, 0
WHITE = 255, 255, 255

# DIMENSIONS
CANVAS_HEIGHT = 480
CANVAS_WIDTH = 640 

# Box
box_x = 300
box_dir = 3

# Prey
prey_size = 5
prey_pop = 50
prey_velocity = 3
prey_color = WHITE

# Init Canvas
pygame.init()
screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
pygame.display.set_caption("Moving Box")
clock = pygame.time.Clock()

class Prey:
  def __init__(self, size, color):
    self.size = size
    self.color = color
    self.velocity = prey_velocity
    self.position = self.getRandomPosition()
    self.orientation = math.radians(random.randint(1, 360))

  def getRandomPosition(self):
    x_coord = random.randint(0, CANVAS_WIDTH)
    y_coord = random.randint(0, CANVAS_HEIGHT)
    return {'x': x_coord, 'y': y_coord}

  def getPosition(self):
    return (self.position['x'], self.position['y'])

  def updatePosition(self):
    # current coordinates
    curr_x = self.position['x']
    curr_y = self.position['y']

    # reverse direction if prey hits a wall
    if curr_x <= 0 or curr_x >= CANVAS_WIDTH:
      self.velocity *= -1
    elif curr_y <= 0 or curr_y >= CANVAS_HEIGHT:
      self.velocity *= -1

    # how much organism will move in x and y direction?
    x_delta = int(round(math.cos(self.orientation) * self.velocity)) 
    y_delta = int(round(math.sin(self.orientation) * self.velocity))

    # new coordinates
    new_x = curr_x + x_delta
    new_y = curr_y + y_delta

    # update position
    self.position['x'] = new_x
    self.position['y'] = new_y

# intialize first generation of prey
prey = [Prey(prey_size, prey_color) for i in xrange(prey_pop)]

# Universe loop, draws a new frame every iteration
while 1:
  clock.tick(50)
 
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
 
  screen.fill(BLACK)

  box_x += box_dir
  if box_x >= 620:
    box_x = 620
    box_dir = -3
  elif box_x <= 0:
    box_x = 0
    box_dir = 3
 
  pygame.draw.rect(screen, WHITE, (box_x, 200, 20, 20))
  pygame.draw.circle(screen, WHITE, (box_x, 250), 20)

  # Draw all prey
  for p in prey:
    pygame.draw.circle(screen, WHITE, p.getPosition(), p.size)

  # Update Positions of all prey
  for p in prey:
    p.updatePosition()

  # Progress to the next frame of the universe
  pygame.display.flip()
