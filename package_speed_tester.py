import socket
import json


class UdpDatagram:

    def __init__(self, data, destination):
        self.data = data
        self.destination = destination


class FpgaConnectionSpeedTester:

    def __init__(self, setup_filename):
        self.set_setup_from_file(setup_filename)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.fcst_ip, self.fcst_port))

    def set_setup_from_file(self, setup_filename):
        with open(setup_filename, 'r') as read_file:
            predefined_setup = json.load(read_file)
        self.set_general_setup(predefined_setup)
        self.prepare_setup_datagrams(predefined_setup)

    def start_test(self):
        pass

    def send_setup_to_fpga(self):
        for datagram in self.setup_datagrams:
            self.sock.sendto(datagram.data, datagram.destination)

    def set_general_setup(self, predefined_setup):
        self.fpga_ip = predefined_setup['fpga_ip']
        self.fcst_ip = predefined_setup['fcst_ip']
        self.fcst_port = predefined_setup['fcst_port']

    def prepare_setup_datagrams(self, predefined_setup):
        self.setup_datagrams = []
        for setup_datagram in predefined_setup['setup_datagrams']:
            datagram = UdpDatagram(int(setup_datagram['data'], 2).to_bytes(2, byteorder='big'),
                                   (predefined_setup['fpga_ip'], setup_datagram['fpga_port']))
            self.setup_datagrams.append(datagram)


if __name__ == '__main__':
    fcst = FpgaConnectionSpeedTester('fcst_setup.json')
    fcst.send_setup_to_fpga()
