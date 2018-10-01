import logging

from decouple import config
from redis import Redis
from rq import Queue
from tweepy import RateLimitError

from logic.logic_job import get_job, post_job_is_active, post_job_initialize
from logic.logic_profile import get_profile_with_max_score, create_profile_from_dict, post_profile_unauthorized, \
    update_profile
from logic.logic_twitter import get_profiles_from_twitter, get_followers_page_and_next_cursor, \
    AccountUnauthorizedException, create_tweepy_api
from models.Profile import Profile


def functionify(job_dict):
    job_dict["crawling_score"] = code_to_python_function(job_dict["crawling_score"])[0]

    classifiers_text = job_dict["classifiers"]
    job_dict["classifiers"] = {}

    for func in code_to_python_function(classifiers_text):
        job_dict["classifiers"][func.__name__] = func

    # TODO : Is it logical to do this ?
    # Create Tweepy api from given credentials
    job_dict["tweepy_api"] = create_tweepy_api(job_dict)


def code_to_python_function(code):
    # Converts functions in string form to real python functions
    context = {}
    exec(code, context, context)

    funcs = []

    for _, value in context.items():
        if callable(value):
            funcs.append(value)

    return funcs


def execute_job(job_id):
    logging.info("Executing job with job_id: {0}".format(job_id))

    job_dict = get_job(job_id)
    if job_dict["is_active"]:
        logging.info("Job with job_id {0} already active !")
        return


    try:
        # job is active now
        post_job_is_active(job_id, True)

        functionify(job_dict)
        print("here")

        if not job_dict["initialized"]:
            initialize_job(job_dict)

        while True:
            next_user = get_profile_with_max_score(job_id)

            try:
                process_user(job_dict, next_user)
            except RateLimitError:
                # TODO : Add job id to waiting queue
                pass

    except Exception:
        print("WTF")
        logging.exception("An exception occured !")
        post_job_is_active(job_id, False)


def initialize_job(job_dict):
    user_profiles = get_profiles_from_twitter(job_dict["tweepy_api"], job_dict["seed_list"])

    profiles = [create_profile_from_dict(job_dict, user_profile) for user_profile in user_profiles]

    Profile.objects.insert(profiles)

    post_job_initialize(job_dict["id"])


def process_user(job_dict, profile_dict):
    try:
        page, next_cursor = get_followers_page_and_next_cursor(job_dict["tweepy_api"], profile_dict["user_id"],
                                                               profile_dict["last_cursor"])
    except AccountUnauthorizedException:
        post_profile_unauthorized(profile_dict["id"])

        return

    # Add a job to redis
    q = Queue(config("PROFILE_RQ_WORKER_Q_NAME"), Redis(host=config("REDIS_SERVER_IP")))
    q.enqueue(save_new_profiles, args=(job_dict["id"], page))

    update_profile(profile_dict["id"], last_cursor=next_cursor, finished=(next_cursor == 0), follower_ids=page)


def save_new_profiles(job_id, user_ids):
    pipeline = [
        {"$group": {
            "_id": None,
            "distinct_ids": {"$push": "$id"}
        }
        },
        {
            "$project": {
                "_id": 0,
                "new_ids": {"$setDifference": [user_ids, "$distinct_ids"]}
            }
        }
    ]

    response = Profile.objects(job_id=job_id).aggregate(*pipeline)
    new_user_ids = list(response)[0]["new_ids"]

    job = get_job(job_id)
    job_dict = job.to_dict()
    functionify(job_dict)

    # Fetch profiles from Twitter and save to db
    twitter_profiles = get_profiles_from_twitter(job_dict["tweepy_api"], new_user_ids)

    profile_list = [create_profile_from_dict(job_dict, profile_dict) for profile_dict in twitter_profiles]

    Profile.objects.insert(profile_list)
