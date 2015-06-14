from tornado.gen import coroutine, Return

from common.log import logger


class DoublyLinkedNode(object):
    '''
    Doubly Linked Node to be used by the Doubly Linked List
    '''

    def __init__(self, content):
        self.content = content
        self.left = None
        self.right = None


class Queue(object):
    '''
    Doubly Linked List implementing a Queue data structure.
    All operations take constant time O(n)
    '''

    def __init__(self):
        self.len = 0
        self.head = None
        self.tail = None

    def __len__(self):
        return self.len

    def enqueue(self, new_node):
        '''
        Adds an instance of DoublyLinkedNode to the end of the list
        '''
        if self.head is None and self.tail is None:
            self.tail = new_node
            self.head = self.tail

        else:
            self.tail.right = new_node
            new_node.left = self.tail
            self.tail = new_node

        self.len += 1

    def dequeue(self):
        '''
        Removes the first element from the list and returns its content
        '''
        if self.len == 0:
            raise IndexError()

        content = self.head.content

        if self.len == 1:
            self.head = None
            self.tail = None
        else:
            self.head = self.head.right

        if self.len == 2:
            self.tail.left = None

        self.len -= 1
        return content


class LRUCache(object):
    '''
    Least Recently Used cache. All operations take constant time O(1)
    '''

    def __init__(self, max_size, retrieval_method):
        self.max_size = max_size
        self.retrieval_method = retrieval_method
        self.elements = {}
        self.lru_queue = Queue()
        self.len = 0

    def __len__(self):
        return self.len

    @coroutine
    def get(self, key):
        '''
        Retrieve an element from the cache using its key. If it is not found,
        use the retrieval_method to find it
        '''
        try:
            results, node = self.elements[key]
        except KeyError:
            logger.debug('Cache miss for key "{0}"'.format(key))
            results = yield self.retrieval_method(key)

            # Check that another request hasn't added the key already
            try:
                results, node = self.elements[key]
            except KeyError:
                self._add_to_cache(key, results)
                raise Return(results)

        logger.debug('Cache hit for key "{0}"'.format(key))
        self._reorder_lru(node)
        raise Return(results)

    def _add_to_cache(self, key, results):
        '''
        Adds the pair (key, value) to the cache. Preempts the least recently
        used value if the cache is full
        '''
        if self.len >= self.max_size:
            removed_key = self.lru_queue.dequeue()
            del self.elements[removed_key]
            self.len -= 1

        node = DoublyLinkedNode(key)
        self.elements[key] = (results, node)
        self.lru_queue.enqueue(node)
        self.len += 1

    def _reorder_lru(self, node):
        '''
        Reorders the queue so that the node with key "key" is removed and appended
        at the end
        '''
        if node is self.lru_queue.tail:
            return

        # Remove node from current position
        if node is self.lru_queue.head:
            self.lru_queue.head = node.right
        else:
            node.left.right = node.right

        node.right.left = node.left

        # Add node reference to the end of the list
        node.left = None
        node.right = None
        self.lru_queue.enqueue(node)
