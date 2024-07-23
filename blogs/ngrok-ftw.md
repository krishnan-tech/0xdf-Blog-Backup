# ngrok FTW

[ctf](/tags#ctf ) [ngrok](/tags#ngrok ) [tunnel](/tags#tunnel )  
  
May 12, 2020

ngrok FTW

![](https://0xdfimages.gitlab.io/img/ngrok-cover.png)

When I did the COVID-19 CTF, I needed a way to exploit one of the targets and
have it callback to me. I spent a lot of time trying to get socket reuse
shellcode to work, and if I had just tried a reverse shell payload, I would
have gotten there a lot sooner. But getting the connection back to me seemed
hard. I’d heard of ngrok for years as some kind of tunneling service. I’d seen
malware use it. But I never really looked into how it worked or how I could
use it, and it turns out to be super handy and really dead simple. This is
barely worth a blog post, and it won’t help with HackTheBox, but it’s just one
of those things that when you have a need for it, it’s so easy and useful.

## What Is It?

### From ngrok

In it’s own words:

> ngrok exposes local servers behind NATs and firewalls to the public internet
> over secure tunnels.

For this conversation a service can be anything - a webserver (http or https),
ssh, or even a nc listener.

### Why?

My home network, like most networks, is behind a router doing network address
translation, or NAT. My home network has IP addresses in the
[RFC-1918](https://tools.ietf.org/html/rfc1918) defined ranges for private
internets. So when my computer sends a request out, the source address is
something like 192.168.1.100. When it gets to the router, the router replaces
that source address with its public IP, and records in a NAT table the source
port and the original IP. When the response comes back, it looks up the
destination port in the table, and replaces the destination IP address with
the private IP of my computer.

![image-20200512134448751](https://0xdfimages.gitlab.io/img/image-20200512134448751.png)

This all works well for my initiating contact with services on the internet,
but it fails when something outside my router wants to initiate contact with a
service inside my private network. I can go into the router settings and
configure a port to forward to a specific host in my network, but that is a
pain at best, and not possible when in a hotel or coffee shop.

### ngrok

ngrok has two components:

  * A service running in the cloud.
  * A binary that runs on my local system.

When I start the binary on my system, I give it the kind of traffic I’m
looking to handle, and where the service is. It then creates a connect to the
server in the cloud, and stands up a tunnel. Now, anyone on the internet can
connect to the listener in the cloud, and it will tunnel through the binary on
my host, and to the named service.

![image-20200512135819467](https://0xdfimages.gitlab.io/img/image-20200512135819467.png)

In the image above, `ngrok` creates a tunnels so that any traffic to
`http://023504c7.ngrok.io` will be tunnels through my computer and send to
`http://192.168.1.100`.

In a CTF context, if there’s a target on the internet that I want to exploit,
and I want it to call back to me, I can use `ngrok` to create a tunnel so that
it can connect to me.

## Using ngrok

### Installation

Instructions to get up and running are [here](https://dashboard.ngrok.com/get-
started/setup). You’ll need to create an account. Then download the binary,
connect your account with the command they give you, and you’re ready to go.

### Run It

Let’s say I’m doing the [covid CTF](/2020/05/04/covid-19-ctf-
covidscammers.html#exploit2-for-shell) and I want my shellcode to connect back
to me. I can run something like `ngrok tcp 4343`, and it will fill my terminal
with this:

![image-20200512153949257](https://0xdfimages.gitlab.io/img/image-20200512153949257.png)

Now I start `nc -lnvp 4343`, and have my shellcode connect to 0.tcp.ngrok.io
on port 16434, and it will arrive at my listener.

## Non-CTF Applications

### For Red

`ngrok` might be a nice utility for getting around NAT and other tunneling
situations. It’s probably relatively good for obscuring your identity, unless
your target is going to work with law enforcement to get connection
information from Ngrok. That said, it might have some utility as a C2 channel,
but I suspect it is more likely to stand out in logs.

### For Blue

I’d suggest at least doing a survey of your logs to see if Ngrok is in regular
use by your business units. There is unlikely to be a good reason why your
organization should be bypassing firewalls with Ngrok, when other solutions
like VPN can be made available to get people from outside the firewall to
internal applications more securely.

On the other hand, I’ve been aware of actual threats using Ngrok for C2 for
years. Here are some recent examples:

  * [Sly malware author hides cryptomining botnet behind ever-shifting proxy service [13 Sept 2018]](https://www.zdnet.com/article/sly-malware-author-hides-cryptomining-botnet-behind-ever-shifting-proxy-service/)
  * [A Secure Tunnel to Deliver LokiBot [31 May 2019]](https://fortiguard.com/resources/threat-brief/2019/05/31/fortiguard-threat-intelligence-brief-may-31-2019)
  * [Virus Bulletin research discovers new Lord exploit kit [5 Aug 2019]](https://www.virusbulletin.com/blog/2019/08/virus-bulletin-researcher-discovers-new-lord-exploit-kit/)
  * [Fraudsters cloak credit card skimmer with fake content delivery network, ngrok server [26 Feb 2020]](https://blog.malwarebytes.com/threat-analysis/2020/02/fraudsters-cloak-credit-card-skimmer-with-fake-content-delivery-network-ngrok-server/)

Connections to subdomains of ngrok[.]io would be blocking connections going
into someone else’s network, obsecured by Ngrok. This seems like a reasonable
thing to block or at least log.

You may also want to block the connection from the `ngrok` binary creating the
tunnel. When the tunnel is created, I observed a DNS resolution of
`tunnel.us.ngrok.com`, followed by a TLS connection to that IP on TCP port
443.

![image-20200512180824203](https://0xdfimages.gitlab.io/img/image-20200512180824203.png)

Traffic continues to to come in over this connection, which is held open, so
this would also come up on any hunt rules for long lifetime connections.

[](/2020/05/12/ngrok-ftw.html)

