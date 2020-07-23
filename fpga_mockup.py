import socket

SETUP_IP = '127.0.0.1'
SETUP_UDP_PORT = 12666
setup_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
setup_sock.bind((SETUP_IP, SETUP_UDP_PORT))

SPEED_TESTING_IP = '127.0.0.2'
SPEED_TESTING_UDP_PORT = 5005
speed_test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    data, addr = setup_sock.recvfrom(1024)
    print('Received setup, setup message: %s' % data)
    break

print('Sending 10 packets')
for i in range(0, 10):
    setup_sock.sendto(b'Speed test package',
                      (SPEED_TESTING_IP, SPEED_TESTING_UDP_PORT))
