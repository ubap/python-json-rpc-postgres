from jsonrpc.errors import JSONRPCInvalidRequest, JSONRPCParseError
from jsonrpc.exceptions import JSONRPCInvalidRequestException, JSONRPCParseException
from jsonrpc.request import JSONRPCSingleRequest, JSONRPCBatchRequest
from jsonrpc.response import JSONRPCSingleResponse
from jsonrpc.base import JSONSerializable


class JSONRPCResponseManager(JSONSerializable):
    """ JSON-RPC response manager. """

    def handle(self, request_string, dispatcher):
        """
        Method brings syntactic sugar into library.
        Given dispatcher it handles request (both single and batch) and handles errors.
        Request could be handled in parallel, it is server responsibility.

        :param request_string: JSON string.
            Will be converted into JSONRPCSingleRequest or JSONRPCBatchRequest
        :type request_string: str
        :type dispatcher: Dispatcher or dict
        :rtype: JSONRPCSingleResponse or JSONRPCBatchResponse
        """

        try:
            data = self.deserialize(request_string)
            if isinstance(data, list):
                request = JSONRPCBatchRequest(data, serialize_hook=self.serialize_hook)
            elif isinstance(data, dict):
                request = JSONRPCSingleRequest(data, serialize_hook=self.serialize_hook)
            else:
                raise JSONRPCInvalidRequestException
        except (TypeError, ValueError, JSONRPCParseException):
            return JSONRPCParseError().as_response()
        except JSONRPCInvalidRequestException:
            return JSONRPCInvalidRequest().as_response()
        else:
            return request.process(dispatcher)
