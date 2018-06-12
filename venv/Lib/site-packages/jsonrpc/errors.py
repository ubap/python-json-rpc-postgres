from jsonrpc.response import JSONRPCError


class JSONRPCParseError(JSONRPCError):
    """ Parse Error.

    Invalid JSON was received by the server.
    An error occurred on the server while parsing the JSON text.
    """

    def __init__(self, **kwargs):
        super().__init__(-32700, "Parse error", **kwargs)


class JSONRPCInvalidRequest(JSONRPCError):
    """ Invalid Request.

    The JSON sent is not a valid Request object.
    """

    def __init__(self, **kwargs):
        super().__init__(-32600, "Invalid Request", **kwargs)


class JSONRPCMethodNotFound(JSONRPCError):
    """ Method not found.

    The method does not exist / is not available.
    """

    def __init__(self, **kwargs):
        super().__init__(-32601, "Method not found", **kwargs)


class JSONRPCInvalidParams(JSONRPCError):
    """ Invalid params.

    Invalid method parameter(s).
    """

    def __init__(self, **kwargs):
        super().__init__(-32602, "Invalid params", **kwargs)


class JSONRPCInternalError(JSONRPCError):
    """ Internal error.

    Internal JSON-RPC error.
    """

    def __init__(self, **kwargs):
        super().__init__(-32603, "Internal error", **kwargs)


class JSONRPCServerError(JSONRPCError):
    """ Server error.

    Reserved for implementation-defined server-errors.
    """

    def __init__(self, **kwargs):
        super().__init__(-32000, "Server error", **kwargs)
