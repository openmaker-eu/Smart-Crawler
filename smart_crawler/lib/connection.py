import pymongo
from decouple import config
from .singleton import Singleton
from redis import Redis
from tweepy import OAuthHandler
import tweepy

# Accessing Twitter API
consumer_key = config("TWITTER_CONSUMER_KEY")  # API key
consumer_secret = config("TWITTER_CONSUMER_SECRET")  # API secret

@Singleton
class Connection:
    def __init__(self):
        try:
            self.MongoDBClient = pymongo.MongoClient(
                'mongodb://' + config("MONGODB_USER") + ":" + config("MONGODB_PASSWORD") + '@' + config(
                    "MONGODB_SERVER_IP") + ':27017/',
                connect=False)

            self.jobs_db = self.MongoDBClient["jobsDB"]

            self.redis_server = Redis(host=config("REDIS_SERVER_IP"))

            # TODO : maybe add auth without access tokens and only with consumer key/secret
            # TODO : move self.api to job.py, so that each job can have its unique api access
            self.api = None
        except e:
            print(e)

    def job_exists(self, job):
        return job.name in self.jobs_db.collection_names()

    def set_access_token_secret(self, access_token, access_secret):
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
