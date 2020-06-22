# def simulate(mct):
#     for _ in range(200):
#         mct.simulate()
#     return mct


def main():
    print('Hello, World')
    # tree_error = None
    # reject_error = None
    # with tf.device('/device:GPU:0'):
    #     start_time = time.monotonic()
    #     try:
    #         train_manger(1)
    #     except RejectedActionError as reject_e:
    #         print('rejected')
    #         reject_error = reject_e
    #     except TreeError as tree_e:
    #         print('search error')
    #         tree_error = tree_e
    #     print(f'slept for {time.monotonic() - start_time}')

    # game = InternationalGame(1, MonteCarloAgent(0.3), MonteCarloAgent(0.7), None)
    # game = InternationalGame(1, MiniMaxAgent(1, 3, 1), MiniMaxAgent(2, 3, 1), None)
    # game.init()
    #
    # game.player1.on_start(game)
    # game.player2.on_start(game)
    # while not game.end():
    #     action = game.get_current_player().act(game)
    #
    #     while not game.is_legal_action(action):
    #         action = game.get_current_player().act(game)
    #     game.apply_action(action)
    #
    #     game.player1.on_update(action)
    #     game.player2.on_update(action)
    #
    #     print(game.grid)
    # game.print_the_winner()

    # from ai.alpha_beta_search import AlphaBetaSearch
    # from ai.utils import GameState
    # search = AlphaBetaSearch(GameState(game))
    # search.get_best_action()
    #
    # print(len(search.tree))
    # print(len(search.transposition_table))

    #
    # game = InternationalGame(1, None, None, None)
    # game.init()

    # mct = pts.ParallelMCTree(uty.GameState(game))
    # mct1 = pts.ParallelMCTree(uty.GameState(game))
    # mct2 = pts.ParallelMCTree(uty.GameState(game))
    # mct3 = pts.ParallelMCTree(uty.GameState(game))
    #
    # start_t = time.monotonic()
    #
    # with mp.Pool() as p:
    #     mct, mct1, mct2, mct3 = p.map(simulate, [mct, mct1, mct2, mct3])
    # mct.dfs(mct.root, mct1.root)
    # mct.dfs(mct.root, mct2.root)
    # mct.dfs(mct.root, mct3.root)
    #
    # print(time.monotonic() - start_t)
    #
    # mct4 = pts.ParallelMCTree(uty.GameState(game))
    #
    # start_t = time.monotonic()
    #
    # for _ in range(200):
    #     #start_t1 = time.monotonic()
    #     mct4.simulate()
    #     #print(time.monotonic() - start_t1)
    #
    # print(time.monotonic() - start_t)
    #
    # print(len(mct.tree))


if __name__ == '__main__':
    main()
