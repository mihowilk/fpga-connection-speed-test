import socket
from scapy.packet import Raw
from scapy.layers.inet import IP, UDP

FPGA_IP = '127.0.0.11'
FPGA_UDP_PORT = 12666
SPEED_TESTING_IP = '127.0.0.12'
SPEED_TESTING_UDP_PORT = 12666
IFACE = 'lo'
PADDING_VALUE = b'\xd1'


def is_nth_bit_set(x: int, n: int):
    if x & (1 << n):
        return True
    return False

class FpgaMockup:
    def __init__(self, setup_iface):
        self.setup_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
        self.setup_sock.bind((setup_iface, 0))
        self.setup_sock.settimeout(1.0)
        self.on = False
        self.mode = 0
        self.padding = 0
        self.number_of_test_packets = 10

    def listening(self):
        try:
            print("Listening...")
            received_data = self.setup_sock.recv(4096)
            data = IP(received_data)
            if(data.getfieldval('dport') == 12666):
                self.received_on_12666(data.getfieldval('load'))
            if(data.getfieldval('dport') == 14666):
                self.received_on_14666(data.getfieldval('load'))
            if(data.getfieldval('dport') == 15666):
                self.received_on_15666(data.getfieldval('load'))
            print("Stoped")
        except socket.timeout: 
            print("Timed out")
            pass
        except AttributeError:
            print("Atribute Error")
            pass

    def received_on_12666(self, data):
        print(f'Received setup on port 12666, setup message: {data}')
        integer = int.from_bytes(data, 'big')

        if is_nth_bit_set(integer, 9):
            if is_nth_bit_set(integer, 8):
                self.mode = 3               #11 - not used 
            else:
                self.mode = 2               #10 - continous mode 
        else:
            if is_nth_bit_set(integer, 8):
                self.mode = 1               #01 - burst mode
            else:
                self.mode = 0               #00 - single shot

        print(f'Mode set to: {self.mode}')
        
        self.on = is_nth_bit_set(integer, 7)
        print(f'Start sending = {self.on}')

    def received_on_14666(self, data):
        print(f'Received setup on port 14666, setup message: {data}')
        self.padding = int.from_bytes(data, 'big')
        print(f"Set padding to {self.padding}")

    def received_on_15666(self, data):
        print(f'Received setup on port 15666, setup message: {data}')
        self.number_of_test_packets = int.from_bytes(data, 'big')
        print(f"Set number of packets to {self.number_of_test_packets}")

    def send_packet(self, packet):
        self.setup_sock.send(packet)

    def sending(self, dst_ip, src_ip, dstport, srcport):
        if self.mode == 1:
            print(f'Sending {self.number_of_test_packets} packets')
            for i in range(self.number_of_test_packets):
                packet = IP(dst=dst_ip, src=src_ip)/UDP(dport=dstport, sport=srcport)/Raw(load=((i+1).to_bytes(8, "big")+PADDING_VALUE*self.padding))
                self.send_packet(raw(packet))

        if self.mode == 0:
            print(f'Sending single packet')
            packet = IP(dst=dst_ip, src=src_ip)/UDP(dport=dstport, sport=srcport)/Raw(load=((1).to_bytes(8, "big")+PADDING_VALUE*self.padding))
            self.send_packet(raw(packet))

        if self.mode == 2:
            print(f'Sending continous packets')
            counter = 1
            while(True):
                packet = IP(dst=dst_ip, src=src_ip)/UDP(dport=dstport, sport=srcport)/Raw(load=((i+1).to_bytes(8, "big")+PADDING_VALUE*self.padding))
                self.send_packet(raw(packet))
                counter += 1

        if self.mode == 3:
            print(f'Not sending packets')

if __name__ == "__main__":
    testing_fpga = FpgaMockup(IFACE)
    while(testing_fpga.on == False):
        testing_fpga.listening()

    testing_fpga.sending(SPEED_TESTING_IP, FPGA_IP, SPEED_TESTING_UDP_PORT, FPGA_UDP_PORT)
    print("Finished sending.")