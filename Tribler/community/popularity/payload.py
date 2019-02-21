from __future__ import absolute_import

from struct import calcsize, pack, unpack_from

from Tribler.pyipv8.ipv8.messaging.payload import Payload
from Tribler.pyipv8.ipv8.messaging.serialization import default_serializer


def encode_values(values):
    encoded_list = [value.encode('utf-8') for value in values]
    return ''.join([pack('!H', len(encoded)) + encoded for encoded in encoded_list])


def decode_values(values_str):
    values = []
    index = 0
    while index < len(values_str):
        length = unpack_from('!H', values_str[index:])[0]
        index += calcsize('!H')
        values.append(values_str[index:index + length].decode('utf-8'))
        index += length
    return values


def unpack_responses(serialized_responses, as_payload=False):
    """
    Unpack a custom serialization of a list of SearchResponseItemPayload payloads.

    :param serialized_responses: the serialized data
    :return: [[str, str, int, int, str, int, int, int, str]] or SearchResponseItemPayload
    """
    data = serialized_responses
    out = []
    while data:
        unpacked, data = default_serializer.unpack_to_serializables([SearchResponseItemPayload], data)
        if as_payload:
            out.append(unpacked)
        else:
            out.append([unpacked.infohash, unpacked.name, unpacked.length, unpacked.num_files, unpacked.category_list,
                        unpacked.creation_date, unpacked.seeders, unpacked.leechers, unpacked.cid])
    return out


class ContentSubscription(Payload):

    format_list = ['I', '?']

    def __init__(self, identifier, subscribe):
        super(ContentSubscription, self).__init__()
        self.identifier = identifier
        self.subscribe = subscribe

    def to_pack_list(self):
        data = [('I', self.identifier),
                ('?', self.subscribe)]
        return data

    @classmethod
    def from_unpack_list(cls, *args):
        (identifier, subscribe) = args
        return ContentSubscription(identifier, subscribe)


class TorrentHealthPayload(Payload):

    format_list = ['20s', 'I', 'I', 'Q']

    def __init__(self, infohash, num_seeders, num_leechers, timestamp):
        super(TorrentHealthPayload, self).__init__()
        self.infohash = infohash
        self.num_seeders = num_seeders or 0
        self.num_leechers = num_leechers or 0
        self.timestamp = timestamp or 0

    def to_pack_list(self):
        data = [('20s', self.infohash),
                ('I', self.num_seeders),
                ('I', self.num_leechers),
                ('Q', self.timestamp)]

        return data

    @classmethod
    def from_unpack_list(cls, *args):
        (infohash, num_seeders, num_leechers, timestamp) = args
        return TorrentHealthPayload(infohash, num_seeders, num_leechers, timestamp)
