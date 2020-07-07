import json
import random
import time
from copy import deepcopy
from typing import Optional

import numpy as np
import tensorflow.keras as tk

import ai.config as config
import ai.utils as ut
import model.game as cgm
from ai.agent import AlphaZero
from model.international_game import InternationalGame


def get_models():
    current = ut.load_best_model()
    best = ut.load_best_model()
    best.set_weights(current.get_weights())
    return current, best


class RejectedActionError(Exception):
    def __init__(self, action, game, tau, agent, other_agent):
        self.action = action
        self.game = game
        self.tau = tau
        self.agent = agent
        self.other_agent = other_agent


class TreeError(Exception):
    def __init__(self, action_id, game, tau, agent, other_agent):
        self.action_id = action_id
        self.game = game
        self.tau = tau
        self.other_agent = other_agent
        self.agent = agent


# random.seed(101)
# np.random.seed(101)
# tf.random.set_seed(101)


def play_match(model: tk.models.Model,
               other_model: Optional[tk.models.Model] = None, turns_until_tau0=0):
    self_play = True if other_model is None else False

    current_game = InternationalGame(1, None, None, None)
    sample_builder = ut.SampleBuilder()

    current_game.init()

    agent = AlphaZero(config.MCTS_SIMS)

    if not self_play:
        other_agent = AlphaZero(config.MCTS_SIMS)
    else:
        other_agent = None

    agent.build_mct(ut.GameState(deepcopy(current_game)), model)

    if not self_play:
        other_agent.build_mct(ut.GameState(deepcopy(current_game)), other_model)

    turn = 0
    while not current_game.end():
        if not self_play:
            current_agent = agent if current_game.current_turn == 1 else other_agent
        else:
            current_agent = agent

        tau = 1 if turn < turns_until_tau0 else 0

        try:
            action, flip_flag, state_stack, value, pi = current_agent.train_act(tau)
        except KeyError as e:
            raise TreeError(e.args[0], current_game, tau, agent, other_agent)

        if not current_game.is_legal_action(action):
            raise RejectedActionError(action, current_game, tau, agent, other_agent)

        current_game.apply_action(action)
        if state_stack.head is None:
            raise TreeError(None, current_game, tau, agent, other_agent)
        sample_builder.add_move(state_stack, pi)

        current_agent.on_update(action)

        if not self_play:
            other_agent.on_update(action)

        turn += 1

        if flip_flag:
            current_game.current_turn = 3 - current_game.current_turn

        print('*', end='' if turn % 20 != 0 else '\n')

    print()

    winner = current_game.get_winner()

    if winner == 1:
        winner = 'agent'
    elif winner == 2:
        winner = 'other'
    else:
        winner = 'draw'

    value = ut.evaluate(current_game)

    sample_builder.commit_sample(value, cgm.MAXIMIZER)

    return sample_builder, winner


def train_batches(mini_batch, batch_size):
    training_states = np.array([sample['state'].get_deep_representation_stack() for sample in mini_batch])

    training_targets = {'value_head': np.array([sample['value'] for sample in mini_batch]),
                        'policy_head': np.array([sample['policy'] for sample in mini_batch])}

    indices = [i for i in range(len(training_states))]
    random.shuffle(indices)
    for i in range(len(indices)):
        start = indices[i] * batch_size
        end = start + batch_size

        yield training_states[start:end], {'value_head': training_targets['value_head'][start:end],
                                           'policy_head': training_targets['policy_head'][start:end]}


def fit(model, samples):
    overall_loss = []
    value_loss = []
    policy_loss = []
    for i in range(config.TRAINING_LOOPS):
        mini_batch = random.sample(samples, min(config.BATCH_SIZE, len(samples)))
        for x_train, y_train in train_batches(mini_batch, 32):
            res = model.train_on_batch(x=x_train, y=y_train, return_dict=True)
            overall_loss.append(res['loss'])
            value_loss.append(res['value_head_loss'])
            policy_loss.append(res['policy_head_loss'])
    return overall_loss, value_loss, policy_loss


def generate_data():
    iteration = 0

    dataset = ut.SampleBuilder()

    current_NN = ut.load_best_model()

    while True:

        for i in range(config.EPISODES):
            print(f'Episode {i + 1} started')
            start_time = time.monotonic()
            sb, _ = play_match(current_NN, turns_until_tau0=config.TURNS_UNTIL_TAU0)
            dataset.samples.extend(sb.samples)
            print(f'Episode {i + 1} ended in {(time.monotonic() - start_time) / 60} minutes')

        size = len(dataset.samples)
        dataset.save(iteration, ''.join([ut.archive_folder, '/tmp']))
        print(f'Gathered {size} sample')

        iteration += 1


def evaluate(best_version, current_NN, best_NN):
    score = {'agent': 0, 'draw': 0, 'other': 0}

    for i in range(config.EVAL_EPISODES):
        print(f'Evaluation episode {i + 1} started')
        start_time = time.monotonic()
        _, winner = play_match(current_NN, best_NN)
        score[winner] += 1
        print(f'Evaluation episode {i + 1} ended in {(time.monotonic() - start_time) / 60} minutes')

    ratio = score['agent'] * 100 // config.EVAL_EPISODES

    print(f'current version win ration: {ratio}')

    if ratio >= config.SCORING_THRESHOLD:
        best_NN.set_weights(current_NN.get_weights())
        best_version = best_version + 1
        ut.save_model(best_NN, version=best_version)
        print('Saving a new version')


def train(current_NN, dataset, iteration):
    try:
        with open('data/alphazero/loss.json', 'r') as f:
            try:
                mp = json.load(f)
            except json.JSONDecodeError:
                mp = {}
    except FileNotFoundError:
        mp = {}

    overall_loss, value_loss, policy_loss = fit(current_NN, dataset.samples)

    mp[f'iteration {iteration}'] = {'overall_loss': overall_loss,
                                    'value_loss': value_loss,
                                    'policy_loss': policy_loss}

    with open('data/alphazero/loss.json', 'w') as f:
        json.dump(mp, f, indent=4)


def merge_datasets(path):
    pass
