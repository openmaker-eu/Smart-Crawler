access_token = "821415961467228161-VACE9uCDD3xbVdDt9jQjVdCWgI1d9bx"
access_secret = "serQc8bRcw1INq7lkREpseSVR1BWAYIJDZI8YeXvvk6Dq"

def classifier_best(profile):
    return 1


def classifier_awesome(profile):
    return 0


user_limit = 10000


def crawling_strategy(collection_job):
    active_users = collection_job.find({"finished": False, "authorized": True})

    # choose one of them randomly. Implement a better strategy that solves
    # exploration-exploitation problem
    index = randint(0, active_users.count())

    try:
        user = active_users.skip(index)[0]
    except IndexError:
        print(index, active_users.count())
        # TODO : if this block of code runs, then user is not created ???

    return user

