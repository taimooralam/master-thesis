This module contains the two programs that act at the sensor (or filesystem) periphery at the vehicle and the operator end-point in a teleoperated driving scenario.

`pcd_read <directory>` iteratively read .pcd files from the source directory, reads them, compresses them using PCL Octree Compression and forwards them using a named pipe to QUIC GO client that then transmits the data over to the network using QUIC to the operator end-point.

`pcd_write` on the other hand, reads the compressed data from the QUIC server once it has arrived that operator end-point using named pipe, decompresses it and saves it to the `data` directory.

To run the code, go to build directory in both `pcd_read` and `pcd_write` and run `make`. Pcl and boost need to be installed as a prerequisite for this to build properly.
