#https://realpython.com/python-sockets/

import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 3000        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   s.bind((HOST, PORT))
   s.listen()
   conn, addr = s.accept()
   with conn:
       print('Connected by', addr)
       while True:
           data = conn.recv(1024)
           if not data:
               print("Nodata")
               break
           #print(data)
           b = bytes("lololo", 'utf-8')
           conn.sendall(data)