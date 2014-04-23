# import unittest

# from nmmd.ext.regex import RegexDispatcher

# class Processor:
#     '''A toy dispatcher client.
#     '''
#     dispatcher = RegexDispatcher()

#     @dispatcher(r'\((\d{3})\)\s*(\d{3})\-?(\d{4})')
#     def handle_phone(self, string, matchobj):
#         from nose.tools import set_trace; set_trace()

#     @dispatcher(r'\d{3}-\d{2}-\d{4}')
#     def handle_ssn(self, string, matchobj):
#         from nose.tools import set_trace; set_trace()

#     @dispatcher(r'moomoo')
#     def handle_cow(self, string, matchobj):
#         from nose.tools import set_trace; set_trace()

#     def process(self, *args, **kwargs):
#         return self.dispatcher.dispatch(*args, **kwargs)


# class TestRegexDispatcher(unittest.TestCase):

#     processor = Processor()

#     def test_phone(self):
#         method, meta = self.processor.dispatcher.get_method('(123) 555-1234')
#         self.assertEqual(method, self.processor.handle_phone)

#     def test_ssn(self):
#         method, meta = self.processor.dispatcher.get_method('123-45-6789')
#         self.assertEqual(method, self.processor.handle_ssn)

#     def test_cow(self):
#         method, meta = self.processor.dispatcher.get_method('moomoomoo')
#         self.assertEqual(method, self.processor.handle_cow)
