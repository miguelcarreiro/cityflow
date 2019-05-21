#!/usr/bin/python
import sys, select
from server_comm_services import find_ip_port, create_server_socket, connect_to_client, message_from_client, message_to_client
from control_services import read_gpio_conf, gpio_init, remote_control_action, stop_control, stop_gpio

TIME_OUT = 5



#def find_ip_addr(argv):
#    try:
#        server_host = argv[1]
#    except:
#        server_host = HOME_IP
#    return server_host


def main(argv):

    server_host, server_port = find_ip_port(sys.argv)
    print (server_host)
    server_sock = create_server_socket(server_host, server_port)
    inputs = [server_sock]
    print ('Server started succesfully')

    gpio_data = {}
    gpio_data = read_gpio_conf("gpio_pins")
    pwm_motor = {}
    gpio_init(gpio_data, pwm_motor)
    print ('gpio started succesfully')

    control_on = True
    while control_on:
        infds, outfds, errfds = select.select(inputs, inputs, [], TIME_OUT)
        if len(infds) != 0:
            for fds in infds:
                if fds is server_sock:
                    client_sock, client_addr = connect_to_client(fds)
                    inputs.append(client_sock)
                    print ('Connection_from_client')
                else:
                    rxd_msg = {}
                    msg_rxd = message_from_client(fds)
                    control_on = remote_control_action (msg_rxd, gpio_data, pwm_motor)

    print ('server is terminating')
    stop_control(gpio_data, pwm_motor)
    stop_gpio()
    server_sock.close()



if __name__== "__main__":
    main(sys.argv[0:])
