import json
import unittest

from motor import MotorClient
from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test

from common.config import config
from database.dao import movies_dao
from database.query import Query


MOVIES_TEST_COLLECTION = 'movies_test'
old_find_one = Query.find_one
old_find = Query.find


class AsyncTest(AsyncTestCase):

    def _get_query_object(self):
        query = Query(MOVIES_TEST_COLLECTION)
        query._collection = self.collection
        return query

    def _patch_query(self):
        def new_find_one(_self):
            _self._collection = self.collection
            return old_find_one(_self)

        def new_find(_self):
            _self._collection = self.collection
            return old_find(_self)

        Query.find_one = new_find_one
        Query.find = new_find

    def setUp(self):
        '''
        Add test data to movies_test collection
        '''
        super(AsyncTest, self).setUp()
        connection_string = 'mongodb://{user}:{password}@{host}:{port}/{name}'.format(**config['mongo_connection'])

        self.client = MotorClient(connection_string)
        self.collection = self.client[config['mongo_connection']['name']][MOVIES_TEST_COLLECTION]

        self._patch_query()

        self.io_loop.run_sync(self.setup_coroutine)

    @coroutine
    def setup_coroutine(self):
        movies = []
        with open('movies_sample.json') as json_file:
            movies = json.load(json_file)

        yield self.collection.remove()
        yield self.collection.insert(movies)

    @gen_test
    def test_find_by_id(self):
        '''
        Retrieve a movie given an id
        '''
        movie = yield Query(MOVIES_TEST_COLLECTION).find_one()
        movie = yield movies_dao.find_by_id(movie['id'])

        self.assertIsNot(None, movie)

    @gen_test
    def test_find_by_id_none(self):
        '''
        None if the id doesn't exist
        '''
        movie = yield movies_dao.find_by_id('doesnt_exist')
        self.assertIs(None, movie)

    @gen_test
    def test_search_one_letter(self):
        '''
        Returns all movies containing single letter
        '''
        yield self._get_query_object().ensure_indexes()
        movies = yield movies_dao.search_by_title('a')
        self.assertEquals(5, len(movies))

    @gen_test
    def test_search_one_word(self):
        '''
        Returns one movie with a exact match
        '''
        yield self._get_query_object().ensure_indexes()
        movies = yield movies_dao.search_by_title('copycat')
        self.assertEquals('Copycat', movies[0]['title'])

    @gen_test
    def test_search_several_words(self):
        '''
        Returns all movies with a word match
        '''
        yield self._get_query_object().ensure_indexes()
        movies = yield movies_dao.search_by_title('copycat gentleman')

        titles = [movie['title'] for movie in movies]
        self.assertEquals(['Copycat', 'Gentleman Jim'], sorted(titles))

    @gen_test
    def test_search_no_match(self):
        '''
        Returns an empty list if there is no match
        '''
        yield self._get_query_object().ensure_indexes()
        movies = yield movies_dao.search_by_title('doesnt_exist')
        self.assertEquals([], movies)

    @gen_test
    def test_search_score(self):
        '''
        Returns the one with the highest score first
        '''
        yield self._get_query_object().ensure_indexes()
        movies = yield movies_dao.search_by_title('copycat a')
        self.assertEquals('Copycat', movies[0]['title'])

    @gen_test
    def test_search_non_zero_score(self):
        '''
        Returns a score bigger than 0 for a word match
        '''
        yield self._get_query_object().ensure_indexes()
        movies = yield movies_dao.search_by_title('copycat')
        self.assertNotEquals(0, movies[0]['score'])

    @gen_test
    def tearDown(self):
        '''
        Remove test data
        '''
        Query.find_one = old_find_one
        Query.find = old_find
        yield self.collection.remove()


if __name__ == '__main__':
    unittest.main()
