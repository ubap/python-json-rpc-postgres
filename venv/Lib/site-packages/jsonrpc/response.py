""" JSON-RPC response wrappers """
from jsonrpc.base import JSONSerializable
from jsonrpc.exceptions import JSONRPCException


class JSONRPCError(JSONSerializable):
    """ Error for JSON-RPC communication.

    The error codes from and including -32768 to -32000 are reserved for
    pre-defined errors. Any code within this range, but not defined explicitly
    below is reserved for future use. The error codes are nearly the same as
    those suggested for XML-RPC at the following
    url: http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php
    """

    def __init__(self, code, message, data=None, serialize_hook=None, deserialize_hook=None):
        """
        When a rpc call encounters an error, the Response Object MUST contain the
        error member with a value that is a Object with the following members in __init__

        :param int code: A Number that indicates the error type that occurred.
            This MUST be an integer.
        :param str message: A String providing a short description of the error.
            The message SHOULD be limited to a concise single sentence.
        :param data: A Primitive or Structured value that contains additional
            information about the error.
            This may be omitted.
            The value of this member is defined by the Server (e.g. detailed error
            information, nested errors etc.).
        :type data: None or int or str or dict or list
        """

        super().__init__(serialize_hook=serialize_hook, deserialize_hook=deserialize_hook)
        self._container = {}
        if not isinstance(code, int):
            raise ValueError("Error code should be integer")
        else:
            self._container['code'] = code

        if not isinstance(message, str):
            raise ValueError("Error message should be string")
        else:
            self._container['message'] = message

        if data is not None:
            self._container['data'] = data

    @property
    def code(self):
        return self._container['code']

    @property
    def message(self):
        return self._container['message']

    @property
    def data(self):
        return self._container.get('data')

    @property
    def json(self):
        return self.serialize(self._container)

    def as_response(self):
        return JSONRPCSingleResponse(payload=self._container, error=True)


class JSONRPCSingleResponse(JSONSerializable):
    """ JSON-RPC response object to JSONRPCRequest. """
    _error_flag = None
    _payload = None
    _request = None

    def __init__(self, payload, request=None, error=None, serialize_hook=None, deserialize_hook=None):
        """
        :param request: Bound request for response
        :type request: JSONRPCSingleRequest
        :param payload: Result or error dict
        :param error: Error Flag
        :type error: bool
        """
        super().__init__(serialize_hook=serialize_hook, deserialize_hook=deserialize_hook)
        if not error:
            if request is None:
                raise ValueError("Can't create non-error Response object without request object!")
        else:
            if not isinstance(payload, dict):
                raise TypeError("Error payload should be dict, not {0}".format(type(payload)))
            if 'code' not in payload or 'message' not in payload:
                raise ValueError("Can't find code and/or message in payload")
            if not isinstance(payload['code'], int):
                raise ValueError("Error code should be integer")
            if not isinstance(payload['message'], str):
                raise ValueError("Error message should be string")

        self._request = request
        self._payload = payload
        self._error_flag = error

    def __iter__(self):
        yield self

    @property
    def result(self):
        return self._payload if not self._error_flag else None

    @property
    def error(self):
        return self._payload if self._error_flag else None

    @property
    def id(self):
        return self._request.id if not self._error_flag else None

    @property
    def container(self):
        data = {"jsonrpc": "2.0", "id": self.id}
        if self._error_flag:
            data["error"] = self.error
        else:
            data["result"] = self.result
        return data

    @property
    def json(self):
        return self.serialize(self.container)


class JSONRPCBatchResponse(JSONSerializable):
    _data = []

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    @property
    def json(self):
        return self.serialize([response.container for response in self])

    def __init__(self, response, serialize_hook=None):
        super().__init__(serialize_hook=serialize_hook)
        self._data = self._validate(response)

    def _validate(self, raw_data):
        self._valid_flag = False
        data = []
        if not raw_data:
            raise JSONRPCException("Empty batch response data!")

        if isinstance(raw_data, (list, tuple, JSONRPCSingleResponse)):
            for item in raw_data:
                if isinstance(item, JSONRPCSingleResponse):
                    data.append(item)
                else:
                    raise TypeError(
                        "Response item must be JSONRPCSingleResponse instance, not {0}"
                        .format(type(raw_data))
                    )
        else:
            raise TypeError(
                "Responses must be list, tuple or JSONRPCSingleResponse, not {0}"
                .format(type(raw_data))
            )
        self._valid_flag = True
        return data
