#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController
from time import sleep
import sys


protocol = sys.argv[1] if sys.argv[1] else "udp"
latency = str(float(sys.argv[2][:-2])/2)+sys.argv[2][-2:] if sys.argv[2] else "1ms"
loss = float(sys.argv[3])/2 if sys.argv[3] else 2


class SingleSwitchTopo(Topo):

    def build(self, n=2):
        switch = self.addSwitch('s1')
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
            # linkopts = dict(bw=10, delay='200us', loss=2, max_queue_size=1000, use_htb=True)
            linkopts = dict(delay=latency, loss=float(loss), use_htb=True)
            self.addLink( host, switch, **linkopts)
            # self.addLink(host, switch)


def perfTest():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo(n=2)
    net = Mininet(topo=topo, link=TCLink, controller=OVSController)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()

    h1, h2 = net.get('h1', 'h2')
    
    driver_command = "sudo python driver.py " + ' '.join(map(str,sys.argv[1:])) + " &"
    h1.cmd(driver_command)
    pid_h1 = int(h1.cmd('echo $!'))
    print driver_command + " at process number: {0}".format(pid_h1)

    sleep(3)
    car_command = "sudo python car.py " + ' '.join(map(str,sys.argv[1:])) + " &"
    h2.cmd(car_command)
    pid_h2 = int(h2.cmd('echo $!'))
    print car_command + " at process number: {0}".format(pid_h2)

    h2.cmd('wait', pid_h2)
    h1.cmd('wait', pid_h1)
    print pid_h1
    print pid_h2

    
    #h1.sendCmd('echo $$')
    #h2.sendCmd('echo $$')


    print"Slept 5"
    #net.iperf( (h1, h2) )
    #h2.waitOutput()
    #h1.waitOutput()


    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    perfTest()
