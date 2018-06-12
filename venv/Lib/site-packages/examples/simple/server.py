""" Example of json-rpc usage with Wergzeug and requests.

NOTE: there are no Werkzeug and requests in dependencies of json-rpc.
NOTE: server handles all url paths the same way (there are no different urls).
"""

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

from api import dispatcher


manager = JSONRPCResponseManager()


@Request.application
def application(request):
    response = manager.handle(request.get_data(cache=False, as_text=True), dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)
