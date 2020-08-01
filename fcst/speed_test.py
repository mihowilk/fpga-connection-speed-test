import socket
import time
import logging
import sys
from datetime import datetime


class SpeedTest:
    """
    FCST module responsible for receiving packets from FPGA, measuring raw data flow rate, and logging it.
    """

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

        self.logger = self.setup_logger()

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
                    self.log_snapshot(speed_data)
            except socket.timeout:
                ongoing = False
                self.calculate_result_parameters()
                self.successfully_ended = True
                self.logger.info('Successfully ended test')
                self.log_results()
        if self.successfully_ended is False:
            self.logger.error('Test not ended successfully')

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
        self.udp_data_throughput = self.udp_data_length * 8 * counter_difference / self.last_packet_delta_time / 1e6

    def log_snapshot(self, speed_data):
        self.logger.info(f'Delta time: {speed_data[0]}; Current counter: {speed_data[1]}')

    @staticmethod
    def extract_packet_counter(data):
        return int(data.hex()[:16], 16)

    @staticmethod
    def setup_logger(result_filename=f"results_{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}.json"):
        logger = logging.getLogger("speed_test_logger")
        logger.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter("%(asctime)s "
                                          "[%(levelname)s] %(message)s")

        file_handler = logging.FileHandler(result_filename, mode="w")
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)

        return logger

    def log_results(self):
        self.logger.info(f"Transmitted {self.packets_transmitted} packets in {self.time_elapsed} seconds")
        self.logger.info(f"Raw ethernet packet data length: {self.eth_data_length} bytes")
        self.logger.info(f"Raw ethernet packet throughput: {self.eth_throughput} Mbps")
        self.logger.info(f"Raw UDP packet data length: {self.udp_data_length} bytes")
        self.logger.info(f"Raw UDP packet throughput: {self.udp_data_throughput} Mbps")
