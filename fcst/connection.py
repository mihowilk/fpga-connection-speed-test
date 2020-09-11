import socket
from scapy.packet import Raw
from scapy.layers.inet import IP, UDP

ETH_P_ALL = 3

class Connection:

    def __init__(self, setup):
        self.setup = setup
        self.sock_out = None
        self.sock_in = None

    def prepare_sockets(self):
        self.sock_out = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
        self.sock_out.bind((self.setup.iface, 0))

        self.sock_in = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
        self.sock_in.settimeout(1.0)
        self.sock_in.bind((self.setup.iface))

    def send_to_fpga(self, datagram):
        packet = IP(dst=datagram.destination, src=SRC_IP)/UDP(sport=12666, dport=12666)/Raw(load=datagram.data)
        self.sock_out.send(packet)

    def rec_from_fpga(self, buffer_size):
        return self.sock_in.recv(buffer_size)
