class Topic:
    def __init__(self, topic):
        self.topic: str = topic

    def __str__(self):
        return self.topic


class Rating:
    """Rating class to store topic and rating"""

    def __init__(self, topic):
        # if isinstance(topic, str):
        # topic = Topic(topic)
        self.topic: str = topic
        self.total_votes_casted: int = 0
        self.correct_votes_casted: int = 0

    @property
    def rating(self):
        if self.total_votes_casted == 0:
            return 0
        return self.correct_votes_casted / self.total_votes_casted

    def __str__(self):
        return f"{self.topic} ({self.rating})"
