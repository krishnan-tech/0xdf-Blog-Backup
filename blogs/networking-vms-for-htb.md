# Networking VMs for HTB

[ctf](/tags#ctf ) [hackthebox](/tags#hackthebox )
[configuration](/tags#configuration ) [virtual-machine](/tags#virtual-machine
) [parrot-os](/tags#parrot-os )  
  
May 4, 2021

Networking VMs for HTB

![VM Config](https://0xdfimages.gitlab.io/img/vms-cover.png)

When doing HTB or other CTFs, I typically run from a Linux VM (formerly Kali,
lately Parrot), but I also need to use a Windows VM from time to time as well.
Some of those times, I’ll need to interact with the HTB machines over the VPN
from the Windows host, and it’s always a bit of a pain to turn off the VPN in
the Linux VM, and then turn it on from Windows. This post shows how I
configured my VMs so that Windows traffic can route through the Linux VM to
HTB.

## Network

I’ve configured my VMs such that each has a second NIC that they can use to
talk to each other. In VirtualBox, it looks like this:

![image-20210430133215223](https://0xdfimages.gitlab.io/img/image-20210430133215223.png)

Then I gave each box a static IP on that interface. With the VPN connected,
the network looks like:

[![](https://0xdfimages.gitlab.io/img/VMConfig.png)_Click for full size
image_](https://0xdfimages.gitlab.io/img/VMConfig.png)

If you’re just setting this up, assign the IPs to the VM network and then make
sure you can ping each box from the other.

## Configuration

### Enable Routing in Parrot

Linux has a setting that’s stored in `/proc/sys/net/ipv4/ip_forward`. If that
is set to 1, the OS will allow routing of packets. If it’s set to 0, it will
only process packets destined for itself.

To change this until the next reboot:

    
    
    #echo 1 > /proc/sys/net/ipv4/ip_forward
    

To change it persistently:

    
    
    #sysctl -w net.ipv4.ip_forward=1
    

### Add Route in Windows

In Window, I’ll add a route for HTB:

    
    
    C:\Windows\system32>route add 10.10.10.0/23 MASK 255.255.255.0 192.168.223.110
     OK!
    

This says that for any destination on 10.10.10.0.23, the packet should route
to 192.168.223.110, the Parrot VM.

### Enable NAT

It’s tempting to think this is enough. It is enough to get packets from
Windows to HTB. But when the packet reaches a HTB machine, the source address
will be 192.168.223.120. When it tries to send a packet back, the destination
IP will be 192.168.223.120, and it doesn’t know how to get it there. The
packet will go to the router, 10.10.10.2, but that packet will drop it as non-
routable.

I’ll add an `iptables` rule that will look at any packet with a source IP in
192.168.223.0/24 that’s going out on tun0, and use the NAT process to re-write
the source address as my tun0 IP. Then, when the packet reached HTB, it will
send back to the tun0 IP on my Linux VM, which it can do over the VPN without
issue. When the Linux VM receives that packet, it will check the NAT table and
replace the destination address with the Windows IP 192.168.223.120, and
forward it along.

The command is:

    
    
    #iptables -t nat -A POSTROUTING -s 192.168.223.0/24 -o tun0 -j MASQUERADE
    

If there’s any kind of `iptables` rules blocking, you may also need a rule or
two to allow the traffic between adapters, but I believe by default this is
open.

To make sure this rule survives reboot, I’ll install `iptables-persistent`,
and then use `iptables-save > /etc/iptables/rules.v4` to save the rules so
that they get loaded at boot.

## HTB To Windows

At this point, I’ve got everything covered except if there were a case where I
wanted a connection to come from a HTB machine back to my Windows OS. The IP
tables rules I have set up manage existing connections using the NAT setup,
but any SYN packets coming in will end at Parrot. I can’t quite come up with
why I would need to do this, but it is still possible.

The easiest way to do this would be using a SOCAT tunnel:

    
    
    # socat TCP-LISTEN:[port],fork TCP:192.168.223.120:[port]
    

Standing that up would forward any incoming traffic on a given port to the
Windows VM on the given port (obviously add your own Windows VM IP in there).

If I wanted something more persistent (ie, forever forward this port to
Windows), I could configure `iptables` to handle that.

[](/2021/05/04/networking-vms-for-htb.html)

