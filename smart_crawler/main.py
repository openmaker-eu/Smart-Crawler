import multiprocessing
import sys
from decouple import config


from lib.connection import Connection
from lib.helpers import save_new_users, get_user_profiles_single_request, get_followers_page_and_next_cursor

from rq import Queue

from lib.job import Job
import jobs

# DONE 1: initialization kısmını, seed userların idlerini job olarak başta redis queue'ya atmak olarak güncelle. FIX :  şimdilik sadece 100 tane alacak şekilde yap
# TODO 2: seed list'i al(search api'dan çek ai için), profilleri çek ve
# DONE :  classifier fonksiyonlarından geçir (dictionray şekilde, keyler fonksiyon ismi)
# DONE 3: her adımda crawling stratefy fonksiyonunu çalıştır, bir user seç, onun followerlarını çek (1 page) ve user id'lerden bir job(profilleri çek ve classifier fonksiyonundan geçir) oluştur
# TODO 4: output için html output, relevancy'ye göre sort edilmiş. Classifierların sonuçlarını gösteren bir şey de olsun (her user için)
# TODO 5: tweepy birden 1fazla token kullanabiliyor mu ?
# TODO 6: start/stop özelliği olabilir (process gibi olabilir)
# TODO 7: spark nasıl çalışıyor, her şeyi spark'ta yapabilir miyiz ? dask'ın sparktan farkı ne, dask mı spark mı daha çok işimize yarar ? (bu daha çok prediction kısmı için)


class JobProcess(multiprocessing.Process):

    def __init__(self, job):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.job = job
        from lib.connection import Connection
        from lib.helpers import save_new_users, get_user_profiles_single_request, get_followers_page_and_next_cursor

    def stop(self):
        self.exit.set()

    def run(self):
        Connection.Instance().set_access_token_secret(self.job.access_token, self.job.access_secret)

        if not Connection.Instance().job_exists(self.job):
            initialize_job(self.job)

        print("{} started !".format(self.job.name))

        collection_job = Connection.Instance().jobs_db[self.job.name]

        current_number_of_users = collection_job.count()

        while current_number_of_users < self.job.user_limit and not self.exit.is_set():
            print("Heartbeat from job {}, access token = {}, access_secret = {}".format(self.job.name, self.job.access_token, self.job.access_secret))
            next_user = self.job.crawling_strategy(collection_job)

            print("Fetching followers of {}...".format(next_user["screen_name"]))

            process_user(next_user, self.job, collection_job)

            current_number_of_users = collection_job.count()
        else:
            print("!!!JOB FINISHED!!!\nuser limit : {}, number of collected users : {}".format(self.job.user_limit,
                                                                                current_number_of_users))


def execute_job(job):
    Connection.Instance().set_access_token_secret(job.access_token, job.access_secret)

    if not Connection.Instance().job_exists(job):
        initialize_job(job)

    print("{} started !".format(job.name))

    collection_job = Connection.Instance().jobs_db[job.name]

    current_number_of_users = collection_job.count()

    while current_number_of_users < job.user_limit:
        next_user = job.crawling_strategy(collection_job)

        print("Fetching followers of {}...".format(next_user["screen_name"]))

        process_user(next_user, job, collection_job)

        current_number_of_users = collection_job.count()
    else:
        print("!!!JOB FINISHED!!!\nuser limit : {}, number of collected users : {}".format(job.user_limit,
                                                                                           current_number_of_users))


def process_user(user, job,collection_job):
    result = get_followers_page_and_next_cursor(user["screen_name"], user["last_cursor"])

    if result:
        page, next_cursor = result
    else:
        print("...Account unauthorized, skipping")
        collection_job.update_one({"id": user["id"]}, {"$set": {"authorized": False}})
        return

    # find user id's that are not currently in the database and fetch their profiles
    try:
        q = Queue("default", connection=Connection.Instance().redis_server)
        ret = q.enqueue(save_new_users, args=(page, job.name,))
    except ModuleNotFoundError as e:
        print(e)

    collection_job.update({"id": user["id"]}, {"$addToSet":
                                                   {"follower_ids": {"$each": page}},
                                               "$set": {"finished": next_cursor == 0, "last_cursor": next_cursor}})


# Create new database for job, save profile of seed users into database
def initialize_job(job):
    print("Initializing job : {}".format(job.name))

    user_profiles = get_user_profiles_single_request(job.seed_list)

    # Determine features for each profile
    for profile in user_profiles:
        profile["features"] = {func.__name__ : func(profile) for func in job.classifiers}

    db = Connection.Instance().jobs_db

    collection_job = db[job.name]

    collection_job.create_index("id", unique=True)

    collection_job.insert_many(user_profiles)



def main():
    job_list = jobs.job_list

    job_proc_dict = {j.name:JobProcess(j) for j in job_list}

    if not job_list:
        print("No jobs found ...")
        return

    print("List of jobs found:")
    for index, job in enumerate(job_list, 1):
        print('{}) "{}"\n'.format(index, job.name))


    choice = 1
    while choice:
        print("What do you want to do ?\n1) View status of jobs\n2) Start a job\n3) Stop a job\n0) Exit")
        choice = int(input().strip())

        if choice == 1:
            print(job_proc_dict)
        elif choice == 2:
            print("Please enter the name of the job you want to start")
            job_name = input().strip()
            if job_name in job_proc_dict and not job_proc_dict[job_name].is_alive():
                job_proc_dict[job_name].start()
        elif choice == 3:
            print("Please enter the name of the job you want to stop")
            job_name = input().strip()
            if job_name in job_proc_dict and job_proc_dict[job_name].is_alive():
                job_proc_dict[job_name].stop()
                job_proc_dict[job_name].join()
        elif choice == 0:
            pass
        else:
            print("Please try again")


    job_name = input("Please type the name of the job you want to start").strip()
    #job_list = Job.get_job_list(job_names)
    execute_job(job_list[index - 1][1])


if __name__ == "__main__":
    main()
