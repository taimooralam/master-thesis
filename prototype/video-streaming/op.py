#operator.py
import pickle
import cv2
import base64
import config
import struct
from socket import *
import sys
import time
import numpy as np
import helper
from multiprocessing import Process, Pipe
from cStringIO import StringIO

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Operator(object):

    def __init__(self):
        self.driver_host = config.host
        self.driver_port = config.port
        self.driver_address = (self.driver_host, self.driver_port)
        self.driver_socket = None
        self.car_address = None

    def start_listening(self):
        logger.info("Operator operating on UDP")
        self.driver_socket = socket(AF_INET, SOCK_DGRAM)
        self.driver_socket.bind(self.driver_address)

    def get(self, length):
        return self.driver_socket.recvfrom(length)

    def __del__(self):
        self.driver_socket.close()

def collect(buffer_r, render_w):
    e_frame_number = 1
    e_chunk_number = 1
    file_str = StringIO()
    frame_is_complete = True
    while True:
        packet = buffer_r.recv()
        #logger.info("Got a packet:{0}".format(len(packet)))
        instruction, frame_number, total_chunks, chunk_number, packet_length, chunk = helper.unpack_helper("Biiii", packet)
        #logger.info("Chunk_number: {0}, total chunks: {1}".format(chunk_number, total_chunks))
        if instruction == 3: #instruction was given to stop
            logger.info("Exit instruction received:{0}".format(instruction))
            buffer_r.close()
            break
        if packet_length != len(packet): #do not stich together the packet
            e_chunk_number = 1
            e_frame_number = frame_number + 1 #broken packet
        else:
            #start to stich together the chunks to form a frame.
            if frame_number == e_frame_number: #the chunks need to be still added to form the complete frame
                if chunk_number == e_chunk_number: #the chunk is of the correct sequence
                    file_str.write(chunk)
                    if chunk_number == total_chunks:
                        frame_with_metadata = file_str.getvalue()
                        #logger.info('Got frame with length: {0}'.format(len(frame_with_metadata)))
                        render_w.send(frame_with_metadata)
                        e_chunk_number = 1
                        e_frame_number = frame_number + 1
                        file_str.close()
                        file_str = StringIO()
                    else:
                        e_chunk_number = e_chunk_number + 1
                else: #the chunk is out of order, discard the whole frame
                    e_chunk_number = 1
                    e_frame_number = frame_number + 1 #out of order chunk
            else: #frame is complete or wait for the next frame
                logger.info("Frame is incomplete")


def show(render_r):
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter("out.mp4", fourcc, 20.0, (1280, 720))
    while True:
        frame_with_metadata = render_r.recv()
        frame_number, timestamp, frame_length, serialized_data = helper.unpack_helper("idi", frame_with_metadata)
        if frame_length == len(frame_with_metadata):
            logger.info('show: Got frame with length: {0}'.format(len(frame_with_metadata)))
            raw_data = pickle.loads(serialized_data)
            dtype = np.dtype(raw_data[0])
            shape = raw_data[2]
            base64_string = raw_data[1]
            jpeg_bytes = base64.b64decode(base64_string)
            jpeg = np.fromstring(jpeg_bytes,dtype=dtype)
            jpeg.shape = shape
            image = cv2.imdecode(jpeg,cv2.IMREAD_COLOR)
            out.write(image)
            #cv2.imshow("Show", image)
            #cv2.waitKey(0)



        else:
            logger.info('show: Frame lost: Current_length: {0}, Length in packet: {1}'.format(len(frame_with_metadata),frame_length))


try:

    #create a pipe
    buffer_r, buffer_w = Pipe()
    render_r, render_w = Pipe()
    bufferingProcess = Process(target=collect, args=(buffer_r, render_w))
    renderingProcess = Process(target=show, args=(render_r,))
    renderingProcess.start()
    bufferingProcess.start()

    operator = Operator()
    operator.start_listening()

    while True:
        packet, address = operator.get(config.buf + struct.calcsize("Biiii"))
        #logger.info("Length received:{0}".format(len(packet)))
        if struct.unpack("B",packet[:struct.calcsize("B")]) == 3:
            buffer_w.close()
            render_w.close()
            bufferingProcess.join()
            renderingProcess.join()
            break
        else:
            buffer_w.send(packet)

except timeout:
    logger.info("Timed out. Cannot receive data from car")
    del operator
    bufferingProcess.join()
    renderingProcess.join()

except KeyboardInterrupt:
    del operator
    cv2.destroyAllWindows()
    bufferingProcess.join()
    renderingProcess.join()
    print "Operator Left."
