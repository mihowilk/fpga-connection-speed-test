import socket
import time

from exceptions import NoPacketsReceived


class SpeedTest:

    def __init__(self, logger, connection):
        self.start_time = None
        self.first_packet_counter = None
        self.latest_packet_counter = None
        self.latest_packet_delta_time = None

        self.packets_transmitted = None
        self.packets_received = 0
        self.time_elapsed = None
        self.udp_data_length = None
        self.udp_data_throughput = None

        self.successfully_ended = None
        self.snapshot_offset = 1000

        self.logger = logger
        self.connection = connection

    def run(self):
        self._receive_first_packet()
        self._listen_and_snapshot()

    def _receive_first_packet(self):
        try:
            data = self.connection.rec_from_fpga(buffer_size=1500)
            self.packets_received += 1
            self.start_time = time.time()
            self.first_packet_counter = self._extract_packet_counter(data)
            self.udp_data_length = len(data)
        except socket.timeout:
            raise NoPacketsReceived

    def _listen_and_snapshot(self):
        ongoing = True
        while ongoing:
            try:
                data = self.connection.rec_from_fpga(buffer_size=16)
                self.packets_received += 1
                self.latest_packet_counter = self._extract_packet_counter(data)
                self.latest_packet_delta_time = time.time() - self.start_time
                self.logger.snapshot(self.latest_packet_delta_time, self.latest_packet_counter, self.packets_received)
            except socket.timeout:
                ongoing = False
                self.calculate_result_parameters()
                self.logger.successfully_ended(self.packets_transmitted,
                                               self.packets_received,
                                               self.time_elapsed, self.udp_data_length, self.udp_data_throughput)

    def calculate_result_parameters(self):
        self.packets_transmitted = self.latest_packet_counter - (self.first_packet_counter - 1)
        self.time_elapsed = self.latest_packet_delta_time
        counter_difference = self.latest_packet_counter - self.first_packet_counter
        self.udp_data_throughput = self.udp_data_length * 8 * counter_difference / self.latest_packet_delta_time / 1e6

    @staticmethod
    def _extract_packet_counter(data):
        return int(data.hex()[:16], 16)
