import math, random

class Organism:
  def __init__(self, size, color, velocity, max_x, max_y):
    self.size = size
    self.color = color
    self.velocity = velocity
    self.max_x = max_x
    self.max_y = max_y
    self.position = self.getRandomPosition()
    self.orientation = math.radians(random.randint(1, 360))

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

  def updatePosition(self):
    # current coordinates
    curr_x = self.getX()
    curr_y = self.getY()

    # reverse direction if prey hits a wall
    if curr_x <= 0 or curr_x >= self.max_x:
      self.velocity *= -1
    elif curr_y <= 0 or curr_y >= self.max_y:
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
  def __init__(self, size, color, velocity, max_x, max_y):
    Organism.__init__(self, size, color, velocity, max_x, max_y)
    self.is_alive = True

  def isAlive(self):
    return self.is_alive

  def calcSurvival(self, predators):
    def isEatenBy(p):
        # assume predator and prey are circles
        # check that distance between centers > sum of radii
        prey_x = self.getX()
        prey_y = self.getY()
        pred_x = p.getX()
        pred_y = p.getY()

        return math.sqrt((prey_x - pred_x)**2 + (prey_y - pred_y)**2) <= self.size + p.size

    for p in predators:
        if isEatenBy(p):
            self.is_alive = False
            break

class Predator(Organism):
  def __init__(self, size, color, velocity, max_x, max_y):
    Organism.__init__(self, size, color, velocity, max_x, max_y)

