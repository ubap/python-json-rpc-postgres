from jsonrpc import dispatcher


def dict_to_list(dictionary):
    return list(dictionary.items())


@dispatcher.add_method
def simple_add(first=0, **kwargs):
    return first + kwargs["second"]


def echo_with_long_name(msg):
    return msg

dispatcher.add_method(echo_with_long_name, name='echo')

dispatcher['subtract'] = lambda a, b: a - b
dispatcher['dict_to_list'] = dict_to_list
