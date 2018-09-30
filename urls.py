from handlers.base import StaticHandler
from handlers.handler_home import HomeHandler
from handlers.handler_job import JobHandler, JobsHandler
from handlers.handler_profile import ProfilesHandler
from settings import app_settings

url_patterns = [
    # --- HOME --- #
    (r"/", HomeHandler),

    # --- JOB --- #
    (r"/job/(.*)$", JobHandler),
    (r"/job", JobHandler),
    (r"/jobs", JobsHandler),

    # --- PROFILES --- #
    (r"/profiles", ProfilesHandler),

    (r"/static/(.*)", StaticHandler, {'path': app_settings['template_path']}),
]
