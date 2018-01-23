# system imports
import math
import pygame
import random
import sys

# local imports
from organisms import Prey, Predator

# COLORS
BLACK = 0, 0, 0
WHITE = 255, 255, 255
ORANGE = 255, 86, 0
BLUE = 0, 169, 255

# DIMENSIONS
CANVAS_HEIGHT = 480
CANVAS_WIDTH = 640 

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

# intialize first generation of prey and predators
prey = [Prey(PREY_SIZE, PREY_COLOR, PREY_VELOCITY, CANVAS_WIDTH, CANVAS_HEIGHT) for i in xrange(PREY_POP)]
predators = [Predator(PRED_SIZE, PRED_COLOR, PRED_VELOCITY, CANVAS_WIDTH, CANVAS_HEIGHT) for i in xrange(PRED_POP)]

# Universe loop, draws a new frame every iteration
while 1:
  clock.tick(50)
 
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
 
  screen.fill(BLACK)

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
