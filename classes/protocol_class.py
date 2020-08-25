import config


class Protocol:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def is_valid_protocol(self):
        return self.name == config.PROTOCOL

    def is_valid_version(self):
        return self.version[0] > config.PROTOCOL_VERSION[0]\
               or (self.version[0] == config.PROTOCOL_VERSION[0] and self.version[1] >= config.PROTOCOL_VERSION[1])

    def __str__(self):
        return "{}/{}.{}".format(self.name, self.version[0], self.version[1])
