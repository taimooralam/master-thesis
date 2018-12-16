This is the experiment to determine what is the median one-way target latency amoung the protocols TCP UDP and QUIC.

The TCP and UDP experiments are in `tcpudp` folder, while the QUIC experiments are in the QUIC folder. 

In the TCP UDP folder, the files `car.py` and `driver.py` are the files for signifying the sending of 50000 packets from the car to the driver with a base latency of 30ms and packet loss of 1% of mininet. The TT is calculated for all the packets and plotted via plotly in the `graphs` folder. The mininet topology is present in the `topologies/lat_udp_1.py`.

To run the experiment for both tcp and udp with 30ms of base latency and 1% of packet loss run the following two commands while being in the `tcpudp` directory:

- `sudo python topologies/lat_udp_1.py tcp 30ms 1`
- `sudo python topologies/lat_udp_1.py udp 30ms 1`

These commands will create the relevant topologies for TCP and UDP and ultimately create a line plot and box plot in the directories `graphs/lines` and `graphs/histogram` respectively, for which ever TCP or UDP iteration of the experiment is done. If the tcp experiment is done the two files that will generate will be `graphs/lines/tcp_30ms_1.html` and `graphs/histogram/tcp_30ms_1.html`. 

The QUIC is in the `https://github.com/taimooralam/quic-go/example/echo/` in the thesis branch. Run `go run cli.go` and `go run serv.go` in two different terminals to launch the experiment. The QUIC experiment logs the values of the latency array in `quic/data/Log.txt` make sure that this file is removed before running the experiment to begin with fresh data by `sudo rm ~/experiment/quic/data/Log.txt`. Also make sure that the log file path in `serv.go`points correctly to the Log.txt file in the `quic/data` repository in this directory.

After the quic experiment is run, go to run `sudo python quic/graph.py data/Log.txt` to make plotly graphs of the QUIC protocol in the `graphs` directory. Make sure that the graph.py file has your plotly username and API key
