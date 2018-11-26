import math, random, numpy


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
      return math.radians(random.randint(1, 360))
        
    return brain

  def detectCollisions(self, p):
    # assume predator and prey are circles
    # check that distance between centers > sum of radii

    # self coordinates
    s_x = self.getX()
    s_y = self.getY()
    S = numpy.array([s_x, s_y])

    # other organism coords
    p_x = p.getX()
    p_y = p.getY()
    P = numpy.array([p_x, p_y])

    # how far apart are the organisms
    # dist_bt_centers = math.sqrt((s_x - p_x)**2 + (s_y - p_y)**2)
    dist_bt_centers = numpy.linalg.norm(S-P)

    # Do they collide
    collision = dist_bt_centers <= self.size + p.size

    # Does self see other
    sees_p = dist_bt_centers <= (p.size + self.vision_range)

    dirr, sight_dist = None, 0

    if sees_p:
      # Direction is relative to self and depends on orientation
      # We are computing whether the point on the organism closest to us is within
      # each of our site wedges. Can only be seen by one wedge at a time.

      # Find point on organism closest to self (C)
      # https://math.stackexchange.com/questions/127613/closest-point-on-circle-edge-from-point-outside-inside-the-circle
      Cx = s_x + self.vision_range * (p_x - s_x) / dist_bt_centers 
      Cy = s_y + self.vision_range * (p_y - s_y) / dist_bt_centers 
      C = numpy.array([Cx, Cy])

      # Find distance between center of self and closest point on other organism (C)
      #sight_dist = math.sqrt((s_x - Cx)**2 + (s_y - Cy)**2)
      sight_dist = numpy.linalg.norm(S-C)

      # Get current vectors for each sight wedge
      D1x = sight_dist * math.cos(self.orientation) + s_x
      D1y = sight_dist * math.sin(self.orientation) + s_y

      # Since our sight vectors are perpendicular (normal) to each other
      # we can find the other wedges easily via rotation
      D1 = numpy.array([D1x, D1y])
      D2 = numpy.array([-D1y, D1x])
      D3 = numpy.array([-D1x, -D1y])
      D4 = numpy.array([D1y, -D1x])

      # For each sight wedge (defined by orientation and site_distance)
      # find whether closest point on organism (C) is within the wedge
      # https://stackoverflow.com/questions/13652518/efficiently-find-points-inside-a-circle-sector
      wedges = [
        ['above', D1],
        ['left',  D2],
        ['below', D3],
        ['right', D4]
      ]

      for i in range(len(wedges)):
        D = wedges[i][1]

        # Is C counter-clockwise of wedge starting arm?
        # i.e. projection of C onto counter-clockwise normal N of D positive?
        # Bc wedges are already normal to each other, we can just grab the
        # coords of neighboring wedge
        N = wedges[(i + 1) % len(wedges)][1]

        # Here we define the boundry bt wedges to be from defining vector up to
        # but not including next wedge 
        is_ccw = numpy.dot(C, N) >= 0

        # Is C clockwise of wedge ending arm?
        # wedges are already normal to each other
        is_cw = numpy.dot(C, D) > 0

        # Can only be true for one wedge
        if is_ccw and is_cw:
          dirr = wedges[i][0] 
          break

    result = {
      'collision': collision,
      'sees_p': sees_p,
      'type': p.o_type,
      'dirr': dirr,
      'dist': sight_dist
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
        self.activate(data['dirr'], data['dist'], (self.o_type == data['type']))

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

