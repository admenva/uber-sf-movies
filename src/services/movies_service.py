#!/usr/bin/env python

import logging.config
import sys
import yaml

from os import path
from tornado.ioloop import IOLoop
from tornado.web import Application, url

from common.config import config
from common.log import logger
from services.handlers import movies_handler


if __name__ == '__main__':
    logging_conf = path.join(path.dirname(path.abspath(sys.modules['__main__'].__file__)), 'movies-logging.yaml')
    if path.exists(logging_conf):
        with open(logging_conf) as conf:
            logging.config.dictConfig(yaml.load(conf))

    app = Application([
        url(r'/api/movies/([a-z0-9]+)', movies_handler.GetMovieByIdHandler),
        url(r'/api/search/movies', movies_handler.MoviesSearchHandler)
    ])

    port = config['web_app']['port']
    logger.info('Starting Tornado server in port {0}'.format(port))

    app.listen(port)
    IOLoop.current().start()
