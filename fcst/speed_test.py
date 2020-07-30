import socket
import time


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
        self.udp_data_throughput = self.udp_data_length * 8 * counter_difference / self.last_packet_delta_time / 1e6

    @staticmethod
    def snapshot_to_file(speed_data):
        print(f'Delta time: {speed_data[0]}')
        print(f'Current counter: {speed_data[1]}')
        print(f'Udp length: {speed_data[2]}')

    @staticmethod
    def extract_packet_counter(data):
        return int(data.hex()[:16], 16)
