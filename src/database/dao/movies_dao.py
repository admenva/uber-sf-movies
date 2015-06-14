import re

from bson.errors import InvalidId
from bson.objectid import ObjectId
from tornado.gen import coroutine, Return

from common.config import config
from database.query import MOVIES_COLLECTION, Query


@coroutine
def find_by_id(movie_id):
    '''
    Retrieves a movie by its id from the database
    '''
    try:
        result = yield Query(MOVIES_COLLECTION).where({'_id': ObjectId(movie_id)}).find_one()
    except InvalidId:
        result = None

    raise Return(result)


@coroutine
def search_by_title(title_text):
    '''
    Retrieves a list of movies matching a given text from the database
    '''
    title_regex = '({0})'.format('|'.join(title_text.split(' ')))

    search_criteria = {'$or': [{'$text': {'$search': title_text}}, {'title': re.compile(title_regex, re.IGNORECASE)}]}
    selection = {'score': {'$meta': 'textScore'}, '_id': True, 'title': True, 'release_year': True}
    sort_criteria = [('score', {'$meta': 'textScore'})]
    limit = config['pagination']['max_movies_per_search']

    result = yield Query(MOVIES_COLLECTION).where(
        search_criteria).select(selection).sort(sort_criteria).limit(limit).find()
    raise Return(result)
