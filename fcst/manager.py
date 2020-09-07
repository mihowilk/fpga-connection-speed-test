from setup import Setup, NotProperlyConfigured
from speed_test import SpeedTest
from logger import Logger
from connection import Connection


class Manager:

    def __init__(self):
        self.setup = None
        self.sock_out = None

        self.logger = Logger()
        self.setup = Setup()
        self.connection = Connection(self.setup)

    def load_setup(self, setup_filename):
        try:
            self.setup.load_from_file(setup_filename)
            self.connection.prepare_sockets()
        except NotProperlyConfigured:
            self.setup = None
            raise NotProperlyConfigured from NotProperlyConfigured

    def send_setup_to_fpga(self):
        for datagram in self.setup.setup_datagrams:
            self.connection.send_to_fpga(datagram)

    def start_test(self):
        if self.setup is not None:
            self.connection.send_to_fpga(self.setup.start_datagram)
            self._listen_and_measure_speed()
        else:
            raise IncompleteSetup

    def _listen_and_measure_speed(self):
        speed_test = SpeedTest(self.logger, self.connection)

        speed_test.run()


class IncompleteSetup(Exception):
    pass
