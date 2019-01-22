import tweepy
from decouple import config
from tweepy import TweepError, OAuthHandler, RateLimitError


class AccountUnauthorizedException(Exception):
    pass


def get_profiles_from_twitter(api, user_ids):
    slices = (user_ids[i:i + 100] for i in range(0, len(user_ids), 100))

    profiles = []

    for sl in slices:
        profiles += get_profiles_from_twitter_helper(api, sl)

    return profiles


def get_profiles_from_twitter_helper(api, user_ids):
    # At most 100 user ids
    return [x._json for x in api.lookup_users(user_ids)]


def get_followers_page_and_next_cursor(api, user_id, cursor=-1):
    cursor = tweepy.Cursor(api.followers_ids, user_id=user_id, cursor=cursor).pages()

    try:
        page = cursor.next()
    except RateLimitError:
        raise RateLimitError("RateLimitError")
    except TweepError as e:
        raise AccountUnauthorizedException(e)

    next_cursor = cursor.next_cursor

    return page, next_cursor


def create_tweepy_api(job_dict):
    auth = OAuthHandler(config("TWITTER_CONSUMER_KEY"), config("TWITTER_CONSUMER_SECRET"))
    auth.set_access_token(job_dict["twitter_access_token"], job_dict["twitter_access_secret"])
    return tweepy.API(auth)
