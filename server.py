import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.tcpserver
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
        self.set_header('Content-Type', 'video/mpeg')
        self.flush()

    async def write_media(self, data):
        try:
            self.write(data)
            await self.flush()
        except StreamClosedError:
            pass


class Server(tornado.tcpserver.TCPServer):

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        print('Streamer connected.')

        while True:
            if stream.reading():
                continue

            try:
                data = yield stream.read_bytes(1024, partial=True)
                self.send_data(data)
            except StreamClosedError:
                print('Streamer disconnected.')
                stream.close()

    def send_data(self, data):
        try:
            for client in StreamHandler.CLIENTS:
                self.io_loop.add_callback(client.write_media, data)
        except Exception as e:
            print(e)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(
            """
<video autoplay="true" controls="controls" width="640" height="480">
    <source src="/stream" type="video/webm" />
    Your browser does not support HTML5 streaming!
</video>
"""
        )


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/stream', StreamHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': '.'})
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
