import time
import multiprocessing as mp

import ai.parallel_tree_search as pts
import ai.utils as uty
from model.international_game import InternationalGame


def simulate(mct):
    for _ in range(200):
        mct.simulate()
    return mct


def main():
    game = InternationalGame(1, None, None, None)
    game.init()
    mct = pts.MCTree(uty.GameState(game))
    mct1 = pts.MCTree(uty.GameState(game))
    mct2 = pts.MCTree(uty.GameState(game))
    mct3 = pts.MCTree(uty.GameState(game))
    mct4 = pts.MCTree(uty.GameState(game))

    start_t = time.monotonic()
    with mp.Pool() as p:
        mct, mct1, mct2, mct3, mct4 = p.map(simulate, [mct, mct1, mct2, mct3, mct4])
    mct.dfs(mct.root, mct1.root)
    mct.dfs(mct.root, mct2.root)
    mct.dfs(mct.root, mct3.root)
    mct.dfs(mct.root, mct4.root)
    print(time.monotonic() - start_t)

    mct5 = pts.MCTree(uty.GameState(game))
    start_t = time.monotonic()
    for _ in range(800):
        mct5.simulate()
    print(time.monotonic() - start_t)

    # print(len(mct.tree)))


if __name__ == '__main__':
    main()
