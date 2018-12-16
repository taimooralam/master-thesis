# car.py

from source import VideoSource
import cv2
import time
from socket import *
import helper as help
import msgpack as pack
import struct
import math
import sys
import os

gprotocol = sys.argv[1] if (sys.argv[1] in {"udp", "tcp", "sctp"}) else "udp"
log_file_relative_path = './data/car.txt'

orig_stdout = sys.stdout
orig_stderr = sys.stderr
if 'log_file_relative_path' in locals():
    new_path = help.give_complete_file_path(log_file_relative_path)
    f = open(new_path, 'w')
    sys.stdout = f
    sys.stderr = f


class Car(object):

    def __init__(self):
        self.video_source = VideoSource(True)
        self.driver_host = help.host
        self.driver_port = help.port
        self.driver_address = (self.driver_host, self.driver_port)
        self.driver_socket = None
        self.connection = None #to be used in case of tcp
        self.protocol = None

    def start(self, protocol="udp"):
        self.protocol = protocol if protocol in {"udp", "tcp", "sctp"} else "udp"
        if self.protocol == "udp":
            print "Car operating on UDP ........\n"
            self.driver_socket = socket(AF_INET, SOCK_DGRAM)
        elif self.protocol == "tcp":
            print "Car operating on TCP ........{0}\n".format(time.time())
            self.driver_socket = socket(AF_INET, SOCK_STREAM)
            print "Car socket created  .........{0}\n".format(time.time())
            self.driver_socket.connect(self.driver_address)
            print "Connected to driver: at {0}".format(time.time())

    def get_data(self):
        return self.video_source.get_random_data()

    def send_data(self, data):
        if self.protocol == "udp":
            return self.driver_socket.sendto(data, self.driver_address)
        elif self.protocol == "tcp":
            totalsent = 0
            if data == "":
                self.driver_socket.send(data)
                return totalsent
            while totalsent < len(data):
                sent = self.driver_socket.send(data[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent
            return totalsent

    def stop(self):
        self.driver_socket.close()
        del self.video_source



try:
    print "THIS IS CAR"
    car = Car()
    car.start(gprotocol)
    print"Car Started.\n"

    print"Sending data to remote driver at {0}:{1} at time: {2}".format(car.driver_host, car.driver_port, time.time())
    chunk_sequence = 0 #is also the RTP packet sequence
    while chunk_sequence < help.chunks_num:
        unserialized_data = car.get_data()
        chunk_sequence += 1
        rtp_header = struct.pack('!BBHdI', 128, 26, chunk_sequence, time.time(), 1)

        # add the RTP header to the chunk and send the data
        sent = car.send_data(rtp_header + unserialized_data)
	print chunk_sequence

        if not sent:
            print "Data not sent at chunk_sequence: {0}".format(chunk_sequence) + "\n"

    for i in range(0,1):
    	car.send_data(struct.pack('!BBHdI', 128, 26, chunk_sequence + 1, time.time(), 3)+car.get_data())
	time.sleep(10)
    print "ssrc 3 sent"
    if 'log_file_relative_path' in locals():
        f.close()
    sys.stdout = orig_stdout
    sys.stderr = orig_stderr
    sys.exit(1)
except ValueError as msg:
    print "Value Error: {0}".format(msg)

#except Exception, (error, message):
    #print "Cannot connect to remote driver. Error No: {0} Message: {1}".format(error,message)

except KeyboardInterrupt:
    if 'log_file_relative_path' in locals(): 
        f.close()
    car.stop()
    del car
    print "Car Stopped"

