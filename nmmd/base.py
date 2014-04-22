import types
import pickle
import inspect
import collections

from dispatcher.utils import CachedAttr


class DispatchError(Exception):
    '''Raised when someone does something silly, like
    dispatch two conlicting handlers to process the same
    stream input.
    '''


class DispatchInterrupt(Exception):
    '''Raise to stop dispatcher trying additional dispatch methods.
    '''


class ImplementationError(Exception):
    '''Raise if subclass does stuff wrong.
    '''


class BaseDispatcher(object):
    DispatchError = DispatchError
    DispatchInterrupt = DispatchInterrupt

    # Whether to run multiple matching methds or bail after
    # the first (default).
    multi = False

    @CachedAttr
    def dispatch_data(self):
        try:
            return self.prepare()
        except RuntimeError:
            msg ='''
Oh dear. Please don't reference self.dispatch_data inside self.prepare,
because self.dispatch_data references self.prepare. Instead use
self.registry.'''
            raise ImplementationError(msg)

    def prepare(self):
        raise NotImplemented()

    def get_method(self):
        raise NotImplemented()

    def dispatch(self, *args, **kwargs):
        raise NotImplemented()


class Dispatcher(BaseDispatcher):
    '''Implements the base functionality for dispatcher types.
    The node instances delegate their dispatch functions to
    subclasses of Dispatcher.
    '''
    __slots__ = tuple()

    def __call__(self, *args, **kwargs):
        return self._make_decorator(*args, **kwargs)

    def __get__(self, inst, cls=None):
        self.inst = inst
        return self

    def _make_decorator(self, *args, **kwargs):
        def decorator(method):
            self.register(method, args, kwargs)
            return method
        return decorator

    loads = pickle.loads
    dumps = pickle.dumps

    @CachedAttr
    def registry(self):
        return []

    def dump_invoc(self, *args, **kwargs):
        return self.dumps((args, kwargs))

    def load_invoc(self, *args, **kwargs):
        return self.loads((args, kwargs))

    def register(self, method, args, kwargs):
        '''Given a single decorated handler function,
        prepare it for the node __new__ method.
        '''
        invoc = self.dump_invoc(*args, **kwargs)
        self.registry.append((invoc, method.__name__))

    def prepare(self):
        '''Given all the registered handlers for this
        dispatcher instance, return any data required
        by the dispatch method.

        Can be overridden to provide more efficiency,
        simplicity, etc.
        '''
        return self.registry

    def iter_methods(self, *args, **kwargs):
        '''Find all method names this input dispatches to.
        '''
        dispatched = False
        for invoc, methodname in self.registry:
            args, kwargs = self.loads(invoc)
            yield getattr(self.inst, methodname)
            dispatched = True

        if dispatched:
            return
        msg = 'No method was found for %r on %r.'
        raise self.DispatchError(msg % ((args, kwargs), self.inst))

    def get_method(self, *args, **kwargs):
        '''Find the first method this input dispatches to.
        '''
        for method in self.iter_methods(*args, **kwargs):
            return method
        msg = 'No method was found for %r on %r.'
        raise self.DispatchError(msg % ((args, kwargs), self.inst))

    def dispatch(self, *args, **kwargs):
        '''Find and evaluate/return the first method this input dispatches to.
        '''
        for result in self.iter_dispatch(*args, **kwargs):
            return result

    def iter_dispatch(self, *args, **kwargs):
        '''Find and evaluate/yield every method this input dispatches to.
        '''
        for method_data in self.iter_methods(*args, **kwargs):
            if isinstance(method_data, tuple):
                len_method = len(method_data)
                method = method_data[0]
                if 1 < len_method:
                    args = method_data[1]
                if 2 < len_method:
                    kwargs = method_data[2]
            else:
                method = method_data
            yield method(*args, **kwargs)


class Mixin(BaseDispatcher):
    '''A simple mixin for type-based dispatch.
    '''

    method_prefix = 'handle_'
    try_modules = (__builtins__, types, collections)

    def prepare(self):
        data = {}
        prefix = self.method_prefix
        for name in dir(self):
            if name.startswith(prefix):
                typename = name.replace(prefix, '', 1)
                data[typename] = getattr(self, name)
        return data

    def apply_handler(self, handler, token, *args, **kwargs):
        return handler(token, *args, **kwargs)

    gentype = types.GeneratorType

    def dispatch(self, token, *args, **kwargs):
        '''NOTE: need function application separated out.
        '''
        gentype = self.gentype
        typename = type(token).__name__
        data = self.dispatch_data
        dispatch_succeeded = False
        multi = self.multi
        if typename in data:
            handler = data[typename]
            result = self.apply_handler(handler, token, *args, **kwargs)
            if isinstance(result, gentype):
                for yielded in result:
                    yield yielded
            else:
                yield result
            dispatch_succeeded = True

            # Only go on to run other matching methods
            # if multi is True.
            if not multi:
                return

        basetype = None
        try_modules = self.try_modules
        for typename, handler in data.items():

            # Check try_modules types.
            for module in try_modules:
                if isinstance(module, dict):
                    basetype = module.get(typename)
                else:
                    basetype = getattr(module, typename, None)
                if not isinstance(basetype, type):
                    continue
                if basetype is None:
                    continue
                if not isinstance(token, basetype):
                    continue
                result = self.apply_handler(handler, token, *args, **kwargs)
                if isinstance(result, gentype):
                    for yielded in result:
                        yield yielded
                else:
                    yield result
                dispatch_succeeded = True


        if not dispatch_succeeded:
            msg = 'No method was found for %r on %r.'
            raise self.DispatchError(msg % (token, self))



if __name__ == '__main__':

    class MyDisp(Dispatcher):
        pass

    class MyClass:

        dispatch = MyDisp()

        @dispatch('cow')
        def handle_cow(self, cow):
            pass

        @dispatch('pig')
        def handle_pig(self, pig):
            pass

        def __call__(self, *args, **kwargs):
            for result in self.dispatch.dispatch(self, *args, **kwargs):
                yield result


    # myclass = MyClass()
    # myclass('cow')
    # myclass('pig')
    # myclass('donkey')

    class MyDispatcher(Mixin):

        def handle_int(self, token):
            print(token, 'type is int')

        def handle_basestring(self, token):
            print(token, 'type is basestring')

        def handle_Hashable(self, token):
            print(token, 'is hashable')
            yield 'hooray'
            yield 'yippee'

        def handle_Iterable(self, token):
            print(token, 'is iterable')

        def __call__(self, token):
            for result in self.dispatch(token):
                yield result


    disp = MyDispatcher()
    for val in disp(3):
        print(val)
    list(disp([1, 2, 3]))
    list(disp(set(['a', 'b'])))

