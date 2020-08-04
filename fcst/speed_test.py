import socket
import time
import logging
import sys
import os

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
        self.packets_received = 0

        self.last_packet_counter = None
        self.last_packet_delta_time = None
        self.successfully_ended = None
        self.snapshot_offset = 1000

        self.logger = self.setup_logger()
        self.csv_logger = self.setup_csv_logger()

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
                    self.log_snapshot()
            except socket.timeout:
                ongoing = False
                self.calculate_result_parameters()
                self.successfully_ended = True
                self.log_results()
        if self.successfully_ended is False:
            self.logger.error('Test not ended successfully')
            self.csv_logger.error('Test not ended successfully')

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

    def log_snapshot(self):
        self.logger.info(f'Delta time: {self.last_packet_delta_time}; Current counter: {self.last_packet_counter}')
        self.csv_logger.info(f'{self.last_packet_delta_time},{self.last_packet_counter}')

    @staticmethod
    def extract_packet_counter(data):
        return int(data.hex()[:16], 16)

    @staticmethod
    def setup_logger(result_filename=f"results/results_{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}.json"):

        if not os.path.exists('results'):
            os.mkdir('results')

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

    @staticmethod
    def setup_csv_logger(result_filename=f"results/results_{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}.csv"):

        if not os.path.exists('results'):
            os.mkdir('results')

        logger = logging.getLogger("csv_results_logger")
        logger.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter("%(message)s")

        file_handler = logging.FileHandler(result_filename, mode="w")
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        return logger

    def log_results(self):
        self.logger.info(f"Successfully ended test\n"
                         f"Transmitted {self.last_packet_counter - self.start_packet_counter + 1} packets\n"
                         f"Received {self.packets_received} packets in {self.time_elapsed} seconds\n"
                         f"Raw UDP packet data length: {self.udp_data_length} bytes\n"
                         f"Raw UDP packet throughput: {self.udp_data_throughput} Mbps")
