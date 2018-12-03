import pickle
import cv2
import sys
import base64
import config
import struct
import helper
from socket import *
import time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoSource(object):


    def __init__(self):
        self.video = cv2.VideoCapture('video.mp4') #0 for camera
        self.fps = self.video.get(5)

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        success, image = self.video.read()
        if not success:
            sys.stderr.write('Could not read the image from the source')
            return None
        else:
             #cv2.imshow("l", image) #show the image here
             encoding_success, jpeg = cv2.imencode('.jpg', image)
             if not encoding_success:
                 sys.stderr.write('Could not encode the image')
                 return None
             else:
                #logger.info(type(jpeg.shape))
                logger.info(jpeg.shape)
                #logger.info(jpeg.dtype)
                #logger.info(type(jpeg.dtype))
                #logger.info(type(base64.b64encode(jpeg.tobytes())))
                data_with_information = [str(jpeg.dtype), base64.b64encode(jpeg.tobytes()),jpeg.shape]
                return data_with_information

class Vehicle(object):

    def __init__(self):
        self.video_source = VideoSource()
        self.driver_host = config.host
        self.driver_port = config.port
        self.driver_address = (self.driver_host, self.driver_port)
        self.driver_socket = None

    def start(self):
        logger.info("Connecting vehicle over UDP")
        self.driver_socket = socket(AF_INET, SOCK_DGRAM)

    def get_data(self):
        return self.video_source.get_frame()

    def send_data(self, data):
        #logger.info("Data sent of length {0}".format (len(data)))
        return self.driver_socket.sendto(data, self.driver_address)

    def stop(self):
        self.driver_socket.close()
        del self.video_source
        logger.info('Vehcile stopped')


try:
    # create the socket connection
    vehicle = Vehicle()
    vehicle.start()

    frame_number = 1
    # while the video has not ended
    while True:

        #logger.info('get the image')
        raw_data = vehicle.get_data()
        if raw_data is None:
            for i in range(0,5):
                vehicle.send_data(struct.pack("Biiii", 3, 0, 0, 0, struct.calcsize("Biiii")))
            break
        else:
            serialized_data = pickle.dumps(raw_data)


        #logger.info('add timestamp,frame number, length, and related meta-info from mumpy as well as n chunks')
        frame_with_metadata = struct.pack("idi", frame_number, time.time(),
                                          struct.calcsize("idi") + len(serialized_data)) + serialized_data

        chunk_number = 1
        # divide the image into n chunks
        chunks = list(helper.chunks(frame_with_metadata, config.buf))
        total_chunks = len(chunks)
        for chunk in chunks:
            # for each of those chunks, add chunk number, frame number, length of the chunk and chunk data and send it over the operator
            chunk_with_metadata = struct.pack("Biiii", 1, frame_number, total_chunks ,chunk_number,
                                              struct.calcsize("Biiii") + len(chunk)) + chunk
            vehicle.send_data(chunk_with_metadata)
            chunk_number = chunk_number + 1
        frame_number = frame_number + 1

    # close the connection
    vehicle.stop()

except ValueError as msg:
    print "Value Error: {0}".format(msg)

except KeyboardInterrupt:
    vehicle.stop()
    del vehicle
    print "Vehicle Stopped"



