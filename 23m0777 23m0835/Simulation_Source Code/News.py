import hashlib
import time

from Rating import Rating, Topic


class News:
    def __init__(self, author, title, body, topics: list[Topic], truth_value):
        self.body = body
        self.title = title
        self.author = author
        self.topics = topics
        self.truth_value = truth_value
        self.timestamp = time.time()
        self.votes = []

        self.detected_truthy = None
        self.accuracy = None

        # Create a hash of the news content
        content = "".join(
            [str(self.author), self.body, "".join(self.topics), str(self.timestamp)]
        )
        self.news_id = hashlib.sha256(content.encode()).hexdigest()

    def cast_vote(self, voter, vote_value):
        """Cast a vote on the news"""
        self.votes.append({"voter": voter, "vote_value": vote_value})

    @property
    def is_true(self):
        if self.detected_truthy is None:
            raise ValueError("News accuracy not calculated")
        return self.detected_truthy

    def __repr__(self) -> str:
        return f"News({self.title})"
