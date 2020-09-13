import socket
from scapy.all import *
from .exceptions import WrongPort

ETH_P_ALL = 3

class Connection:

    def __init__(self, setup):
        self.setup = setup
        self.sock = None

    def prepare_sockets(self):
        self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
        self.sock.bind((self.setup.fcst_iface, 0))

    def send_to_fpga(self, datagram, setup):
        packet = IP(dst=datagram.destination[0], src=setup.fcst_ip)/UDP(dport=datagram.destination[1], sport=setup.fcst_port_out)/Raw(load=datagram.data)
        self.sock.send(raw(packet))

    def rec_from_fpga(self, buffer_size):
        received_data = self.sock.recv(buffer_size)
        data = IP(received_data)
        if(data.getfieldval('dport') == 12666):
            return data.getfieldval('load')
        else:
            raise WrongPort


