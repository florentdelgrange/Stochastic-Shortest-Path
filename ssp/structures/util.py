import functools


class ReadOnlyList(list):
    """
    A read only proxy for list.
    """

    def __init__(self, other):
        self._list = other

    def __getitem__(self, index):
        return self._list[index]

    def __iter__(self):
        return iter(self._list)

    def __slice__(self, *args, **kw):
        return self._list.__slice__(*args, **kw)

    def __repr__(self):
        return repr(self._list)

    def __len__(self):
        return len(self._list)

    def NotImplemented(self, *args, **kw):
        raise ValueError("Read Only list proxy")

    append = pop = __setitem__ = __setslice__ = __delitem__ = NotImplemented


@functools.total_ordering
class NeverSmaller(object):
    def __le__(self, other):
        return False


class Bot(NeverSmaller, int):
    def __add__(self, other):
        return Bot()

    def __radd__(self, other):
        return Bot()

    def __repr__(self):
        return '⊥'

    def __str__(self):
        return self.__repr__()