# source.py

import cv2
import base64
import helper as help
import os

# search public data so that we can know reliability vs latency
# how does packet loss impact latency
# ahmed mobile networks
# ASIL standard - find figures - testing vehicular software/hardware
# requirement: find out how much reliable a car system has to be?

class VideoSource(object):

    def __init__(self, is_file=False):
        self.is_file = is_file
        if not is_file:
            self.video = cv2.VideoCapture(0)
            self.fps = self.video.get(5)
        else:
            self.video = cv2.VideoCapture('video.mp4')
            self.fps = self.video.get(5)
        print "Frame rate: {0}".format(self.fps)

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        success, image = self.video.read()
        if success:
            #cv2.imshow("l", image)
            encoding_success, jpeg = cv2.imencode('.jpg',image)
            if encoding_success:
                data_with_information = [str(jpeg.dtype),base64.b64encode(jpeg.tobytes()),jpeg.shape]
                return data_with_information
            else:
                print "No encoding success"
                return None
        else:
            print "No reading success"
            return None

    def get_random_data(self):
        return os.urandom(help.buf)
