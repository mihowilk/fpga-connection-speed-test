import socket


class Connection:

    def __init__(self, setup):
        self.setup = setup
        self.sock_out = None
        self.sock_in = None

    def prepare_sockets(self):
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_out.bind((self.setup.fcst_ip, self.setup.fcst_port_out))

    def send_to_fpga(self, datagram):
        self.sock_out.sendto(datagram.data, datagram.destination)
