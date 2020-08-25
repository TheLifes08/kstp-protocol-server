import config
from classes.protocol_class import Protocol
from classes.message_class import Message
from socketserver import BaseRequestHandler


class RequestHandler(BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.m_response = None

    def handle(self):
        print("[Status] Get message from {}:{}".format(self.client_address[0], self.client_address[1]))
        raw_data = bytes()

        while True:
            raw_data_part = self.request.recv(config.PACKET_SIZE)
            raw_data += raw_data_part
            if len(raw_data_part) < config.PACKET_SIZE:
                break

        m_request, error_code, error_description = RequestHandler.get_message_from_raw_data(raw_data)

        if m_request is None:
            self.m_response = Message.get_error(error_code, error_description)
            return

        if "method" not in m_request.headers.keys():
            self.m_response = Message.get_error(109, "Missing header 'method'")
            return

        if m_request.headers["method"] == "get":
            self.m_response = Message.get_response(200, "Super secret data")
        else:
            self.m_response = Message.get_error(108, "Unknown method: {}".format(m_request.headers["method"]))
            return

    def finish(self):
        if self.m_response is None:
            self.request.sendall(Message.get_response(100, "Unknown error").to_raw_data())
        else:
            print("[Status] Send response to {}:{}".format(self.client_address[0], self.client_address[1]))
            self.request.sendall(self.m_response.to_raw_data())

    @staticmethod
    def get_message_from_raw_data(raw_data):
        message = Message()
        raw_data_split = raw_data.split(b'\n\n', 2)
        data_availability = 3

        if len(raw_data_split) < 3:
            if len(raw_data_split) == 2:
                data_availability = 2
            else:
                if len(raw_data) == 0:
                    data_availability = 0
                else:
                    data_availability = 1

        if data_availability == 0:
            return None, 101, "Empty request"

        if data_availability >= 1:
            protocol_data = raw_data_split[0].decode('utf-8').split('/')

            if len(protocol_data) != 2:
                return None, 102, "Invalid protocol structure"

            try:
                protocol_version = tuple(map(int, protocol_data[1].split('.')))
            except ValueError:
                return None, 103, "Invalid protocol version"
            else:
                if len(protocol_version) != 2:
                    return None, 103, "Invalid protocol version"
                else:
                    message.protocol = Protocol(protocol_data[0], protocol_version)

            if not message.protocol.is_valid_protocol():
                return None, 104, "Wrong protocol: {}".format(message.protocol.name)

            if not message.protocol.is_valid_version():
                return None, 105, "Your KSTP protocol version is {}.{}, needed: {}.{}".format(message.protocol.version[0],
                                                                                         message.protocol.version[1],
                                                                                         config.PROTOCOL_VERSION[0],
                                                                                         config.PROTOCOL_VERSION[1])

        if data_availability >= 2:
            headers_data = raw_data_split[1].decode('utf-8').split('\n')
            for header in headers_data:
                split_header = header.split(':')
                if len(split_header) == 2:
                    message.headers[split_header[0]] = split_header[1]

        if "message-type" in message.headers.keys():
            if message.headers["message-type"] != "request":
                if message.headers["message-type"] == "response":
                    return None, 107, "Expected request message type, got response message type"
                else:
                    return None, 108, "Unknown message type: {}".format(message.headers["message-type"])
        else:
            return None, 106, "Missing header 'message-type'"

        if data_availability == 3:
            encoding = 'utf-8'
            if "data-encoding" in message.headers.keys():
                encoding = message.headers["data-encoding"]

            message.data = raw_data_split[2].decode(encoding)

        return message, 200, "Success"
