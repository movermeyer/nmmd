import re

from nmmd import Dispatcher


class RegexDispatcher(Dispatcher):

    def prepare(self):
        data = []
        for invoc, method in self.registry:
            args, kwargs = self.loads(invoc)
            rgx = re.compile(*args, **kwargs)
            data.append((rgx, method))
        return data

    def gen_methods(self, string):
        for rgx, methodname in self.dispatch_data:
            matchobj = rgx.match(string)
            if matchobj:
                method = getattr(self.inst, methodname)
                yield method, (string, matchobj)

        # Else try inst.generic_handler
        generic = getattr(self.inst, 'generic_handler', None)
        if generic is not None:
            yield generic

