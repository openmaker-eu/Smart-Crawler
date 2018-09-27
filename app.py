import tornado.ioloop
from tornado.options import options
import tornado.web

from decouple import config
from settings import app_settings

from urls import url_patterns
from logging import handlers
import logging
from mongoengine import connect
import time
import os

os.makedirs('./logs', exist_ok=True)

log_file = "./logs/daily_" + time.strftime("%d-%m-%Y") + ".log"

daily_handler = handlers.TimedRotatingFileHandler(
    log_file,
    when='midnight',
    interval=1,
    backupCount=7
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s %(asctime)s %(pathname)s@%(funcName)s:%(lineno)s] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    handlers=[
        daily_handler,
        logging.StreamHandler()
    ],
)


class SmartCrawlerApp(tornado.web.Application):
    def __init__(self, testing=False):
        super(SmartCrawlerApp, self).__init__(url_patterns, **app_settings, autoreload=not testing)


def main():
    options.parse_command_line()

    logging.getLogger('tornado.access').disabled = True

    app = SmartCrawlerApp()
    app.listen(app_settings["port"])

    connect(
        config('MONGODB_DB'),
        username=config('MONGODB_USER'),
        password=config('MONGODB_PASSWORD'),
        host=config('MONGODB_HOST'),
        port=config('MONGODB_PORT', cast=int),
        authentication_source='admin',
        connect=False
    )

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
