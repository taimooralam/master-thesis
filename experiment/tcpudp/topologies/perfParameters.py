#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts"
    def build(self, n=2):
        switch = self.addSwitch('s1')
        for h in range(n):
            #Each hosts gets 50%/n of system CPU
            host = self.addHost('h%s'%(h+1), CPU=.5/n)
            #10 MBps, 5ms delay, 2%loss, 1000 packet queue
            self.addLink(host, switch, bw=10, delay='5ms', loss = 2, max_queue_size = 1000 , use_htb=True)

def perfTest():
    "Create a network and run simple performance test"
    topo = SingleSwitchTopo(n=4)
    net = Mininet(topo = topo, host = CPULimitedHost , link = TCLink)
    net.start()

    print "Dumping Host Connections"
    dumpNodeConnections(net.hosts)

    print "Testing network Connectivity"
    h1, h4 = net.get('h1' , 'h4')
    net.iperf((h1, h4))
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    perfTest()
