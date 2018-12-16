#visualize the data that go produced

import os
import sys
import plotly
import plotly.offline as offline
import plotly.graph_objs as go
import helper as help
plotly.tools.set_credentials_file(username="<>", api_key="<>")

gprotocol = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "quic" else "quic"
latency = sys.argv[3] if len(sys.argv) > 3 else "30ms"
packet_loss = sys.argv[4] if len(sys.argv) > 4 else 1
save_file_name_lines = "../graphs/lines/" + gprotocol +"_"+ latency +"_"+ str(packet_loss) + ".html"
save_filename_histogram = "../graphs/histogram/" + gprotocol + "_" + latency + "_" + str(packet_loss) + ".html"
save_filename_histogram_real = "../graphs/histogram/" + gprotocol + "_" + latency + "_" + str(packet_loss) + "_hist.html"
#log_relative_file_path = "./data/creating_quic_graphs.txt"
data_file_name = sys.argv[1] if len(sys.argv) > 1 else "./data/Log.txt"
orig_stdout = sys.stdout
orig_stderr = sys.stderr

if 'log_relative_file_path' in locals():
	new_path = help.give_complete_file_path(log_relative_file_path)
	f = open(new_path, 'w')
	sys.stdout = f
	sys.stderr = f

def give_dropped(val):
	if val is None:
		return 0
	else:
		return None

try:
	print "Opening the file ..."
	# open the file from the command line
	print help.give_complete_file_path(data_file_name)
	datafile = open(help.give_complete_file_path(data_file_name), "r+")

	print "Reading the lines ..."
	# read the lines of the file
	lines = datafile.readlines()
	numberOfPackets = int(lines[0][:-1])
	print "Number of packets: {0}".format(numberOfPackets)
	final_deltas = [None] * numberOfPackets

	print "Converting strings to integers..."	
	# get the number of the data as an int
	print lines[1]
	allAsStrings = lines[1].split(' ')[:-1]	
	
	for x in allAsStrings:
		pair = x.split(":")
		print pair
		sequence_number = int(pair[0])
		delta = float(pair[1])
		final_deltas[sequence_number-1] = delta
	print "Got the integers..."
	#print the delta array
	print final_deltas

	print "Starting to make graphs"
	trace1 = go.Scatter(
		x=range(0, numberOfPackets),
		y=final_deltas,
		mode = 'lines',
		name = 'latency3'
	)

	missed_sequences_data = map( give_dropped , final_deltas)
	
	trace2 = go.Scatter(
		x = range(0, numberOfPackets),
		y = missed_sequences_data,
		mode = 'markers',
		name = 'dropped'
	)

	data = [trace1]
	
	layout_lines = dict(
		font=dict(size=20),
		xaxis = dict(title="Packet number"),
		yaxis = dict(title="Latency (seconds)")
	)
	fig_lines = dict(data=data, layout=layout_lines)
	print help.give_complete_file_path(save_file_name_lines)
	offline.plot(fig_lines, filename=help.give_complete_file_path(save_file_name_lines), auto_open=False)

	trace3 = go.Box(
		x=final_deltas
	)
	layout_histogram = dict(
		font=dict(size=20),
		xaxis = dict(title = "Latency(seconds)")
	)
	fig_box = dict(data = [trace3], layout=layout_histogram)
	print help.give_complete_file_path(save_filename_histogram)
	offline.plot(fig_box, filename=help.give_complete_file_path(save_filename_histogram), auto_open=False)

	
	trace4 = go.Histogram(
		x=final_deltas,
		nbinsx=10		
	)
	layout_histogram_real = dict(
		font=dict(size=20),
		xaxis = dict(title = "Latency(seconds)")
	)
	fig_hist = dict(data = [trace4], layout=layout_histogram_real)
	print help.give_complete_file_path(save_filename_histogram_real)
	offline.plot(fig_hist, filename=help.give_complete_file_path(save_filename_histogram_real), auto_open=False)

	datafile.close()

	#if log_relative_file_path in locals():
		#f.close()
	sys.stdout = orig_stdout
	sys.stderr = orig_stderr


	

except IOError:
	print "Could not open the file"
	print sys.exc_info()
except:
	print "An error occured\n"
	print sys.exc_info()

