import requests

from unittest.case import TestCase

from common.config import config


class Test(TestCase):

    def setUp(self):
        services_url = 'http://{host}:{port}/api'.format(**config['web_app'])
        self.movie_endpoint = '{0}/movies'.format(services_url)
        self.search_movie_endpoint = '{0}/search/movies'.format(services_url)

    def test_get_movie(self):
        '''
        Getting a movie with the correct id returns it
        '''
        movies = requests.get(self.search_movie_endpoint + '?query=a').json()
        movie_title = movies[0]['title']

        movie = requests.get(self.movie_endpoint + '/' + movies[0]['id']).json()

        self.assertNotEquals('', movie['title'])
        self.assertEquals(movie_title, movie['title'])

    def test_get_movie_status_code(self):
        '''
        Getting a movie with the correct id returns a 200 status code
        '''
        movies = requests.get(self.search_movie_endpoint + '?query=a').json()
        response = requests.get(self.movie_endpoint + '/' + movies[0]['id'])

        self.assertEquals(200, response.status_code)

    def test_get_movie_json(self):
        '''
        Getting a movie with the correct id returns JSON content
        '''
        movies = requests.get(self.search_movie_endpoint + '?query=a').json()
        response = requests.get(self.movie_endpoint + '/' + movies[0]['id'])

        self.assertEquals('application/json', response.headers['content-type'])

    def test_get_movie_404_status_code(self):
        '''
        Getting a movie with a non existing id returns a 404 status code
        '''
        response = requests.get(self.movie_endpoint + '/aaaaaaaaaaaaaaaaaaaaaaaa')
        self.assertEquals(404, response.status_code)

    def test_get_movie_400_status_code(self):
        '''
        Getting a movie with an invalid id returns a 404 status code
        '''
        response = requests.get(self.movie_endpoint + '/abc')
        self.assertEquals(404, response.status_code)

    def test_search(self):
        '''
        Searching with a letter returns results
        '''
        movies = requests.get(self.search_movie_endpoint + '?query=a').json()
        self.assertNotEquals(0, len(movies))

    def test_search_no_results(self):
        '''
        Searching with a query that doesn't match anything returns an empty array
        '''
        movies = requests.get(self.search_movie_endpoint + '?query=abcdefghijk').json()
        self.assertEquals([], movies)

    def test_search_no_query(self):
        '''
        Searching without the query parameter is a bad request
        '''
        response = requests.get(self.search_movie_endpoint)
        self.assertEquals(400, response.status_code)

    def test_search_keys(self):
        '''
        All elements of a search contain: id and title
        '''
        movies = requests.get(self.search_movie_endpoint + '?query=a').json()
        for movie in movies:
            self.assertIn('id', movie.keys())
            self.assertIn('title', movie.keys())
