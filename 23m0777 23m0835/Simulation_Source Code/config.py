class Config:
    N = 100  # number of voters
    Q = 0.05  # malicious
    P = 0.05  # trustworthy

    INITIAL_RATING_MALICIOUS = 0.9  # initial rating for malicious voters

    TOPICS = ["topic1", "topic2", "topic3", "topic4", "topic5"]  # topics list
    NUM_TRUE_NEWS = 5000  # number of true news created
    NUM_FALSE_NEWS = 5000  # number of false news created
