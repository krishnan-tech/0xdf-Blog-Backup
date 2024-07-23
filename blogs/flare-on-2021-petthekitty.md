# Flare-On 2021: PetTheKitty

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
petthekitty](/tags#flare-on-petthekitty ) [reverse-engineering](/tags#reverse-
engineering ) [youtube](/tags#youtube ) [wireshark](/tags#wireshark ) [delta-
patch](/tags#delta-patch ) [dll](/tags#dll ) [ghidra](/tags#ghidra )
[python](/tags#python ) [scapy](/tags#scapy )  
  
Nov 3, 2021

  * [[1] credchecker](/flare-on-2021/credchecker)
  * [[2] known](/flare-on-2021/known)
  * [[3] antioch](/flare-on-2021/antioch)
  * [[4] myaquaticlife](/flare-on-2021/myaquaticlife)
  * [[5] FLARE Linux VM](/flare-on-2021/flarelinuxvm)
  * [6] PetTheKitty
  * [[7] spel](/flare-on-2021/spel)
  * [[8] beelogin](/flare-on-2021/beelogin)
  * [9] evil - no writeup :(
  * [[10] wizardcult](/flare-on-2021/wizardcult)

![petthekitty](https://0xdfimages.gitlab.io/img/flare2021-petthekitty-
cover.png)

PetTheKitty started with a PCAP with two streams. The first was used to
download and run a DLL malware, and the second was the C2 communications of
that malware. The malware and the initial downloader user Windows Delta
patches to exchange information. I’ll reverse the binary to understand the
algorithm and decode the reverse shell session to find the flag.

## Challenge

> Hello,
>
> Recently we experienced an attack against our super secure MEOW-5000
> network.
>
> Forensic analysis discovered evidence of the files PurrMachine.exe and
> PetTheKitty.jpg; however, these files were ultimately unrecoverable.
>
> We suspect PurrMachine.exe to be a downloader and do not know what role
> PetTheKitty.jpg plays (likely a second-stage payload).
>
> Our incident responders were able to recover malicious traffic from the
> infected machine.
>
> Please analyze the PCAP file and extract additional artifacts.
>
> Looking forward to your analysis,
>
> ~Meow

The download includes a ~700K packet capture file:

    
    
    $ file IR_PURRMACHINE.pcapng 
    IR_PURRMACHINE.pcapng: pcapng capture file - version 1.0
    $ ls -lh IR_PURRMACHINE.pcapng
    -rwxrwx--- 1 root vboxsf 693K Sep  2 23:56 IR_PURRMACHINE.pcapng
    

## PCAP

### Conversations

The PCAP is not noisy. There are only two TCP streams:

![image-20210918071639897](https://0xdfimages.gitlab.io/img/image-20210918071639897.png)

The timeline is:

  * 172.16.111.139 (which I’ll refer to as client) makes a DNS query for `xn--zn8hscq4eeafedhjjkl.flare-on.com`. 172.16.111.144 (which I’ll refer to as server) responds that it is that domain.
  * Client connects to server on TCP port 7331 and over about 0.3 seconds downloads 676k.
  * 0.05 seconds later, client makes a DNS query for `xn--zn8hrcq4eeadihijjk.flare-on.com` (different subdomain). Server replies with it’s IP.
  * Immediately client connects to server on TCP 1337, sending 15k and receiving 22k.

### First Stream (2020 <–> 7331)

#### Analysis

The first TCP stream looks like the client is requesting a “meme”, and the
server responds “MEOW” and eight bytes later the [magic
bytes](https://en.wikipedia.org/wiki/List_of_file_signatures) for a PNG image,
`89 50 4E 47 0D 0A 1A 0A`.

![image-20210918072809479](https://0xdfimages.gitlab.io/img/image-20210918072809479.png)

Looking a bit more closely at the two four byte words that follow `MEOW`, in
both cases they are the same, and look like they could be lengths. In fact, if
I guess that the client is sending the message “~meow~ (=^.^=) ~meow~…. can
haz MeeooowwwMeme???”, the length of that string is 50 bytes, or 0x32, which
matches the two words.

The response then should be 0xa24d0 = 664784 bytes. That means it should end
at 0xa24dc. And looking there in the dump, it does:

![image-20210918073647780](https://0xdfimages.gitlab.io/img/image-20210918073647780.png)

There’s another request from the client, this time, asking for
“MeeeeooooowwWare”. The response is 0x29b1 = 10673 bytes.

#### Files

I’ll carve both files out of the stream. The quickest way I know to do this is
to view the stream as “raw”, copy of the hex of the parts I want to carve, and
then convert them with `xxd`:

    
    
    $ vim tcp_stream1-png.hex
    $ cat tcp_stream1-png.hex | xxd -r -p > tcp_stream1-png.png
    $ file tcp_stream1-png.png
    tcp_stream1-png.png: PNG image data, 1496 x 1122, 8-bit/color RGBA, non-interlaced
    

The image is a cat meme:

![](https://0xdfimages.gitlab.io/img/tcp_stream1-png.png)

The other file isn’t recognized by `file`:

    
    
    $ vim tcp_stream1-binary.hex
    $ cat tcp_stream1-binary.hex | xxd -r -p > tcp_stream1-binary
    $ file tcp_stream1-binary
    tcp_stream1-binary: data
    $ xxd tcp_stream1-binary | head
    00000000: 5041 3330 c0be 4202 77a0 d701 1823 8000  PA30..B.w....#..
    00000010: f215 2100 0198 9902 a440 6812 4548 1582  ..!......@h.EH..
    00000020: c5bb 229a 2102 0020 a8b2 a33a 5b00 a042  ..".!.. ...:[..B
    00000030: c3dd 5404 dbcc 36b3 99dd 6ff6 990f fadb  ..T...6...o.....
    00000040: e2b6 fbee 83ba 6db6 b90f e1e1 6366 ba6f  ......m.....cf.o
    00000050: eeb3 4d6d 6a57 9df9 b7db ec53 b5a9 e90c  ..MmjW.....S....
    00000060: aaae a6fa b1cb e6df 5c67 e2b3 ebec 7189  ........\g....q.
    00000070: d82f 8bcb 2fb1 bb6d ee97 ef71 9f8b cfe3  ./../..m...q....
    00000080: fb7d 8fdb bedd 983f ecfb cee6 9b9d 2dee  .}.....?......-.
    00000090: 1617 8b0b decd e262 fe59 7cf6 87c5 14c0  .......b.Y|.....
    

Checking the Wikipedia page for [List of file
signatures](https://en.wikipedia.org/wiki/List_of_file_signatures), this is a
Windows Update Delta Compression file.

### Second Stream (2021 <–> 1337)

My theory to this point is that the first stream is downloading the second
stage malware to the host, and then the second stream is that malware
communicating with the command and control (C2). Each side sends 37 messages
in this exchange. Looking at the second stream, it has a lot of similarities
to the first stream:

![image-20210918212707904](https://0xdfimages.gitlab.io/img/image-20210918212707904.png)

Each message starts out with `ME0W` followed by two four-byte words. But this
time, they are different. The second one seems to line up with the message
length. It’s not clear what the first is at this point.

Additionally, the body of each message is another delta file. It’s not clear
what to do with that either. I’ll come back once I have the second stage
executable.

## Create DLL

Windows uses this Binary Delta Compression to send a file diff that can be
used to patch an existing file with the minimal amount of space used by the
patch. [This post](https://wumb0.in/extracting-and-diffing-ms-patches-
in-2020.html) from August 2020 goes into a lot of the technical detail for how
that works. It also references a script, `delta_patch.py`. Searching for
`delta_patch.py`, I found [this
gist](https://gist.github.com/wumb0/9542469e3915953f7ae02d63998d2553) from the
same author that has a Python3 version of the script last updated a couple
days ago as I was working on it.

I’ve got this image and this diff. I’ll try applying the diff to the image
itself. From Windows, I’ll download this script and give it a run:

    
    
    PS > python3 .\delta_patch.py -i .\tcp_stream1-png.png -o patched.bin .\tcp_stream1-binary
    Applied 1 patch successfully
    Final hash: OsdAMg6SJ4EFnx69R5NJFq2ToD4utovfwrzBaVxmssk=
    

It seems to work, and `patched.bin` is a x86 Windows executable:

    
    
    $ file patched.bin 
    patched.bin: PE32 executable (DLL) (GUI) Intel 80386, for MS Windows
    

## RE

### Entry

Opening the file in Ghidra, there are two exports listed:

![image-20210919070126880](https://0xdfimages.gitlab.io/img/image-20210919070126880.png)

`entry` has a call to `__DllMainCRTStartup`. Comparing it to the
[documentation on a DllMain entry point](https://docs.microsoft.com/en-
us/windows/win32/dlls/dllmain), this clearly matches. I can rename / retype
things to make it really clear:

    
    
    void entry(HINSTANCE hinstDLL,DWORD fdwReason,LPVOID lpReserved)
    
    {
      if (fdwReason == DLL_PROCESS_ATTACH) {
        ___security_init_cookie();
      }
      ___DllMainCRTStartup(hinstDLL,fdwReason,lpReserved);
      return;
    }
    

`__DllMainCRTStartup` does some checking based on how it is being called, but
basically calls two functions:

    
    
    uint __cdecl ___DllMainCRTStartup(HINSTANCE hinstDLL,DWORD fdwReason,LPVOID lpReserved)
    
    {
      uint res;
      int res2;
      
      _DAT_10004010 = fdwReason;
      if ((fdwReason == DLL_PROCESS_DETACH) && (open_threads == 0)) {
        res = 0;
      }
      else {
        if (((fdwReason != DLL_PROCESS_ATTACH) && (fdwReason != DLL_THREAD_ATTACH)) ||
           (res = lots_of_init(hinstDLL,fdwReason,lpReserved), res != 0)) {
          res = set_image_base_addr(hinstDLL,fdwReason);
          if ((fdwReason == DLL_PROCESS_ATTACH) && (res == 0)) {
            set_image_base_addr(hinstDLL,0);
            lots_of_init(hinstDLL,0,lpReserved);
          }
          if ((fdwReason == DLL_PROCESS_DETACH) || (fdwReason == DLL_THREAD_DETACH)) {
            res2 = lots_of_init(hinstDLL,fdwReason,lpReserved);
            res = res & -(uint)(res2 != 0);
          }
        }
      }
      set_4010_neg_one();
      return res;
    }
    

I named them `set_image_base_addr` and `lots_of_init`, but I didn’t really
dive into either too much.

### send

Since I know the program will connect over the network, I’ll look for the
functions that do that. `ws2_32.dll` is the network library. Interestingly,
all the functions are referenced by ordinal, not function name:

![image-20210919214024991](https://0xdfimages.gitlab.io/img/image-20210919214024991.png)

I found [this
script](https://github.com/phracker/HopperScripts/blob/master/WS2_32.dll%20Ordinals%20to%20Names.py)
which conveniently has a Python dictionary of all the `ws2_32.dll` functions
by ordinal, and renamed them in Ghidra:

![image-20210919214143985](https://0xdfimages.gitlab.io/img/image-20210919214143985.png)

Since the first thing that happens is `send`, I wanted to start with that. I
found where it’s called, and only once, in `FUN_1000111e`, which I named
`msg_send`. The inputs are a socket, a message, and a length.

If starts off XORing the message with `meoow`:

    
    
      if (msglen != 0) {
        do {
          *(byte *)((int)msg + i) = *(byte *)((int)msg + i) ^ "meoow"[i % 5];
          i = i + 1;
        } while (i < msglen);
      }
    

It creates space on the heap and calls a function I called `make_delta`:

    
    
      memcpy(_Dst,delta_base,_Size);
      memcpy(_Dst,msg,msglen);
      me0w_body = make_delta(delta_base,_Size,_Dst,_Size,&local_14)
    

Later that delta is sent:

    
    
        while ((me0w_body != 0 &&
               (bytes_read = send(socket,(int)lpMem + j,me0w_body,0), uVar2 = extraout_DL_02,
               bytes_read != -1))) {
          j = j + bytes_read;
          me0w_body = me0w_body - bytes_read;
        }
    

This fits with the messages in the PCAP being more delta patches.

### recv

The same pattern happens in reverse on the `recv` side. It’s in
`FUN_1000128a`, which I named `msg_recv`. It does a loop to receive bytes
until the connection is done, then applies the delta patch:

    
    
    bytes_recv = delta_is_applied(data_buffer,length,&result);
    

Later that data is passed through the same XOR:

    
    
          if (uStack16 != 0) {
            do {
              imod5 = i % 5;
              *(byte *)((int)*msg + i) = *(byte *)((int)*msg + i) ^ "meoow"[imod5];
              i = i + 1;
            } while (i < *result_len);
          }
    

Looking up one function at what calls this `msg_send` function, `FUN_100015d4`
(renamed to `le_main`), is called from `le_meow` and calls both `msg_send` and
`msg_recv`. It also creates a `cmd.exe` process:

    
    
        res = CreateProcessA((LPCSTR)0x0,"C:\\wiNdOwS\\sYstEm32\\cMd.ExE",(LPSECURITY_ATTRIBUTES)0x0,
                             (LPSECURITY_ATTRIBUTES)0x0,1,0,(LPVOID)0x0,(LPCSTR)0x0,
                             (LPSTARTUPINFOA)&auStack65684,(LPPROCESS_INFORMATION)&_Stack65596);
    

I believe incoming commands are passed to this, and then the output is re-
xored and sent back.

## Decode Messages

### Manual

#### Client 0

At this point, I just needed to do a bit of guessing about what the starting
image was. Given that both the server and the client had the PNG, that made
sense, and it worked. I’ll copy the first message from client to server in hex
and convert it back to binary saving it as `msg_c0.patch`:

    
    
    $ echo "50413330f05e210377a0d7011823c0b29f0b01017a02960713265c397063c490b37a494c6832e6c0899d72313c19b0e7428f036db91a65ca93ad4aa37679220ce815c2812b17aef458d065a95c3e1b3972b56a97af462e2f7a6cb833e242832547b94268d0e5ca882b33da7418d194a95e291fdab4d57367c2803e6d6e722f9ace47cd91116bd91fa12eabc2b48b96746a2ea26971a3c155b46806ece870fe58254ae144ff22a530faa8697056d9010080d23e03" | xxd -r -p > msg_c0.patch
    

I’ll apply that patch to the initial image:

    
    
    PS > python3 delta_patch.py -i tcp_stream1-png.png -o msg_c0.enc msg_c0.patch
    Applied 1 patch successfully
    Final hash: Wgzbt+5elUyLw1b+QkGuJeX1qXGe8uu7HQRFwjRX+v8=
    

Now from a Python terminal I can try to decrypt it:

    
    
    >>> from itertools import cycle
    >>> with open('msg_c0.enc', 'rb') as f:
    ...     enc = f.read()
    ... 
    >>> print(''.join([chr(x^y) for x,y in zip(enc, cycle(b'meoow'))])[:0x8b])
    Microsoft Windows [Version 6.1.7601]
    Copyright (c) 2009 Microsoft Corporation.  All rights reserved.
    
    C:\Users\user\Desktop\SuperSecret>
    

It’s a Windows command prompt! I grabbed only the first 0x8b bytes because
that was what was in the header of the packet:

![image-20210919220447594](https://0xdfimages.gitlab.io/img/image-20210919220447594.png)

#### Server 0

I’ll create the first server patch the same way:

    
    
    $ echo "50413330d084490777a0d7011823c0b29f0b010146009413531acc38d131a0d77807000052fd0c" | xxd -r -p > msg_s0.patch
    

I tried applying this to several things before I found the right thing, but
using `msg_c0.enc` worked:

    
    
    PS > python3 delta_patch.py -i msg_c0.enc -o msg_s0.enc msg_s0.patch
    Applied 1 patch successfully
    Final hash: KEzaz7jAhfQMUyoqNG+M5COMJzah4TxIdgRURbQZITU=
    

Now XOR:

    
    
    >>> print(''.join([chr(x^y) for x,y in zip(enc, cycle(b'meoow'))])[:0x9])
    whoami
    

I was expecting 9 bytes based on the header, but there’s actually `\r\n\x00`,
which I can see if I remove the print:

    
    
    >>> ''.join([chr(x^y) for x,y in zip(enc, cycle(b'meoow'))])[:0x9]
    'whoami\r\n\x00'
    

#### Client 1

I’ll try one more manually before I script this. Create the patch:

    
    
    $ echo "50413330c076ad0777a0d7011823c0b29f0b01010e019113531acc38d131a0772306ec6571672392051746747518d7a5578c7a8992b8b0e2ce4ef4ed8816cc8a1b33ce34e88b14c789fb458a63c4842e03962a3b000070e467" | xxd -r -p > msg_c1.patch
    

Apply it:

    
    
    PS > python3 delta_patch.py -i msg_s0.enc -o msg_c1.enc msg_c1.patch
    Applied 1 patch successfully
    Final hash: 1X2fi7mI2njG4ZVNZ5/wfUV2pOKCiG3G6rUADbE1G48=
    

Decode it:

    
    
    >>> print(''.join([chr(x^y) for x,y in zip(enc, cycle(b'meoow'))])[:0x3a])
    whoami
    user-pc\user
    
    C:\Users\user\Desktop\SuperSecret>
    

### Script

#### Main

I’ll create a script that will process the entire PCAP and print the results.
Because I observed that the client returns both the command and the results,
I’ll just print the client side and get a shell session:

    
    
    #!/usr/bin/env python3    
        
    import struct    
    import delta_patch    
    from itertools import cycle    
    from scapy.all import *    
    
    
    pcap = rdpcap('./IR_PURRMACHINE.pcapng')    
        
    data = b''.join([p[Raw].load for p in pcap if 'TCP' in p and 'Raw' in p and p[TCP].dport == 2020])    
    assert(data[:4] == b'ME0W')    
    msg_len, patch_len  = struct.unpack("<II", data[4:12])    
    image = data[12:12+patch_len]    
    assert(data[12+patch_len:12+patch_len+4] == b'ME0W')
        
    for packet in pcap:    
        if 'TCP' not in packet:    
            continue
        dport = packet[TCP].dport
        if 'Raw' in packet and dport in [1337, 2021]:
            data = packet[Raw].load
            assert(data[:4] == b'ME0W')
            msg_len, patch_len  = struct.unpack("<II", data[4:12])
            patch = data[12:]
            assert(len(patch) == patch_len)
            image = delta_patch.apply_patchbuf_to_buffer(image, len(image), patch, False)
            if dport == 1337:
                print(''.join([chr(x^y) for x,y in zip(image[:msg_len], cycle(b'meoow'))]), end='')   
    

The script uses Scapy to read the PCAP and parse through it. First, it pulls
the image from the PCAP by getting all the TCP packets with a payload that
have destination port 2020. It gets the payload length and then uses that to
pull the PNG image.

Next it loops through the packets in the PCAP looking for both sides of the C2
conversation (the second TCP stream). It pulls the packet and makes sure it
has “ME0W” as the start. Then it pulls the patch length and the message
length. I’m using `asserts` here to check my assumptions about the packets.
Once it has the patch, it will call a (modified) function from `delta_patch`
to apply it to the image, and save the result over the image for the next one.

If it’s from the client, I’ll XOR decode the message and print it.

#### delta_patch

I’m going to loop through the PCAP and pull out patches, and I’ll need to
apply them one by one. Looking at the [download
script](https://gist.github.com/wumb0/9542469e3915953f7ae02d63998d2553), the
function it calls is `apply_patchfile_to_buffer(buf, buflen, patchpath,
legacy)`. The first thing it does is `open(patchpath, 'rb')`, which means it’s
expecting that as a file on disk. I could have my script write the patch to
disk, but that feels messy. I’ll create another copy of that function that
takes in the image and the patch as buffers and returns the updated buffer. I
created a video to show how I worked with this script in a place where I don’t
totally understand how the script works:

The final function is:

    
    
    def apply_patchbuf_to_buffer(buf, buflen, patch_contents, legacy):
    
        buf = cast(buf, wintypes.LPVOID)
    
        # some patches (Windows Update MSU) come with a CRC32 prepended to the file
        # if the file doesn't start with the signature (PA) then check it
        if patch_contents[:2] != b"PA":
            paoff = patch_contents.find(b"PA")
            if paoff != 4:
                raise Exception("Patch is invalid")
            crc = int.from_bytes(patch_contents[:4], 'little')
            patch_contents = patch_contents[4:]
            if zlib.crc32(patch_contents) != crc:
                raise Exception("CRC32 check failed. Patch corrupted or invalid")
    
        applyflags = DELTA_APPLY_FLAG_ALLOW_PA19 if legacy else DELTA_FLAG_NONE
    
        dd = DELTA_INPUT()
        ds = DELTA_INPUT()
        dout = DELTA_OUTPUT()
    
        ds.lpcStart = buf
        ds.uSize = buflen
        ds.Editable = False
    
        dd.lpcStart = cast(patch_contents, wintypes.LPVOID)
        dd.uSize = len(patch_contents)
        dd.Editable = False
    
        status = ApplyDeltaB(applyflags, ds, dd, byref(dout))
        if status == 0:
            raise Exception("Patch {} failed with error {}".format(patchpath, gle()))
            
        to_free = []
        to_free.append(dout.lpStart)
        #import pdb;pdb.set_trace()
        return bytes((c_ubyte*dout.uSize).from_address(dout.lpStart))
    

#### Run It

Putting those together, there’s a bunch of output that mirrors a terminal
session (shell) on the victim. Buried in the middle of a [Rick-
Roll](https://en.wikipedia.org/wiki/Rickrolling) there’s the flag:

    
    
    ...[snip]...
    And if you ask Ã▼ how I'm feeling
    Don't tell me you're tÁ§ blind to see
    1m_H3rE_Liv3_1m_n0t_a_C4t@flare-on.com
    Never gonna give you up, never gonna let you down
    Never gonna run around and desert you
    Never gonna make you cry, never gonna say 
    ...[snip]...
    

The full output is:

    
    
    C:\Users\user\Desktop\SuperSecret>whoami
    user-pc\user
    
    C:\Users\user\Desktop\SuperSecret>net user
    
    User accounts for \\USER-PC
    
    -------------------------------------------------------------------------------
    Administrator            Guest                    user
    The command completed successfully.
    
    
    C:\Users\user\Desktop\SuperSecret>dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret
    
    09/02/2021  11:51 PM    <DIR>          .
    09/02/2021  11:51 PM    <DIR>          ..
    07/23/2021  03:32 PM    <DIR>          2021_FlareOn
    09/02/2021  11:51 PM         1,438,208 PetTheKitty.jpg
    09/02/2021  11:34 PM           205,312 PurrMachine.exe
                   2 File(s)      1,643,520 bytes
                   3 Dir(s)  32,587,169,792 bytes free
    
    C:\Users\user\Desktop\SuperSecret>cd 2021_FlareOn
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn>dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn
    
    07/23/2021  03:32 PM    <DIR>          .
    07/23/2021  03:32 PM    <DIR>          ..
    09/02/2021  11:44 PM    <DIR>          Cat_Memes
    09/02/2021  11:47 PM    <DIR>          Great_Ideas
    07/23/2021  03:18 PM    <DIR>          Never
    09/02/2021  11:44 PM    <DIR>          No_Flags_Here
    09/02/2021  11:45 PM    <DIR>          NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS
    09/02/2021  11:47 PM    <DIR>          Okay_Ideas
    09/02/2021  11:47 PM    <DIR>          Swag
    09/02/2021  11:47 PM    <DIR>          The_BEST_Ideas
                   0 File(s)              0 bytes
                  10 Dir(s)  32,587,169,792 bytes free
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn>cd Cat_Memes
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Cat_Memes>dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Cat_Memes
    
    09/02/2021  11:44 PM    <DIR>          .
    09/02/2021  11:44 PM    <DIR>          ..
    09/02/2021  11:44 PM                64 ãË§w.txt
                   1 File(s)             64 bytes
                   2 Dir(s)  32,587,169,792 bytes free
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Cat_Memes>type ãË§w.txt
             ~Ã▼0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Cat_Memes>cd ..
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn>dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn
    
    07/23/2021  03:32 PM    <DIR>          .
    07/23/2021  03:32 PM    <DIR>          ..
    09/02/2021  11:44 PM    <DIR>          Cat_Memes
    09/02/2021  11:47 PM    <DIR>          Great_Ideas
    07/23/2021  03:18 PM    <DIR>          Never
    09/02/2021  11:44 PM    <DIR>          No_Flags_Here
    09/02/2021  11:45 PM    <DIR>          NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS
    09/02/2021  11:47 PM    <DIR>          Okay_Ideas
    09/02/2021  11:47 PM    <DIR>          Swag
    09/02/2021  11:47 PM    <DIR>          The_BEST_Ideas
                   0 File(s)              0 bytes
                  10 Dir(s)  32,587,169,792 bytes free
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn>cd No_Flags_Here
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\No_Flags_Here>dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn\No_Flags_Here
    
    09/02/2021  11:44 PM    <DIR>          .
    09/02/2021  11:44 PM    <DIR>          ..
    09/02/2021  11:44 PM                64 meow.txt
    07/23/2021  03:26 PM             1,658 what_did_you_expect.txt
                   2 File(s)          1,722 bytes
                   2 Dir(s)  32,587,169,792 bytes free
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\No_Flags_Here>type what_did_you_expect.txt
                              oÁ§o$$$$$$$$$$$$Á§oo
                          oo$$$$$$$$$$$$$$$$$$$$$$$$o
                       §o$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$o         o$   $$ §$
       o $ oo        o$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$o       $$ $$ $$o$
    oÁ $ $ "$      o$$$$$$$$$    $$$$$$$$$$$$$    $$$$$$$$$o       $$$o$$o$
    "$$$$$$o$     §$$$$$$$$$      $$$$$$$$$$$      $$$$$$$$$$o    $$$$$$$$
      $$$$$$$    $$$$$$$$$$$      $$$$$$$$$$$      $$$$$$$$$$$$$$$$$$$$$$$
      $$$$$$$$$$$$$$$$$$$$$$$    $$$$$$$$$$$$$    $$$$$$$$$$$$$$  """$$$
       "$$$""""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     "$$$
        $$$   o$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     "$$$o
       o$$"   $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$       $$$o
       $$$    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" "$$$$$$ooÁ§o$$$$o
      o$$$§ooo$$$$$  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$   o$$$$$$$$$$$$$$$$$
      $$$$$$$$"$$$$   $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     $$$$""""""""
     """"       $$$$    "$$$$$$$$$$$$$$$$$$$$$$$$$$$$"      o$$$
                "$$$§     """$$$$$$$$$$$$$$$$$$"$$"         $$$
                  $$$o          "$$""$$$$$$""""           o$$$
                   $$$$o                 oo             o$$$"
                    "$$$$§      o$$$$$$o"$$$$§        o$$$$
                      "$$$$$§o     ""$$$$o$$$$$o   o$$$$""
                         ""$$$$$ooÁ§  "$$$o$$$$$$$$$"""
                            ""$$$$$$$§o $$$$$$$$$$
                                    """"$$$$$$$$$$$
                                        $$$$$$$$$$$$
                                         $$$$$$$$$$"
                                          "$$$""""
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\No_Flags_Here>type ãË§w.txt
             ~Ã▼0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\No_Flags_Here>cd ..
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn>dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn
    
    07/23/2021  03:32 PM    <DIR>          .
    07/23/2021  03:32 PM    <DIR>          ..
    09/02/2021  11:44 PM    <DIR>          Cat_Memes
    09/02/2021  11:47 PM    <DIR>          Great_Ideas
    07/23/2021  03:18 PM    <DIR>          Never
    09/02/2021  11:44 PM    <DIR>          No_Flags_Here
    09/02/2021  11:45 PM    <DIR>          NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS
    09/02/2021  11:47 PM    <DIR>          Okay_Ideas
    09/02/2021  11:47 PM    <DIR>          Swag
    09/02/2021  11:47 PM    <DIR>          The_BEST_Ideas
                   0 File(s)              0 bytes
                  10 Dir(s)  32,587,169,792 bytes free
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn>cd NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS>dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn\NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS
    
    09/02/2021  11:45 PM    <DIR>          .
    09/02/2021  11:45 PM    <DIR>          ..
    09/02/2021  11:44 PM                64 meow.txt
                   1 File(s)             64 bytes
                   2 Dir(s)  32,587,169,792 bytes free
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS>type ãË§w.txt
             ~Ã▼0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS>cd ..
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn>dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn
    
    07/23/2021  03:32 PM    <DIR>          .
    07/23/2021  03:32 PM    <DIR>          ..
    09/02/2021  11:44 PM    <DIR>          Cat_Memes
    09/02/2021  11:47 PM    <DIR>          Great_Ideas
    07/23/2021  03:18 PM    <DIR>          Never
    09/02/2021  11:44 PM    <DIR>          No_Flags_Here
    09/02/2021  11:45 PM    <DIR>          NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS
    09/02/2021  11:47 PM    <DIR>          Okay_Ideas
    09/02/2021  11:47 PM    <DIR>          Swag
    09/02/2021  11:47 PM    <DIR>          The_BEST_Ideas
                   0 File(s)              0 bytes
                  10 Dir(s)  32,587,169,792 bytes free
    
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn>@echo off & for /f %a in ('dir /s /b') do echo %~fa %~za
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Cat_Memes 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Great_Ideas 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\No_Flags_Here 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Okay_Ideas 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Swag 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\The_BEST_Ideas 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Cat_Memes\ãË§w.txt 64
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Great_Ideas\meow.txt 64
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\FlagPit 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\Gotcha.txt 1806
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\ãË§w.txt 64
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\The_Real_Challenge 0
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\FlagPit\ãË0000000w.txt 812
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\The_Real_Challenge\Mugatuware.exe 1532928
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\The_Real_Challenge\mydude.exe 650105
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\No_Flags_Here\meow.txt 64
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\No_Flags_Here\what_did_you_expect.txt 1658
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\NO_SERIOUSLY_EVEN_MORE_BESTEST_IDEAS\meow.txt 64
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Okay_Ideas\meow.txt 64
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Swag\meow.txt 64
    C:\Users\user\Desktop\SuperSecret\2021_FlareOn\The_BEST_Ideas\meow.txt 64
    cd Never\Gonna\Give\You\Up
    dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up
    
    09/02/2021  11:48 PM    <DIR>          .
    09/02/2021  11:48 PM    <DIR>          ..
    09/02/2021  11:49 PM    <DIR>          FlagPit
    07/23/2021  03:19 PM             1,806 Gotcha.txt
    09/02/2021  11:44 PM                64 meow.txt
    09/02/2021  11:49 PM    <DIR>          The_Real_Challenge
                   2 File(s)          1,870 bytes
                   4 Dir(s)  32,587,169,792 bytes free
    type Gotcha.txt
    We're no strangers to love
    You know the rules and so do I
    A full commitÃ▼nt's what I'm thinking of
    You wouldn't get this from any other guy
    I just wanna tell you how I'm feeling
    Gotta make you understand
    never gonna give you up, never gonna let you dÁ
    Never gonna run around and desert you
    Never gonna make you cry, never gonna say goodbye
    Never gonna t▼ll a lie and hurt you
    n each other for so long
    Your heart's been aching but you're too shy to say it
     what's been going on
     the game and we're gonna play it
    And if you ask Ã▼ how I'm feeling
    Don't tell me you're tÁ§ blind to see
    1m_H3rE_Liv3_1m_n0t_a_C4t@flare-on.com
    Never gonna give you up, never gonna let you down
    Never gonna run around and desert you
    Never gonna make you cry, never gonna say goodbye
    Never gonna tell a lie and hurt you
    never gonna give you up, never gonna let you dÁ
    Never gonna run around and desert you
    Never gonna make you cry, never gonna say goodbye
    Never gonna t▼ll a lie and hurt you
    n each other for so long
    Your heart's been aching but you're too shy to say it
     what's been going on
     the game and we're gonna play it
     I'm fËeling tell you hÁ
    Gotta make you understand
    Never gonna give you up, never gonna let you down
    Never gonna run around and desert you
    Never gonna make you cry, never gonna say goodbye
    Never gonna tell a lie and hurt you
    Never gonna give you up, never gonna let you down
    Never gonna run around and desert you
    Never gonna make you cry, never gonna say goodbye
    Never gonna tell a lie and hurt you
    never gonna give you up, never gonna let you dÁ
    Never gonna run around and desert you
    Never gonna make you cry, never gonna say goodbye
    Never gonna t▼ll a lie and hurt youdir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up
    
    09/02/2021  11:48 PM    <DIR>          .
    09/02/2021  11:48 PM    <DIR>          ..
    09/02/2021  11:49 PM    <DIR>          FlagPit
    07/23/2021  03:19 PM             1,806 Gotcha.txt
    09/02/2021  11:44 PM                64 meow.txt
    09/02/2021  11:49 PM    <DIR>          The_Real_Challenge
                   2 File(s)          1,870 bytes
                   4 Dir(s)  32,587,169,792 bytes free
    cd FlagPit
    dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\FlagPit
    
    09/02/2021  11:49 PM    <DIR>          .
    09/02/2021  11:49 PM    <DIR>          ..
    09/02/2021  11:50 PM               812 me0000000w.txt
                   1 File(s)            812 bytes
                   2 Dir(s)  32,587,169,792 bytes free
    type Ã▼0000000w.txt
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~Ã▼0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~Ã▼0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/
             ~me0w~
      /\_/\
     ( ^.^ )
     (")_(")_/   cd ..
    dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up
    
    09/02/2021  11:48 PM    <DIR>          .
    09/02/2021  11:48 PM    <DIR>          ..
    09/02/2021  11:49 PM    <DIR>          FlagPit
    07/23/2021  03:19 PM             1,806 Gotcha.txt
    09/02/2021  11:44 PM                64 meow.txt
    09/02/2021  11:49 PM    <DIR>          The_Real_Challenge
                   2 File(s)          1,870 bytes
                   4 Dir(s)  32,587,169,792 bytes free
    cd The_Real_Challenge
    dir
     VoluÃ▼ in drive C has no label.
     Volume Serial Number is 9C63-6ACB
    
     Directory of C:\Users\user\Desktop\SuperSecret\2021_FlareOn\Never\Gonna\Give\You\Up\The_Real_Challenge
    
    09/02/2021  11:49 PM    <DIR>          .
    09/02/2021  11:49 PM    <DIR>          ..
    05/01/2019  02:18 PM         1,532,928 Mugatuware.exe
    07/27/2020  05:37 PM           650,105 mydude.exe
                   2 File(s)      2,183,033 bytes
                   2 Dir(s)  32,587,169,792 bytes free
    cd ..
    type ãË§w.txt
             ~Ã▼0w~
      /\_/\
     ( ^.^ )
     (")_(")_/   rundll32.exe user32.dll,LockWorkStation
    

**Flag: 1m_H3rE_Liv3_1m_n0t_a_C4t@flare-on.com**

[](/flare-on-2021/petthekitty)

