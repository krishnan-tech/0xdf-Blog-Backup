# Pivoting off Phishing Domain

[forensics](/tags#forensics ) [threat-intel](/tags#threat-intel )
[phishing](/tags#phishing ) [riskiq](/tags#riskiq ) [maltego](/tags#maltego )
[youtube](/tags#youtube )  
  
Aug 27, 2021

Pivoting off Phishing Domain

![cascade](https://0xdfimages.gitlab.io/img/image-20210827040428323.png)

John Hammond YouTube channel is full of neat stuff, from CTF solutions to real
malware analysis. Recently, he did an analysis of an email with an HTML
attachment which presented as a fake Microsoft login page. When a victim
enters creds, the page would send them to www.hurleyauctions[.]us, and
redirect the user to an actual Microsoft Outlook site. John looked at bit at
the registration information on the domain, but I wanted to dive a bit deeper,
specifically using RiskIQ and Maltego.

For Background, here’s [John’s
video](https://www.youtube.com/watch?v=YWarpd4G5YM):

## Tools

Going beyond what John looked into, I’ll introduce two tools.

### RiskIQ

When I worked in a threat-intel shop, RiskIQ was one of my favorite data
sources / tools to use. They pull together all kinds of information, but the
two parts I found most useful were the domain registration information and the
passive DNS data. Passive DNS is data collected from across the internet
showing DNS requests and responses. It can serve as a good history for what
kinds of activity occurred on a domain / IP.

The free account is significantly limited vs what I used to have with an
enterprise license, but it still does some good stuff.

### Maltego

Maltego is a tool for producing graphs. The power comes in the transforms.
They connect to different data source APIs and make connections for you. Let’s
say you have ten related domain names. You can select them all, and then use
the PassiveTotal (RiskIQ) Get Passive DNS with Time transform, and it will
query RiskIQ, get all the DNS resolutions for each of the ten domains, as well
as the first and last seen dates, and put those nodes onto the graphs with
arrows from the domains to each IP they resolve to. It’s incredibly powerful
for quickly pivoting using many different data sources.

It’s relatively inexpensive for a corporate tool (still not something I’m
going to buy on my own), and there’s a free version that limits how many nodes
can add to a graph and how many results can come back from a single transform.

## Domain Pivoting

### WhoIs

On finding the domain www.hurleyauctions[.]us, Jonh looked at the WhoIs
information and noted that it had a “real” information (as opposed to privacy
shielded):

    
    
    $ whois hurleyauctions.us
    Domain Name: hurleyauctions.us
    Registry Domain ID: D1E32ACF651C44F3C828FC9111A6EEDEF-NSR
    Registrar WHOIS Server: whois.namecheap.com
    Registrar URL: http://www.namecheap.com
    Updated Date: 2021-07-06T12:09:58Z
    Creation Date: 2021-07-01T12:09:53Z
    Registry Expiry Date: 2022-07-01T12:09:53Z
    Registrar: NameCheap, Inc.
    Registrar IANA ID: 1068
    Registrar Abuse Contact Email: abuse@namecheap.com
    Registrar Abuse Contact Phone: +1.6613102107
    Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
    Registry Registrant ID: C248C372558784C4D9CF845CE1D4F0422-NSR
    Registrant Name: Karen Abrams
    Registrant Organization:
    Registrant Street: 10755 Ve10755 Venice Blvd
    Registrant Street:
    Registrant Street:
    Registrant City: Los Angeles
    Registrant State/Province: NY
    Registrant Postal Code: 90034
    Registrant Country: US
    Registrant Phone: +1.3109454167
    Registrant Phone Ext:
    Registrant Fax:
    Registrant Fax Ext:
    Registrant Email: alomamrs@gmail.com
    Registrant Application Purpose: P1
    Registrant Nexus Category: C11
    Registry Admin ID: C336A6E3274E148B9825D5ADB91069FD0-NSR
    Admin Name: Karen Abrams
    Admin Organization:
    Admin Street: 10755 Ve10755 Venice Blvd
    Admin Street:
    Admin Street:
    Admin City: Los Angeles
    Admin State/Province: NY
    Admin Postal Code: 90034
    Admin Country: US
    Admin Phone: +1.3109454167
    Admin Phone Ext:
    Admin Fax:
    Admin Fax Ext:
    Admin Email: alomamrs@gmail.com
    Registry Tech ID: CD20F8910EB1F43CC8A4789C1C6D095F8-NSR
    Tech Name: Karen Abrams
    Tech Organization:
    Tech Street: 10755 Ve10755 Venice Blvd
    Tech Street:
    Tech Street:
    Tech City: Los Angeles
    Tech State/Province: NY
    Tech Postal Code: 90034
    Tech Country: US
    Tech Phone: +1.3109454167
    Tech Phone Ext:
    Tech Fax:
    Tech Fax Ext:
    Tech Email: alomamrs@gmail.com
    Name Server: dns1.registrar-servers.com
    Name Server: dns2.registrar-servers.com
    DNSSEC: unsigned
    URL of the ICANN Whois Inaccuracy Complaint Form: https://www.icann.org/wicf/
    

The name Karen Abrams, and the email `alomamrs@gmail.com` are interesting.
There’s an address there, though with some typos in it. If I assume that’s
10755 Venice Blvd, Google Street View takes me
[here](https://www.google.com/maps/place/RDL+Inc/@34.0180452,-118.4083911,3a,75y,324.33h,90.46t/data=!3m6!1e1!3m4!1surX22mkeR0LLTczEKDun0A!2e0!7i16384!8i8192!4m13!1m7!3m6!1s0x80c2ba30e6f3a901:0x452b3ec98dbb55ea!2s10755+Venice+Blvd.,+Los+Angeles,+CA+90034!3b1!8m2!3d34.0186243!4d-118.4087797!3m4!1s0x80c2ba30e6d1a071:0xc5d9efd71318542f!8m2!3d34.0186914!4d-118.4086919):

![image-20210825205512470](https://0xdfimages.gitlab.io/img/image-20210825205512470.png)

Looks like it belongs to RLD Inc, and also that, at the time of the picture,
the building may have been for lease? Regardless, pretty high chance that
address isn’t real. There’s a phone number as well, 310-945-4176, which is a
California area code.

### RiskIQ

Dropping that domain into RiskIQ, it provides a bunch of tabs with
information. The “Resolutions” tab show a history of the passive DNS data
associated with the domain:

![image-20210825210228184](https://0xdfimages.gitlab.io/img/image-20210825210228184.png)

In the free version, there’s almost certainly a limit on how far it goes back.
In previous jobs where I had a paid subscription, it went back for years.

That is the IP that John noticed in the video. Clicking on it gives three
domains that have resolved to that IP:

![image-20210825210340919](https://0xdfimages.gitlab.io/img/image-20210825210340919.png)

Interestingly, more subdomains of hurleyauctions[.]us.

Going back to the page for www.hurleyauctions[.]us, the “WhoIs” tab has
similar information to what I pulled above:

![image-20210825210504343](https://0xdfimages.gitlab.io/img/image-20210825210504343.png)

But here is where the fun starts, and where I can go beyond what John looked
at in the video. Clicking on the email address, it brings up other domains
registered by that address:

![image-20210825210609983](https://0xdfimages.gitlab.io/img/image-20210825210609983.png)

Three of them have been tagged as Phishing and Blocklist, which is
interesting.

From here, I can start to build a list of suspected indicators associated with
this threat actor, including domains, IPs, and emails.

## Scaling

At this point, it’s time to drop this domain into Maltego. I recorded this as
a YouTube video:

At the end, I have this nice graph of activity and associated indicators:

[![image-20210827040428323](https://0xdfimages.gitlab.io/img/image-20210827040428323.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20210827040428323.png)

That’s nine new domains, their IPs, and some associated malware samples.

[](/2021/08/27/pivoting-off-phishing-domain.html)

