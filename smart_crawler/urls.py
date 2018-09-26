from smart_crawler.handlers.base import StaticHandler
from smart_crawler.handlers.handler_job import JobHandler
from smart_crawler.settings import app_settings

url_patterns = [
    # --- JOB --- #
    (r"/job", JobHandler),
    (r"/job/(.*)$", JobHandler),
    (r"/jobs", JobHandler),

    (r"/static/(.*)", StaticHandler, {'path': app_settings['template_path']}),
]
