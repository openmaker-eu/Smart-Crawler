from handlers.base import StaticHandler
from handlers.handler_home import HomeHandler
from handlers.handler_job import JobHandler, JobsHandler
from settings import app_settings

url_patterns = [
    # --- HOME --- #
    (r"/", HomeHandler),

    # --- JOB --- #
    (r"/job/(.*)$", JobHandler),
    (r"/job", JobHandler),
    (r"/jobs", JobsHandler),

    (r"/static/(.*)", StaticHandler, {'path': app_settings['template_path']}),
]
