import socket
import json


class FpgaConnectionSpeedTester:
    """
    Or fcst for short. Measures raw data flow rate during transmission of UDP datagrams from FPGA. Setup datagrams
    and connection parameters are configured using json.
    """

    def __init__(self, setup_filename):
        self.setup = FcstSetup()
        self.setup.set_setup_from_file(setup_filename)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.setup.fcst_ip, self.setup.fcst_port))

    def start_test(self):
        if self.setup.is_properly_configured():
            print('Starting test.')
            self.sock.sendto(self.setup.start_datagram.data, self.setup.start_datagram.destination)
        else:
            print('Cannot start test. Setup is incomplete.')

    def send_setup_to_fpga(self):
        for datagram in self.setup.setup_datagrams:
            self.sock.sendto(datagram.data, datagram.destination)


class FcstSetup:

    def set_setup_from_file(self, setup_filename):
        with open(setup_filename, 'r') as read_file:
            predefined_setup = json.load(read_file)
        self.set_general_setup(predefined_setup)
        self.prepare_setup_datagrams(predefined_setup)
        if not self.is_properly_configured():
            print('Error occurred while loading configuration. Setup incomplete.')
        else:
            print('Setup complete.')

    def set_general_setup(self, predefined_setup):
        self.fpga_ip = predefined_setup['fpga_ip']
        self.fcst_ip = predefined_setup['fcst_ip']
        self.fcst_port = predefined_setup['fcst_port']

    def prepare_setup_datagrams(self, predefined_setup):
        self.setup_datagrams = []
        for predefined_datagram in predefined_setup['setup_datagrams']:
            try:
                self.start_datagram = self.prepare_as_start_datagram(predefined_datagram)
            except KeyError:
                setup_datagram = self.prepare_as_setup_datagram(predefined_datagram)
                self.setup_datagrams.append(setup_datagram)

    def prepare_as_setup_datagram(self, predefined_datagram):
        return self.make_datagram_from_predefined_setup(predefined_datagram)

    def prepare_as_start_datagram(self, predefined_datagram):
        if predefined_datagram['is_start_datagram']:
            return self.make_datagram_from_predefined_setup(predefined_datagram)

    def make_datagram_from_predefined_setup(self, datagram):
        return UdpDatagram(int(datagram['data'], 2).to_bytes(2, byteorder='big'),
                           (self.fpga_ip, datagram['fpga_port']))

    def is_properly_configured(self):
        try:
            if self.fpga_ip is not None and self.fcst_ip is not None and self.fcst_port is not None and \
                    self.setup_datagrams is not None and self.start_datagram is not None:
                return True
        except:
            return False


class UdpDatagram:

    def __init__(self, data, destination):
        self.data = data
        self.destination = destination


if __name__ == '__main__':
    fcst = FpgaConnectionSpeedTester('fcst_setup.json')
    fcst.send_setup_to_fpga()
    fcst.start_test()
