import json


class SetupManager:

    def __init__(self):
        self.fpga_ip = None
        self.fcst_ip = None
        self.fcst_port_in = None
        self.fcst_port_out = None
        self.start_datagram = None
        self.setup_datagrams = None

    def load_setup_from_file(self, setup_filename):
        with open(setup_filename, 'r') as read_file:
            predefined_setup = json.load(read_file)
        self.load_general_setup(predefined_setup)
        self.load_start_datagram(predefined_setup)
        self.load_setup_datagrams(predefined_setup)
        if not self.is_properly_configured():
            raise NotProperlyConfigured

    def load_general_setup(self, predefined_setup):
        self.fpga_ip = predefined_setup['fpga_ip']
        self.fcst_ip = predefined_setup['fcst_ip']
        self.fcst_port_in = predefined_setup['fcst_port_in']
        self.fcst_port_out = predefined_setup['fcst_port_out']

    def load_start_datagram(self, predefined_setup):
        self.start_datagram = self.make_datagram_from_predefined_data(predefined_setup['start_datagram'])

    def load_setup_datagrams(self, predefined_setup):
        self.setup_datagrams = []
        for predefined_datagram in predefined_setup['setup_datagrams']:
            setup_datagram = self.make_datagram_from_predefined_data(predefined_datagram)
            self.setup_datagrams.append(setup_datagram)

    def make_datagram_from_predefined_data(self, predefined_datagram):  # TODO add whitespace characters ignoring
        if 'data' in predefined_datagram:
            return UdpDatagram(int(predefined_datagram['data'], 16).to_bytes(2, byteorder='big'),
                               (self.fpga_ip, predefined_datagram['fpga_port']))
        if 'data_bin' in predefined_datagram:
            return UdpDatagram(int(predefined_datagram['data_bin'], 2).to_bytes(2, byteorder='big'),
                               (self.fpga_ip, predefined_datagram['fpga_port']))

    def is_properly_configured(self):
        if self.fpga_ip is not None and self.fcst_ip is not None and self.fcst_port_in is not None and \
                self.setup_datagrams is not None and self.start_datagram is not None and self.fcst_port_in is not None:
            return True
        return False


class NotProperlyConfigured(Exception):
    pass


class UdpDatagram:

    def __init__(self, data, destination):
        self.data = data
        self.destination = destination
