from mininet.topo import Topo
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections                                                                   
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import os
class MyTopo( Topo ):
    def __init__( self,x,y):
        
        Topo.__init__( self )

        switch=[]
        for i in xrange(0,x):
            switch.append(self.addSwitch('s'+str(i+1)))

        host=[]
        for j in xrange(0,y):
            host.append(self.addHost('h'+str(j+1), ip='10.0.0.'+str(j+1)))
          
        
        for i in xrange(len(switch)):
            for j in xrange(i+1,len(switch)):
                self.addLink(switch[i], switch[j])

        for i in xrange(len(switch)):
            try:
                self.addLink(host[(2*i)+1],switch[i],bw=1)
            except:
                c = 1
            try:
                self.addLink(host[(2*i)],switch[i],bw=2)
            except:
                c=1
        if y>2*x:
            for i in xrange(2*x,y):
                if (i+1)%2==0:
                    self.addLink(host[i],switch[x-1],bw=2)
                else:
                    self.addLink(host[i],switch[x-1],bw=1)


def  required(x,y):
    topo = MyTopo(x, y)
    net = Mininet(topo,host=CPULimitedHost, link=TCLink)
    net.start()

    for i in xrange(y):
        for j in xrange(y):
            if (i+1)%2==0 and (j+1)%2==1:
                net.nameToNode["h"+str(i+1)].cmd("iptables -A OUTPUT -o h"+str(i+1)+"-eth0 -d 10.0.0."+ str(j+1)+" -j DROP")
                net.nameToNode["h"+str(j+1)].cmd("iptables -A OUTPUT -o h"+str(j+1)+"-eth0 -d 10.0.0."+ str(i+1)+" -j DROP")
            elif (i+1)%2==1 and (j+1)%2==0:
                net.nameToNode["h"+str(i+1)].cmd("iptables -A OUTPUT -o h"+str(i+1)+"-eth0 -d 10.0.0."+ str(j+1)+" -j DROP")
                net.nameToNode["h"+str(j+1)].cmd("iptables -A OUTPUT -o h"+str(j+1)+"-eth0 -d 10.0.0."+ str(i+1)+" -j DROP")
    
    net.pingAll()
    try:
        
        print "Testing bandwidth between h1 and h3"
        h1, h3 = net.get('h1', 'h3')
        net.iperf((h1, h3))
    except:
        c=1
    try:
        
        print "Testing bandwidth between h1 and h3"
        h4, h2 = net.get('h2', 'h4')
        net.iperf((h2, h4))
    except:
        c=1

    
    dumpNodeConnections(net.switches)
    CLI(net)
    net.stop()


if __name__ == '__main__':
    x = int(raw_input("Enter Number of Switches: "))
    y = int(raw_input("Enter Number of Nodes   : "))
    topos = { 'mytopo': ( lambda: MyTopo(x, y) ) }
    required(x, y)
