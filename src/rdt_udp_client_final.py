import socket
from socket import timeout
import time
import os

BUFFER_SIZE = 20

serverName = 'localhost'

PortRecv = 15001
PortSend = 15000

recv = (serverName, PortRecv)
send = (serverName, PortSend)

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

recv_sock.bind(recv)

recv_sock.settimeout(30)

seq = 0
content = open('a.txt', "rb")

def process_ACK(message):
    if message == "":
        return  []
    acks = ([int(x) for x in message.split(",")])
    acks.sort()
    return acks

# 2 modes, create and update
# In update, first extra argument would be the ACK array from the server
#            second extra argument would be the last positive ack
def update_queue(arr=[], mode="create", N=100, neg_acks = [], last_ack=-1):
    global seq
    global content
    if mode=="create":
        seq = 0
        data = content.read(BUFFER_SIZE)
        while N>0 and data != b'':
            arr += [(seq, data)]
            seq += 1
            N -= 1
            # Prevent reading extra bits
            if N>0:
                data = content.read(BUFFER_SIZE)
    elif mode=="update":
        seq = arr[-1][0] + 1
        index = 0
        ack_index = 0
        
        # Removing successfully transmitted packets
        while index<len(arr) and arr[index][0]<=last_ack:
            #print("index, ack_index, len(neg_acks), len(arr):{},{},{},{}".format(index, ack_index, len(neg_acks), len(arr)))
            if ack_index==len(neg_acks):
                print("Element:{} popped".format(arr[index][0]))
                arr.pop(index)
            elif neg_acks[ack_index] > arr[index][0]:
                print("element:{} popped".format(arr[index][0]))
                arr.pop(index)
            else:
                print("Element:{} skipped".format(arr[index][0]))
                index += 1
                ack_index += 1
        
        # Adding new packets in new empty spaces
        extra_space = N-len(arr)
        if extra_space>0:
            data = content.read(BUFFER_SIZE)
            while extra_space>0 and len(data) >0:
                arr += [(seq, data)]
                seq += 1
                extra_space -= 1
                if extra_space>0:
                    data = content.read(BUFFER_SIZE)
    return arr


def make_packet(seq,ack,data):
    seq_field = (seq).to_bytes(4,byteorder='big')
    ack_field = (ack).to_bytes(4,byteorder='big')
    packet =  seq_field + ack_field + data
    return packet

def upld(file_name):
    global seq
    global content
    seq = 0
    content = open(file_name, "rb")
    finished = os.path.getsize(file_name)//BUFFER_SIZE
    N = 3
    last_ack = -1
    current_queue = update_queue(N=N)
    print(current_queue)
    while current_queue:
        for part in current_queue:
            packet = make_packet(part[0], finished, part[1])
            send_sock.sendto(packet,send)
        print("Sent next Queue")
        while True:
            try:
                response ,address = recv_sock.recvfrom(4096)
                if last_ack < int.from_bytes(response[4:8],byteorder='big'):
                    break
            except timeout:
                break
        recv_sock.settimeout(3)
        #seq = int.from_bytes(packet[:4],byteorder='big')
        #ack = int.from_bytes(packet[4:8],byteorder='big')
        #data = packet[8:].decode()
        
        negative_acks = process_ACK(response[8:].decode()) #******************** Edit the slicing according to packet
        last_ack = int.from_bytes(response[4:8],byteorder='big')  # Last positive ack is stored here
        current_queue = update_queue(current_queue, mode="update", N=N, neg_acks = negative_acks, last_ack=last_ack)
        print("current_queue:{}".format(current_queue))
    # record throughput and time etc
    content.close()
    return


upld("a.txt")