import socket
import json
import time


class FpgaConnectionSpeedTester:
    """
    Or fcst for short. Measures raw data flow rate during transmission of UDP datagrams from FPGA. Setup datagrams
    and connection parameters are configured using json.
    """

    def __init__(self, setup_filename):
        self.setup = self.load_setup(setup_filename)
        # self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock_in.bind((self.setup.fcst_ip, self.setup.fcst_port_in))
        self.sock_out.bind((self.setup.fcst_ip, self.setup.fcst_port_out))

    @staticmethod
    def load_setup(setup_filename):
        try:
            setup = FcstSetup()
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


class FcstSetup:

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


class SpeedTest:

    def __init__(self):
        self.start_time = None
        self.start_packet_counter = None
        self.udp_data_length = None
        self.eth_data_length = None

        self.udp_data_throughput = None
        self.eth_throughput = None
        self.time_elapsed = None
        self.packets_transmitted = None

        self.last_packet_counter = None
        self.last_packet_delta_time = None
        self.successfully_ended = None
        self.snapshot_offset = 1000

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)

    def bind_socket_to_address(self, addr):
        self.sock.bind(addr)

    def run(self):
        self.receive_start_packet()
        self.listen_and_snapshot()

    def listen_and_snapshot(self):
        ongoing = True
        i = 0
        while ongoing and self.successfully_ended is not False:
            i += 1
            try:
                data = self.sock.recv(1024)
                self.last_packet_counter = self.extract_packet_counter(data)
                current_time = time.time()
                self.last_packet_delta_time = current_time - self.start_time

                speed_data = (self.last_packet_delta_time, self.last_packet_counter, self.udp_data_length)
                if i % self.snapshot_offset == 0:
                    self.snapshot_to_file(speed_data)
            except socket.timeout:
                ongoing = False
                self.calculate_result_parameters()
                self.successfully_ended = True

    def receive_start_packet(self):
        try:
            data = self.sock.recv(1024)
            self.start_time = time.time()
            self.start_packet_counter = self.extract_packet_counter(data)
            self.udp_data_length = len(data)
        except socket.timeout:
            self.successfully_ended = False

    def calculate_result_parameters(self):
        self.packets_transmitted = self.last_packet_counter - self.start_packet_counter
        self.time_elapsed = self.last_packet_delta_time
        counter_difference = self.last_packet_counter - self.start_packet_counter
        self.udp_data_throughput = self.udp_data_length * 8 * counter_difference/self.last_packet_delta_time / 1e6

    @staticmethod
    def snapshot_to_file(speed_data):
        print(f'Delta time: {speed_data[0]}')
        print(f'Current counter: {speed_data[1]}')
        print(f'Udp length: {speed_data[2]}')

    @staticmethod
    def extract_packet_counter(data):
        return int(data.hex()[:16], 16)


class UdpDatagram:

    def __init__(self, data, destination):
        self.data = data
        self.destination = destination


class NotProperlyConfigured(Exception):
    pass


if __name__ == '__main__':
    fcst = FpgaConnectionSpeedTester('fcst_setup.json')
    fcst.send_setup_to_fpga()
    fcst.start_test()
