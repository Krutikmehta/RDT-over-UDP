import socket
from socket import timeout

serverName = 'localhost'

PortRecv = 15000
PortSend = 15001

BUFFER_SIZE = 2048

recv = (serverName, PortRecv)
send = (serverName, PortSend)

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

recv_sock.bind(recv)



output_file = 5  # some random assignment
seq_from = -1
buffer_acks = []

def make_packet(seq,ack,data):
    seq_field = (seq).to_bytes(4,byteorder='big')
    ack_field = (ack).to_bytes(4,byteorder='big')
    packet =  seq_field + ack_field + data
    return packet

def update_queue(recv_packets):
    global seq_from
    global output_file
    global buffer_acks
    if len(recv_packets)>0:
        buffer_acks += recv_packets
    buffer_acks = list(set(buffer_acks))
    buffer_acks.sort()
    last_ack = buffer_acks[-1][0]
    while len(buffer_acks)>0:
        if buffer_acks[0][0]<=seq_from:
            buffer_acks.pop(0)
        elif buffer_acks[0][0]==seq_from+1:
            output_file.write(buffer_acks[0][1])
            buffer_acks.pop(0)
            seq_from += 1
        else:
            break
    
    # making the neg acks into a packet
    neg_seqs = set(range(seq_from+1, last_ack+1))
    buffer_seqs = []
    for i in buffer_acks:
        buffer_seqs += [i[0]]
    buffer_seqs = set(buffer_seqs)
    neg_seqs -= buffer_seqs
    ans = [str(x) for x in neg_seqs]
    return ",".join(ans), last_ack

def upld(file_name):
    global seq_from
    global output_file
    global buffer_acks
    seq_from = -1
    output_file = open(file_name, "wb")
    last_ack_packet = None
    recv_packets = []
    buffer_acks = []
    transmission_complete = False
    while not transmission_complete or len(buffer_acks)>0:
        recv_packets = []
        recv_sock.settimeout(30) # timeout 1
        while True:
            try:
                print("waiting...")
                message, address = recv_sock.recvfrom(BUFFER_SIZE)
                seq = int.from_bytes(message[:4],byteorder='big')
                ack = int.from_bytes(message[4:8],byteorder='big')
                if ack==seq and seq >0:
                    transmission_complete = True
                recv_packets += [ (int.from_bytes(message[:4],byteorder='big'), message[8:]) ] # Storing (seq, data)
                print("recieved:{}".format(int.from_bytes(message[:4],byteorder='big')))
                break 
            except timeout:
                if last_ack_packet:
                    send_sock.sendto(last_ack_packet,send)
                if transmission_complete:
                    break
        recv_sock.settimeout(1) # different from prev timeout
        while True:
            try:
                message, address = recv_sock.recvfrom(BUFFER_SIZE)
                seq = int.from_bytes(message[:4],byteorder='big')
                ack = int.from_bytes(message[4:8],byteorder='big')
                print(seq, ack)
                if ack==seq and seq >0:
                    transmission_complete = True
                recv_packets += [ (int.from_bytes(message[:4],byteorder='big'), message[8:]) ]
                print("recieved:{}".format(int.from_bytes(message[:4],byteorder='big')))
                if transmission_complete:
                    break
            except timeout:
                break
        neg_seqs, last_ack = update_queue(recv_packets)
        last_ack_packet = make_packet(last_ack, last_ack, neg_seqs.encode())
        send_sock.sendto(last_ack_packet,send)
        print("Sent negative acks")
        print(transmission_complete)
        print(buffer_acks)
        #recv_sock.settimeout(1)
    output_file.close()
    print("Transfer Complete")


upld("recv.txt")