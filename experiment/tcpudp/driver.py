
# driver.py

from socket import *
import helper as help
import sys
import cv2
import struct
import time
import datetime
import json
import os

import plotly
import plotly.plotly as py
import plotly.offline as offline
import plotly.graph_objs as go
plotly.tools.set_credentials_file(username="<>", api_key="<>")

gprotocol = sys.argv[1] if (sys.argv[1] in {"udp", "tcp"}) else "udp"
log_file_relative_path = './data/driver.txt'

orig_stdout = sys.stdout
orig_stderr = sys.stderr
if 'log_file_relative_path' in locals():
    new_path = help.give_complete_file_path(log_file_relative_path)
    f = open(new_path, 'w')
    sys.stdout = f
    sys.stderr = f


def give_dropped(val):
    if val is None:
        return 0
    else:
        return None


class Driver(object):

    def __init__(self):
        self.driver_host = help.host
        self.driver_port = help.port
        self.driver_address = (self.driver_host, self.driver_port)
        self.driver_socket = None
        self.connection = None
        self.car_address = None
        self.protocol = None

    def start_listening(self, protocol="udp"):
        self.protocol = protocol if protocol in {"udp", "tcp"} else "udp"
        if self.protocol == "udp":
            print "Driver operating on UDP ........\n"
            self.driver_socket = socket(AF_INET, SOCK_DGRAM)
            self.driver_socket.bind(self.driver_address)
        elif self.protocol == "tcp":
            print "Driver operating on TCP .........{0}\n".format(time.time())
            self.driver_socket = socket(AF_INET, SOCK_STREAM)
            print "Driver socket created .........{0}\n".format(time.time())
            self.driver_socket.bind(self.driver_address)
            print "Driver socket bound .........{0}\n".format(time.time())
            self.driver_socket.listen(5)
            print "Driver listening .........{0}\n".format(time.time())
            self.connection, self.car_address = self.driver_socket.accept()
            print "Connected to: "+str(self.car_address)

    def get(self, length):
        if self.protocol == "udp":
            return self.driver_socket.recvfrom(length)
        elif self.protocol == "tcp":
            #data = self.connection.recv(length)
            #print "length of data received: {0}".format(len(data))
            chunks = []
            bytes_recd = 0
            while bytes_recd < length:
                chunk = self.connection.recv(min(length - bytes_recd, length))
                if chunk == '':
                    raise RuntimeError("socket connection broken")
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            return ''.join(chunks), self.car_address

    def __del__(self):
        self.driver_socket.close()




try:
    print "THIS IS DRIVER"
    driver = Driver()
    driver.start_listening(gprotocol)
    print "Driver at {0}:{1} started listening for a car at time: {2}".format(driver.driver_host, driver.driver_port, time.time())

    chunk_sequence = 1
    delta_time = [None] * help.chunks_num
    times = []
    while True:
        # get the chunk with the rtp header and parse all the RTP header values
        rtp_packet, address = driver.get(help.buf+16)
        vpxccm, payload_type, gotten_chunk_sequence, timestamp, ssrc = struct.unpack('!BBHdI', rtp_packet[0:16])
        if ssrc == 3:
            break
        now = time.time()

        delta_time[gotten_chunk_sequence-1] = now-timestamp
	print gotten_chunk_sequence
        # if chunk_sequence < gotten_chunk_sequence:
        #    print "{0}<{1}".format(chunk_sequence, gotten_chunk_sequence)
        #    this_time = help.simplify_time(now)
        #    while chunk_sequence < gotten_chunk_sequence:
        #        chunk_sequence += 1
        #        delta_time.append(None)
        #        missed_sequences_data.append(0.0)
        #        times.append(this_time)
        # else:
        #    print "{0},{1}".format(chunk_sequence, gotten_chunk_sequence)
        #    delta_time.append()
        #    missed_sequences_data.append(None)
        #    times.append(help.simplify_time(now))
        #    chunk_sequence += 1
    print "Max sequence number: {0}, length of delta_time: {1}".format(gotten_chunk_sequence, len(delta_time))

    # x_axis = times
    x_axis = range(0, gotten_chunk_sequence-1)
    now = datetime.datetime.now()

    missed_sequences_data = map(give_dropped, delta_time)

    trace1 = go.Scatter(
        x=x_axis,
        y=delta_time,
        mode='lines',
        name='latency'
    )

    trace2 = go.Scatter(
        x=x_axis,
        y=missed_sequences_data,
        mode='markers',
        name='dropped packets'
    )

    data = [trace1, trace2]

    lines_path = help.give_complete_file_path("../graphs/lines/{0}_{1}_{2}.html".format(sys.argv[1], sys.argv[2], sys.argv[3]))
    print "Lines at {0}".format(lines_path)
    layout_lines = dict(
        yaxis=dict(title='Latency (seconds)'),
        xaxis=dict(title='Packet Number'),
	font = dict(size=20))
    fig = dict(data=data, layout=layout_lines)
    offline.plot(fig, filename=lines_path, auto_open=False)

    histogram_path = help.give_complete_file_path("../graphs/histogram/{0}_{1}_{2}.html".format(sys.argv[1], sys.argv[2], sys.argv[3]))
    print "histogram at {0}".format(histogram_path)
    layout_histogram = dict(
        xaxis= dict(title = "Latency(seconds)"),
	font = dict(size=20)
	)
    trace3 = go.Box(x=delta_time)
    fig_box = dict(data = [trace3], layout = layout_histogram)
    offline.plot(fig_box, filename=histogram_path, auto_open=False)

    if "log_file_relative_path" in locals():
        f.close()
    sys.stdout = orig_stdout
    sys.stderr = orig_stderr
    sys.exit(1)

except timeout:
    if 'log_file_relative_path' in locals():
        f.close()
    print "Timed out. Cannot receive data from car"
    del driver

except KeyboardInterrupt:
    del driver
    #cv2.destroyAllWindows()
    print "Driver Left."

