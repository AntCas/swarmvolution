import math, random, numpy as np

PREY = 'prey'
PRED = 'pred'
ABOVE = 'above'
BELOW = 'below'
LEFT = 'left'
RIGHT = 'right'


class Organism(object):
  def __init__(self, o_type, size, color, velocity, max_x, max_y, vision_range, dna=None):
    self.is_alive = True
    self.score = 0

    # input variables
    self.o_type = o_type
    self.size = size # radius of organism
    self.base_color = color
    self.color = color
    self.velocity = velocity
    self.max_x = max_x
    self.max_y = max_y
    self.vision_range = vision_range # how far can organims see

    # initialize dna (defined as weights that control brain function)
    if dna:
      self.dna = dna
    else:
      self.dna = np.random.rand(40) # 40 = len(L) + len(O)

    L, O = np.split(self.dna, [32]) # 32 = len(L) = num_nodes_hidden * num_nodes_input
    L = np.split(L, 8) #
    O = np.split(O, 4) # 

    # Add the brain
    self.brain = self.gen_brain(L, O)
    #self.brain = self.gen_brain_dumb()

    self.position = self.getRandomPosition()
    self.orientation = math.radians(random.randint(1, 360))

    # input layer
    self.senses = {
      # 'direction': [distance, isSame, isDiff]
      ABOVE: [0.0, 0.0],
      BELOW: [0.0, 0.0],
      LEFT: [0.0, 0.0],
      RIGHT: [0.0, 0.0]
    }

  def isAlive(self):
    return self.is_alive

  # perceptron driven brain
  def gen_brain(self, hl_weights, ol_weights):
    def sigmoid(x):
      return 1 / (1 + np.exp(-x))

    def relu(x):
      return x * (x > 0)

    def brain(senses):
      input_layer = np.concatenate(senses.values())
      hidden_layer = relu(np.dot(input_layer, hl_weights))
      output_layer = sigmoid(np.dot(hidden_layer, ol_weights))
      return output_layer

    return brain

  # procedural if/then dumb brain
  def gen_brain_dumb(self):
    def brain(senses):
      # flee different if prey
      # turn away from closest different
      curr_max_same = 0
      max_dirr_same = None
      curr_max_diff = 0
      max_dirr_diff = None

      is_pred = True if self.o_type == PRED else False

      for sense in senses:
        if senses[sense][0] > curr_max_diff:
          curr_max_diff = senses[sense][0]
          max_dirr_diff = sense
        if senses[sense][1] > curr_max_same:
          curr_max_same = senses[sense][1]
          max_dirr_same = sense

      if not max_dirr_diff:
        if not max_dirr_same:
          return [0, 0]
        elif max_dirr_same == ABOVE or max_dirr_same == LEFT:
          return [0, .1] if is_pred else [.1, 0]
        elif max_dirr_same == RIGHT or max_dirr_same == BELOW:
          return [.1, 0] if is_pred else [0, .1]
      elif max_dirr_diff == ABOVE or max_dirr_diff == LEFT:
        return [0, .1] if is_pred else [.1, 0]
      elif max_dirr_diff == RIGHT or max_dirr_diff == BELOW:
        return [.1, 0] if is_pred else [0, .1]
          
      return self.orientation
        
    return brain

  def detectCollisions(self, p):
    # assume predator and prey are circles
    # check that distance between centers > sum of radii

    # self coordinates
    s_x = self.getX()
    s_y = self.getY()
    S = np.array([s_x, s_y])

    # other organism coords
    p_x = p.getX()
    p_y = p.getY()
    P = np.array([p_x, p_y])

    # how far apart are the organisms
    # dist_bt_centers = math.sqrt((s_x - p_x)**2 + (s_y - p_y)**2)
    dist_bt_centers = np.linalg.norm(S-P)

    # Do they collide
    collision = dist_bt_centers <= self.size + p.size

    # Does self see other
    sees_p = dist_bt_centers <= (p.size + self.vision_range)

    dirr, sight_dist = None, 0

    if sees_p and not collision:
      # Direction is relative to self and depends on orientation
      # We are computing whether the point on the organism closest to us is within
      # each of our site wedges. Can only be seen by one wedge at a time.

      # Find point on organism closest to self (C)
      # https://math.stackexchange.com/questions/127613/closest-point-on-circle-edge-from-point-outside-inside-the-circle
      Cx = s_x + self.vision_range * (p_x - s_x) / dist_bt_centers 
      Cy = s_y + self.vision_range * (p_y - s_y) / dist_bt_centers 
      C = np.array([Cx, Cy])

      # Find distance between center of self and closest point on other organism (C)
      #sight_dist = math.sqrt((s_x - Cx)**2 + (s_y - Cy)**2)
      sight_dist = np.linalg.norm(S-C)

      # Get current vectors for each sight wedge
      D1x = sight_dist * math.cos(self.orientation) + s_x
      D1y = sight_dist * math.sin(self.orientation) + s_y

      # Since our sight vectors are perpendicular (normal) to each other
      # we can find the other wedges easily via rotation
      D1 = np.array([D1x, D1y])
      D2 = np.array([-D1y, D1x])
      D3 = np.array([-D1x, -D1y])
      D4 = np.array([D1y, -D1x])

      # For each sight wedge (defined by orientation and site_distance)
      # find whether closest point on organism (C) is within the wedge
      # https://stackoverflow.com/questions/13652518/efficiently-find-points-inside-a-circle-sector
      wedges = [
        [ABOVE, D1],
        [LEFT,  D2],
        [BELOW, D3],
        [RIGHT, D4]
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
        is_ccw = np.dot(C, N) >= 0

        # Is C clockwise of wedge ending arm?
        # wedges are already normal to each other
        is_cw = np.dot(C, D) >= 0

        # Can only be true for one wedge
        if is_ccw and is_cw:
          dirr = wedges[i][0] 
          break

    if sees_p and not dirr:
      sees_p = False

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
        # if self.o_type == PRED and p.o_type == PREY:
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

    # only senses closest organism of type
    # first weight senses like organisms, second weight senses different organisms
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
      ABOVE: [0.0, 0.0],
      BELOW: [0.0, 0.0],
      LEFT: [0.0, 0.0],
      RIGHT: [0.0, 0.0]
    }

  def updatePosition(self):
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
    steering = self.brain(self.senses)

    if steering[0] > steering[1]:
      self.orientation -= .1
    elif steering[0] < steering[1]:
      self.orientation += .1

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
  def __init__(self, o_type, size, color, velocity, max_x, max_y, vision, dna=None):
    Organism.__init__(self, o_type, size, color, velocity, max_x, max_y, vision, dna)

  def calcCollisions(self, organisms):
    def handleCollision(o):
      if self.o_type != o.o_type:
        self.die()

    super(Prey, self).calcCollisions(organisms, handleCollision)

    if self.is_alive:
      self.score += 1

  def die(self):
    self.is_alive = False

class Predator(Organism):
  def __init__(self, o_type, size, color, velocity, max_x, max_y, vision, dna=None):
    Organism.__init__(self, o_type, size, color, velocity, max_x, max_y, vision, dna)

  def calcCollisions(self, organisms):
    def handleCollision(o):
      if self.o_type != o.o_type:
        self.eatPrey()

    super(Predator, self).calcCollisions(organisms, handleCollision)

  def eatPrey(self):
    self.score += 1

