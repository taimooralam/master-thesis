The video streaming module reads data from a source file called `video.mp4` and  divides it into frames. Each of these frames gets a `frame_number` and a `timestamp`. The frame is then divided into `chunks`, each of the chunks gets its `chunk_number`. Each chunk is then sent to the operator `op.py` from the vehicle `vehicle.py`. On the operator end-point point, the chunks are reconstructed to form the associated frame and save to a video file called `out.mp4`. Length of the chunk and the frame are added to both frame and chunks so that frames with any missing data can be discarded.

`vehicle.py` acts as the UDP client, reads the file with `frames` along with their numbers: `frame_number`. `op.py` acts as the UDP server, reader the chunks and combines them into frames and then stores the frames in a file. `video.mp4` is the source file while `out.mp4` is the destination file.

The program was developed and run on Macbook Air (MacOS Mojave) using PyCharm IDE.

Change `config.py` for IP and port number as well as a single chunk size for the program to work. 
