import socket


class FpgaMockup:
    def __init__(self, SETUP_IP='127.0.0.1', SETUP_UDP_PORT=12666):
        self.SETUP_IP = SETUP_IP
        self.SETUP_UDP_PORT = SETUP_UDP_PORT
        self.setup_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock.bind((SETUP_IP, SETUP_UDP_PORT))

    def listen(self):
        while True:
            print('Waiting for setup...')
            data = self.setup_sock.recvfrom(1024)[0]
            print('Received setup,  data : %s' % data)

    def sending(self, SPEED_TESTING_IP='127.0.0.2', SPEED_TESTING_UDP_PORT=5005):
        print('Sending 10 packets')
        for _ in range(10):
            self.setup_sock.sendto(b'Speed test package',
                                   (SPEED_TESTING_IP, SPEED_TESTING_UDP_PORT))


if __name__ == "__main__":
    testing_fpga = FpgaMockup()
    testing_fpga.listen()
