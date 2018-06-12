""" Test utility functionality."""
from datetime import datetime, date, time, timedelta
import json
import unittest

from jsonrpc.utils import json_datetime_hook, FixedOffset, json_datetime_default


class TestDatetimeEncoderDecoder(unittest.TestCase):
    """ Test DatetimeEncoder and json_datetime_hook functionality."""

    def test_fixed_offset_class(self):
        tzinfo = FixedOffset(3600)
        dt = datetime.now(tz=tzinfo)
        self.assertEqual(dt.dst(), timedelta(0))
        self.assertEqual(dt.tzname(), "TZ offset: 1:00:00 hours")

    def test_incorrect(self):
        obj = NotImplementedError

        with self.assertRaises(TypeError):
            json.dumps(obj)

    def test_datetime(self):
        obj = datetime.now()
        incorrect = NotImplementedError

        with self.assertRaises(TypeError):
            json.dumps(obj)

        with self.assertRaises(TypeError):
            json.dumps(incorrect, default=json_datetime_default)

        string = json.dumps(obj, default=json_datetime_default)

        self.assertEqual(obj, json.loads(string, object_hook=json_datetime_hook))

    def test_date(self):
        obj = date.today()

        string = json.dumps(obj, default=json_datetime_default)

        self.assertEqual(obj, json.loads(string, object_hook=json_datetime_hook))

    def test_time(self):
        obj = datetime.now().time()
        obj_tz = datetime.now().time().replace(tzinfo=FixedOffset(3600))

        string = json.dumps(obj, default=json_datetime_default)
        string_tz = json.dumps(obj_tz, default=json_datetime_default)

        self.assertEqual(obj, json.loads(string, object_hook=json_datetime_hook))
        self.assertEqual(obj_tz, json.loads(string_tz, object_hook=json_datetime_hook))
        self.assertIsNotNone(json.loads(string_tz, object_hook=json_datetime_hook).tzinfo)

    def test_complex(self):
        obj = {'id': '1', 'params': (datetime(2014, 6, 17, 9, 38, 39, 911853),), 'jsonrpc': 2.0, 'method': 'w'}
        json.dumps(obj, default=json_datetime_default)

    def test_skip_nondt_obj(self):
        obj = {'__weird__': True}
        string = json.dumps(obj, default=json_datetime_default)
        self.assertEqual(obj, json.loads(string, object_hook=json_datetime_hook))

    def test_datetime_tzinfo(self):
        obj = datetime.now().replace(tzinfo=FixedOffset(3600))

        with self.assertRaises(TypeError):
            json.dumps(obj)

        string = json.dumps(obj, default=json_datetime_default)

        self.assertEqual(obj, json.loads(string, object_hook=json_datetime_hook))
