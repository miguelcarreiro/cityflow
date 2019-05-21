#!/usr/bin/python
import sys, keyboard

from client_comm_services import find_ip_port, create_client_socket, connect_to_server, message_to_server
from functools import partial


def welcome_info():
    print ('Vehicle remote controller \n')
    print ('To operate the system, please press:')
    print ('\tArrow keys to select the car direction')
    print ('\ttab to stop control')
    print ('\t<ESC> to exit keyboard operation')

def remote_control(client_sock):
    msg = {}
    while True:
        fn = partial(read_keys, client_sock, msg)
        keyboard.hook(fn)
        keyboard.wait('esc')
        keyboard.unhook(fn)
        break
    input ('Controlled system mode is terminating... Press any key to continue.')

def read_keys(client_sock, msg, event):
    line = ','.join(str(code) for code in keyboard._pressed_events)
    if line != '':
        msg['sens_action'] = line
        message_to_server(client_sock, msg)


def main (argv):

    print (sys.argv)
    server_host, server_port = find_ip_port(sys.argv)
    print (server_host)
    client_sock = create_client_socket()
    connect_to_server(client_sock, server_host, server_port)
    welcome_info()
    remote_control(client_sock)
    print ('Client succesfully terminating')
    client_sock.close()

if __name__== "__main__":
    main(sys.argv[0:])
