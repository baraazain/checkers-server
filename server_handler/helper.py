import pickle


def get_player_by_sid(sid, all_player_connecting):
    for key in all_player_connecting:
        if all_player_connecting[key].sid == sid:
            return all_player_connecting[key]
    return None


def get_game_by_sid(id, all_game_playing):
    for key in all_game_playing:
        if all_game_playing[key].id == id:
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


def load_players():
    with open('../players.dat', 'rb') as file:
        return pickle.load(file)


def save_players(players):
    with open('../players.dat', 'wb') as file:
        pickle.dump(players, file)


def load_games():
    with open('../games.dat', 'rb') as file:
        return pickle.load(file)


def save_games(games):
    with open('../games.dat', 'wb') as file:
        pickle.dump(games, file)


def load_contest():
    with open('../contest.dat', 'rb') as file:
        return pickle.load(file)


def save_contest(contests):
    with open('../contest.dat', 'wb') as file:
        pickle.dump(contests, file)
