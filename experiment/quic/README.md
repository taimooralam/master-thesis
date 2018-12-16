The repository for the QUIC experiment points at https://github.com/taimooralam/quic-go/tree/thesis/example/echo.

(Before running the QUIC experiment `sudo rm data/Log.txt`)

Go that repository and run `go run cli.go` and `go run serv.go` in two different terminals. The `cli.go` file shall send 50000 packets to the `serv.go` file and the latencies shall be stored in this repository in `experiment/quic/data/Log.txt`.

Then in this repository run sudo python graph.py and it will plot a graph of quic in `graphs/lines` and `graphs/histograms`.
