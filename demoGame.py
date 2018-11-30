# system imports
import argparse
import hashlib
import itertools
import math
import numpy as np
import pygame
import random
import sys

# local imports
from organisms import Prey, Predator

# ---------------- HYPER-PARAMETERS ---------------

# COLORS
BLACK = 0, 0, 0
WHITE = 255, 255, 255
ORANGE = 255, 86, 0
BLUE = 0, 169, 255

# DIMENSIONS 
CANVAS_HEIGHT = 480 #480
CANVAS_WIDTH = 640 #640

# Prey
PREY_TYPE = 'prey'
PREY_POP = 50
PREY_SIZE = 2
PREY_VELOCITY = 1
PREY_COLOR = BLUE
PREY_VISION = 40

# PREDATOR
PRED_TYPE = 'pred'
PRED_POP = 5
PRED_SIZE = 6
PRED_VELOCITY = 3
PRED_COLOR = ORANGE
PRED_VISION = 40

# UNIVERSE
GEN_TIME_LIMIT = 850
GENERATIONS = 1000

# EVOLUTION
MUTATION_RATE = .01


# ---------------- STATS & LOGS ---------------

def getStats(predators, prey, generation):
  # calc stats
  prey_eaten = sum([p.score for p in predators])
  living_prey = PREY_POP - prey_eaten
  avg_lifespan_prey = sum([p.score for p in prey]) / PREY_POP

  # init text object to display stats
  stats = ("Gen [%s of %s] | Living prey: %s, Prey eaten: %s, Avg prey lifespan: %s"
            % (generation, GENERATIONS, living_prey, prey_eaten, avg_lifespan_prey))

  return stats

def printStatsToScreen(predators, prey, generation):
  text = basic_font.render(getStats(predators, prey, generation), True, WHITE)
  textrect = text.get_rect()
  textrect.centerx = screen.get_rect().centerx
  textrect.centery = screen.get_rect().centery

  # print stats
  screen.blit(text, textrect)

# ---------------- DRAW & UPDATE ---------------

def drawOrganisms(organisms):
  for p in organisms:
    if p.isAlive():
      pygame.draw.circle(screen, p.color, p.getCoords(), p.size)

def updatePositions(predators, prey):
  # We handle collissions for both types before updating positions so that
  # the world state doesn't change for one set of organisms before the other

  # predators must be processed first so that they can eat before their prey dies
  for o in itertools.chain(predators, prey):
    if o.is_alive:
      o.calcCollisions(itertools.chain(predators, prey))

  for o in itertools.chain(predators, prey):
    if o.is_alive:
      o.updatePosition()

# ---------------- GENETICS ---------------

def new_pred(dna=None):
  return Predator(PRED_TYPE, PRED_SIZE, PRED_COLOR, PRED_VELOCITY, CANVAS_WIDTH, CANVAS_HEIGHT, PRED_VISION, dna)

def new_prey(dna=None):
  return Prey(PREY_TYPE, PREY_SIZE, PREY_COLOR, PREY_VELOCITY, CANVAS_WIDTH, CANVAS_HEIGHT, PREY_VISION, dna)

# randomly mutates a gene some percentage of the time
def mutate(gene, rate):
    if random.random() < rate:
        return random.random()
    else:
        return gene

# breeds two organisms
def breed(mother, father, species):
    # A child randomly inherits each gene (weight) from either the mother or the father
    child_dna = [0] * len(mother.dna)
    for i in xrange(len(mother.dna)):
        child_dna[i] = mother.dna[i] if random.random() < .5 else father.dna[i]
        child_dna[i] = mutate(child_dna[i], MUTATION_RATE)

    if species == PREY_TYPE:
      return new_prey(child_dna)
    else:
      return new_pred(child_dna)

# assigns each organism a breeding potential based on its relative fitness
def gen_gene_pool(generation):
    # each organism gets exactly the share of the gene pool it contributes
    total_fitness = sum(o.score for o in generation)

    # sometimes predators didn't get to eat anything, so they're all equally fit
    if total_fitness == 0:
      gene_pool = [(o, 1 / len(generation)) for o in generation]
    else:
      gene_pool = [(o, o.score / float(total_fitness)) for o in generation]
    return gene_pool

# selects an organism to be a father based on its relative fitness
# source: http://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
def select_father(gene_pool):
    total = sum(w for c, w in gene_pool)
    r = random.uniform(0, total)
    upto = 0
    for c, w in gene_pool:
        if upto + w >= r:
            return c
        upto += w
    print gene_pool
    assert False, "Shouldn't get here" # No more diversity left in the gene pool

def next_generation(gen, species):
  next_gen = [None] * len(gen)

  # create the gene_pool roulette wheel
  gene_pool = gen_gene_pool(gen)

  # each organism gets to breed once (mother a signle offspring)
  # strong organisms have better chance to breed again (father multiple offspring)
  for i in xrange(len(gen)):
    father = select_father(gene_pool)
    next_gen[i] = breed(gen[i], father, species)

  return next_gen

def next_pred_generation(pred_gen):
  if len(pred_gen) is 0: 
    if args.predDna is not None:
      with open(args.predDna, 'r') as o:
        pred_dna = np.load(o)
        return [new_pred(pred_dna[i]) for i in xrange(len(pred_dna))]
    return [new_pred() for i in xrange(PRED_POP)]
  return next_generation(pred_gen, PRED_TYPE)

def next_prey_generation(prey_gen):
  if len(prey_gen) is 0:
    if args.preyDna is not None:
      with open(args.preyDna, 'r') as o:
        prey_dna = np.load(o)
        return [new_prey(prey_dna[i]) for i in xrange(len(prey_dna))]
    return [new_prey() for i in xrange(PREY_POP)]
  return next_generation(prey_gen, PREY_TYPE)

# ---------------- RUN THE UNIVERSE ---------------

# ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("--blind", action="store_true", help="don't show the gameworld")
parser.add_argument("--predDna", help="load pre-trained predator dna from file")
parser.add_argument("--preyDna", help="load pre-trained prey dna from file")
args = parser.parse_args()

show_world = not args.blind

if show_world:
  # init font
  pygame.font.init()
  basic_font = pygame.font.SysFont(None, 12)

  # init canvas
  pygame.init()
  screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
  pygame.display.set_caption("Swarm Evolution")

  # init clock
  clock = pygame.time.Clock()

prey, pred = [], []

# Generation loop
for i in xrange(GENERATIONS):
  prey = next_prey_generation(prey)
  pred = next_pred_generation(pred)

  # Universe loop, draws a new frame every iteration
  for j in xrange(GEN_TIME_LIMIT):
    if show_world:
      clock.tick() # can pass an int (max framerate) to tick() to slow down time
     
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          sys.exit()
   
      screen.fill(BLACK)
      drawOrganisms(itertools.chain(pred, prey)) 
      printStatsToScreen(pred, prey, i)

      # Progress to the next frame of the universe
      pygame.display.flip()

    updatePositions(pred, prey)

  print getStats(pred, prey, i)

  # save brains every 100 generations
  if ((i+1) % 25 == 0):
    # Save the brains
    prey_dna = np.array([p.dna for p in prey])
    pred_dna = np.array([p.dna for p in pred])

    id_str = hashlib.md5(str(prey_dna)+str(pred_dna)).hexdigest()

    with open('prey_dna_gen_%s_%s.npy' % (i+1, id_str), 'w') as o:
      np.save(o, prey_dna)

    with open('pred_dna_gen_%s_%s.npy' % (i+1, id_str), 'w') as o:
      np.save(o, pred_dna)
