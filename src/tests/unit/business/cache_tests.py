from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test
from unittest.case import TestCase

from business.cache import LRUCache


class AsyncTest(AsyncTestCase):

    @gen_test
    def test_cache_miss(self):
        '''
        A cache miss retrieves an element from retrieval_method
        '''
        @coroutine
        def retrieval_method(key):
            return 'value'

        cache = LRUCache(4, retrieval_method)
        result = yield cache.get('key')

        self.assertEquals('value', result)

    @gen_test
    def test_cache_hit(self):
        '''
        A cache hit does not call retrieval_method and gets the value from the cache
        '''
        @coroutine
        def retrieval_method(key):
            return 'value'

        @coroutine
        def retrieval_method_raise(key):
            raise Exception('This shouldnt be called anymore')

        cache = LRUCache(4, retrieval_method)
        yield cache.get('key')  # Cache miss

        cache.retrieval_method = retrieval_method_raise
        result = yield cache.get('key')  # Hit. Otherwise raises Exceptoin

        self.assertEquals('value', result)

    @gen_test
    def test_cache_already_added_key(self):
        '''
        If another request sets the key before retrieval_method is done the method is read normally
        '''
        cache = None

        @coroutine
        def retrieval_method(key):
            cache._add_to_cache('key', 'value')
            return 'value'

        cache = LRUCache(4, retrieval_method)
        result = yield cache.get('key')

        self.assertEquals('value', result)


class Test(TestCase):

    def _queue_to_list(self, queue):
        result = []
        node = queue.head

        while node is not None:
            result.append(node.content)
            node = node.right

        return result

    def test_add_to_cache_keys(self):
        '''
        _add_to_cache adds keys to the dict
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4']
        for key in keys:
            cache._add_to_cache(key, 'value')

        self.assertEquals(sorted(cache.elements.keys()), keys)

    def test_add_to_cache_values(self):
        '''
        _add_to_cache adds values to the dict
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4']
        for key in keys:
            cache._add_to_cache(key, 'value_{0}'.format(key))

        expected_values = ['value_{0}'.format(key) for key in keys]
        values = [value[0] for value in cache.elements.values()]

        self.assertEquals(expected_values, sorted(values))

    def test_add_to_cache_node(self):
        '''
        _add_to_cache adds a node to the dict that is the same as the last one of the queue
        '''
        cache = LRUCache(4, lambda _: None)
        cache._add_to_cache('key', 'value')

        node = cache.elements['key'][1]

        self.assertIs(node, cache.lru_queue.tail)

    def test_add_to_cache_increase_len(self):
        '''
        _add_to_cache increases length
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4']
        for key in keys:
            cache._add_to_cache(key, 'value')

        self.assertEquals(len(keys), len(cache))

    def test_add_to_cache_preempt(self):
        '''
        _add_to_cache preempts least recently used key
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4', 'key5']
        for key in keys:
            cache._add_to_cache(key, 'value')

        self.assertEquals(4, len(cache))
        self.assertEquals(4, len(cache.elements))
        self.assertEquals(4, len(cache.lru_queue))
        self.assertEquals(keys[1:], self._queue_to_list(cache.lru_queue))

    def test_add_to_cache_preempt_dict(self):
        '''
        _add_to_cache removes key from dict
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4', 'key5']
        for key in keys:
            cache._add_to_cache(key, 'value')

        self.assertNotIn('key1', cache.elements)

    def test_add_to_cache_preempt_several(self):
        '''
        _add_to_cache preempts several keys
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4', 'key5', 'key6', 'key7', 'key8', 'key9']
        for key in keys:
            cache._add_to_cache(key, 'value')

        self.assertEquals(4, len(cache))
        self.assertEquals(4, len(cache.elements))
        self.assertEquals(4, len(cache.lru_queue))
        self.assertEquals(keys[5:], self._queue_to_list(cache.lru_queue))

    def test_reorder_lru(self):
        '''
        _reorder_lru does nothing with last element
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4']
        for key in keys:
            cache._add_to_cache(key, 'value')

        tail = cache.elements['key4'][1]

        before_reorder_list = self._queue_to_list(cache.lru_queue)
        cache._reorder_lru(tail)
        after_reorder_list = self._queue_to_list(cache.lru_queue)

        self.assertEquals(before_reorder_list, after_reorder_list)

    def test_reorder_lru_put_first_back(self):
        '''
        _reorder_lru puts first element back
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4']
        for key in keys:
            cache._add_to_cache(key, 'value')

        node = cache.elements['key1'][1]

        cache._reorder_lru(node)
        after_reorder_list = self._queue_to_list(cache.lru_queue)

        self.assertEquals(4, len(after_reorder_list))
        self.assertEquals(['key2', 'key3', 'key4', 'key1'], after_reorder_list)

    def test_reorder_lru_put_middle_back(self):
        '''
        _reorder_lru puts an element in the middle back
        '''
        cache = LRUCache(4, lambda _: None)

        keys = ['key1', 'key2', 'key3', 'key4']
        for key in keys:
            cache._add_to_cache(key, 'value')

        node = cache.elements['key2'][1]

        cache._reorder_lru(node)
        after_reorder_list = self._queue_to_list(cache.lru_queue)

        self.assertEquals(4, len(after_reorder_list))
        self.assertEquals(['key1', 'key3', 'key4', 'key2'], after_reorder_list)
