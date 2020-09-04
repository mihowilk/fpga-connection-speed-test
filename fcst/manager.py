import socket

from setup_manager import SetupManager, NotProperlyConfigured
from speed_test import SpeedTest


class Manager:

    def __init__(self):
        self.setup = None
        self.sock_out = None

    def load_setup(self, setup_filename):
        try:
            self.setup = SetupManager()
            self.setup.load_setup_from_file(setup_filename)
        except NotProperlyConfigured:
            self.setup = None
            raise NotProperlyConfigured from NotProperlyConfigured

    def send_setup_to_fpga(self):
        for datagram in self.setup.setup_datagrams:
            self.sock_out.sendto(datagram.data, datagram.destination)

    def start_test(self):
        if self.setup is not None:
            self.sock_out.sendto(self.setup.start_datagram.data, self.setup.start_datagram.destination)
            self._listen_and_measure_speed()
        else:
            raise IncompleteSetup

    def _listen_and_measure_speed(self):
        speed_test = SpeedTest()
        speed_test.bind_socket_to_address((self.setup.fcst_ip, self.setup.fcst_port_in))

        speed_test.run()

    def prepare_socket(self):  # todo remove, possibly move to another class
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_out.bind((self.setup.fcst_ip, self.setup.fcst_port_out))


class IncompleteSetup(Exception):
    pass
