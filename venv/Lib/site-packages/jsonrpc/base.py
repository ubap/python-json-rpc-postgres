from functools import partial
from json import loads, dumps


class JSONSerializable:
    """ Common functionality for json serializable objects.
    Provides support for custom json serialization/deserialization hooks
    via serialize_hook — dumps(default=…) and deserialize_hook — loads(object_hook=…)
    """

    def __init__(self, serialize_hook=None, deserialize_hook=None):
        self.serialize = partial(dumps, default=serialize_hook)
        self.deserialize = partial(loads, object_hook=deserialize_hook)
        self.serialize_hook = serialize_hook
        self.deserialize_hook = deserialize_hook
