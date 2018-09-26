from .connection import Connection
from tweepy.error import TweepError
from pymongo.errors import BulkWriteError
import tweepy


def save_new_users(user_ids, job):
    collection_job = Connection.Instance().jobs_db[job.name]

    res = collection_job.aggregate(
       [
         {  "$group" : {
                "_id" : None,
                "distinct_ids" : {"$push" : "$id"}
            }
         },
         {
            "$project" : {
                "_id" : 0,
                "new_ids" : {"$setDifference" : [user_ids , "$distinct_ids"]}
            }
         }
       ]
    )

    new_user_ids = list(res)[0]["new_ids"]

    user_profiles = []
    for i in range(0, len(new_user_ids) , 100):
        slice_user_ids = new_user_ids[i:i+100]
        user_profiles += get_user_profiles_single_request(slice_user_ids)

    # Determine features for each profile
    for profile in user_profiles:
        profile["features"] = {func.__name__ : func(profile) for func in job.classifiers}

    try:
        collection_job.insert_many(user_profiles, ordered=False)
        print("Profiles saved !")
    except BulkWriteError as bwe:
        print(bwe.details)
        raise Exception("STOOOOOAHP!!!")


# Fetches up to 100 twitter accounts
def get_user_profiles_single_request(user_ids):
    assert len(user_ids) <= 100

    user_profiles =  [x._json for x in Connection.Instance().api.lookup_users(user_ids)]

    for user in user_profiles:
        user["finished"] = False
        user["follower_ids"] = []
        user["last_cursor"] = -1
        user["authorized"] = True

    return user_profiles


def get_followers_page_and_next_cursor(_screen_name, _cursor = -1):
    cursor = tweepy.Cursor(Connection.Instance().api.followers_ids, screen_name=_screen_name , cursor = _cursor).pages()

    try:
        page = cursor.next()
    except TweepError:
        return None

    next_cursor = cursor.next_cursor

    return (page, next_cursor)
