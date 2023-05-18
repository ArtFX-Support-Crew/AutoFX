
from karma import Karma

class TestKarma:

 # Tests that the Karma object is initialized with the default file name "karma.json". 
    def test_init_default_file(self):
        karma = Karma()
        assert karma.file_name == "karma.json"

    # Tests that the Karma object is initialized with a custom file name. 
    def test_init_custom_file(self):
        karma = Karma("custom_karma.json")
        assert karma.file_name == "custom_karma.json"

    # Tests that retrieving karma total for a nonexistent user returns None. 
    def test_get_karma_total_nonexistent_user(self):
        karma = Karma()
        assert karma.get_karma_total("nonexistent_user") is None

    # Tests that user karma is incremented for a new user. 
    def test_increment_user_karma_new_user(self):
        self._extracted_from_test_increment_user_karma_valid_id_2("new_user", 1)

    # Tests that user karma is incremented with a valid user ID and amount. 
    def test_increment_user_karma_valid_id(self):
        self._extracted_from_test_increment_user_karma_valid_id_2("user1", 5)

    # TODO Rename this here and in `test_increment_user_karma_new_user` and `test_increment_user_karma_valid_id`
    def _extracted_from_test_increment_user_karma_valid_id_2(self, arg0, arg1):
        karma = Karma()
        karma.increment_user_karma(arg0, arg1)
        assert karma.get_karma_total(arg0) == arg1

    # Tests that the leaderboard is sorted in descending order by karma total. 
    def test_get_leaderboard(self):
        karma = Karma()
        karma.increment_user_karma("user1", 5)
        karma.increment_user_karma("user2", 10)
        karma.increment_user_karma("user3", 3)
        leaderboard = karma.get_leaderboard()
        assert leaderboard == [("user2", 10), ("user1", 5), ("user3", 3)]