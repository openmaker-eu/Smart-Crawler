import logging

from mongoengine import DoesNotExist

from models.Job import Job
from models.Profile import Profile


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
