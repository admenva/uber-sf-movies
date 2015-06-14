from unittest.case import TestCase

from business.cache import DoublyLinkedNode, Queue


class Test(TestCase):

    def _to_list(self, queue):
        result = []
        node = queue.head

        while node is not None:
            result.append(node)
            node = node.right

        return result

    def _get_queue_with_elements(self):
        queue = Queue()
        elements = [DoublyLinkedNode(1), DoublyLinkedNode(2), DoublyLinkedNode(3), DoublyLinkedNode(4)]

        for node in elements:
            queue.enqueue(node)

        return queue, elements

    def test_enqueue(self):
        '''
        Enqueueing operation adds all elements in order (to the end)
        '''
        queue, elements = self._get_queue_with_elements()
        self.assertEqual(elements, self._to_list(queue))

    def test_enqueue_length(self):
        '''
        Enqueue keeps track of the length of the queue
        '''
        queue, elements = self._get_queue_with_elements()
        self.assertEqual(len(elements), len(queue))

    def test_enqueue_head(self):
        '''
        Head points to the first element of the queue
        '''
        queue, elements = self._get_queue_with_elements()
        self.assertEqual(elements[0], queue.head)

    def test_enqueue_tail(self):
        '''
        Tail points to the last element of the queue
        '''
        queue, elements = self._get_queue_with_elements()
        self.assertEqual(elements[len(elements) - 1], queue.tail)

    def test_enqueue_content(self):
        '''
        Content of the nodes is correct
        '''
        queue, elements = self._get_queue_with_elements()

        expected_content = [elem.content for elem in elements]
        content = [elem.content for elem in self._to_list(queue)]

        self.assertEqual(expected_content, content)

    def test_dequeue_empty(self):
        '''
        Dequeueing an empty queue throws an IndexError exception
        '''
        queue = Queue()
        with self.assertRaises(IndexError):
            queue.dequeue()

    def test_dequeue_all(self):
        '''
        Dequeueing all the elements leaves an empty queue
        '''
        queue, elements = self._get_queue_with_elements()

        for _ in elements:
            queue.dequeue()

        self.assertEqual([], self._to_list(queue))

    def test_dequeue_all_length(self):
        '''
        Dequeueing all the elements leaves a queue with length 0
        '''
        queue, elements = self._get_queue_with_elements()

        for _ in elements:
            queue.dequeue()

        self.assertEqual(0, len(queue))

    def test_dequeue_all_head(self):
        '''
        Dequeueing all the elements sets head to None
        '''
        queue, elements = self._get_queue_with_elements()

        for _ in elements:
            queue.dequeue()

        self.assertIs(None, queue.head)

    def test_dequeue_all_tail(self):
        '''
        Dequeueing all the elements sets tail to None
        '''
        queue, elements = self._get_queue_with_elements()

        for _ in elements:
            queue.dequeue()

        self.assertIs(None, queue.tail)

    def test_dequeue_head_equals_tail(self):
        '''
        Dequeueing all but one has same head than tail
        '''
        queue, elements = self._get_queue_with_elements()

        for _ in range(1, len(elements)):
            queue.dequeue()

        self.assertIs(queue.head, queue.tail)

    def test_dequeue_one(self):
        '''
        Dequeueing one element returns the front element
        '''
        queue, elements = self._get_queue_with_elements()
        element = queue.dequeue()

        self.assertEqual(elements[0].content, element)

    def test_dequeue_one_order(self):
        '''
        Dequeueing one element leaves the rest untouched
        '''
        queue, elements = self._get_queue_with_elements()
        queue.dequeue()

        self.assertEqual(elements[1:], self._to_list(queue))
