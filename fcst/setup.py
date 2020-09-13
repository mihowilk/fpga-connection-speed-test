import json

from .exceptions import *


class Setup:

    def __init__(self):
        self.fpga_ip = None
        self.fcst_ip = None
        self.fcst_port_in = None
        self.fcst_port_out = None
        self.start_datagram = None
        self.setup_datagrams = None

    def load_from_file(self, setup_filename):
        with open(setup_filename, 'r') as read_file:
            predefined_setup = json.load(read_file)
        self._load_general_setup(predefined_setup)
        self._load_start_datagram(predefined_setup)
        self._load_setup_datagrams(predefined_setup)

    def _load_general_setup(self, predefined_setup):
        try:
            self.fpga_ip = predefined_setup['fpga_ip']
            self.fcst_ip = predefined_setup['fcst_ip']
            self.fcst_port_in = predefined_setup['fcst_port_in']
            self.fcst_port_out = predefined_setup['fcst_port_out']
            self.fcst_iface = predefined_setup['fcst_iface'] 
        except KeyError:
            raise GeneralSetupError

    def _load_start_datagram(self, predefined_setup):
        try:
            self.start_datagram = self._make_datagram(predefined_setup['start_datagram'])
        except (WrongDatagramData, KeyError):
            raise StartDatagramError

    def _load_setup_datagrams(self, predefined_setup):
        self.setup_datagrams = []
        try:
            for predefined_datagram in predefined_setup['setup_datagrams']:
                setup_datagram = self._make_datagram(predefined_datagram)
                self.setup_datagrams.append(setup_datagram)
        except (KeyError, WrongDatagramData):
            raise SetupDatagramError

    def _make_datagram(self, predefined_datagram):
        try:
            if 'data_hex' in predefined_datagram:
                return self._make_datagram_from_data(predefined_datagram, int(predefined_datagram['data_hex'], 16))
            if 'data_dec' in predefined_datagram:
                return self._make_datagram_from_data(predefined_datagram, int(predefined_datagram['data_dec'], 10))
            if 'data_bin' in predefined_datagram:
                return self._make_datagram_from_data(predefined_datagram, int(predefined_datagram['data_bin'], 2))
        except KeyError:
            raise WrongDatagramData
        raise WrongDatagramData

    def _make_datagram_from_data(self, predefined_datagram, data_int):
        if 'data_length' in predefined_datagram:
            data_length = predefined_datagram['data_length']
        else:
            data_length = self._calculate_data_length(data_int)
        return UdpDatagram(data_int.to_bytes(data_length, byteorder='big'),
                           (self.fpga_ip, predefined_datagram['fpga_port']))

    def is_properly_configured(self):
        if self.fpga_ip is not None and self.fcst_ip is not None and self.fcst_port_in is not None and \
                self.setup_datagrams is not None and self.start_datagram is not None and self.fcst_port_in is not None:
            return True
        return False

    @staticmethod
    def _calculate_data_length(data_int):
        data_length = 1
        while 256 ** data_length < data_int:
            data_length += 1
        return data_length


class UdpDatagram:

    def __init__(self, data, destination):
        self.data = data
        self.destination = destination
