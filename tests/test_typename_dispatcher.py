import unittest

from nmmd import TypenameDispatcher

class Processor:
    '''A toy dispatcher client.
    '''
    dispatcher = TypenameDispatcher()

    def handle_str(self, token):
        return 'str'

    def handle_int(self, token):
        return 'int'

    def handle_dict(self, token):
        return 'int'

    def handle_Hashable(self, token, matchobj):
        return 'Hashable'

    def handle_Iterable(self, token, matchobj):
        return 'Iterable'

    def handle_MethodType(self, token, matchobj):
        return 'MethodType'

    def process(self, *args, **kwargs):
        return self.dispatcher.dispatch(*args, **kwargs)


class TestTypenameDispatcher(unittest.TestCase):

    processor = Processor()

    def test_str(self):
        methods = self.processor.dispatcher.gen_methods('somestring')
        methods = set(methods)
        expected = {
            self.processor.handle_str,
            self.processor.handle_Iterable,
            self.processor.handle_Hashable,
            }
        assert methods == expected

    def test_int(self):
        methods = self.processor.dispatcher.gen_methods(1)
        methods = tuple(methods)
        expected = (
            self.processor.handle_int,
            self.processor.handle_Hashable,
            )
        assert methods == expected

    def test_Hashable(self):
        methods = self.processor.dispatcher.gen_methods(dict(cow=1))
        methods = tuple(methods)
        expected = (
            self.processor.handle_dict,
            self.processor.handle_Iterable,
            )
        assert methods == expected

    def test_MethodType(self):
        '''Here we test that a bound method gets caught properly.
        Note that we expect type handlers (i.e., MethodType) to be \
        yielded earlier that interface handlers (i.e., Hashable)
        '''
        class A:
            def b(self):
                pass
        methods = self.processor.dispatcher.gen_methods(A().b)
        methods = tuple(methods)
        expected = (
            self.processor.handle_MethodType,
            self.processor.handle_Hashable,
            )
        assert methods == expected

