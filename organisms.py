import math, random


class Organism(object):
  def __init__(self, o_type, size, color, velocity, max_x, max_y, vision_range):
    self.is_alive = True
    self.lifespan = 0

    # input variables
    self.o_type = o_type
    self.size = size # radius of organism
    self.base_color = color
    self.color = color
    self.velocity = velocity
    self.max_x = max_x
    self.max_y = max_y
    self.vision_range = vision_range # how far can organims see

    # add a brain
    self.brain = self.gen_brain()

    self.position = self.getRandomPosition()
    self.orientation = math.radians(random.randint(1, 360))

    # input layer
    self.senses = {
      # 'direction': [distance, isSame, isDiff]
      'above': [0.0, 0.0],
      'below': [0.0, 0.0],
      'left': [0.0, 0.0],
      'right': [0.0, 0.0]
    }

  def gen_brain(self):
    def brain(senses):
      return  math.radians(random.randint(1, 360))
        
    return brain

  def detectCollisions(self, p):
    # assume predator and prey are circles
    # check that distance between centers > sum of radii

    # self coordinates
    s_x = self.getX()
    s_y = self.getY()

    # other organism coords
    p_x = p.getX()
    p_y = p.getY()

    # how far apart are the organisms
    dist_bt_centers = math.sqrt((s_x - p_x)**2 + (s_y - p_y)**2)

    # Do they collide
    collision = dist_bt_centers <= self.size + p.size

    # Does self see other
    sees_p = dist_bt_centers <= self.size + p.size + self.vision_range

    # What direction is the other from self
    above, below, left, right, dist = False, False, False, False, 0.0
    if sees_p:
      # one of each direction pair must be <= to prevent blindspot
      above = s_y <= p_y
      below = s_y > p_y
      left = s_x <= p_x
      right = s_x > p_x
      dist = dist_bt_centers # only gets distance if p in sight range

    result = {
      'collision': collision,
      'sees_p': sees_p,
      'type': p.o_type,
      'above': above,
      'below': below,
      'left': left,
      'right': right,
      'dist': dist
    }

    return result

  def calcCollisions(self, organisms, handleCollision):
    saw_something = False
    for p in organisms:
      if id(self) == id(p):
        continue # Don't detect collisions with yourself

      if not p.is_alive:
        continue # Don't care about dead things

      data = self.detectCollisions(p)
      
      if data['collision']:
        # if self.o_type == 'pred' and p.o_type == 'prey':
        #  print "%s [%s], eats %s [%s]" % (id(self), self.o_type, id(p), p.o_type)
        handleCollision(p)

      if data['sees_p']:
        self.color = (255,255,255)
        saw_something = True
        for dirr in ['above', 'below', 'left', 'right']:
          if data[dirr]:
            self.activate(dirr, data['dist'], (self.o_type == data['type']))

    # reset color when out of sight range
    if not saw_something:
      self.color = self.base_color

  def activate(self, dirr, dist, is_same):
    # Vision activation values:
    # 1.0 -> collision
    # 0.0 -> nothing in range
    activation = 1.0 - float(dist) / float(self.vision_range)

    # only senses closes organism of type
    # first weight senses like organims, second weight senses different
    neuron = int(is_same)
    self.senses[dirr][neuron] = max(self.senses[dirr][neuron], activation)
 
  def getRandomPosition(self):
    x_coord = random.randint(0, self.max_x)
    y_coord = random.randint(0, self.max_y)
    return {'x': x_coord, 'y': y_coord}

  def getCoords(self):
    return (self.getX(), self.getY())

  def getX(self):
    return self.position['x']

  def getY(self):
    return self.position['y']

  def resetInputLayer(self):
    self.senses = {
      # 'direction': [same, other]
      'above': [0.0, 0.0],
      'below': [0.0, 0.0],
      'left': [0.0, 0.0],
      'right': [0.0, 0.0]
    }

  def updatePosition(self):
    # update lifespan to help judge fitness
    self.lifespan += 1

    # print "I'm a %s seeing %s" % (self.o_type, self.o_type)
    # current coordinates
    curr_x = self.getX()
    curr_y = self.getY()

    # reverse direction if prey hits a wall
    if curr_x <= 0 or curr_x >= self.max_x:
      self.velocity *= -1
    elif curr_y <= 0 or curr_y >= self.max_y:
      self.velocity *= -1

    # update orientation
    self.orientation = self.brain(self.senses)

    # how much organism will move in x and y direction?
    x_delta = int(round(math.cos(self.orientation) * self.velocity)) 
    y_delta = int(round(math.sin(self.orientation) * self.velocity))

    # new coordinates
    new_x = curr_x + x_delta
    new_y = curr_y + y_delta

    # update position
    self.position['x'] = new_x
    self.position['y'] = new_y

    # reset activations
    self.resetInputLayer()
    # print self.senses

class Prey(Organism):
  def __init__(self, o_type, size, color, velocity, max_x, max_y, vision):
    Organism.__init__(self, o_type, size, color, velocity, max_x, max_y, vision)

  def isAlive(self):
    return self.is_alive

  def calcCollisions(self, organisms):
    def handleCollision(o):
      if self.o_type != o.o_type:
        self.die()

    super(Prey, self).calcCollisions(organisms, handleCollision)

  def die(self):
    self.is_alive = False

class Predator(Organism):
  def __init__(self, o_type, size, color, velocity, max_x, max_y, vision):
    Organism.__init__(self, o_type, size, color, velocity, max_x, max_y, vision)
    self.prey_eaten = 0

  def calcCollisions(self, organisms):
    def handleCollision(o):
      if self.o_type != o.o_type:
        self.eatPrey()

    super(Predator, self).calcCollisions(organisms, handleCollision)

  def eatPrey(self):
    self.prey_eaten += 1

