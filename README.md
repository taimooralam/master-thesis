# master-thesis
## Cross-sensor synchronisation in Teleoperated Driving

This repository contains the experiment and protytpe for master thesis at TUM, chair of Connected Mobility under the advisory of Stefan Neumeier and the supervision of Prof Joerg Ott.

The experiment contains the experimental code to test the one-way latency of the three transport layer protocols: QUIC, TCP and UDP. A mininet simulator is run with a base latency of 30ms and packet loss of 1% between two hosts and TT is calculated with 50000 packets being sent from one host to the other over each of the three protocols. Some details are mentioned in the README files inside the experiment folder, while other's are mentioned in the thesis document.

The prototype folder contains two modules: video transmission and point-cloud transission. The video transmission module tranmits motion JPEG data in python from one end-point to another over UDP. Frames are read from file, they are then timestamped, broken into chunks with each chunk being transmitted in one packet. The point-cloud transmission module reads data from .pcd files compresses it using PCL library and transmits it over QUIC-Go from one end-point to another. At the receiving end-point it is again passed on to a PCL decompression using named-pipes. The PCL decompression module then write the data to the disk. QUIC-Go transport portion of the point-cloud streaming can be found [here](https://github.com/taimooralam/quic-go/tree/thesis/example/echo).
