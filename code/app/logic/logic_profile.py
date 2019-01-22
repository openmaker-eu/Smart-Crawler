import logging

from mongoengine import DoesNotExist

from models.Job import Job
from models.Profile import Profile


def get_profile(profile_id):
    logging.info("get_profile | profile_id: {0}".format(profile_id))
    if type(profile_id) is not str:
        return {'error': 'profile_id must be string!'}

    try:
        profile = Profile.objects.get(id=profile_id)
    except DoesNotExist:
        return {}
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    if profile is None:
        return {}

    return profile.to_dict()


def get_profiles(job_id, skip, limit):
    logging.info("job_id: {0}".format(job_id))

    try:
        job = Job.objects.get(id=job_id)
    except DoesNotExist:
        return []
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    try:
        profiles = Profile.objects.filter(job_id=job.id).order_by('-crawling_score')[skip: skip + limit]
    except DoesNotExist:
        return {}
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    if profiles is None:
        return []

    profiles_json = []

    for profile in profiles:
        profiles_json.append(profile.to_dict())

    return profiles_json


def update_profile(profile_id, last_cursor, finished, follower_ids):
    logging.info("update_profile | profile_id: {0}".format(profile_id))

    try:
        profile = Profile.objects.get(id=profile_id)
    except DoesNotExist:
        return {
            'message': 'profile not found',
            'response': False
        }
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    profile.update(set__last_cursor=last_cursor, set__finished=finished, add_to_set__follower_ids=follower_ids)


def get_profile_with_max_score(job_id):
    logging.info("get_profile_with_max_score | job_id: {0}".format(job_id))

    try:
        profile = Profile.objects(job_id=job_id, authorized=True, finished=False).order_by("-crawling_score").first()
    except DoesNotExist:
        return None
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    if profile is None:
        return {}

    return profile.to_dict()


def create_profile_from_dict(job_dict, profile_dict):
    logging.info("create_profile_from_dict | profile_id: {0}".format(profile_dict["id"]))
    classifier_scores = {key: func(profile_dict) for key, func in job_dict["classifiers"].items()}
    crawling_score = job_dict["crawling_score"]({**profile_dict, **classifier_scores})

    parameters = {
        "job_id": job_dict["id"],
        "profile": profile_dict,
        "user_id": profile_dict["id"],
        "classifier_scores": classifier_scores,
        "crawling_score": crawling_score,
    }

    return Profile(**parameters)


def post_profile_unauthorized(profile_id):
    logging.info("post_profile_unauthorized | profile_id: {0}".format(profile_id))
    if type(profile_id) is not str:
        return {'error': 'job_id must be string!'}

    try:
        profile = Profile.objects.get(id=profile_id)
    except DoesNotExist:
        return {
            'message': 'profile not found',
            'response': False
        }
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    profile.update(set__authorized = False)

    return {'response': True}
