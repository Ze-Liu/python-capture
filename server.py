import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.tcpserver
from functools import partial
from tornado.iostream import StreamClosedError


class StreamHandler(tornado.web.RequestHandler):
    CLIENTS = []

    def initialize(self):
        print('Client connected')
        self.CLIENTS.append(self)

    def on_connection_close(self):
        print('Client disconnected')
        self.CLIENTS.remove(self)
        super().on_connection_close()

    @tornado.web.asynchronous
    def get(self):
        self.set_header('Content-Type', 'video/mpg')
        self.flush()

    @tornado.gen.coroutine
    def write_media(self, data):
        try:
            self.write(data)
            yield self.flush()
        except StreamClosedError:
            pass


class Server(tornado.tcpserver.TCPServer):
    def handle_stream(self, stream, addresss):
        print('Streamer connected')
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.stream = stream
        self.read()

    def read(self):
        self.stream.read_bytes(1024, self.send_data)

    def send_data(self, data):
        try:
            for client in StreamHandler.CLIENTS:
                self.ioloop.add_callback(partial(client.write_media, data))
        except Exception as e:
            print(e)
        self.read()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(
            """
<video width="640" height="480" controls>
  <source src="/stream" type="video/mp4">
  Your browser does not support the video tag.
</video>
"""
        )


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/stream', StreamHandler)
    ], debug=True)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)

    server = Server()
    server.listen(8889)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print('Server exiting...')
