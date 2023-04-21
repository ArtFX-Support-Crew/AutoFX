import json

class Karma:
    def __init__(self, file_name="karma.json"):
        self.file_name = file_name
        try:
            with open(file_name, "r") as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}

    def save(self):
        with open(self.file_name, "w") as f:
            json.dump(self.users, f, indent=4)

    def increment_user_karma(self, user_id, amount):
        if user_id not in self.users:
            self.users[user_id] = 0
        self.users[user_id] += amount
        self.save()

    def get_users(self):
        return self.users