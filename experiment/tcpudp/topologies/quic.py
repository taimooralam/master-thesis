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


protocol = sys.argv[1] if sys.argv[1] else "quic"
latency = str(float(sys.argv[2][:-2])/2)+sys.argv[2][-2:] if sys.argv[2] else "27ms"
loss = float(sys.argv[3])/2 if sys.argv[3] else 0.5


class SingleSwitchTopo(Topo):

    def build(self, n=2):
        switch = self.addSwitch('s1')
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
            # linkopts = dict(bw=10, delay='200us', loss=2, max_queue_size=1000, use_htb=True)
            linkopts = dict(delay=latency, max_queue_size=3000, loss=float(loss), use_htb=True)
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
    
    driver_command = "go run /home/alam/code/godir/src/github.com/lucas-clemente/quic-go/example/echo/serv.go &"
    h1.cmd(driver_command)
    string_h1 = h1.cmd('echo $!')
    print string_h1
    pid_h1 = int(string_h1)
    print driver_command + " at process number: {0}".format(pid_h1)

    sleep(1)
    car_command = "go run /home/alam/code/godir/src/github.com/lucas-clemente/quic-go/example/echo/cli.go &"
    h2.cmd(car_command)
    string_h2 = h2.cmd('echo $!')
    print string_h2
    pid_h2 = int(string_h2)
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
