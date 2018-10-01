from mongoengine import StringField, DictField, LongField, ListField, BooleanField

from .Base import BaseDocument, BaseSchema, BaseFactory


class Job(BaseDocument):
    name = StringField(max_length=20, unique=True)
    classifiers = StringField()
    crawling_score = StringField()

    # TODO : Is the assumption that the maximum length is 100 logical ?
    seed_list = ListField(LongField(), max_length=100)

    twitter_access_token = StringField()
    twitter_access_secret = StringField()
    is_active = BooleanField(default=False)
    meta = {'collection': 'jobs'}

    def schema(self):
        return JobSchema()


class JobSchema(BaseSchema):
    class Meta:
        model = Job
        model_fields_kwargs = {'twitter_credentials': {'load_only': True}}


class JobFactory(BaseFactory):
    class Meta:
        model = Job
