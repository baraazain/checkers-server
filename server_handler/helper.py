import os
import pickle


def get_player_by_sid(sid, all_player_connecting):
    for key in all_player_connecting:
        if all_player_connecting[key].sid == sid:
            return all_player_connecting[key]
    return None


def get_game_by_sid(_id, all_game_playing):
    for key in all_game_playing:
        if all_game_playing[key].id == _id:
            return all_game_playing[key]
    return None


def get_player_by_name(name):
    players = load_players()
    for player in players:
        if player.name == name:
            return player
    return None


def get_player_by_id(_id):
    players = load_players()
    for player in players:
        if player.id == _id:
            return player
    return None


def get_game_by_id(_id):
    games = load_games()
    for game in games:
        if game.id == _id:
            return game

    return None


def get_contest_by_id(_id):
    contests = load_contest()
    for contest in contests:
        if contest.id == _id:
            return contest
    return None


def load_players():
    with open('../players.dat', 'rb') as file:
        if os.path.getsize('../players.dat') == 0:
            print('File is  empty')
            return []
        else:
            print('File is not empty')
            players: list = pickle.load(file)
            return sorted(players, key=lambda x: x.id)


def save_players(players):
    with open('../players.dat', 'wb') as file:
        pickle.dump(players, file)


def load_games():
    with open('../games.dat', 'rb') as file:
        if os.path.getsize('../games.dat') == 0:
            print('File is  empty')
            return []
        else:
            print('File is not empty')
            games: list = pickle.load(file)
            return sorted(games, key=lambda x: x.id)


def save_games(games):
    with open('../games.dat', 'wb') as file:
        pickle.dump(games, file)


def load_contest():
    with open('../contests.dat', 'rb') as file:
        if os.path.getsize('../contest.dat') == 0:
            print('File is  empty')
            return []
        else:
            print('File is not empty')
            contests: list = pickle.load(file)
            return sorted(contests, key=lambda x: x.id)


def save_contest(contests):
    with open('../contests.dat', 'wb') as file:
        pickle.dump(contests, file)


def save_contest_available(contests):
    with open('../contests_available.dat', 'wb') as file:
        pickle.dump(contests, file)


def load_contest_available():
    with open('../contests_available.dat', 'rb') as file:
        if os.path.getsize('../contest_available.dat') == 0:
            print('File is  empty')
            return []
        else:
            print('File is not empty')
            contests: list = pickle.load(file)
            return sorted(contests, key=lambda x: x.id)


def remove_contest_available(_id):
    contests = load_contest_available()
    for contest in contests:
        if contest.id == _id:
            contests.remove(contest)
    save_contest_available(contests)


def print_players():
    with open('../players.dat', 'rb') as file:
        if os.path.getsize('../players.dat') == 0:
            print('File is  empty')
            return []
        else:
            print('File is not empty')
            players: list = pickle.load(file)
            p = sorted(players, key=lambda x: x.id)
            for i in p:
                print(i.id, i.name, i.password)


def print_games():
    with open('../games.dat', 'rb') as file:
        if os.path.getsize('../games.dat') == 0:
            print('File is  empty')
            return []
        else:
            print('File is not empty')
            games: list = pickle.load(file)
            p = sorted(games, key=lambda x: x.id)
            for i in p:
                print(i.id)


def print_contests():
    with open('../contests.dat', 'rb') as file:
        if os.path.getsize('../contests.dat') == 0:
            print('File is  empty')
            return []
        else:
            print('File is not empty')
            contests: list = pickle.load(file)
            c = sorted(contests, key=lambda x: x.id)
            for i in c:
                print(i.id, i.name, i.date, i.mode)


def remove_players():
    with open('../players.dat', 'wb') as file:
        pickle.dump([], file)


def remove_contests():
    with open('../contests.dat', 'wb') as file:
        pickle.dump([], file)
