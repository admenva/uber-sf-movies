from unittest.case import TestCase

import business.movies


class Test(TestCase):

    def test_sanitize_input_invalid(self):
        '''
        _sanitize_input removes characters that don't match "[A-Za-z0-9 ]"
        '''
        result = business.movies._sanitize_input(r'HEllo 123~`@#$%^&*()-_+={}[]\|:;"/?.,<> World')
        self.assertEquals('HEllo 123 World', result)

    def test_sanitize_input_valid(self):
        '''
        A text with only valid characters is left untached
        '''
        result = business.movies._sanitize_input('ABCDE abcde 12345')
        self.assertEquals('ABCDE abcde 12345', result)
