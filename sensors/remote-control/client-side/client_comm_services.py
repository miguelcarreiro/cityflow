#!/usr/bin/python
import socket, sys, json

MSG_SIZE = 1024
HOME_IP = '127.0.0.1'
HOME_PORT = 5003

# Client communication functions

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
    
def create_client_socket():
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print ('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
        sys.exit();
    return my_socket

def connect_to_server(my_sock, host, port):
    try:
        my_sock.connect((host, port))
    except socket.error as msg:
        print ('Failed to connect to server: {}'.format(msg))

def message_to_server(my_sock, data):
    print ('data' , data)
    msg_to_server = json.dumps(data)
    print ('msg_to_server', msg_to_server)
    encoded_msg = msg_to_server.encode('utf-8')
    print (encoded_msg)
    my_sock.send(encoded_msg)

def message_from_server(my_sock):
    msg_from_server = my_sock.recv(MSG_SIZE)
    msg_from_server_json = json.loads(msg_from_server.decode('utf-8'))
    return msg_from_server_json
