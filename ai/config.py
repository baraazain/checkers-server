# Training settings
CURRENT_VERSION = 1
CURRENT_DATASET = None


# Constants
MAXIMIZER = 1

# ========================= HYPERPARAMETERS ===============================

# Self-play
EPISODES = 1 # How many games
MCTS_SIMS = 50
TURNS_UNTIL_TAU0 = 10  # turn on which it starts playing deterministically
CPUCT = 1 # constant determining the level of exploration 
EPSILON = 0.25 # Dirichlet noise amount
ALPHA = 0.8 # prior probability

# resNet 
BATCH_SIZE = 256
EPOCHS = 1
REG_CONST = 0.0001
LEARNING_RATE = 0.1
TRAINING_LOOPS = 10

HIDDEN_CNN_LAYERS = [
    {'filters': 75, 'kernel_size': (3, 3)},
    {'filters': 75, 'kernel_size': (3, 3)},
    {'filters': 75, 'kernel_size': (3, 3)},
    {'filters': 75, 'kernel_size': (3, 3)},
    {'filters': 75, 'kernel_size': (3, 3)},
    {'filters': 75, 'kernel_size': (3, 3)},
]

# Evaluation 
EVAL_EPISODES = 20
SCORING_THRESHOLD = 55

# ========================================================================
