import os
import socket
import subprocess
import time

import sys


class Streamer:
    command = 'ffmpeg ' \
              '-y ' \
              '-f avfoundation ' \
              '-r 30 ' \
              '-pixel_format bgr0 ' \
              '-s 640x480 ' \
              '-video_device_index 0 ' \
              '-i ":0" ' \
              '-c:v libvpx ' \
              '-b:v 1M ' \
              '-c:a libvorbis ' \
              '-b:a 96k ' \
              '-deadline realtime ' \
              '-flags +global_header ' \
              '-cpu-used 1 ' \
              '-threads 8 ' \
              '-f segment ' \
              '-f webm ' \
              '-'

    __connected = False

    def __init__(self, host, port):
        self.server = None
        self.host = host
        self.port = port

    def connect(self):
        while True:
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print('Connecting to {}:{}...'.format(self.host, self.port))
                self.server.connect((self.host, self.port))
                self.__connected = True
                print('Connected.\n')
                break
            except ConnectionRefusedError:
                print('Connection refused. Retrying in 3 seconds.\n')
                time.sleep(3)

    def stream(self):
        p = subprocess.Popen(self.command.split(), stdin=open(os.devnull), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('Streaming...\n')
        while True:
            data = p.stdout.read(1024)
            if len(data) == 0:
                err = p.stderr.readlines()
                if len(err) > 0:
                    print('Error')
                    print(''.join([l.decode() for l in err]))
                    break
            try:
                self.server.send(data)
            except BrokenPipeError:
                print('Disconnected from server. Reconnecting in 3 seconds\n')
                time.sleep(3)
                self.connect()
                print('Streaming...\n')

    def close(self):
        if not self.connected:
            return
        print('Disconnected.')
        self.server.close()

    @property
    def connected(self):
        return self.__connected

if __name__ == '__main__':
    try:
        host = sys.argv[1]
    except IndexError:
        host = 'localhost'

    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 8889
    except ValueError:
        print('Invalid port.')
        exit(1)

    streamer = Streamer(host, port)
    try:
        streamer.connect()
        streamer.stream()
    except KeyboardInterrupt:
        print('Exiting...')
    except OSError as e:
        print(e)
        exit(1)
    finally:
        streamer.close()
