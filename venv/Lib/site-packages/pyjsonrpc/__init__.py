#!/usr/bin/env python2.7

import gevent
from gevent.monkey import patch_all; patch_all()
from gevent.event import AsyncResult
from gevent.queue import Queue
import itertools
import json
from ws4py.client.geventclient import WebSocketClient


_status_code = itertools.count(600)


STATUS_CODES = dict(
  SUCCESS_AUTHENTICATED    = _status_code.next(),
  ERROR_NOT_IMPLEMENTED    = _status_code.next(),
  ERROR_NOT_AUTHENTICATED  = _status_code.next(),
  ERROR_NOT_AUTHORIZED     = _status_code.next(),
  ERROR_REQUEST_NOT_VALID  = _status_code.next(),
  ERROR_TOKEN_NOT_VALID    = _status_code.next(),
  ERROR_TOKEN_NBF_FAILED   = _status_code.next(),
  ERROR_TOKEN_EXP_FAILED   = _status_code.next(),
  ERROR_UNKNOWN            = _status_code.next(),
  ERROR_DEPENDENCY_FAILED  = _status_code.next(),
  ERROR_RESPONSE_NOT_VALID = _status_code.next(),
  ERROR_REQUEST_TIMED_OUT  = _status_code.next(),
  ERROR_SERVICE_TIMED_OUT  = _status_code.next())


STATUS_CODE_NAMES = dict((status_code, name) for name, status_code in STATUS_CODES.iteritems())


SUCCESS_AUTHENTICATED = STATUS_CODES["SUCCESS_AUTHENTICATED"]


class JWTHandshakeException(Exception):
  def __init__(self, code):
    self.code = code

  def __str__(self):
    return "<JWTHandshakeException code: %d name: %r>" % (
      self.code,
      STATUS_CODE_NAMES.get(self.code))


class JSONRPCException(Exception):
  def __init__(self, reason):
    self.reason = reason

  def __str__(self):
    return "<JSONRPCException reason: %r>" % (self.reason,)


class JSONRPCClient(WebSocketClient):
  class Stream(object):
    def __init__(self):
      self.responses = Queue()
      self.error = AsyncResult()

  def __init__(self, server=None, origin=None, token=None):
    self._token = token
    self._ids = itertools.count(0)
    self._results = {}
    self._streams = {}
    headers = []
    if origin is not None:
      headers.append((u"Origin", unicode(origin)))
    WebSocketClient.__init__(self, server, protocols=["http-only"], headers=headers)

  def connect(self):
    WebSocketClient.connect(self)
    self.send(self._token)
    code = int(str(self.receive()))
    if code != SUCCESS_AUTHENTICATED:
      raise JWTHandshakeException(code)
    self._result_processor = gevent.spawn(self._process_results)

  def _process_call_result(self, id, response):
      result = self._results[id]
      del self._results[id]
      if "result" in response:
        result.set(response["result"])
      elif "error" in response:
        result.set_exception(JSONRPCException(response["error"]))

  def _process_stream_result(self, id, response):
    stream = self._streams[id]
    if "error" in response and response["error"] == "EOS":
      if response["error"] == "EOS":
        del self._streams[id]
        stream.responses.put(StopIteration)
        if not stream.error.ready():
          stream.error.set(None)
    elif "result" in response:
      stream.responses.put(response["result"])
    elif "error" in response:
      if not stream.error.ready():
        stream.error.set_exception(JSONRPCException(response["error"]))

  def _process_results(self):
    while True:
      message = self.receive()
      if message:
        self._process_result(message)
      else:
        break

  def _process_result(self, message):
    response = json.loads(str(message))

    if "id" not in response or ("result" in response) != ("error" in response):
      raise RuntimeError("JSONRPC response malformed")

    id = response["id"]
    if id in self._results:
      self._process_call_result(id, response)
    elif id in self._streams:
      self._process_stream_result(id, response)
    else:
      raise RuntimeError("JSONRPC unknown ID")

  def call(self, method, param, streaming=False):
    i = self._ids.next()
    if streaming:
      retval = self._streams[i] = self.Stream()
    else:
      retval = self._results[i] = AsyncResult()
    self.send(json.dumps(dict(method=method, params=[param], id=i)))
    return retval

  def close(self, *args, **kwargs):
    gevent.kill(self._result_processor)
    return super(JSONRPCClient, self).close(*args, **kwargs)


# This is used as a test of the client.  When we have a Python server we should
# write an integration test between the package and itself, but until then this
# will exist as a gut-check.
def main():
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument("--origin", type=str, required=True)
  parser.add_argument("--server", type=str, required=True)
  parser.add_argument("--token", type=str, required=True)

  args = parser.parse_args()
  with open(args.token, "rb") as f:
    token = f.read()

  client = JSONRPCClient(server=args.server, origin=args.origin, token=token)
  try:
    client.connect()
    result = client.call("Calculator.Calculate", dict(Operator="add", Operands=dict(A=5, B=7)))
    print repr(result.get())
    stream = client.call("Calculator.Sequence", dict(Start=0, Stop=10), streaming=True)
    for response in stream.responses:
      print repr(response)
    print stream.error.get()
  finally:
    client.close()


if __name__ == "__main__":
  main()
