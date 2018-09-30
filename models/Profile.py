from mongoengine import DictField, LongField, ReferenceField, ListField, FloatField, BooleanField, CASCADE

from .Job import Job
from .Base import BaseDocument, BaseSchema, BaseFactory


class Profile(BaseDocument):
    job_id = ReferenceField(Job, reverse_delete_rule=CASCADE)
    profile = DictField()
    user_id = LongField()
    classifier_scores = ListField(FloatField())
    crawling_score = FloatField()
    follower_ids = ListField(LongField())
    authorized = BooleanField(default=True)
    last_cursor = LongField(default=-1)
    finished = BooleanField(default=False)
    meta = {
        'collection': 'profiles',
        'index_background': True,
        'auto_create_index': True,
        'indexes': [
            'job_id',
            'user_id',
            '-crawling_score'
        ]
    }

    def schema(self):
        return ProfileSchema()


class ProfileSchema(BaseSchema):
    class Meta:
        model = Profile


class ProfileFactory(BaseFactory):
    class Meta:
        model = Profile
