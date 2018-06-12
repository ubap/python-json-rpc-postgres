""" JSON-RPC request wrappers """
from jsonrpc.base import JSONSerializable
from jsonrpc.response import JSONRPCBatchResponse, JSONRPCSingleResponse
from jsonrpc.exceptions import JSONRPCParseException, JSONRPCMultipleRequestException, JSONRPCInvalidRequestException
from jsonrpc.errors import JSONRPCMethodNotFound, JSONRPCInvalidParams, JSONRPCServerError


class JSONRPCBaseRequest(JSONSerializable):
    """ Base wrapper class for JSON-RPC requests
    :param _data: Dictionary with internal data
    :type _data: dict
    :param _valid_flag: Internal flag. True, if request is valid. Used by __bool__()
    :type _valid_flag: bool
    """

    _data = None
    _valid_flag = False

    def __init__(self, request, serialize_hook=None, deserialize_hook=None):
        """ Initialize request and validate input data"""
        super().__init__(serialize_hook=serialize_hook, deserialize_hook=deserialize_hook)
        self._data = self._validate(request)

    def __iter__(self):
        yield self

    def __bool__(self):
        return self._valid_flag


class JSONRPCSingleRequest(JSONRPCBaseRequest):
    """ Main object wrapper for JSON-RPC request """

    result = None
    _data = {}
    _notification_flag = None

    REQUIRED_FIELDS = {"jsonrpc", "method"}
    POSSIBLE_FIELDS = {"jsonrpc", "method", "params", "id"}

    @property
    def args(self):
        """ Request args
        :rtype: tuple
        """
        return tuple(self.params) if isinstance(self.params, (list, tuple)) else ()

    @property
    def kwargs(self):
        """ Request kwargs
        :rtype: dict
        """
        return self.params if isinstance(self.params, dict) else {}

    @property
    def json(self):
        """ Serialized request, ready for sending
        :return: JSON-RPC request
        :rtype: str
        """
        return self.serialize(self.data)

    @property
    def data(self):
        """ Deserialized request
        :rtype: dict
        """
        data = {'jsonrpc': '2.0', 'method': self.method}
        if self.params is not None:
            data['params'] = self.params
        if not self.is_notification:
            data['id'] = self.id
        return data

    @data.setter
    def data(self, value):
        """ Set new data for request object (replaces old)
        :type value: dict
        """
        self._data = self._validate(value)

    @property
    def method(self):
        """ Request method name
        :rtype: str
        """
        return self._data.get('method')

    @property
    def params(self):
        """ Request params
        :rtype: tuple or dict or None
        """
        return self._data.get('params')

    @property
    def id(self):
        """ Request ID
        :rtype: str or int
        """
        return self._data.get('id')

    @property
    def is_notification(self):
        """ Notification flag. If Request object is notification, server never sends reply.
        If self.id is not set, flag sets automatically
        :rtype: bool
        """
        return 'id' not in self._data or self._notification_flag

    @is_notification.setter
    def is_notification(self, value):
        """ Set notification flag
        :type value: bool
        """
        self._notification_flag = bool(value)

    def process(self, dispatcher):
        """ Process request with method taken from dispatcher registry
        :type dispatcher: Dispatcher
        :rtype: JSONRPCSingleResponse or None
        """
        output = None
        try:
            method = dispatcher[self.method]
        except KeyError:
            output = JSONRPCMethodNotFound().as_response()
        else:
            try:
                result = method(*self.args, **self.kwargs)
            except TypeError:
                output = JSONRPCInvalidParams().as_response()
            except Exception as e:
                data = {'type': e.__class__.__name__, 'message': str(e)}
                output = JSONRPCServerError(data=data).as_response()
            else:
                output = JSONRPCSingleResponse(
                    result,
                    request=self,
                    serialize_hook=self.serialize_hook,
                    deserialize_hook=self.deserialize_hook
                )
        finally:
            if not self.is_notification:
                return output

    def _parse(self, string):
        try:
            data = self.deserialize(string)
        except:
            raise JSONRPCParseException("Cannot deserialize!")
        else:
            if isinstance(data, (list, tuple)):
                raise JSONRPCMultipleRequestException
            return data

    def _validate(self, raw_data):
        """ Validates request data
        :param raw_data: request
        :type raw_data: str or dict
        :return: Cleaned data
        :rtype: dict
        :raise JSONRPCInvalidRequestException:
        """
        self._valid_flag = False

        if isinstance(raw_data, str):
            data = self._parse(raw_data)
        elif isinstance(raw_data, (list, tuple)):
            raise JSONRPCMultipleRequestException
        elif isinstance(raw_data, dict):
            data = raw_data
        else:
            raise JSONRPCInvalidRequestException("Request must be str or dict, not {0}".format(type(raw_data)))

        if not data:
            raise JSONRPCInvalidRequestException("Empty data!")

        if not self.REQUIRED_FIELDS <= set(data.keys()) <= self.POSSIBLE_FIELDS:
            raise JSONRPCInvalidRequestException(
                'Invalid request. Extra fields: {0}, Missed fields: {1}'
                .format(set(data.keys()) - self.POSSIBLE_FIELDS, self.REQUIRED_FIELDS - set(data.keys()))
            )

        if data['jsonrpc'] != '2.0':
            raise JSONRPCInvalidRequestException('"jsonrpc" field MUST be set to "2.0"')

        if not isinstance(data['method'], str):
            raise JSONRPCInvalidRequestException('"method" should be str or dict, not {0}'.format(type(data['method'])))

        if data['method'].startswith('rpc.'):
            raise JSONRPCInvalidRequestException(
                'Method names that begin with the word rpc followed by a period character (U+002E or ASCII 46) '
                'are reserved for rpc-internal methods and extensions and MUST NOT be used for anything else.'
            )

        if 'id' in data and not isinstance(data['id'], (str, int)):
            raise JSONRPCInvalidRequestException('"id" must be string or integer, not {0}'.format(type(data['id'])))

        if 'params' in data and not isinstance(data['params'], (tuple, list, dict)):
            raise JSONRPCInvalidRequestException(
                '"params" should be tuple, list or dict, not {0}'
                .format(type(data['params']))
            )

        self._notification_flag = True if 'id' not in data else False
        self._valid_flag = True
        return data


class JSONRPCBatchRequest(JSONRPCBaseRequest):
    """ Batch list of JSON-RPC 2.0 Request """

    _data = []

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    @property
    def json(self):
        return self.serialize([request.data for request in self])

    def process(self, dispatcher):
        responses = list(filter(None, [request.process(dispatcher) for request in self]))
        if responses:
            return JSONRPCBatchResponse(responses, serialize_hook=self.serialize_hook)

    def _validate(self, raw_data):
        self._valid_flag = False
        data = []
        if not raw_data:
            raise JSONRPCInvalidRequestException("Empty data!")

        if isinstance(raw_data, (list, tuple, JSONRPCSingleRequest)):
            for item in raw_data:
                if isinstance(item, dict):
                    data.append(JSONRPCSingleRequest(item))
                elif isinstance(item, JSONRPCSingleRequest):
                    data.append(item)
                else:
                    raise JSONRPCInvalidRequestException(
                        "Request must be dict, or JSONRPCSingleRequest instance, not {0}"
                        .format(type(raw_data))
                    )
        elif isinstance(raw_data, str):
            raw_data = self.deserialize(raw_data)
            if isinstance(raw_data, list):
                data = [JSONRPCSingleRequest(item) for item in data]
        else:
            raise JSONRPCInvalidRequestException(
                "Requests must be list, tuple, JSONRPCSingleRequest or str, not {0}"
                .format(type(raw_data))
            )

        self._valid_flag = True
        return data
