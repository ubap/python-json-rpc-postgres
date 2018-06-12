""" Test utility functionality."""
import unittest

from jsonrpc.base import JSONSerializable


class TestJSONSerializable(unittest.TestCase):
    """ Test JSONSerializable functionality."""

    def setUp(self):
        self._class = JSONSerializable

    def test_definse_serialize_deserialize(self):
        """ Test classmethods of inherited class."""
        self.assertEqual(self._class().serialize({}), "{}")
        self.assertEqual(self._class().deserialize("{}"), {})
