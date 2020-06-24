# Training settings
CURRENT_VERSION = None
CURRENT_DATASET = None

# ========================= HYPERPARAMETERS ===============================

# Self-play
EPISODES = 50  # How many games
MCTS_SIMS = 60
TURNS_UNTIL_TAU0 = 30  # turn on which it starts playing deterministically, to give the strongest possible play
CPUCT = 1  # constant determining the level of exploration
EPSILON = 0.25  # Dirichlet noise amount
ALPHA = 0.8  # prior probability
DATA_LEN = 10000

# Evaluation
EVAL_EPISODES = 20
SCORING_THRESHOLD = 55  # winning ratio after which we replace the best version AlphaZero

# Training
REG_CONST = 0.0001  # regularization
LEARNING_RATE = 0.1
BATCH_SIZE = 256
TRAINING_LOOPS = 10

# ========================================================================
