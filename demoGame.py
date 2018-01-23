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

# FONTS
pygame.font.init()
basic_font = pygame.font.SysFont(None, 12)

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

def printStats():
  # calc stats
  prey_eaten = sum([p.prey_eaten for p in predators])
  living_prey = PREY_POP - prey_eaten

  # init text object to display stats
  status = "Living prey: %s, Prey eaten: %s" % (living_prey, prey_eaten)
  text = basic_font.render(status, True, WHITE)
  textrect = text.get_rect()
  textrect.centerx = screen.get_rect().centerx
  textrect.centery = screen.get_rect().centery

  # print stats
  screen.blit(text, textrect)

# Universe loop, draws a new frame every iteration
while 1:
  clock.tick(50)
 
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
 
  screen.fill(BLACK)

  # Draw all organisms
  for p in prey:
    if p.isAlive():
      pygame.draw.circle(screen, p.color, p.getCoords(), p.size)

  for p in predators:
    pygame.draw.circle(screen, p.color, p.getCoords(), p.size)

  # Update Positions of all organisms
  for p in prey:
    p.calcSurvival(predators)
    p.updatePosition()

  for p in predators:
    p.updatePosition()

  printStats()

  # Progress to the next frame of the universe
  pygame.display.flip()
