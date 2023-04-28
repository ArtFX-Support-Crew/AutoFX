import json
class Karma:
    def __init__(self, file_name="karma.json"):
        self.file_name = file_name
        try:
            with open(file_name, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"users": {}, "threads": {}}

    def save(self):
        with open(self.file_name, "w") as f:
            json.dump(self.data, f, indent=4)

    def increment_user_karma(self, user_id, amount):
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = 1
        else:
            self.data["users"][user_id] += amount
            self.save()

    def get_users(self):
        print(self.data['users'])
        return self.data["users"]

    def get_karma_total(self, user_id):
        return self.data["users"].get(user_id)

    def get_leaderboard(self):
        users = self.get_users()
        leaderboard = []
        for user_id in users:
            karma_total = self.get_karma_total(user_id)
            leaderboard.append((user_id, karma_total))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        return leaderboard

  
   


