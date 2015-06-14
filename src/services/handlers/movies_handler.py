import json

from tornado.gen import coroutine
from tornado.web import RequestHandler

from common.log import logger
from business import movies


class GetMovieByIdHandler(RequestHandler):

    @coroutine
    def get(self, movie_id):
        '''
        Returns JSON data with a movie given an id
        '''
        logger.info('Processing request /movies/{0}'.format(movie_id))
        movie = yield movies.get(movie_id)

        if movie is None:
            self.set_status(404)
        else:
            self.write(json.dumps(movie))
            self.set_header('Content-Type', 'application/json')


class MoviesSearchHandler(RequestHandler):

    @coroutine
    def get(self):
        '''
        Returns an array of movies in JSON format matching a given search query.
        The query must be included in a parameter called "query"
        '''
        search_text = self.get_argument('query', strip=True)
        logger.info('Processing request /search/movies with query "{0}"'.format(search_text))

        result = yield movies.search_by_title(search_text)

        self.write(json.dumps(result))
        self.set_header('Content-Type', 'application/json')
