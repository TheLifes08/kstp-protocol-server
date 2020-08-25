import config
from socketserver import ThreadingTCPServer
from classes.request_handler_class import RequestHandler

if __name__ == '__main__':
    with ThreadingTCPServer(config.ADDRESS, RequestHandler) as server:
        print("[Status] Server starts.")
        server.serve_forever()
