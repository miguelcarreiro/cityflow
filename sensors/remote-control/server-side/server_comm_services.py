#!/usr/bin/python
import socket, sys, json

back_log = 5
msg_size = 1024
HOME_IP = '127.0.0.1'
HOME_PORT = 5003

# Server communication functions
def find_ip_port(argv):
    try:
        server_host = argv[1]
    except:
        server_host = HOME_IP
    try:
        server_port = int(argv[2])
    except:
        server_port = HOME_PORT
    return server_host, server_port

def create_server_socket(host, port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_sock.bind((host, port))
    except socket.error as msg:
        print(msg)
    server_sock.listen(back_log)
    return server_sock

def connect_to_client(server_sock):
    sock, addr = server_sock.accept()
    return sock, addr

def message_to_client(my_sock, data):
    client_data = json.dumps(data)
    my_sock.send(client_data.encode('utf-8'))

def message_from_client(my_sock):
    data_message = my_sock.recv(msg_size)
    print(data_message)
    client_data = json.loads(data_message.decode('utf-8'))
    return client_data
