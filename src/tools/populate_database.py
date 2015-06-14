#!/usr/bin/env python

import json
import time
import urllib

from pymongo.errors import DuplicateKeyError
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.gen import coroutine, Return
from tornado.ioloop import IOLoop

from database.query import MOVIES_COLLECTION, Query


GOOGLE_GEOCODE_ENDPOINT = 'http://maps.googleapis.com/maps/api/geocode/json'
HTTP_RETRIES = 5


@coroutine
def http_retry_get(url):
    '''
    Retries a request if either it receives an status code different than 200 or if
    the response status content indicates that the status is not "OK"
    '''
    result = None
    retries = 0

    while retries < HTTP_RETRIES:
        try:
            http_client = AsyncHTTPClient()
            result = yield http_client.fetch(url)

            json_result = json.loads(result.body)
            if json_result['status'] == 'OK':
                raise Return(json_result['results'])

        except HTTPError:
            pass

        retries += 1
        time.sleep(1)


@coroutine
def get_location(address):
    '''
    Gets the coordinates of an address using Google's Geolocation API
    '''
    location = None

    if address is not None:
        result = yield http_retry_get('{0}?address=san+francisco+{1}'.format(
            GOOGLE_GEOCODE_ENDPOINT, urllib.quote_plus(address.encode('utf-8'))))

        if result is not None:
            coordinates = result[0]['geometry']['location']
            location = {
                'address': address,
                'lat': coordinates['lat'],
                'lng': coordinates['lng']
            }
        else:
            print('Could not find coordinates for address {0}'.format(address.encode('utf-8')))

    raise Return(location)


@coroutine
def load_data():
    '''
    Loads the movie's data and calculate the coordinates for each location
    '''
    with open('tools/sf_movie_locations.json') as json_file:
        json_data = json.load(json_file)
        movies = {}
        movie_id = 1

        for movie in json_data['data']:
            title = movie[8]
            address = movie[10]
            location = yield get_location(address)

            if title in movies:
                if location is not None:
                    movies[title]['locations'].append(location)
            else:
                movies[title] = {
                    'title': title,
                    'release_year': movie[9],
                    'locations': [location] if location is not None else [],
                    'fun_facts': movie[11],
                    'production_company': movie[12],
                    'distributor': movie[13],
                    'director': movie[14],
                    'writer': movie[15],
                    'actors': [f for f in movie[16:19] if f is not None]
                }

                movie_id += 1

    raise Return(movies.values())


@coroutine
def main():
    '''
    Creates the database with the JSON information of movies and its indexes
    '''
    yield Query(MOVIES_COLLECTION).ensure_indexes()

    movies = yield load_data()

    try:
        yield Query(MOVIES_COLLECTION).insert(movies)
    except DuplicateKeyError:
        print('Documents already inserted to the database.')

    IOLoop.current().stop()


if __name__ == '__main__':
    IOLoop.current().add_callback(main)
    IOLoop.current().start()
