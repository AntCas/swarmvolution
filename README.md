# swarmvolution
Will a group of neural-nets with aligned interests evolve cooperative behavior?

# Demo Instructions

Run the simulator:

`python demoGame.py`

Run the simulation without visualization:

`python demoGame.py --blind`


# Experiment

You can adjust hyperparameters at the top of `demoGame.py`

You can modify how the organisms breed, what activation functions the neural net uses, and otherwise mess with the organism code in `organisms.py`


# DONE:
* game world
* naive predator and prey organisms
* predators eat prey
* print stats, argparse
* Implement organism vision
* have one iteration pass to detect all organism collision (instead of 4)
* move behavior decisions into the organism classes
* add organism type (PREY, PREDATOR) to organism class attributes
* fix stats summary (double counting things currently)
* implement nn brains
* implement dna
* Implement fitness functions for prey and predators
* Add control via neural-net
* Implement genetic algorithm

# TODO:
* Make more parameters and hyperparameters accesible from command line
* Pickle neural-nets/universe for later use
* Refactor code to be less monolithic
* Make it easier to change placement of sensors
* Make it easier to change neural net
