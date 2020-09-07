import logging
import os
from datetime import datetime


class Logger:

    def __init__(self):
        self.logger = Logger.setup_logger()
        self.csv_logger = Logger.setup_csv_logger()

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
        self.logger.info(f'Delta time: {last_packet_delta_time}; Current counter: {last_packet_counter}')
        self.csv_logger.info(f'{last_packet_delta_time},{last_packet_counter}')

    def successfully_ended(self, first_packet_counter, last_packet_counter, packets_received, time_elapsed,
                           udp_data_length,
                           udp_data_throughput):
        self.logger.info(f"Successfully ended test\n"
                         f"Transmitted {last_packet_counter - (first_packet_counter - 1)} packets\n"
                         f"Received {packets_received} packets in {time_elapsed} seconds\n"
                         f"Raw UDP packet data length: {udp_data_length} bytes\n"
                         f"Raw UDP packet throughput: {udp_data_throughput} Mbps")
