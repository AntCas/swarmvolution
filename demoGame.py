import math
import pygame
import random
import sys

# COLORS
BLACK = 0, 0, 0
WHITE = 255, 255, 255
ORANGE = 255, 86, 0
BLUE = 0, 169, 255

# DIMENSIONS
CANVAS_HEIGHT = 480
CANVAS_WIDTH = 640 

# Box
box_x = 300
box_dir = 3

# Prey
PREY_POP = 50
PREY_SIZE = 2
PREY_VELOCITY = 2
PREY_COLOR = BLUE

# PREDATOR
PRED_POP = 5
PRED_SIZE = 5
PRED_VELOCITY = 5
PRED_COLOR = ORANGE

# Init Canvas
pygame.init()
screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
pygame.display.set_caption("Swarm Evolution")
clock = pygame.time.Clock()

class Organism:
  def __init__(self, size, color, velocity):
    self.size = size
    self.color = color
    self.velocity = velocity
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

class Prey(Organism):
  def __init__(self):
    Organism.__init__(self, PREY_SIZE, PREY_COLOR, PREY_VELOCITY)

class Predator(Organism):
  def __init__(self):
    Organism.__init__(self, PRED_SIZE, PRED_COLOR, PRED_VELOCITY)

# intialize first generation of prey and predators
prey = [Prey() for i in xrange(PREY_POP)]
predators = [Predator() for i in xrange(PRED_POP)]

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

  # Draw all organisms
  for p in prey:
    pygame.draw.circle(screen, p.color, p.getPosition(), p.size)

  for p in predators:
    pygame.draw.circle(screen, p.color, p.getPosition(), p.size)

  # Update Positions of all organisms
  for p in prey:
    p.updatePosition()

  for p in predators:
    p.updatePosition()

  # Progress to the next frame of the universe
  pygame.display.flip()
