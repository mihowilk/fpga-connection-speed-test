import socket
import time

from exceptions import NoPacketsReceived


class SpeedTest:

    def __init__(self, logger, connection):
        self.start_time = None
        self.first_packet_counter = None
        self.latest_packet_counter = None
        self.latest_packet_delta_time = None

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
            ResultParameters.packets_received += 1
            self.start_time = time.time()
            self.latest_packet_delta_time = 0
            self.first_packet_counter = self.latest_packet_counter = self._extract_packet_counter(data)
            ResultParameters.udp_data_length = len(data)
        except socket.timeout:
            raise NoPacketsReceived

    def _listen_and_snapshot(self):
        ongoing = True
        while ongoing:
            try:
                data = self.connection.rec_from_fpga(buffer_size=16)
                ResultParameters.packets_received += 1
                self.latest_packet_counter = self._extract_packet_counter(data)
                self.latest_packet_delta_time = time.time() - self.start_time
                self.logger.snapshot(self.latest_packet_delta_time, self.latest_packet_counter)
            except socket.timeout:
                ongoing = False
                self._calculate_result_parameters()
                self.logger.successfully_ended()

    def _calculate_result_parameters(self):
        ResultParameters.packets_transmitted = self.latest_packet_counter - (self.first_packet_counter - 1)
        ResultParameters.time_elapsed = self.latest_packet_delta_time
        if ResultParameters.time_elapsed == 0:
            ResultParameters.udp_data_throughput = 0
        else:
            counter_difference = self.latest_packet_counter - self.first_packet_counter
            ResultParameters.udp_data_throughput = ResultParameters.udp_data_length * 8 * counter_difference / ResultParameters.time_elapsed / 1e6

    @staticmethod
    def _extract_packet_counter(data):
        return int(data.hex()[:16], 16)


class ResultParameters:
    packets_transmitted = None
    packets_received = 0
    time_elapsed = None
    udp_data_length = None
    udp_data_throughput = None
