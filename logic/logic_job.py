import json
import logging

from mongoengine import DoesNotExist

from models.Job import Job


def get_job(job_id):
    logging.info("job_id: {0}".format(job_id))
    if type(job_id) is not str:
        return {'error': 'job_id must be string!'}

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
        return json.dumps([])

    jobs_json = []

    for job in jobs:
        jobs_json.append(job.to_dict())

    return json.dumps(jobs_json)


def post_job(name, classifiers, crawling_strategy, seed_list, twitter_credentials):
    # TODO: Fill the logging statement
    logging.info("")

    data = {
        'name': name,
        'classifiers': classifiers,
        'crawling_strategy': crawling_strategy,
        'seed_list': seed_list,
        'twitter_credentials': twitter_credentials
    }
    try:
        job = Job(**data)
        job.save()
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

    return {
        'response': True,
        'job_id': job.to_dict()['id']
    }


def update_job(job_id, classifiers, crawling_strategy, seed_list, twitter_credentials):
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

    job.classifiers = classifiers
    job.crawling_strategy = crawling_strategy
    job.seed_list = seed_list
    job.twitter_credentials = twitter_credentials

    try:
        job.save()
    except Exception as e:
        logging.error("exception: {0}".format(str(e)))
        return {'error': str(e)}

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