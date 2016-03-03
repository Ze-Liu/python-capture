import socket


HOST = 'localhost'
PORT = 8889


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

conn, addr = sock.accept()

f = open('test.mp4', 'wb')
while True:
    data = conn.recv(1024)
    if not data: break

    f.write(data)
f.close()
    
