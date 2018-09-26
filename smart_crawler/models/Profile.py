from mongoengine import DictField, LongField, ReferenceField, CASCADE

from .Job import Job
from .Base import BaseDocument, BaseSchema, BaseFactory


class Profile(BaseDocument):
    job_id = ReferenceField(Job, reverse_delete_rule=CASCADE)
    profile = DictField()
    code = LongField()
    meta = {
        'collection': 'profiles',
        'index_background': True,
        'auto_create_index': True,
        'indexes': [
            'job_id',
            'code'
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
