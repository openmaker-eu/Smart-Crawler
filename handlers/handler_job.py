import json

from handlers.base import BaseHandler, TemplateRendering
from logic.logic_job import get_jobs, get_job, post_job, post_job_is_active, delete_job, update_job


class JobsHandler(BaseHandler, TemplateRendering):
    def get(self):
        variables = {
            'jobs': get_jobs(),
            'title': "Jobs",
            'type': "jobs"
        }
        self.write(self.render_template("jobs/index.html", variables))


class JobHandler(BaseHandler, TemplateRendering):
    def get(self, job_id='new'):
        variables = {
            'job': get_job(job_id),
            'title': "Jobs",
            'type': "jobs"
        }
        template_name = "jobs/create.html" if job_id=='new' else "jobs/edit.html"
        self.write(self.render_template(template_name, variables))

    def post(self, job_id=None):
        if job_id:
            job_name = self.get_argument("jobName")
            seed_list = self.get_argument("seedList").split(",")
            twitter_access_key = self.get_argument("twAccKey")
            twitter_access_secret = self.get_argument("twAccSecret")

            seed_list = list(map(int, seed_list))

            response = update_job(job_id, job_name, seed_list, twitter_access_key, twitter_access_secret)
        else:
            job_name = self.get_argument("jobName")
            seed_list = self.get_argument("seedList").split(",")
            classifiers = self.get_argument("classifiersEditorValue")
            crawling_score = self.get_argument("crawlingScoresEditorValue")
            twitter_access_key = self.get_argument("twAccKey")
            twitter_access_secret = self.get_argument("twAccSecret")

            seed_list = list(map(int, seed_list))

            response = post_job(job_name, classifiers, crawling_score, seed_list, twitter_access_key, twitter_access_secret)

        self.write(response)

    def put(self, job_id=None):
        is_active = self.get_argument("isActive")
        is_active = True if is_active == "1" else False

        response = post_job_is_active(job_id, is_active)
        self.write(response)

    def delete(self, job_id=None):
        response = delete_job(job_id)
        self.write(response)
