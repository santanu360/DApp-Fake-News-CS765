import random
from tabulate import tabulate

from config import Config
from News import News
from Account import Account
from Rating import Rating

CONFIG = Config()

N = CONFIG.N
Q = CONFIG.Q
P = CONFIG.P

TOPICS = CONFIG.TOPICS
NUM_TRUE_NEWS = CONFIG.NUM_TRUE_NEWS
NUM_FALSE_NEWS = CONFIG.NUM_FALSE_NEWS


def calculate_news_accuracy_topic(news, topic):
    news_accuracies = {True: [], False: []}
    for vote in news.votes:
        voter: Account = vote["voter"]
        vote_value: bool = vote["vote_value"]
        for rating in voter.ratings:
            if rating.topic == topic:
                news_accuracies[vote_value].append(rating.rating)

    news_accuracy = {
        True: (
            sum(news_accuracies[True]) / len(news_accuracies[True])
            if len(news_accuracies[True]) > 0
            else 0
        ),
        False: (
            sum(news_accuracies[False]) / len(news_accuracies[False])
            if len(news_accuracies[False]) > 0
            else 0
        ),
    }
    return news_accuracy


def calculate_news_accuracy(news):
    news_accuracies = {True: [], False: []}
    for topic in news.topics:
        news_accuracies_topic = calculate_news_accuracy_topic(news, topic)
        news_accuracies[True].append(news_accuracies_topic[True])
        news_accuracies[False].append(news_accuracies_topic[False])

    news_accuracy = {
        True: (
            sum(news_accuracies[True]) / len(news_accuracies[True])
            if len(news_accuracies[True]) > 0
            else 0
        ),
        False: (
            sum(news_accuracies[False]) / len(news_accuracies[False])
            if len(news_accuracies[False]) > 0
            else 0
        ),
    }
    if news_accuracy[True] > news_accuracy[False]:
        news.detected_truthy = True
        try:
            news.accuracy = news_accuracy[True] / (
                news_accuracy[True] + news_accuracy[False]
            )
        except ZeroDivisionError:
            news.accuracy = 0
    else:
        news.detected_truthy = False
        try:
            news.accuracy = news_accuracy[False] / (
                news_accuracy[True] + news_accuracy[False]
            )
        except ZeroDivisionError:
            news.accuracy = 0
    return news_accuracy


def tabulate_results(results, corner="", transpose=False):
    def do_transpose(data):
        transposed = {}
        for key, val in data.items():
            for key2, val in val.items():
                if key2 not in transposed:
                    transposed[key2] = {}
                transposed[key2][key] = val
        return transposed

    if transpose:
        results = do_transpose(results)

    table = [[key] + list(value.values()) for key, value in results.items()]
    headers = [corner] + list(results[list(results.keys())[0]].keys())
    print(tabulate(table, headers, tablefmt="grid"))


def cal_voter_statistics(voters):
    honest_count = len(list(filter(lambda voter: voter.type == "honest", voters)))
    trustworthy_count = len(
        list(filter(lambda voter: voter.type == "trustworthy", voters))
    )
    malicious_count = len(list(filter(lambda voter: voter.type == "malicious", voters)))
    voters_statistics = {
        "number": {
            "honest": honest_count,
            "trustworthy": trustworthy_count,
            "malicious": malicious_count,
        }
    }
    print("\nVoters statistics:")
    tabulate_results(voters_statistics, corner="Voter type")
    return voters_statistics


def cal_news_statistics(newss):
    news_statistics = {
        "news": {
            "true": len(list(filter(lambda news: news.truth_value, newss))),
            "false": len(list(filter(lambda news: not news.truth_value, newss))),
        }
    }
    __news_statistics = {}
    __news_statistics["number"] = news_statistics["news"]
    print("\nNews statistics:")
    tabulate_results(__news_statistics, corner="News type")
    return news_statistics


def cal_votes_statistics(newss):
    vote_statistics = {
        "true": {
            "honest -> true": 0,
            "honest -> false": 0,
            "trustworthy -> true": 0,
            "trustworthy -> false": 0,
            "malicious -> true": 0,
            "malicious -> false": 0,
        },
        "false": {
            "honest -> true": 0,
            "honest -> false": 0,
            "trustworthy -> true": 0,
            "trustworthy -> false": 0,
            "malicious -> true": 0,
            "malicious -> false": 0,
        },
    }
    for news in newss:
        if news.truth_value:
            for vote in news.votes:
                if vote["vote_value"]:
                    vote_statistics["true"][f"{vote['voter'].type} -> true"] += 1
                else:
                    vote_statistics["true"][f"{vote['voter'].type} -> false"] += 1
        else:
            for vote in news.votes:
                if vote["vote_value"]:
                    vote_statistics["false"][f"{vote['voter'].type} -> true"] += 1
                else:
                    vote_statistics["false"][f"{vote['voter'].type} -> false"] += 1
    print("\nVote statistics:")
    tabulate_results(vote_statistics, corner="votes \\ news type", transpose=True)
    return vote_statistics


def cal_news_detection_stats(newss, news_statistics):
    detection = {
        "Actually True": {
            "Predicted True": 0,
            "Predicted False": 0,
        },
        "Actually False": {
            "Predicted True": 0,
            "Predicted False": 0,
        },
    }
    for news in newss:
        if news.truth_value:
            if news.detected_truthy:
                detection["Actually True"]["Predicted True"] += 1
            else:
                detection["Actually True"]["Predicted False"] += 1
        else:
            if news.detected_truthy:
                detection["Actually False"]["Predicted True"] += 1
            else:
                detection["Actually False"]["Predicted False"] += 1
    detection["Actually True"]["Predicted True"] = (
        str(
            round(
                detection["Actually True"]["Predicted True"]
                / news_statistics["news"]["true"]
                * 100,
                2,
            )
        )
        + "%"
    )
    detection["Actually True"]["Predicted False"] = (
        str(
            round(
                detection["Actually True"]["Predicted False"]
                / news_statistics["news"]["true"]
                * 100,
                2,
            )
        )
        + "%"
    )
    detection["Actually False"]["Predicted True"] = (
        str(
            round(
                detection["Actually False"]["Predicted True"]
                / news_statistics["news"]["false"]
                * 100,
                2,
            )
        )
        + "%"
    )
    detection["Actually False"]["Predicted False"] = (
        str(
            round(
                detection["Actually False"]["Predicted False"]
                / news_statistics["news"]["false"]
                * 100,
                2,
            )
        )
        + "%"
    )
    print("\nNews Detection results:")
    tabulate_results(detection, corner="real\predicted")


def cal_voter_detection_stats(voters):
    stats = {
        "honest": [],
        "trustworthy": [],
        "malicious": [],
    }
    for voter in voters:
        stats[f"{voter.type}"].append(voter.avg_rating)

    stats["honest"] = {
        "avg predicted rating": round(sum(stats["honest"]) / len(stats["honest"]), 2)
    }
    stats["trustworthy"] = {
        "avg predicted rating": round(
            sum(stats["trustworthy"]) / len(stats["trustworthy"]), 2
        )
    }
    stats["malicious"] = {
        "avg predicted rating": round(
            sum(stats["malicious"]) / len(stats["malicious"]), 2
        )
    }

    print("\nVoter Detection results:")
    tabulate_results(stats, corner="Voter type", transpose=True)


def cal_config():
    stats = {
        "Value": {
            "N": CONFIG.N,
            "Q": CONFIG.Q,
            "P": CONFIG.P,
            "INITIAL_RATING_MALICIOUS": CONFIG.INITIAL_RATING_MALICIOUS,
        }
    }
    print("\nInput parameters:")
    tabulate_results(stats, corner="parameter")


def main():

    print("\n\n" + "-" * 70)

    cal_config()

    malicious_count = int(N * Q)
    trustworthy_count = int((N - malicious_count) * P)
    honest_count = N - malicious_count - trustworthy_count

    users = (
        ["malicious"] * malicious_count
        + ["trustworthy"] * trustworthy_count
        + ["honest"] * honest_count
    )
    random.shuffle(users)

    voters: list[Account] = [Account(user_type) for user_type in users]
    for voter in voters:
        voter.ratings = [Rating(topic) for topic in TOPICS]
        if voter.type == "trustworthy":
            for rating in voter.ratings:
                rating.total_votes_casted = 1
                rating.correct_votes_casted = 1
        if voter.type == "malicious" and CONFIG.INITIAL_RATING_MALICIOUS:
            for rating in voter.ratings:
                rating.total_votes_casted = 1
                rating.correct_votes_casted = 1 * CONFIG.INITIAL_RATING_MALICIOUS
    voter_statistics = cal_voter_statistics(voters)

    newss: list[News] = []
    for i in range(NUM_TRUE_NEWS):
        true_news = News(
            author="author",
            title=f"True news {i}",
            body="body",
            topics=random.choices(TOPICS, k=2),
            truth_value=True,
        )
        newss.append(true_news)
    for i in range(NUM_FALSE_NEWS):
        false_news = News(
            author="author",
            title=f"False news {i}",
            body="body",
            topics=random.choices(TOPICS, k=2),
            truth_value=False,
        )
        newss.append(false_news)
    random.shuffle(newss)
    news_statistics = cal_news_statistics(newss)

    for news in newss:
        for voter in voters:
            voter.vote(news)
        news.accuracy = calculate_news_accuracy(news)
        for vote in news.votes:
            vote["voter"].update_rating(vote["vote_value"] == news.is_true, news.topics)

    cal_votes_statistics(newss)
    cal_news_detection_stats(newss, news_statistics)
    cal_voter_detection_stats(voters)


if __name__ == "__main__":
    main()
