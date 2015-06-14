import pymongo

from tornado.gen import coroutine, Return

from database.connection import motor_client


MOVIES_COLLECTION = 'movies'


class Query(object):
    '''
    Abstraction to retrieve documents from the database
    '''

    def __init__(self, collection):
        self._collection = motor_client[collection]
        self._criteria = {}
        self._fields = None
        self._limit = 0
        self._sort = None

    def limit(self, limit):
        '''
        Sets the maximum number of documents to retrieve
        '''
        self._limit = limit
        return self

    def select(self, fields):
        '''
        Sets the fields that should or should not be retrieved
        '''
        self._fields = fields
        return self

    def sort(self, criteria):
        '''
        Specifies the search criteria
        '''
        self._sort = criteria
        return self

    def where(self, criteria):
        '''
        Specifies the criteria for the documents to retrieve
        '''
        self._criteria = criteria
        return self

    @coroutine
    def find_one(self):
        '''
        Retrieve a single document
        '''
        result = yield self._collection.find_one(self._criteria, self._fields)
        raise Return(self._prepare_document(result))

    @coroutine
    def find(self):
        '''
        Retrieve multiple documents and return them in a list
        '''
        cursor = self._collection.find(self._criteria, self._fields)

        if self._sort is not None:
            cursor.sort(self._sort)

        cursor.limit(self._limit)

        documents = []
        while (yield cursor.fetch_next):
            documents.append(self._prepare_document(cursor.next_object()))

        raise Return(documents)

    @coroutine
    def insert(self, documents):
        '''
        Insert one or multiple documents
        '''
        result = yield self._collection.insert(documents)
        raise Return(result)

    @coroutine
    def ensure_indexes(self):
        '''
        Creates all the indexes of the database
        '''
        # Text index to perform search queries on title
        yield self._collection.ensure_index([('title', pymongo.TEXT)])

        # Normal index on title
        yield self._collection.ensure_index('title', unique=True)

    def _prepare_document(self, document):
        '''
        Converts the field _id to a string and renames it to id
        '''
        if document is None:
            return document

        document['id'] = str(document['_id'])
        del document['_id']
        return document
