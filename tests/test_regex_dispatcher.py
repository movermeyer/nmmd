import re
import unittest
from nose.tools import assert_raises

from nmmd import DispatchError
from nmmd.ext.regex import RegexDispatcher


class Processor:
    '''A toy dispatcher client.
    '''
    dispatcher = RegexDispatcher()

    def process(self, *args, **kwargs):
        return self.dispatcher.dispatch(*args, **kwargs)

    # -----------------------------------------------------------------------
    # Function dispatch methods.
    # -----------------------------------------------------------------------
    @dispatcher(r'\((\d{3})\)\s*(\d{3})\-?(\d{4})')
    def handle_phone(self, string, matchobj):
        return 'phone'

    @dispatcher(r'\d{3}-\d{2}-\d{4}')
    def handle_ssn(self, string, matchobj):
        return 'ssn'

    @dispatcher(r'moomoo')
    def handle_cow(self, string, matchobj):
        return 'cow'

    # -----------------------------------------------------------------------
    # Iter dispatch methods.
    # -----------------------------------------------------------------------
    @dispatcher(r'a', flags=re.I)
    def handle_a(self, string, matchobj):
        return 'a'

    @dispatcher(r'[aeiou]', flags=re.I)
    def handle_vowel(self, string, matchobj):
        return 'vowel'

    @dispatcher(r'[bcdfhjklmnp]', flags=re.I)
    def handle_consonant(self, string, matchobj):
        return 'consonant'

    @dispatcher(r'[a-z]', flags=re.I)
    def handle_letter(self, string, matchobj):
        return 'letter'


class TestRegexDispatcher(unittest.TestCase):

    processor = Processor()

    # -----------------------------------------------------------------------
    # Test basic method resolution.
    # -----------------------------------------------------------------------
    def test_resolve_phone(self):
        method, meta = self.processor.dispatcher.get_method('(123) 555-1234')
        self.assertEqual(method, self.processor.handle_phone)

    def test_resolve_ssn(self):
        method, meta = self.processor.dispatcher.get_method('123-45-6789')
        self.assertEqual(method, self.processor.handle_ssn)

    def test_resolve_cow(self):
        method, meta = self.processor.dispatcher.get_method('moomoomoo')
        self.assertEqual(method, self.processor.handle_cow)

    def test_resolve_failure(self):
        method = self.processor.dispatcher.get_method
        assert_raises(DispatchError, method, '1')

    # -----------------------------------------------------------------------
    # Test basic method dispatch.
    # -----------------------------------------------------------------------
    def test_dispatch_phone(self):
        result = self.processor.dispatcher.dispatch('(123) 555-1234')
        self.assertEqual(result, 'phone')

    def test_dispatch_ssn(self):
        result = self.processor.dispatcher.dispatch('123-45-6789')
        self.assertEqual(result, 'ssn')

    def test_dispatch_cow(self):
        result = self.processor.dispatcher.dispatch('moomoomoo')
        self.assertEqual(result, 'cow')

    # -----------------------------------------------------------------------
    # Test iter method resolution.
    # -----------------------------------------------------------------------
    def test_resolve_vowel(self):
        expected = set([
            self.processor.handle_vowel,
            self.processor.handle_letter
            ])
        methods = self.processor.dispatcher.gen_methods('e')
        methods = set(dict(methods))
        self.assertEqual(methods, expected)

    def test_resolve_a(self):
        expected = set([
            self.processor.handle_vowel,
            self.processor.handle_letter,
            self.processor.handle_a,
            ])
        methods = self.processor.dispatcher.gen_methods('A')
        methods = set(dict(methods))
        self.assertEqual(methods, expected)

    def test_resolve_consonant(self):
        expected = set([
            self.processor.handle_consonant,
            self.processor.handle_letter
            ])
        methods = self.processor.dispatcher.gen_methods('b')
        methods = set(dict(methods))
        self.assertEqual(methods, expected)

    # -----------------------------------------------------------------------
    # Test iter method dispatch.
    # -----------------------------------------------------------------------
    def test_dispatch_vowel(self):
        expected = set(['vowel', 'letter'])
        vals = set(self.processor.dispatcher.gen_dispatch('e'))
        self.assertEqual(vals, expected)

    def test_dispatch_a(self):
        expected = set(['vowel', 'letter', 'a'])
        vals = set(self.processor.dispatcher.gen_dispatch('A'))
        self.assertEqual(vals, expected)

    def test_dispatch_consonant(self):
        expected = set(['consonant', 'letter'])
        vals = set(self.processor.dispatcher.gen_dispatch('b'))
        self.assertEqual(vals, expected)
