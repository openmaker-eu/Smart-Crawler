import sys
from utils.connections import Connection
from utils.helpers import save_new_users, get_user_profiles_single_request, get_followers_page_and_next_cursor
from decouple import config
from random import randint
from rq import Queue
import argparse
from job import Job

sys.path.insert(0, config("ROOT_DIR"))

# create parser for arguments
parser = argparse.ArgumentParser(description='Process jobs')
parser.add_argument('--jobs', nargs='*', help='jobs to execute')

def execute_job(job):
    if not Connection.Instance().job_exists(job):
        initialize_job(job)

    print("{} started !".format(job.name))

    collection_job = Connection.Instance().jobs_db[job.name]

    current_number_of_users = collection_job.count()

    while(current_number_of_users < job.user_limit):
        next_user = choose_next_user(collection_job)

        print("Fetching followers of {}...".format(next_user["screen_name"]))

        process_user(next_user, collection_job)

        current_number_of_users = collection_job.count()
    else:
        print("!!!JOB FINISHED!!!\nuser limit : {}, number of collected users : {}".format(job.user_limit , current_number_of_users))

def process_user(user,collection_job):
    result = get_followers_page_and_next_cursor(user["screen_name"], user["last_cursor"])

    if result:
        page, next_cursor = result
    else:
        print("...Account unauthorized, skipping")
        collection_job.update_one({"id" : user["id"]} , {"$set" : {"authorized" : False}})
        return

    # find user id's that are not currently in the database and fetch their profiles
    q = Queue("default",connection=Connection.Instance().redis_server)
    ret = q.enqueue(save_new_users, args=(page,collection_job.name,))

    collection_job.update({"id" : user["id"]} , {"$addToSet" : 
        {"follower_ids" : {"$each" : page}} , "$set" : {"finished" : next_cursor == 0, "last_cursor" : next_cursor}})

def choose_next_user(collection_job):
    active_users = collection_job.find({"finished" : False, "authorized" : True})

    # choose one of them randomly. Implement a better strategy that solves
    # exploration-exploitation problem
    index = randint(0,active_users.count())

    try:
        user = active_users.skip(index)[0]
    except IndexError:
        print(index,active_users.count())

    return user

#Create new database for job, save profile of seed users into database
def initialize_job(job):
    print("Initializing job : {}".format(job.name))
    user_profiles =  get_user_profiles_single_request(job.seed_list)

    db = Connection.Instance().jobs_db
    
    collection_job = db[job.name]

    collection_job.create_index("id", unique=True)

    collection_job.insert_many(user_profiles)

def main():
    job_names = parser.parse_args().jobs
    job_list = Job.get_job_list(job_names)
    execute_job(job_list[0])

if __name__ == "__main__":
    main()