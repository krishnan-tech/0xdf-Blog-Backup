# Flare-On 2019: DNS Chess

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-dnschess](/tags#flare-
on-dnschess ) [peda](/tags#peda ) [gdb](/tags#gdb )
[wireshark](/tags#wireshark ) [python](/tags#python ) [dns](/tags#dns )
[ida](/tags#ida ) [reverse-engineering](/tags#reverse-engineering )  
  
Oct 4, 2019

  * [[1] Memecat Battlestation](/flare-on-2019/memecat-battlestation.html)
  * [[2] Overlong](/flare-on-2019/overlong.html)
  * [[3] Flarebear](/flare-on-2019/flarebear.html)
  * [4] DNS Chess
  * [[5] demo](/flare-on-2019/demo.html)
  * [[6] bmphide](/flare-on-2019/bmphide.html)
  * [[7] wopr](/flare-on-2019/wopr.html)

![](https://0xdfimages.gitlab.io/img/flare2019-4-cover.png)

DNS Chess was really fun. I’m given a pcap, and elf executable, and an elf
shared library. The two binaries form a game of chess, where commands are sent
to an AI over DNS. I’ll need to figure out how to spoof valid moves by
reversing the binary, and then use valid moves to win the game.

## Challenge

> Some suspicious network traffic led us to this unauthorized chess program
> running on an Ubuntu desktop. This appears to be the work of cyberspace
> computer hackers. You’ll need to make the right moves to solve this one.
> Good luck!

I’m given two 64-bit ELFs and a pcap:

    
    
    $ file *
    capture.pcap: pcap capture file, microsecond ts (little-endian) - version 2.4 (Ethernet, capture length 262144)
    ChessAI.so:   ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, BuildID[sha1]=ed3bd3fae8d4a8e27e4565f31c9af58231319190, stripped
    ChessUI:      ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=c30ec8b70e255aec7c93eb80321e4eab7bd52b3f, for GNU/Linux 3.2.0, stripped
    Message.txt:  ASCII text
    

## Running It

Running it opens a chess game:

![1567262377880](https://0xdfimages.gitlab.io/img/1567262377880.png)

Any move I try seems to result in:

![1567262401934](https://0xdfimages.gitlab.io/img/1567262401934.png)

## PCAP

### Sample

On opening `capture.pcap`, I find 80 UDP DNS packets, 40 requests and 40
responses. The client is 192.168.122.1, and the DNS server is 192.168.122.29.
There are 40 different chess moves represented:

![1567430275705](https://0xdfimages.gitlab.io/img/1567430275705.png)

### Sniffing

When I make a move, if I have wireshark running I can see a DNS request going
out of the same format, the domain representing the move I just made. The
response that comes back is that no record was found. This is likely why the
opponent resigns.

I can update my `/etc/hosts` file such that a response does come back. There’s
no wildcarding in the `hosts` file, so I’ll have to set each move
individually. I set a specific pawn move to 127.0.0.1, and then make that
move. The AI resigns. I try a handful of the moves from the pcap. Still,
everything results in the AI resigning. I’m going to have to reverse this a
bit.

## RE

### Overview of Two Binaries

I’ve got two files to look at, `ChessUI` and `ChessAI.so`. Giving both a look
with `readelf -s` to see what functions they implement, import, and export, I
see `ChessAI.so` has a couple interesting bits:

    
    
    $ readelf -s ChessAI.so 
    
    Symbol table '.dynsym' contains 13 entries:
       Num:    Value          Size Type    Bind   Vis      Ndx Name
         0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
         1: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND _ITM_deregisterTMCloneTab
         2: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strcpy@GLIBC_2.2.5 (2)
         3: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __stack_chk_fail@GLIBC_2.4 (3)
         4: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND gethostbyname@GLIBC_2.2.5 (2)
         5: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND __gmon_start__
         6: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strcat@GLIBC_2.2.5 (2)
         7: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND _ITM_registerTMCloneTable
         8: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND sleep@GLIBC_2.2.5 (2)
         9: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND __cxa_finalize@GLIBC_2.2.5 (2)
        10: 00000000000011c1   479 FUNC    GLOBAL DEFAULT   12 getNextMove
        11: 00000000000013a0    13 FUNC    GLOBAL DEFAULT   12 getAiName
        12: 00000000000013ad    13 FUNC    GLOBAL DEFAULT   12 getAiGreeting
    

It exports the function `getNextMove`. It also imports `gethostbyname` from
libc, which is likely making the DNS calls. I’m going to start here.

### Debugging Tips

While static analysis is great, it’s really useful for me to watch an example
work its way through the code by debugging. Debugging these binaries is a bit
tricky because they are stripped and use PIE and therefore the offsets move
around in memory space.

To debug `getNextMove`, I first found the offset of 0x11c1 in the output of
`readelf` above.

Now I’ll start the game, `./ChessUI`. Next I’ll attach `gdb` (I use
[peda](https://github.com/longld/peda) as it makes it more readable):

    
    
    # ./ChessUI & gdb -q -p $(pidof ChessUI)
    [4] 23168
    20014: No such file or directory.
    Attaching to process 23168
    [New LWP 23171]
    [New LWP 23172]
    [New LWP 23174]
    [New LWP 23175]
    [Thread debugging using libthread_db enabled]
    Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
    [----------------------------------registers-----------------------------------]
    RAX: 0x55e6f37ed360 --> 0x55e6f37edeb8 --> 0x0 
    RBX: 0x55e6f38d6070 --> 0x55e6f37ed360 --> 0x55e6f37edeb8 --> 0x0 
    RCX: 0x55e6f38d6070 --> 0x55e6f37ed360 --> 0x55e6f37edeb8 --> 0x0 
    RDX: 0x26e6 
    RSI: 0x55e6f38d6120 --> 0x55e6f38d60c8 --> 0x0 
    RDI: 0x55e6f38d6070 --> 0x55e6f37ed360 --> 0x55e6f37edeb8 --> 0x0 
    RBP: 0x7ffd37e52158 --> 0x55e6f38d60c8 --> 0x0 
    RSP: 0x7ffd37e52070 --> 0x55e6f38d6070 --> 0x55e6f37ed360 --> 0x55e6f37edeb8 --> 0x0 
    RIP: 0x7fd1ec9abb54 (mov    r8,rdi)
    R8 : 0x55e6f37ede60 --> 0x55e6f38d6070 --> 0x55e6f37ed360 --> 0x55e6f37edeb8 --> 0x0 
    R9 : 0x29e4 
    R10: 0x0 
    R11: 0x2a ('*')
    R12: 0x55e6f37edeb8 --> 0x0 
    R13: 0x55e6f37edfa0 --> 0x55e6f37edfb0 --> 0x55e6f37edf90 --> 0x55e6f37edf28 --> 0x0 
    R14: 0x55e6f37ed100 --> 0x7fd1ec9abde0 (test   rdi,rdi)
    R15: 0x55e6f37ed100 --> 0x7fd1ec9abde0 (test   rdi,rdi)
    EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
    [-------------------------------------code-------------------------------------]
       0x7fd1ec9abb4b:      jmp    0x7fd1ec9abb5a
       0x7fd1ec9abb4d:      nop    DWORD PTR [rax]
       0x7fd1ec9abb50:      mov    r9d,DWORD PTR [rax+0x1c]
    => 0x7fd1ec9abb54:      mov    r8,rdi
       0x7fd1ec9abb57:      mov    rdi,rax
       0x7fd1ec9abb5a:      cmp    r9d,edx
       0x7fd1ec9abb5d:      jg     0x7fd1ec9abbf0
       0x7fd1ec9abb63:      mov    rax,QWORD PTR [rdi]
    [------------------------------------stack-------------------------------------]
    0000| 0x7ffd37e52070 --> 0x55e6f38d6070 --> 0x55e6f37ed360 --> 0x55e6f37edeb8 --> 0x0 
    0008| 0x7ffd37e52078 --> 0x9b581f95deeee600 
    0016| 0x7ffd37e52080 --> 0x55e6f37ed100 --> 0x7fd1ec9abde0 (test   rdi,rdi)
    0024| 0x7ffd37e52088 --> 0x7fd1ec9ac720 (mov    QWORD PTR [rbp+0x0],0x0)
    0032| 0x7ffd37e52090 --> 0x7 
    0040| 0x7ffd37e52098 --> 0x2000000030 ('0')
    0048| 0x7ffd37e520a0 --> 0x17 
    0056| 0x7ffd37e520a8 --> 0x29e4 
    [------------------------------------------------------------------------------]
    Legend: code, data, rodata, value
    0x00007fd1ec9abb54 in ?? () from /lib/x86_64-linux-gnu/libcairo.so.2
    

I can now reference the function to put a breakpoint:

    
    
    gdb-peda$ b *getNextMove+4
    Breakpoint 1 at 0x7fd1e9ae91c5
    

If `gdb` can’t recognize the function name (this will be the case if I wade
into the main binary), the following steps will work. First, I’ll get the
offset of 0x11c1 to the function from the `readelf` output above.

Now I need to find where `ChessAI.so` is loaded into memory by running `info
proc mappings`:

    
    
    gdb-peda$ info proc mappings                                                                                                                                                                                                
    process 22076                                                                                                                                                                                                               
    Mapped address spaces:                                                                                                                                                                                                      
                                                                                                                                                                                                                                
              Start Addr           End Addr       Size     Offset objfile                                                                                                                                                       
          0x562744309000     0x56274430c000     0x3000        0x0 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessUI                                                                                                              
          0x56274430c000     0x56274430f000     0x3000     0x3000 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessUI                                                                                                              
          0x56274430f000     0x562744314000     0x5000     0x6000 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessUI                                                                                                              
          0x562744315000     0x562744316000     0x1000     0xb000 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessUI                                                                                                              
          0x562744316000     0x562744317000     0x1000     0xc000 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessUI                                                                                                              
          0x5627451b4000     0x562745838000   0x684000        0x0 [heap]                                                                                                                                                        
          0x7f5aa0000000     0x7f5aa0021000    0x21000        0x0                                                                                                                                                               
          0x7f5aa0021000     0x7f5aa4000000  0x3fdf000        0x0                                                                                                                                                               
          0x7f5aa8000000     0x7f5aa8021000    0x21000        0x0                  
    ...[snip]...
          0x7f5aba5e2000     0x7f5aba5e3000     0x1000        0x0 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessAI.so                                                                                                           
          0x7f5aba5e3000     0x7f5aba5e4000     0x1000     0x1000 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessAI.so                                                                                                           
          0x7f5aba5e4000     0x7f5aba5e5000     0x1000     0x2000 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessAI.so                                                                                                           
          0x7f5aba5e5000     0x7f5aba5e6000     0x1000     0x2000 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessAI.so                                                                                                           
          0x7f5aba5e6000     0x7f5aba5e7000     0x1000     0x3000 /media/sf_CTFs/flareon-2019/4 - Dnschess/ChessAI.so   
    ...[snip]...
    

I can grab that base address, 0x7f5aba5e2000, and add my offset to get the
address of the function at 0x7f5aba5e31c1:

    
    
    gdb-peda$ x/3i 0x7f5aba5e31c1
       0x7f5aba5e31c1 <getNextMove>:        push   rbp
       0x7f5aba5e31c2 <getNextMove+1>:      mov    rbp,rsp
       0x7f5aba5e31c5 <getNextMove+4>:      add    rsp,0xffffffffffffff80
    

I can set breakpoints using that address.

### ChessAI.so

The `getNextMove` function has three main parts:

![1567432687544](https://0xdfimages.gitlab.io/img/1567432687544.png)

The function takes five arguments, the turn number, the piece name, the
starting spot, the ending spot, and the pointer to the struct for the results
of the function:

![1567433058683](https://0xdfimages.gitlab.io/img/1567433058683.png)

It then goes through a series of conversations to convert the integer space
values to a domain name. The spaces are numbered starting at 0 in the bottom
left corner, working up to 7 in the upper left corner, back to the bottom,
second column for 8, and so on up to 63 at the top right.

Once the string is generated, it’s passed to `gethostbyname`.

In the second phase of this function, the results of that call are checked.
All of the following must be true, or the code branches to set the return
value to 2, and returns:

  * DNS request succeeds
  * IP address first octet is 127
  * IP address last octet is even
  * Low four bits of the IP address 3rd octet match the turn number

![1567433498229](https://0xdfimages.gitlab.io/img/1567433498229.png)

The return value of 2 causes the AI to resign.

For any packets that pass the checks, there are a series of calculations.
While I did spend a fair amount of time examining them, the details are not
actually important to solving the problem.

### ChessUI

I did dive into what calls `getNextMove` and start looking around in
`ChessUI`. It’s easy to get lost in all the GUI code, and not really important
here to solving the problem, so I won’t go into it.

## Solve

### Back to PCAP

Now that I understand the way that `getNextMove` processes the DNS replies, I
wonder how many valid requests are in the given pcap, and for what turns are
they good. I’ll write a `python` script to parse the pcap. There’s two tables
it outputs. The first is something I can put into my `/etc/hosts` file if I
want to replicate the same moves that were in that pcap. The second is a list
of the valid moves, including what turn they are valid on.

    
    
      1 #!/usr/bin/env python3
      2 
      3 from scapy.all import *
      4 
      5 
      6 packets = rdpcap('capture.pcap')
      7 
      8 hosts = {}
      9 turns = {}
     10 
     11 for pks in packets[DNS]:
     12 
     13     if pks[UDP].an:
     14         ip = pks[DNS].an.rdata
     15         octets = ip.split('.')
     16         if octets[0] == '127' and int(octets[3]) % 2 == 0:
     17             turn = int(octets[2]) % 16
     18             rrname = pks[DNS].an.rrname.decode()
     19             turns[turn] = rrname.split('.')[0]
     20             hosts[ip] = rrname.rstrip('.')
     21 
     22 print("For /etc/hosts:")
     23 for k in hosts:
     24     print(f"{k:15s} {hosts[k]}")
     25 
     26 print()
     27 print("Turns in order:")
     28 for k in sorted(turns):
     29     print(f"[{k:02d}] {turns[k]}")
    

This checks for ips that meet the two necessary conditions, the first octet
being 127 and the last being even. Then it calculates the turn and saves both
the pairing of domain to ip and of move to turn. At the end it prints both
tables.

    
    
    $ ./parse_moves.py 
    For /etc/hosts:
    127.252.212.90  knight-g1-f3.game-of-thrones.flare-on.com
    127.215.177.38  pawn-c2-c4.game-of-thrones.flare-on.com
    127.89.38.84    bishop-f1-e2.game-of-thrones.flare-on.com
    127.217.37.102  bishop-c1-f4.game-of-thrones.flare-on.com
    127.49.59.14    bishop-c6-a8.game-of-thrones.flare-on.com
    127.182.147.24  pawn-e2-e4.game-of-thrones.flare-on.com
    127.200.76.108  pawn-e5-e6.game-of-thrones.flare-on.com
    127.99.253.122  queen-d1-h5.game-of-thrones.flare-on.com
    127.25.74.92    bishop-f3-c6.game-of-thrones.flare-on.com
    127.108.24.10   bishop-f4-g3.game-of-thrones.flare-on.com
    127.34.217.88   pawn-e4-e5.game-of-thrones.flare-on.com
    127.141.14.174  queen-h5-f7.game-of-thrones.flare-on.com
    127.230.231.104 bishop-e2-f3.game-of-thrones.flare-on.com
    127.159.162.42  knight-b1-c3.game-of-thrones.flare-on.com
    127.53.176.56   pawn-d2-d4.game-of-thrones.flare-on.com
    
    Turns in order:
    [00] pawn-d2-d4
    [01] pawn-c2-c4
    [02] knight-b1-c3
    [03] pawn-e2-e4
    [04] knight-g1-f3
    [05] bishop-c1-f4
    [06] bishop-f1-e2
    [07] bishop-e2-f3
    [08] bishop-f4-g3
    [09] pawn-e4-e5
    [10] bishop-f3-c6
    [11] bishop-c6-a8
    [12] pawn-e5-e6
    [13] queen-d1-h5
    [14] queen-h5-f7
    

It is promising that of the 40 requests, only 14 were valid, and it happens to
be one from each turn.

### Play the Game

Now I’ll update my hosts file with the lines from the top, and play the game,
following the move list above:

![](https://0xdfimages.gitlab.io/img/chess.gif)

When I get check-mate, I also get the flag:

![1570097966238](https://0xdfimages.gitlab.io/img/1570097966238.png)

**Flag: LooksLikeYouLockedUpTheLookupZ@flare-on.com**

[](/flare-on-2019/dnschess.html)

