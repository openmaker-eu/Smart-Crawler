from utils.connections import Connection
import tweepy
from decouple import config
from tweepy import OAuthHandler
from tweepy.error import TweepError
from pymongo.errors import BulkWriteError

# Accessing Twitter API
consumer_key = config("TWITTER_CONSUMER_KEY")  # API key
consumer_secret = config("TWITTER_CONSUMER_SECRET")  # API secret
access_token = config("TWITTER_ACCESS_TOKEN")
access_secret = config("TWITTER_ACCESS_SECRET")

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def save_new_users(user_ids, job_name):
    collection_job = Connection.Instance().jobs_db[job_name]

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

    try:
        collection_job.insert_many(user_profiles, ordered=False)
        print("Profiles saved !")
    except BulkWriteError as bwe:
        print(bwe.details)
        raise Exception("STOOOOOAHP!!!")


# Fetches up to 100 twitter accounts
def get_user_profiles_single_request(user_ids):
    assert len(user_ids) <= 100

    user_profiles =  [x._json for x in api.lookup_users(user_ids)]

    for user in user_profiles:
        user["finished"] = False
        user["follower_ids"] = []
        user["last_cursor"] = -1
        user["authorized"] = True

    return user_profiles

def get_followers_page_and_next_cursor(_screen_name, _cursor = -1):
    cursor = tweepy.Cursor(api.followers_ids, screen_name=_screen_name , cursor = _cursor).pages()

    try:
        page = cursor.next()
    except TweepError:
        return None

    next_cursor = cursor.next_cursor

    return (page, next_cursor)