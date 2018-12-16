#!/usr/bin/python

from  mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class SingleSwitchTopo(Topo): #Topo is the base class for mininet topologies
    "Single Switch Connected to n hosts"
    def build(self, n=2):   # the method to override in your topology class,  constructor topologies will be passed to it automatically
        switch = self.addSwitch('s1') #adds a switch to the topology and returns the switch name
        #python's range generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h+1)) #adds a host to the topolgy and returns the host name
            self.addLink(host, switch) #adds a birdirectional link to the topology, returns a link key, links are bidirectional unles noted otherwise


def simpleTest():
    "Create and test a simple network"
    topo = SingleSwitchTopo(n=4)
    net = Mininet(topo) #main class to create an manage a network
    net.start() #starts your netwowrk
    print "Duming host connections"
    dumpNodeConnections(net.hosts) #dumps connections to/from a network
    print "Testing Network Connectivity"
    net.pingAll() #tests connection by having all nodes ping each other
    net.stop() #stops your netwrk

if __name__ == '__main__':
    #Tell mininet to print useful information
    setLogLevel('info') #sets log levels to info, debug or outut
    simpleTest()
