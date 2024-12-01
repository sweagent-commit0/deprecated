import inspect
import warnings
import types
import functools
import platform
import wrapt

try:
    import wrapt._wrappers
    _routine_stacklevel = 2
    _class_stacklevel = 2
except ImportError:
    _routine_stacklevel = 3
    if platform.python_implementation() == 'PyPy':
        _class_stacklevel = 2
    else:
        _class_stacklevel = 3

string_types = (type(b''), type(u''))

class ClassicAdapter(wrapt.AdapterFactory):
    def __init__(self, reason='', version='', action=None, category=DeprecationWarning):
        self.reason = reason or ''
        self.version = version or ''
        self.action = action
        self.category = category
        super(ClassicAdapter, self).__init__()

    def get_deprecated_msg(self, wrapped, instance):
        if instance is None:
            if inspect.isclass(wrapped):
                fmt = "Class {name} is deprecated."
            else:
                fmt = "Function {name} is deprecated."
        else:
            if inspect.isclass(instance):
                fmt = "Class method {name} is deprecated."
            else:
                fmt = "Method {name} is deprecated."
        if self.reason:
            fmt += " {reason}"
        if self.version:
            fmt += " -- Deprecated since version {version}."
        return fmt.format(name=wrapped.__name__, reason=self.reason, version=self.version)

    def __call__(self, wrapped):
        if inspect.isclass(wrapped):
            old_new1 = wrapped.__new__

            def wrapped_cls(cls, *args, **kwargs):
                msg = self.get_deprecated_msg(wrapped, None)
                if self.action:
                    with warnings.catch_warnings():
                        warnings.simplefilter(self.action, self.category)
                        warnings.warn(msg, category=self.category, stacklevel=_class_stacklevel)
                else:
                    warnings.warn(msg, category=self.category, stacklevel=_class_stacklevel)
                if old_new1 is object.__new__:
                    return old_new1(cls)
                return old_new1(cls, *args, **kwargs)
            wrapped.__new__ = staticmethod(wrapped_cls)
        return wrapped

def deprecated(*args, **kwargs):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    **Classic usage:**

    To use this, decorate your deprecated function with **@deprecated** decorator:

    .. code-block:: python

       from deprecated import deprecated


       @deprecated
       def some_old_function(x, y):
           return x + y

    You can also decorate a class or a method:

    .. code-block:: python

       from deprecated import deprecated


       class SomeClass(object):
           @deprecated
           def some_old_method(self, x, y):
               return x + y


       @deprecated
       class SomeOldClass(object):
           pass

    You can give a *reason* message to help the developer to choose another function/class,
    and a *version* number to specify the starting version number of the deprecation.

    .. code-block:: python

       from deprecated import deprecated


       @deprecated(reason="use another function", version='1.2.0')
       def some_old_function(x, y):
           return x + y

    The *category* keyword argument allow you to specify the deprecation warning class of your choice.
    By default, :exc:`DeprecationWarning` is used but you can choose :exc:`FutureWarning`,
    :exc:`PendingDeprecationWarning` or a custom subclass.

    .. code-block:: python

       from deprecated import deprecated


       @deprecated(category=PendingDeprecationWarning)
       def some_old_function(x, y):
           return x + y

    The *action* keyword argument allow you to locally change the warning filtering.
    *action* can be one of "error", "ignore", "always", "default", "module", or "once".
    If ``None``, empty or missing, the the global filtering mechanism is used.
    See: `The Warnings Filter`_ in the Python documentation.

    .. code-block:: python

       from deprecated import deprecated


       @deprecated(action="error")
       def some_old_function(x, y):
           return x + y

    """
    if args and isinstance(args[0], (type, types.FunctionType, types.MethodType)):
        # This is the decorator without arguments
        return ClassicAdapter()(args[0])
    else:
        # This is the decorator with arguments
        return ClassicAdapter(*args, **kwargs)
