import string

from tornado.gen import coroutine, Return

from business.cache import LRUCache
from database.dao import movies_dao


@coroutine
def get(movie_id):
    '''
    Returns a movie given its id
    '''
    movie = yield movies_dao.find_by_id(movie_id)
    raise Return(movie)


@coroutine
def search_by_title(search_text):
    '''
    Returns a list of movies matching the search criteria
    '''
    search_text = _sanitize_input(search_text)

    if len(search_text) > 0:
        movies = yield search_cache.get(search_text)
    else:
        movies = []

    raise Return(movies)


def _sanitize_input(text):
    '''
    Sanitizes the input leaving only characters matching "[A-Za-z0-9 ]"
    '''
    valid_chars = string.ascii_letters + string.digits + ' '
    delete_table = string.maketrans(valid_chars, '_' * len(valid_chars))
    return text.encode('utf-8').translate(None, delete_table)


search_cache = LRUCache(10, movies_dao.search_by_title)
