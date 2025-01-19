from pymongo import MongoClient
from pickle import loads, dumps

class Database:
    def __init__(self, connection_token):
        self.client = MongoClient(connection_token)
        self.db = self.client['discord_bot_db']
        self.users = self.db['users']

    def game_to_serial(self, game):
        if game:
            serial = dumps(game)
            return serial
        return None
    
    def serial_to_game(self, serial):
        if serial:
            game = loads(serial)
            return game
        return None

    def find_user(self, id):
        query = {'_id': id}
        return self.users.find_one(query)

    def insert_user(self, id, game, total_games=0, score=[0,0,0,0,0,0]):
        serial = self.game_to_serial(game)
        data = { '_id': id, 'total_games': total_games, 'score': score, 'game_serial': serial}
        self.users.insert_one(data)

    def update_user_game(self, id, game):
        serial = self.game_to_serial(game)
        query = {'_id': id}
        new_game = { "$set": {'game_serial': serial}}
        self.users.update_one(query, new_game)

    def update_user_score(self, id, score):
        query = {'_id': id}
        new_score = { "$set": {'score': score}}
        self.users.update_one(query, new_score)

    def update_user_total_games(self, id, total_games):
        query = {'_id': id}
        new_total_games = { "$set": {'total_games': total_games}}
        self.users.update_one(query, new_total_games)

    def get_user_game(self, id):
        query = {'_id': id}
        serial = self.users.find_one(query)['game_serial']
        game = self.serial_to_game(serial)
        return game
    
    def get_user_score(self, id):
        query = {'_id': id}
        score = self.users.find_one(query)['score']
        return score
    
    def get_user_total_games(self, id):
        query = {'_id': id}
        total_games = self.users.find_one(query)['total_games']
        return total_games
    
    def get_leaderboard(self):
        leaderboard = sorted(self.users.find(), key=lambda d: sum(d['score']), reverse=True)
        return leaderboard
    