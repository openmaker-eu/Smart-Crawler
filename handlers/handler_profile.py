from handlers.base import BaseHandler, TemplateRendering
from logic.logic_job import get_jobs, get_job
from logic.logic_profile import get_profiles


class ProfilesHandler(BaseHandler, TemplateRendering):
    def get(self):
        job_id = self.get_argument('job_id', None)
        if job_id:
            limit = int(self.get_argument('limit', 24))
            skip = int(self.get_argument('skip', 0))
            profiles = get_profiles(job_id, limit, skip)
            variables = {
                'profiles': profiles,
                'jobs': get_jobs(),
                'current_job': get_job(job_id),
                'title': "Profiles",
                'type': "profiles"
            }
            if skip != 0:
                response = self.render_template("profiles/show.html", {'profiles': profiles})
            else:
                response = self.render_template("profiles/index.html", variables)
        else:
            variables = {
                'profiles': [],
                'jobs': get_jobs(),
                'current_job': None,
                'title': "Profiles",
                'type': "profiles"
            }
            response = self.render_template("profiles/index.html", variables)

        self.write(response)
