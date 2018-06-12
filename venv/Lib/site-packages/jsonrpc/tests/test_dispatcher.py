from jsonrpc.dispatcher import Dispatcher
import unittest


class TestDispatcher(unittest.TestCase):

    """ Test Dispatcher functionality."""

    def setUp(self):
        self.d = Dispatcher()

    def test_getter(self):

        with self.assertRaises(KeyError):
            print(self.d["method"])

        self.d["add"] = lambda *args: sum(args)
        self.assertEqual(self.d["add"](1, 1), 2)

    def test_len(self):
        self.d["add"] = lambda *args: sum(args)
        self.assertEqual(len(self.d), 1)

    def test_in(self):
        self.d["method"] = lambda: ""
        self.assertIn("method", self.d)

    def test_add_method(self):

        @self.d.add_method
        def add(x, y):
            return x + y

        self.assertIn("add", self.d)
        self.assertEqual(self.d["add"](1, 1), 2)

    def test_add_method_keep_function_definitions(self):

        @self.d.add_method
        def one(x):
            return x

        self.assertIsNotNone(one)

    def test_del_method(self):
        self.d["method"] = lambda: ""
        self.assertIn("method", self.d)

        del self.d["method"]
        self.assertNotIn("method", self.d)

    def test_to_dict(self):
        func = lambda: ""
        self.d["method"] = func
        self.assertEqual(dict(self.d), {"method": func})

    def test_init_from_object_instance(self):

        class Dummy():

            def one(self):
                pass

            def two(self):
                pass

        dummy = Dummy()

        d = Dispatcher(dummy)

        self.assertIn("one", d)
        self.assertIn("two", d)
        self.assertNotIn("__class__", d)

    def test_init_from_dictionary(self):

        dummy = {
            'one': lambda x: x,
            'two': lambda x: x,
        }

        d = Dispatcher(dummy)

        self.assertIn("one", d)
        self.assertIn("two", d)

    def test_dispatcher_representation(self):

        self.assertEqual('{}', repr(self.d))
