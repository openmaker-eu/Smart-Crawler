import pymongo
from decouple import config
from utils.singleton import Singleton
from redis import Redis

@Singleton
class Connection:
    def __init__(self):
        try:
            self.MongoDBClient = pymongo.MongoClient(
                'mongodb://' + config("MONGODB_USER") + ":" + config("MONGODB_PASSWORD") + '@' + config("MONGODB_SERVER_IP") + ':27017/',
                connect=False)

            self.jobs_db = self.MongoDBClient["jobsDB"]

            self.redis_server = Redis(host=config("REDIS_SERVER_IP"))
        except e:
        	print(e)

    def job_exists(self,job):
    	return job.name in self.jobs_db.collection_names()
