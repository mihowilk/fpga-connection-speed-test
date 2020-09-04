import socket

from setup_manager import SetupManager, NotProperlyConfigured
from speed_test import SpeedTest


class Manager:

    def __init__(self, setup_filename):
        self.setup = self._load_setup(setup_filename)
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_out.bind((self.setup.fcst_ip, self.setup.fcst_port_out))

    def start_test(self):
        if self.setup is not None:
            self.sock_out.sendto(self.setup.start_datagram.data, self.setup.start_datagram.destination)
            self._listen_and_measure_speed()
        else:
            raise IncompleteSetup

    def send_setup_to_fpga(self):
        for datagram in self.setup.setup_datagrams:
            self.sock_out.sendto(datagram.data, datagram.destination)

    def _listen_and_measure_speed(self):
        speed_test = SpeedTest()
        speed_test.bind_socket_to_address((self.setup.fcst_ip, self.setup.fcst_port_in))

        speed_test.run()

    @staticmethod
    def _load_setup(setup_filename):
        try:
            setup = SetupManager()
            setup.load_setup_from_file(setup_filename)
            print('Setup complete')
            return setup
        except NotProperlyConfigured:
            setup = None
            print('Error occurred while loading configuration. Setup incomplete.')
            return setup


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("filename", type=str,
#                         help="name of json file")
#     args = parser.parse_args()
#     fcst = Main(args.filename)
#     fcst.send_setup_to_fpga()
#     fcst.start_test()

class IncompleteSetup(Exception):
    pass
