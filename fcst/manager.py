from .setup import Setup
from .speed_test import SpeedTest
from .logger import Logger
from .connection import Connection
from .exceptions import IncompleteSetup


class Manager:

    def __init__(self):
        self.setup = None
        self.sock_out = None

        self.logger = Logger()
        self.setup = Setup()
        self.connection = Connection(self.setup)

    def load_setup(self, setup_filename):
        self.setup.load_from_file(setup_filename)
        self.connection.prepare_sockets()

    def send_setup_to_fpga(self):
        if not self.setup.is_properly_configured():
            raise IncompleteSetup
        for datagram in self.setup.setup_datagrams:
            self.connection.send_to_fpga(datagram, self.setup)

    def start_test(self):
        if not self.setup.is_properly_configured():
            raise IncompleteSetup
        self.connection.send_to_fpga(self.setup.start_datagram, self.setup)
        SpeedTest(self.logger, self.connection).run()


