import json
class Points:
    global required_points
    required_points = 1
    

    def __init__(self, filename='feedback_points.json'):
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

    # gets the users in a thread
    def get_users(self):
        return self.data['users']

    # adds the thread to the json file
    def add_thread(self, thread_id):
        self.data['threads'][thread_id] = []

    # adds a user to the json file
    def add_user(self, user_id):
        self.data['users'][user_id] = 0

    # rewards a user with points
    def increment_user_points(self, user_id, points_change=required_points):
        new_points = self.data['users'][user_id] + points_change
        self.data['users'][user_id] = min(new_points, required_points)

    def add_user_to_thread(self, thread_id, user_id):
        self.data['threads'][thread_id].append(user_id)

    def user_in_thread(self, thread_id, user_id):
        return user_id in self.data['threads'][thread_id]

    # checks if a user exists in the json file
    def user_exists(self, user_id):
        return user_id in self.data['users']
    
    # checks if a user has enough points
    def has_enough(self, user_id, required_points=required_points):
        points_data = self.load()
        user_points = points_data.get(str(user_id), 0)
        return user_points >= required_points
    
    # gets the number of points a user has
    def get_points(self, user_id):
        return self.data['users'].get(user_id, 0)
    
    # grant points to a user
    def grant_points(self, user_id, points_to_grant):
        """Grant a specific number of feedback points to a user.

        Args:
            user_id (str): The ID of the user to grant points to.
            points_to_grant (int): The number of points to grant.
        """
        if not self.user_exists(user_id):
            self.add_user(user_id)
        self.increment_user_points(user_id, points_to_grant)
        self.save()
    

    