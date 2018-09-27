from handlers.base import StaticHandler
from handlers.handler_job import JobHandler
from settings import app_settings

url_patterns = [
    # --- JOB --- #
    (r"/job", JobHandler),
    (r"/job/(.*)$", JobHandler),
    (r"/jobs", JobHandler),

    (r"/static/(.*)", StaticHandler, {'path': app_settings['template_path']}),
]
