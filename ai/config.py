#### SELF PLAY
MAXIMIZER = 0
EPISODES = 1
MCTS_SIMS = 50
TURNS_UNTIL_TAU0 = 10 # turn on which it starts playing deterministically
CPUCT = 1
EPSILON = 0.75
ALPHA = 0.8

#resNet hyperparameters
BATCH_SIZE = 256
EPOCHS = 1
REG_CONST = 0.0001
LEARNING_RATE = 0.1
TRAINING_LOOPS = 10

HIDDEN_CNN_LAYERS = [
    {'filters':75, 'kernel_size': (3,3)},
    {'filters':75, 'kernel_size': (3,3)},
    {'filters':75, 'kernel_size': (3,3)},
    {'filters':75, 'kernel_size': (3,3)},
    {'filters':75, 'kernel_size': (3,3)},
    {'filters':75, 'kernel_size': (3,3)}
    ]

#### EVALUATION
EVAL_EPISODES = 20
SCORING_THRESHOLD = 55