from feedback_points import Points

"""
AutoFX - Feedback. 
Module test of methods in feedback_points.py.

Methods:
- __init__(self, filename='feedback_points.json'): Initializes the Points object with a filename for the JSON file that stores the feedback points data.
- load(self): Loads the feedback points data from the JSON file.
- save(self): Saves the feedback points data to the JSON file.
- get_threads(self): Returns a dictionary of threads and their associated users.
- get_users(self): Returns a dictionary of users and their associated feedback points.
- add_thread(self, thread_id): Adds a new thread to the feedback points data.
- add_user(self, user_id): Adds a new user to the feedback points data.
- increment_user_points(self, user_id, points_change=required_points): Increases a user's feedback points by a specified amount.
- add_user_to_thread(self, thread_id, user_id): Adds a user to a thread in the feedback points data.
- user_in_thread(self, thread_id, user_id): Checks if a user is in a thread in the feedback points data.
- user_exists(self, user_id): Checks if a user exists in the feedback points data.
- has_enough(self, user_id, required_points=required_points): Checks if a user has enough feedback points to perform a certain action.
- get_points(self, user_id): Returns the number of feedback points a user has.
- grant_points(self, user_id, points_to_grant): Grants a specific number of feedback points to a user.

Fields:
- required_points: A global variable that sets the number of feedback points required for a user to perform a certain action.
- filename: The name of the JSON file that stores the feedback points data.
- data: A dictionary that stores the feedback points data.
"""


class TestPoints:
    # Tests that data can be loaded from file.
    def test_load_from_file(self):
        # Happy path test
        points = Points("test_feedback_points.json")
        assert points.load() == {"threads": {}, "users": {}}

        # Edge case test
        points = Points("nonexistent_file.json")
        assert points.load() == {}

        # General behavior test
        points = Points()
        assert isinstance(points.load(), dict)

    # Tests that a thread can be added.
    def test_add_thread(self):
        # Happy path test
        points = Points()
        points.add_thread("thread1")
        assert "thread1" in points.get_threads()

        # Edge case test
        points = Points()
        points.add_thread("")
        assert "" not in points.get_threads()

        # General behavior test
        points = Points()
        initial_threads = points.get_threads()
        points.add_thread("thread1")
        assert len(points.get_threads()) == len(initial_threads) + 1

    # Tests that a user can be added.
    def test_add_user(self):
        # Happy path test
        points = Points()
        points.add_user("user1")
        assert "user1" in points.get_users()

        # Edge case test
        points = Points()
        points.add_user("")
        assert "" not in points.get_users()

        # General behavior test
        points = Points()
        initial_users = points.get_users()
        points.add_user("user1")
        assert len(points.get_users()) == len(initial_users) + 1

    # Tests that user points can be incremented.
    def test_increment_user_points(self):
        # Happy path test
        points = Points()
        points.add_user("user1")
        points.increment_user_points("user1")
        assert points.get_points("user1") == 1

        # Edge case test
        points = Points()
        points.add_user("user1")
        points.increment_user_points("user1", 2)
        assert points.get_points("user1") == 1

        # General behavior test
        points = Points()
        points.add_user("user1")
        initial_points = points.get_points("user1")
        points.increment_user_points("user1")
        assert points.get_points("user1") == initial_points + 1

    # Tests that a user can be added to a thread.
    def test_add_user_to_thread(self):
        points = self._extracted_from_test_add_user_to_thread_3("user1")
        points.add_user_to_thread("thread1", "user1")
        assert "user1" in points.data["threads"]["thread1"]

        points = self._extracted_from_test_add_user_to_thread_3("")
        points.add_user_to_thread("thread1", "")
        assert "" not in points.data["threads"]["thread1"]

        points = self._extracted_from_test_add_user_to_thread_3("user1")
        initial_users = points.data["threads"]["thread1"]
        points.add_user_to_thread("thread1", "user1")
        assert len(points.data["threads"]["thread1"]) == len(initial_users) + 1

    # TODO Rename this here and in `test_add_user_to_thread`
    def _extracted_from_test_add_user_to_thread_3(self, arg0):
        # Happy path test
        result = Points()
        result.add_thread("thread1")
        result.add_user(arg0)
        return result

    # Tests that points can be granted to a user.
    def test_grant_points(self):
        # Happy path test
        points = Points("test_feedback_points.json")
        points.grant_points("user1", 1)
        assert points.get_points("user1") == 1

        # General behavior test
        points = Points()
        initial_points = points.get_points("user1")
        points.grant_points("user1", 2)
        assert points.get_points("user1") == initial_points + 2
