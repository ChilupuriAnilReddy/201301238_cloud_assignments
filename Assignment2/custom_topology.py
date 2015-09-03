from mininet.topo import Topo
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections                                                                   
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
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
                self.addLink(switch[i],host[(2*i)+1])
            except:
                c = 1
            try:
                self.addLink(switch[i],host[(2*i)])
            except:
                c=1
        if y>2*x:
            for i in xrange(2*x,y):
                self.addLink(switch[x-1],host[i])


def  required(x,y):
    topo = MyTopo(x, y)
    net = Mininet(topo)
    net.start()
    #net.addController('c0', controller=RemoteController,ip="127.0.0.1",port=6633)
    for i in xrange(y):
        for j in xrange(y):
            if (i+1)%2==0 and (j+1)%2==1:
                net.nameToNode["h"+str(i+1)].cmd("iptables -A OUTPUT -o h"+str(i+1)+"-eth0 -d 10.0.0."+ str(j+1)+" -j DROP")
                net.nameToNode["h"+str(j+1)].cmd("iptables -A OUTPUT -o h"+str(j+1)+"-eth0 -d 10.0.0."+ str(i+1)+" -j DROP")
            elif (i+1)%2==1 and (j+1)%2==0:
                net.nameToNode["h"+str(i+1)].cmd("iptables -A OUTPUT -o h"+str(i+1)+"-eth0 -d 10.0.0."+ str(j+1)+" -j DROP")
                net.nameToNode["h"+str(j+1)].cmd("iptables -A OUTPUT -o h"+str(j+1)+"-eth0 -d 10.0.0."+ str(i+1)+" -j DROP")
    dumpNodeConnections(net.switches)
    CLI(net)


if __name__ == '__main__':
    x = int(raw_input("Enter Number of Switches: "))
    y = int(raw_input("Enter Number of Nodes   : "))
    topos = { 'mytopo': ( lambda: MyTopo(x, y) ) }
    required(x, y)