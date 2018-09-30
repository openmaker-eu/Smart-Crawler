import json
import logging

from mongoengine import DoesNotExist

from models.Job import Job


def get_job(job_id):
    logging.info("job_id: {0}".format(job_id))
    if type(job_id) is not str:
        return {'error': 'job_id must be string!'}

    if job_id == 'new':
        job = {
            'name': '',
        }
        return job
    try:
        job = Job.objects.get(id=job_id)
    except DoesNotExist:
        return {}
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    if job is None:
        return {}

    return job.to_dict()


def get_jobs():
    # TODO: Fill the logging statement
    logging.info("")

    try:
        jobs = Job.objects.filter()
    except DoesNotExist:
        return {}
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    if jobs is None:
        return []

    jobs_json = []

    for job in jobs:
        jobs_json.append(job.to_dict())

    return jobs_json


def post_job(name, classifiers, crawling_score, seed_list, twitter_access_key, twitter_access_secret):
    # TODO: Fill the logging statement
    logging.info("")

    data = {
        'name': name,
        'classifiers': json.dumps(classifiers),
        'crawling_strategy': json.dumps(crawling_score),
        'seed_list': seed_list,
        'twitter_access_token': twitter_access_key,
        'twitter_access_secret': twitter_access_secret
    }
    try:
        job = Job(**data)
        job.save()
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'response': False, 'error': str(e)}

    return {
        'response': True,
        'job_id': job.to_dict()['id']
    }


def update_job(job_id, name, seed_list, twitter_access_key, twitter_access_secret):
    logging.info("job_id: {0}".format(job_id))

    try:
        job = Job.objects.get(id=job_id)
    except DoesNotExist:
        return {
            'message': 'job not found',
            'response': False
        }
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    job.name = name
    job.seed_list = seed_list
    job.twitter_access_token = twitter_access_key
    job.twitter_access_secret = twitter_access_secret

    try:
        job.save()
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'response': False, 'error': str(e)}

    return {
        'response': True,
    }


def delete_job(job_id):
    logging.info("job_id: {0}".format(job_id))
    if type(job_id) is not str:
        return {'error': 'job_id must be string!'}

    try:
        job = Job.objects.get(id=job_id)
    except DoesNotExist:
        return {
            'message': 'job not found',
            'response': False
        }
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    job.delete()

    return {'response': True}


def post_job_is_active(job_id, is_active):
    logging.info("job_id: {0}".format(job_id))
    if type(job_id) is not str:
        return {'error': 'job_id must be string!'}

    try:
        job = Job.objects.get(id=job_id)
    except DoesNotExist:
        return {
            'message': 'job not found',
            'response': False
        }
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    job.is_active = is_active

    job.save()

    return {'response': True}


def post_job_initialize(job_id):
    logging.info("job_id: {0}".format(job_id))
    if type(job_id) is not str:
        return {'error': 'job_id must be string!'}

    try:
        job = Job.objects.get(id=job_id)
    except DoesNotExist:
        return {
            'message': 'job not found',
            'response': False
        }
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    job._initialised = True

    job.save()

    return {'response': True}