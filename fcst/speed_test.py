import socket
import time


class SpeedTest:

    def __init__(self, logger):
        self.start_time = None
        self.start_packet_counter = None
        self.udp_data_length = None
        self.eth_data_length = None

        self.udp_data_throughput = None
        self.eth_throughput = None
        self.time_elapsed = None
        self.packets_received = 0

        self.last_packet_counter = None
        self.last_packet_delta_time = None
        self.successfully_ended = None
        self.snapshot_offset = 1000

        self.logger = logger

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)

    def bind_socket_to_address(self, addr):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(addr)

    def run(self):
        self.receive_start_packet()
        self.listen_and_snapshot()

    def listen_and_snapshot(self):
        ongoing = True
        while ongoing and self.successfully_ended is not False:
            self.packets_received += 1
            try:
                data = self.sock.recv(16)
                self.last_packet_counter = self.extract_packet_counter(data)
                current_time = time.time()
                self.last_packet_delta_time = current_time - self.start_time

                if self.packets_received % self.snapshot_offset == 0:
                    self.logger.snapshot(self.last_packet_delta_time, self.last_packet_counter)
            except socket.timeout:
                ongoing = False
                self.calculate_result_parameters()
                self.successfully_ended = True
                self.logger.successfully_ended(self.start_packet_counter, self.last_packet_counter,
                                               self.packets_received,
                                               self.time_elapsed, self.udp_data_length, self.udp_data_throughput)
        if self.successfully_ended is False:
            raise Exception  # todo make relevant exception
            # self.logger.error('Test not ended successfully')
            # self.csv_logger.error('Test not ended successfully')

    def receive_start_packet(self):
        try:
            data = self.sock.recv(1500)
            self.packets_received += 1
            self.start_time = time.time()
            self.start_packet_counter = self.extract_packet_counter(data)
            self.udp_data_length = len(data)
        except socket.timeout:
            self.successfully_ended = False

    def calculate_result_parameters(self):
        self.packets_received = self.last_packet_counter - self.start_packet_counter
        self.time_elapsed = self.last_packet_delta_time
        counter_difference = self.last_packet_counter - self.start_packet_counter
        self.udp_data_throughput = self.udp_data_length * 8 * counter_difference / self.last_packet_delta_time / 1e6

    @staticmethod
    def extract_packet_counter(data):
        return int(data.hex()[:16], 16)
