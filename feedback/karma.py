import json
class Karma:

    def __init__(self, filename='karma.json'):
        self.filename = filename
        self.data = self.load()

    def load(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_threads(self):
        return self.data['threads']

    def get_users(self):
        return self.data['users']

    def add_thread(self, thread_id):
        self.data['threads'][thread_id] = []

    def add_user(self, user_id):
        self.data['users'][user_id] = 1

    def increment_user_karma(self, user_id):
        self.data['users'][user_id] += 1

    def add_user_to_thread(self, thread_id, user_id):
        self.data['threads'][thread_id].append(user_id)

    def user_in_thread(self, thread_id, user_id):
        return user_id in self.data['threads'][thread_id]

    def user_exists(self, user_id):
        return user_id in self.data['users']