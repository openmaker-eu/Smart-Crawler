import logging

from decouple import config
from mongoengine import StringField, DictField, LongField, ListField, BooleanField, signals
from redis import ConnectionPool, Redis
from rq import Queue

from .Base import BaseDocument, BaseSchema, BaseFactory

pool = ConnectionPool(host='db', port=6379, password=config("REDIS_PASSWORD"), db=0)
redis_conn = Redis(connection_pool=pool)
q = Queue(config("JOB_RQ_WORKER_Q_NAME"), connection=redis_conn)


class Job(BaseDocument):
    name = StringField(max_length=20, unique=True)
    classifiers = StringField()
    crawling_score = StringField()

    # TODO : Is the assumption that the maximum length is 100 logical ?
    seed_list = ListField(LongField(), max_length=100)

    twitter_access_token = StringField()
    twitter_access_secret = StringField()
    is_active = BooleanField(default=False)
    initialized = BooleanField(default=False)
    meta = {'collection': 'jobs'}

    def schema(self):
        return JobSchema()

    def save(self, *args, **kw):
        logging.warning("Save Triggered !!!")
        old = type(self).objects.get(pk=self.pk) if self.pk else None
        super(Job, self).save(*args, **kw)

        if old and not old.is_active and self.is_active:
            from logic.logic_execute_job import execute_job
            q.enqueue(execute_job, args=(str(self.id),))


class JobSchema(BaseSchema):
    class Meta:
        model = Job
        model_fields_kwargs = {'twitter_credentials': {'load_only': True}}


class JobFactory(BaseFactory):
    class Meta:
        model = Job
