import unittest

from mock import MagicMock

from jsonrpc.manager import JSONRPCResponseManager
from jsonrpc.request import JSONRPCBatchRequest, JSONRPCSingleRequest
from jsonrpc.response import JSONRPCBatchResponse, JSONRPCSingleResponse


class TestJSONRPCResponseManager(unittest.TestCase):
    def setUp(self):
        def raise_(e):
            raise e

        self.long_time_method = MagicMock()
        self.dispatcher = {
            "add": sum,
            "list_len": len,
            "101_base": lambda **kwargs: int("101", **kwargs),
            "error": lambda: raise_(Exception("error_explanation")),
            "long_time_method": self.long_time_method,
            "echo": lambda x: x,
        }
        self.manager = JSONRPCResponseManager()

    def test_returned_type_response(self):
        request = JSONRPCSingleRequest({'jsonrpc': '2.0', 'method': 'add', 'params': [], 'id': 0})
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)

    def test_returned_type_butch_response(self):
        request = JSONRPCBatchRequest([{'jsonrpc': '2.0', 'method': 'add', 'params': [], 'id': 0}])
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertIsInstance(response, JSONRPCBatchResponse)

    def test_parse_error(self):
        req = '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]'
        response = self.manager.handle(req, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)
        self.assertEqual(response.error["message"], "Parse error")
        self.assertEqual(response.error["code"], -32700)

    def test_echo_request(self):
        req = '{"jsonrpc": "2.0", "method": "echo", "params": ["foo"], "id": 1}'
        response = self.manager.handle(req, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)
        self.assertEqual(response.result, "foo")
        req = '{"jsonrpc": "2.0", "method": "echo", "params": [["foo", "bar"]], "id": 1}'
        response = self.manager.handle(req, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)
        self.assertEqual(response.result, ["foo", "bar"])

    def test_invalid_request(self):
        req = '{"jsonrpc": "2.0", "method": 1, "params": "bar"}'
        response = self.manager.handle(req, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)
        self.assertEqual(response.error["message"], "Invalid Request")
        self.assertEqual(response.error["code"], -32600)
        req = '1'
        response = self.manager.handle(req, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)
        self.assertEqual(response.error["message"], "Invalid Request")
        self.assertEqual(response.error["code"], -32600)

    def test_method_not_found(self):
        request = JSONRPCSingleRequest({'jsonrpc': '2.0', 'method': 'does_not_exist', 'params': [], 'id': 0})
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)
        self.assertEqual(response.error["message"], "Method not found")
        self.assertEqual(response.error["code"], -32601)

    def test_invalid_params(self):
        request = JSONRPCSingleRequest({'jsonrpc': '2.0', 'method': 'add', 'params': {"a": 0}, 'id': 0})
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)
        self.assertEqual(response.error["message"], "Invalid params")
        self.assertEqual(response.error["code"], -32602)

    def test_server_error(self):
        request = JSONRPCSingleRequest({'jsonrpc': '2.0', 'method': 'error', 'id': 0})
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertIsInstance(response, JSONRPCSingleResponse)
        self.assertEqual(response.error["message"], "Server error")
        self.assertEqual(response.error["code"], -32000)
        self.assertEqual(response.error["data"], {
            "type": "Exception",
            "message": 'error_explanation',
        })

    def test_notification_calls_method(self):
        request = JSONRPCSingleRequest({'jsonrpc': '2.0', 'method': 'long_time_method'})
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertEqual(response, None)
        self.long_time_method.assert_called_once_with()

    def test_notification_does_not_return_error_does_not_exist(self):
        request = JSONRPCSingleRequest({'jsonrpc': '2.0', 'method': 'does_not_exist'})
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertEqual(response, None)

    def test_notification_does_not_return_error_invalid_params(self):
        request = JSONRPCSingleRequest({'jsonrpc': '2.0', 'method': 'does_not_exist', 'params': {"a": 0}})
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertEqual(response, None)

    def test_notification_does_not_return_error(self):
        request = JSONRPCSingleRequest({'jsonrpc': '2.0', 'method': 'error'})
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertEqual(response, None)
