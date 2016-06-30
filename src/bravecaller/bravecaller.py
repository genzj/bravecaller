# -*- encoding: utf-8 -*-

from functools import wraps, partial
from inspect import isclass

def unwrap_static_class_method(fn):
    if isinstance(fn, (staticmethod, classmethod)):
        # workaround of staticmethod alike objects
        fn = fn.__func__
    return fn

def ensure_tuple_of_exception_or_none(x):
    is_exception_class = lambda e: isclass(e) and issubclass(e, Exception)
    if x is None:
        return None
    elif is_exception_class(x):
        return (x,)
    elif all(is_exception_class(e) for e in x):
        return tuple(x)

def safe_call_builder(fn, brave, coward, default):
    brave = ensure_tuple_of_exception_or_none(brave)
    coward = ensure_tuple_of_exception_or_none(coward)

    @wraps(fn)
    def _safe_w(*args, **kwargs):
        try:
            ret = fn(*args, **kwargs)
        except Exception as ex:
            if brave and not isinstance(ex, tuple(brave)):
                raise ex
            if coward and isinstance(ex, tuple(coward)):
                raise ex
            ret = default
        return ret
    return _safe_w

def _bravecall(fn, brave, coward):
    fn = unwrap_static_class_method(fn)

    @wraps(fn)
    def _w(*args, **kwargs):
        return fn(*args, **kwargs)

    setattr(
        _w, 'safe', partial(
            safe_call_builder,
            fn,
            brave,
            coward
        )
    )

    return _w

def bravecall(brave_or_fn, coward=None):
    brave_or_fn = unwrap_static_class_method(brave_or_fn)
    if callable(brave_or_fn):
        return _bravecall(brave_or_fn, None, None)
    else:
        return partial(_bravecall, brave=brave_or_fn, coward=coward)

