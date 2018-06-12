import json

import requests


url = "http://localhost:4000/jsonrpc"
headers = {'content-type': 'application/json'}


def print_result(payload):
    response = requests.post(
        url,
        data=json.dumps(payload),
        headers=headers
    ).json()

    print(
        r"""
        {0}
        {1}
        """.format(payload, response))


def main():
    payloads = [
        {
            "method": "simple_add",
            "params": {"first": 17, "second": 39},
            "jsonrpc": "2.0",
            "id": 0,
        },
        {
            "method": "echo",
            "params": ["Hello!"],
            "jsonrpc": "2.0",
            "id": 1
        },
        {
            "method": "dict_to_list",
            "jsonrpc": "2.0",
            "params": [{1: 3, 'two': 'string', 3: [5, 'list', {'c': 0.3}]}],
            "id": 3
        },
        # Exception!
        {
            "method": "subtract",
            "jsonrpc": "2.0",
            "params": [1, 2, 3],
            "id": 2
        }
    ]
    for payload in payloads:
        print_result(payload)


if __name__ == "__main__":
    main()
