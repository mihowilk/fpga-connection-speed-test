import socket

class FpgaMockup:
    def __init__(self, setup_ip = '127.0.0.1'):
        self.setup_ip = setup_ip
        self.setup_sock_12666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_14666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_15666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_12666.bind((setup_ip, 12666))
        self.setup_sock_14666.bind((setup_ip, 14666))
        self.setup_sock_15666.bind((setup_ip, 15666))
        print('Waiting for setup...')
        data = self.setup_sock_12666.recvfrom(16)[0]        #TO DO: check argument
        print(f'Received setup, setup message: {data}')
        itnigier = int.from_bytes(data, 'big')
        bits = "{0:b}".format(itnigier)
        self.mode = bits[-10:-8]            #[9:8]
        print(f'Mode set to: {self.mode}')
        self.on = False #bool(int(bits[-8:-7]))
        # print(self.on)
        # if self.mode == b'01':
        #     print("BURST!!!")

    def listening(self):
        print("Listening...")

    def sending(self, speed_testing_ip = '127.0.0.2', speed_testing_udp_port = 5005):
        print('Sending 10 packets')
        for _ in range(10):
            self.setup_sock_12666.sendto(b'Speed test package',
                            (speed_testing_ip, speed_testing_udp_port))

if __name__ == "__main__":
    testing_fpga = FpgaMockup()
    while(testing_fpga.on == False):
        testing_fpga.listening()
    testing_fpga.sending()