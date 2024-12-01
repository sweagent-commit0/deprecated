import sys
import warnings
import unittest

from deprecated.classic import deprecated


class MyDeprecationWarning(DeprecationWarning):
    pass


class TestClassicDeprecated(unittest.TestCase):
    def _get_deprecated_func(self, *args, **kwargs):
        @deprecated(*args, **kwargs)
        def foo():
            pass
        return foo

    def _get_deprecated_class(self, *args, **kwargs):
        @deprecated(*args, **kwargs)
        class Foo:
            pass
        return Foo

    def _get_deprecated_method(self, *args, **kwargs):
        class Foo:
            @deprecated(*args, **kwargs)
            def foo(self):
                pass
        return Foo

    def _get_deprecated_static_method(self, *args, **kwargs):
        class Foo:
            @staticmethod
            @deprecated(*args, **kwargs)
            def foo():
                pass
        return Foo.foo

    def test_deprecated_function(self):
        foo = self._get_deprecated_func()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            foo()
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn("Function foo is deprecated.", str(w[-1].message))

    def test_deprecated_class(self):
        Foo = self._get_deprecated_class()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            Foo()
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn("Class Foo is deprecated.", str(w[-1].message))

    def test_deprecated_method(self):
        Foo = self._get_deprecated_method()
        foo = Foo()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            foo.foo()
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn("Method foo is deprecated.", str(w[-1].message))

    def test_deprecated_static_method(self):
        foo = self._get_deprecated_static_method()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            foo()
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn("Function foo is deprecated.", str(w[-1].message))

    def test_deprecated_with_reason(self):
        foo = self._get_deprecated_func(reason="Good reason")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            foo()
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn("Function foo is deprecated. Good reason", str(w[-1].message))

    def test_deprecated_with_version(self):
        foo = self._get_deprecated_func(version="1.2.3")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            foo()
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn("Function foo is deprecated. -- Deprecated since version 1.2.3.", str(w[-1].message))

    def test_deprecated_with_custom_warning(self):
        foo = self._get_deprecated_func(category=MyDeprecationWarning)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            foo()
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, MyDeprecationWarning))


if __name__ == '__main__':
    unittest.main()
