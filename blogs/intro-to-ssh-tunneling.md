# Intro to SSH Tunneling

[hackthebox](/tags#hackthebox ) [ssh](/tags#ssh ) [tunnel](/tags#tunnel )  
  
Jun 10, 2018

Intro to SSH Tunneling

I came across a situation on a [htb](https://www.hackthebox.eu) box today
where I needed IE to get a really slow, older, OWA page to fully function and
do what I needed to do. I had a Windows vm around, but it was relatively
isolated, and no able to talk directly to my kali vm. SSH tunneling turned out
to be the easiest solution here, and since I get questions about SSH tunneling
all the time, I figured it would be good to write up a short description.

## Current Architecture

I’d done most of my CTF-ing from a kali vm, hosted in VirtualBox, with bridged
networking onto my local lan. My host OS is Ubuntu. I also have a malware
analysis set up in VMWare (I need to migrate things one way or the other, but
haven’t found time). This mawlare set-up is a Linux VM and a Windows 10 VM,
both are on a private virtual network. The Linux VM has a second network
interface that is bridged to my local lan. Here’s a diagram:
![](https://0xdfimages.gitlab.io/img/net-diagram.png)

## SSH tunneling - background

When it comes to SSH tunneling, there are three basic options to play with:

  * `-L [local port]:[remote ip]:[remote port]` \- Listen on `[local port] on the local host`, and send any traffic that port receives through the ssh tunnel, and then forwarded by the ssh remote host to `[remote ip]:[remote port]`
  * `-R [remote port]:[dest ip]:[dest port]` \- Listen on `[remote port]` on the remote host being sshed to, and forward and traffic through the ssh tunnel to the local host, which forwards it to `[dest ip]:[dest port]`
    * Note, this has to be enabled in the remote host’s config, and is typically off by default
  * `-D [port]` \- Listen locally on `[port]`, and act as a SOCKS proxy, delivering traffic to the other end of the connection.

## SSH Tunneling - in practice

So in this case, we’ll solve the problem with two tunnels, both using `-L`:

  * Using `putty`, ssh from the Windows malware host into the REMnux Linux host, with an equivalent of `-L 443:localhost:4443`
  * Using `ssh`, ssh from the REMnux host to the kali host, using `-L 4443:10.10.10.X:443`

### Windows –> REMnux

In putty, I’ll use the GUI to set up the tunnels, as opposed to the command
line switch.

Under “Session” –> “Connection” –> “SSH” –> “Tunnels”, there’s a section
entitled “Add new forwarded port:”. Below there, enter `443` for “Source port”
and `localhost:4443` for “Destination”. Leave the radio buttons on “Local” and
“Auto”, and hit the “Add” button. It’ll look like this:
![](https://0xdfimages.gitlab.io/img/putty-tunnel.png)

Then ssh into the host as normal.

This creates a listener on the Windows host on port 443, that will forward any
traffic it receives to the REMnux host, which will take it and send it to
localhost port 4443.

### REMnux –> Kali

On REMnux, I’ll run the command `ssh root@10.1.1.190 -L 4443:10.10.10.X:443`
to connect to the Kali box. This creates a listener on port 4443, that takes
any traffic it receives, and sends it through the ssh tunnel to the Kali box,
who will take it and forward it to the HTB target (10.10.10.X, final octet
hidden because this box is not yet retired) on port 443.

### Visit the site

Now, I can open IE on the Windows host, and visit `https://127.0.0.1/` and see
the site from the HTB target. Why? Because the web browser sends it’s request
to localhost port 443.

Putty is listening on Windows host 443, and passes it to REMnux (green
tunnel), which forwards it to itself on port 4443.

ssh is listening on port 4443, and passed it to Kali (orange tunnel), and kali
forwards it to the htb host.

The responses are tunneled automatically.
![](https://0xdfimages.gitlab.io/img/network-alltun.png)

## Alternative solution

One alternative I could have done was the following two tunnels:

  * Win to REMnux with `-L 8080:localhost:8080`
  * REMnux to Kali with `-D 8080`

Then configure my browser to use 127.0.0.1:8080 as a SOCKS proxy. Then I could
just visit `https://10.10.10.X/` and the browser would first proxy the traffic
through the kali box, and then visit the site.

## Summary

Understanding how to use tunnels is critical if you are ever trying to move
deeper into a network. Othertimes, you gain a foothold on a host, and can ssh
in, and would like to access a service like a database or vnc that’s only
listening on localhost. SSH tunneling is cool tool to have.

[](/2018/06/10/intro-to-ssh-tunneling.html)

