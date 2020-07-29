import socket
import multiprocessing
import time

FPGA_IP = '127.0.0.1'
SPEED_TESTING_IP = '127.0.0.2'
SPEED_TESTING_UDP_PORT = 5005


def is_nth_bit_set(x: int, n: int):
    if x & (1 << n):
        return True
    return False


class FpgaMockup:
    def __init__(self, setup_ip):
        self.setup_ip = setup_ip
        self.setup_sock_12666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_14666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_15666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_12666.bind((setup_ip, 12666))
        self.setup_sock_14666.bind((setup_ip, 14666))
        self.setup_sock_15666.bind((setup_ip, 15666))
        self.on = multiprocessing.Value('b', False)
        self.mode = multiprocessing.Array('c', 16)
        self.padding = multiprocessing.Value('i', 0)
        self.number_of_test_packets = multiprocessing.Value('i', 10)

    def listening_on_12666(self):
        # print("Listening on 12666...")
        data = self.setup_sock_12666.recvfrom(16)[0]
        # print("Finished Listening on 12666.")

        print(f'Received setup on port 12666, setup message: {data}')
        integer = int.from_bytes(data, 'big')

        if is_nth_bit_set(integer, 9):
            if is_nth_bit_set(integer, 8):
                self.mode = 'not used'  # 11
            else:
                self.mode = 'continous mode'  # 10
        else:
            if is_nth_bit_set(integer, 8):
                self.mode = 'burst mode'  # 01
            else:
                self.mode = 'single shot'  # 00

        print(f'Mode set to: {self.mode}')

        self.on.value = is_nth_bit_set(integer, 7)
        if self.on.value == 1:
            print('Received starting datagram')

    def listening_on_14666(self):
        # print("Listening on 14666...")
        data = self.setup_sock_14666.recvfrom(16)[0]
        # print("Finished Listening on 14666.")

        print(f'Received setup on port 14666, setup message: {data}')
        self.padding.value = int.from_bytes(data, 'big')
        print(f"Set padding to {self.padding.value}")

    def listening_on_15666(self):
        # print("Listening on 15666...")
        data = self.setup_sock_15666.recvfrom(64)[0]
        # print("Finished Listening on 15666.")

        print(f'Received setup on port 15666, setup message: {data}')
        self.number_of_test_packets.value = int.from_bytes(data, 'big')
        print(f"Set number of packets to {self.number_of_test_packets.value}")

    def send_packet(self, message, speed_testing_ip, speed_testing_udp_port):
        self.setup_sock_12666.sendto(message,
                                     (speed_testing_ip, speed_testing_udp_port))

    def sending(self, speed_testing_ip, speed_testing_udp_port):
        # if self.mode == "burst mode":
        #     print(f'Sending {self.number_of_test_packets.value} packets')
        #     for _ in range(self.number_of_test_packets.value):
        #         self.send_packet(b'Speed test package', speed_testing_ip, speed_testing_udp_port)
        #
        # if self.mode == 'single shot':
        #     print(f'Sending single packet')
        #     self.send_packet(b'Speed test package', speed_testing_ip, speed_testing_udp_port)
        #
        # if self.mode == "continous mode":
        #     print(f'Sending continous packets')
        #     while (True):
        #         self.send_packet(b'Speed test package', speed_testing_ip, speed_testing_udp_port)
        #
        # if self.mode == "not used":
        #     print(f'Not sending packets')
        number_of_datagrams = 50000
        start_time = time.time()
        for i in range(0, number_of_datagrams):
            data = i.to_bytes(8, byteorder='big')
            padding = i.to_bytes(1016, byteorder='big')
            self.send_packet(data + padding, speed_testing_ip, speed_testing_udp_port)
        stop_time = time.time()
        print(f'Sent {number_of_datagrams} in {stop_time - start_time} seconds')


if __name__ == "__main__":
    testing_fpga = FpgaMockup(FPGA_IP)
    while (testing_fpga.on.value == False):
        p1 = multiprocessing.Process(target=testing_fpga.listening_on_12666)
        p2 = multiprocessing.Process(target=testing_fpga.listening_on_14666)
        p3 = multiprocessing.Process(target=testing_fpga.listening_on_15666)

        p1.start()
        p2.start()
        p3.start()

        p1.join(1)
        p2.join(1)
        p3.join(1)

    print(f'Beginning sending packets to {(SPEED_TESTING_IP, SPEED_TESTING_UDP_PORT)}')
    testing_fpga.sending(SPEED_TESTING_IP, SPEED_TESTING_UDP_PORT)
    print("Finished sending")
