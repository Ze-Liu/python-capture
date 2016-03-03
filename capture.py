import os
import socket
import subprocess
import time

import sys


class Streamer:
    command = (
        'ffmpeg',
        '-f', 'avfoundation',
        '-framerate', '30',
        '-video_size', '640x480',
        '-i', '0:0',
        '-c:v', 'libx264',
        '-crf', '18',
        '-preset', 'ultrafast',
        '-r', '30',
        '-f', 'mpeg',
        '-')
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
        p = subprocess.Popen(self.command, stdin=open(os.devnull), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        port = int(sys.argv[2])
    except ValueError:
        print('Invalid port.')
        exit(1)
    except IndexError:
        host = 'localhost'
        port = 8889

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
