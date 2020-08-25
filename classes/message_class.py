import config
import rsa
from classes.protocol_class import Protocol


class Message:
    def __init__(self):
        self.protocol = Protocol(config.PROTOCOL, config.PROTOCOL_VERSION)
        self.headers = dict()
        self.data = str()

    def head_to_raw_data(self):
        return "{}/{}.{}\n\n".format(self.protocol.name, self.protocol.version[0],
                                     self.protocol.version[1]).encode("utf-8")

    def headers_raw_data(self):
        return ('\n'.join(["{}:{}".format(key, value) for key, value in self.headers.items()]) + '\n\n').encode("utf-8")

    def data_to_raw_data(self):
        encoding = 'utf-8'
        if "data-encoding" in self.headers.keys():
            encoding = self.headers["data-encoding"]
        return self.data.encode(encoding)

    def to_raw_data(self):
        return self.head_to_raw_data() + self.headers_raw_data() + self.data_to_raw_data()

    @staticmethod
    def get_error(error_code, error_description):
        message = Message()
        message.type = config.MESSAGE_TYPES[1]
        message.headers = {"status-code": error_code}
        message.data = "[{}] {}".format(error_code, error_description)
        return message

    @staticmethod
    def get_response(status_code, data):
        message = Message()
        message.type = config.MESSAGE_TYPES[1]
        message.headers = {"status-code": status_code}
        message.data = data
        return message
