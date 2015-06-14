import json
import pymongo

from motor import MotorClient
from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test

from common.config import config
from database.query import Query


MOVIES_TEST_COLLECTION = 'movies_test'


class AsyncTest(AsyncTestCase):

    def _get_query_object(self):
        query = Query(MOVIES_TEST_COLLECTION)
        query._collection = self.collection
        return query

    def setUp(self):
        '''
        Add test data to movies_test collection
        '''
        super(AsyncTest, self).setUp()
        connection_string = 'mongodb://{user}:{password}@{host}:{port}/{name}'.format(**config['mongo_connection'])

        self.client = MotorClient(connection_string)
        self.collection = self.client[config['mongo_connection']['name']][MOVIES_TEST_COLLECTION]

        self.io_loop.run_sync(self.setup_coroutine)

    @coroutine
    def setup_coroutine(self):
        movies = []
        with open('movies_sample.json') as json_file:
            movies = json.load(json_file)

        yield self.collection.remove()
        yield self.collection.insert(movies)

    @gen_test
    def test_limit_empty(self):
        '''
        If no limit is passed to the query, all the documents are retireved
        '''
        movies = yield self._get_query_object().find()
        self.assertEquals(5, len(movies))

    @gen_test
    def test_limit(self):
        '''
        If there is a limit, limit elements are retireved
        '''
        movies = yield self._get_query_object().limit(2).find()
        self.assertEquals(2, len(movies))

    @gen_test
    def test_select_true(self):
        '''
        Selects only the attributes requested and id
        '''
        movie = yield self._get_query_object().select({'title': True, 'fun_facts': True}).find_one()
        self.assertEquals(['fun_facts', 'id', 'title'], sorted(movie.keys()))

    @gen_test
    def test_select_false(self):
        '''
        Does not select requested attributes
        '''
        movie = yield self._get_query_object().select({'title': False, 'fun_facts': False}).find_one()
        self.assertNotIn('fun_facts', movie.keys())
        self.assertNotIn('title', movie.keys())

    @gen_test
    def test_not_found(self):
        '''
        Returns None if no element was found
        '''
        movie = yield self._get_query_object().where({'doesnt': 'exist'}).find_one()
        self.assertIs(None, movie)

    @gen_test
    def test_insert(self):
        '''
        Inserts a document to database
        '''
        yield self._get_query_object().insert({'title': 'movie'})
        movie = yield self._get_query_object().where({'title': 'movie'}).find_one()
        self.assertIsNot(None, movie)

    @gen_test
    def test_find(self):
        '''
        Find returns a list of elements
        '''
        movies = yield self._get_query_object().find()
        expected_titles = [
            '50 First Dates', 'Copycat', 'Gentleman Jim', 'God is a Communist?* (show me heart universe)', 'Heart Beat'
        ]
        titles = [movie['title'] for movie in movies]
        self.assertEquals(expected_titles, sorted(titles))

    @gen_test
    def test_find_empty(self):
        '''
        Find returns an empty list if nothing is found
        '''
        movies = yield self._get_query_object().where({'doesnt': 'exist'}).find()
        self.assertEquals([], movies)

    @gen_test
    def test_removed_id(self):
        '''
        A single movie has id instead of _id
        '''
        movie = yield self._get_query_object().find_one()

        self.assertNotIn('_id', movie.keys())
        self.assertIn('id', movie.keys())

    @gen_test
    def test_removed_id_list(self):
        '''
        Elements have id instead of _id
        '''
        movies = yield self._get_query_object().find()

        for movie in movies:
            self.assertNotIn('_id', movie.keys())
            self.assertIn('id', movie.keys())

    @gen_test
    def test_sort(self):
        '''
        Elements are sorted
        '''
        movies = yield self._get_query_object().sort([('title', 1)]).find()

        expected_titles = [
            '50 First Dates', 'Copycat', 'Gentleman Jim', 'God is a Communist?* (show me heart universe)', 'Heart Beat'
        ]
        titles = [movie['title'] for movie in movies]
        self.assertEquals(expected_titles, titles)

    @gen_test
    def test_sort_descending(self):
        '''
        Elements are sorted in opposite direction
        '''
        movies = yield self._get_query_object().sort([('title', pymongo.DESCENDING)]).find()

        expected_titles = [
            'Heart Beat', 'God is a Communist?* (show me heart universe)', 'Gentleman Jim', 'Copycat', '50 First Dates'
        ]
        titles = [movie['title'] for movie in movies]
        self.assertEquals(expected_titles, titles)

    @gen_test
    def tearDown(self):
        '''
        Remove test data
        '''
        yield self.collection.remove()
