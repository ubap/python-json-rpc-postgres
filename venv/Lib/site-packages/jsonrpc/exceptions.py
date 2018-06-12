class JSONRPCException(Exception):
    """ JSON-RPC Exception."""
    pass


class JSONRPCParseException(Exception):
    """ Can't parse request from string."""
    pass


class JSONRPCMultipleRequestException(Exception):
    """ Found multiple requests. Try use batch instead"""
    pass


class JSONRPCInvalidRequestException(JSONRPCException):
    """ Request is not valid."""
    pass
