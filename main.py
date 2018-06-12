import psycopg2
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher, Dispatcher

dispatcher = Dispatcher()


@dispatcher.add_method
def example_method(*args, **kwargs):
    print("param 1: " + args[0])
    print("param 2: " + args[1])


@dispatcher.add_method
def connect_to_db(*args, **kwargs):
    try:
        connect_str = "dbname='pos_projekt' user='X' host='X' password='X'"
        # use our connection values to establish a connection
        conn = psycopg2.connect(connect_str)
        # create a psycopg2 cursor that can execute queries
        cursor = conn.cursor()
        # create a new table with a single column called "name"
        # cursor.execute("""CREATE TABLE tutorials (name char(40));""")
        # run a SELECT statement - no data in there, but we can try it
        cursor.execute("""SELECT * from User""")
        rows = cursor.fetchall()
        print(rows)
    except Exception as e:
        print("Uh oh, can't connect. Invalid dbname, user or password?")
        print(e)


@Request.application
def application(request):
    handler = JSONRPCResponseManager()
    response = handler.handle(request_string=request.data, dispatcher=dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)
