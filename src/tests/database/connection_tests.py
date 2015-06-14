import json

from motor import MotorClient
from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test

from common.config import config
from database.connection import motor_client


MOVIES_TEST_COLLECTION = 'movies_test'


class AsyncTest(AsyncTestCase):

    def setUp(self):
        '''
        Add test data to movies_test collection
        '''
        super(AsyncTest, self).setUp()
        connection_string = 'mongodb://{user}:{password}@{host}:{port}/{name}'.format(**config['mongo_connection'])
        self.collection = MotorClient(connection_string)[config['mongo_connection']['name']][MOVIES_TEST_COLLECTION]
        self.io_loop.run_sync(self.setup_coroutine)

    @coroutine
    def setup_coroutine(self):
        movies = []
        with open('movies_sample.json') as json_file:
            movies = json.load(json_file)

        yield self.collection.remove()
        yield self.collection.insert(movies)

    def test_right_database(self):
        '''
        Gets the right database
        '''
        self.assertEquals('uber', motor_client.name)

    @gen_test
    def test_operation(self):
        movie = yield self.collection.find_one({'title': 'Copycat'})
        self.assertEqual('Copycat', movie['title'])

    @gen_test
    def tearDown(self):
        '''
        Remove test data
        '''
        yield self.collection.remove()
