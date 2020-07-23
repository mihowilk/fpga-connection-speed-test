import socket

SETUP_IP = '127.0.0.1'
SETUP_UDP_PORT = 12666
SETUP_MESSAGE = b'\x01\x75' #0000000111110101
setup_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SPEED_TESTING_IP = '127.0.0.2'
SPEED_TESTING_UDP_PORT = 5005
speed_test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
speed_test_sock.bind((SPEED_TESTING_IP, SPEED_TESTING_UDP_PORT))

# send setup info to FPGA
setup_sock.sendto(SETUP_MESSAGE, (SETUP_IP, SETUP_UDP_PORT))

# receive packets from FPGA
while True:
    data, addr = speed_test_sock.recvfrom(1024)
    print('Received packet form FPGA, data: %s' % data)
