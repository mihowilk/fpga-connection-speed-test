import socket

from fcst.setup_manager import SetupManager, NotProperlyConfigured
from fcst.speed_test import SpeedTest


class Controller:
    """
    FPGA Connection Speed Tester. Measures raw data flow rate during transmission of UDP datagrams from FPGA.
    Setup datagrams and connection parameters are configured using json.
    """

    def __init__(self, setup_filename):
        self.setup = self.load_setup(setup_filename)
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_out.bind((self.setup.fcst_ip, self.setup.fcst_port_out))

    @staticmethod
    def load_setup(setup_filename):
        try:
            setup = SetupManager()
            setup.load_setup_from_file(setup_filename)
            print('Setup complete')
            return setup
        except NotProperlyConfigured:
            setup = None
            print('Error occurred while loading configuration. Setup incomplete.')
            return setup

    def start_test(self):
        if self.setup is not None:
            print('Starting test')
            self.sock_out.sendto(self.setup.start_datagram.data, self.setup.start_datagram.destination)
            self.listen_and_measure_speed()
        else:
            print('Cannot start test. Setup is incomplete.')

    def send_setup_to_fpga(self):
        for datagram in self.setup.setup_datagrams:
            self.sock_out.sendto(datagram.data, datagram.destination)

    def listen_and_measure_speed(self):
        speed_test = SpeedTest()
        speed_test.bind_socket_to_address((self.setup.fcst_ip, self.setup.fcst_port_in))

        speed_test.run()

        if speed_test.successfully_ended:
            print(f"Transmitted {speed_test.packets_transmitted} packets in {speed_test.time_elapsed} seconds")
            print(f"Raw ethernet packet data length: {speed_test.eth_data_length} bytes")
            print(f"Raw ethernet packet throughput: {speed_test.eth_throughput} Mbps")
            print(f"Raw UDP packet data length: {speed_test.udp_data_length} bytes")
            print(f"Raw UDP packet throughput: {speed_test.udp_data_throughput} Mbps")
        else:
            print("Test not ended successfully")


if __name__ == '__main__':
    fcst = Controller('config.json')
    fcst.send_setup_to_fpga()
    fcst.start_test()
