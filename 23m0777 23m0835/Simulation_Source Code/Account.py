import random
from Rating import Rating


class Account:
    def __init__(self, type):
        if type not in ["malicious", "honest", "trustworthy"]:
            raise ValueError("Invalid account type")
        self.account_id = type[0].upper() + str(random.randint(100, 999))
        self.ratings: list[Rating] = []
        self.type = type

    def vote(self, news):
        """Vote on a news"""
        if self.type == "malicious":
            correct_vote = False
        elif self.type == "trustworthy":
            correct_vote = random.choices([True, False], weights=[0.9, 0.1], k=1)[0]
        else:  # honest
            correct_vote = random.choices([True, False], weights=[0.7, 0.3], k=1)[0]

        if correct_vote == True:
            news.cast_vote(self, news.truth_value)
        else:
            news.cast_vote(self, not news.truth_value)

    def update_rating(self, increase, topics):
        """Update the rating of the account"""
        for rating in self.ratings:
            if rating.topic in topics:
                rating.total_votes_casted += 1
                if increase:
                    rating.correct_votes_casted += 1

    @property
    def avg_rating(self):
        """Return the average rating of the account"""
        return sum([rating.rating for rating in self.ratings]) / len(self.ratings)

    def __repr__(self) -> str:
        return f"Account({self.account_id})"
