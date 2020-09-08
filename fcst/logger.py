import logging
import os
from datetime import datetime

from .speed_test import ResultParameters


class Logger:

    def __init__(self):
        self.logger = Logger.setup_logger()
        self.csv_logger = Logger.setup_csv_logger()
        self.snapshot_interval = 1

    @staticmethod
    def setup_logger():

        if not os.path.exists('results'):
            os.mkdir('results')

        logger = logging.getLogger("speed_test_logger")

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

    def snapshot(self, last_packet_delta_time, last_packet_counter):
        if ResultParameters.packets_received % self.snapshot_interval == 0:
            self.logger.info(f'Delta time: {last_packet_delta_time}; Current counter: {last_packet_counter}')
            self.csv_logger.info(f'{last_packet_delta_time},{last_packet_counter}')

    def successfully_ended(self):
        self.logger.info(f"Successfully ended test\n"
                         f"Transmitted {ResultParameters.packets_transmitted} packets\n"
                         f"Received {ResultParameters.packets_received} packets in {ResultParameters.time_elapsed} seconds\n"
                         f"Raw UDP packet data length: {ResultParameters.udp_data_length} bytes\n"
                         f"Raw UDP packet throughput: {ResultParameters.udp_data_throughput} Mbps")
