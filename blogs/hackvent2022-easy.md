# Hackvent 2022 - Easy

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [qrcode](/tags#qrcode )
[python](/tags#python ) [python-pil](/tags#python-pil )
[zbarimg](/tags#zbarimg ) [python-null-bytes](/tags#python-null-bytes )
[javascript](/tags#javascript ) [pcap](/tags#pcap ) [gcode](/tags#gcode )
[wireshark](/tags#wireshark ) [blockchain](/tags#blockchain )
[solidity](/tags#solidity ) [youtube](/tags#youtube )
[metamask](/tags#metamask ) [remix](/tags#remix ) [python-web3](/tags#python-
web3 ) [micro-qr](/tags#micro-qr )  
  
Jan 3, 2023

  * easy
  * [medium](/hackvent2022/medium)
  * [hard](/hackvent2022/hard)

![](https://0xdfimages.gitlab.io/img/hv22-easy-cover.png)

Hackvent is one of the three holiday CTFs I try to play every December. This
year I made it through 20 of the first 21 days before life got too busy. The
first seven challenges (eight if you count the hidden challenge) were rated
easy, and included some interesting programming challenges, some blockchain,
and lots of QR codes.

## HV22.01

### Challenge

![hv22-ball01](https://0xdfimages.gitlab.io/img/hv22-ball01.png) | HV22.01 QR means quick reactions, right?  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | easy  
Author: |  Deaths Pirate   
  
> Santa’s brother Father Musk just bought out a new decoration factory. He
> sacked all the developers and tried making his own QR code generator but
> something seems off with it. Can you try and see what he’s done wrong?

![](https://0xdfimages.gitlab.io/img/326b39e0-ccf5-4b94-88ff-e1b654e2c5b9.gif)

The ball quickly changes through a bunch of QR codes (if you missed it, open
the image in a new window to see it start again).

### Solution

#### Initial Solve - Python

My initial attempt involved using an online tool to extract the various
frames. It would certainly be possible to then just scan each with my phone
and write down the characters, but that’s no fun. So I went to Python. I had
some issues, so I ended up back at a Python wrapping of the zxing library,
[pyzxing](https://github.com/ChenjieXu/pyzxing). It has to download a Java
dependency, so I’m not sure it’s what I’ll use going forward, but it is able
to recognize the images. I’ll use `PIL` to save each frame to a temp
directory, and then the `BarCodeReader` to get the character:

    
    
    #!/usr/bin/env python3
    
    import os
    import sys
    from PIL import Image
    from pyzxing import BarCodeReader
    from tempfile import TemporaryDirectory
    
    
    reader = BarCodeReader()
    with TemporaryDirectory() as tmpdir:
        with Image.open(sys.argv[1]) as im:
            for i in range(im.n_frames):
                fn = os.path.join(tmpdir, f'{i:02}.png')
                im.seek(i)
                im.save(fn)
                results = reader.decode(fn)
                print(results[0]['raw'].decode(), end='', flush=True)
    print()
    

Running this returns the flag:

    
    
    $ python decode.py 
    HV22{I_CaN_HaZ_Al_T3h_QRs_Plz}
    

**Flag:`HV22{I_CaN_HaZ_Al_T3h_QRs_Plz}`**

#### zbarimg

darkstar told me about a utility, `zabarimg` (part of the `zbar-tools`
package, `apt install zbar-tools`). It will get all the reads from the image
without my having to break out the 30 different images:

    
    
    oxdf@hacky$ zbarimg 326b39e0-ccf5-4b94-88ff-e1b654e2c5b9.gif 
    QR-Code:H
    QR-Code:V
    QR-Code:2
    QR-Code:2
    QR-Code:{
    QR-Code:I
    QR-Code:_
    QR-Code:C
    QR-Code:a
    QR-Code:N
    QR-Code:_
    QR-Code:H
    QR-Code:a
    QR-Code:Z
    QR-Code:_
    QR-Code:A
    QR-Code:l
    QR-Code:_
    QR-Code:T
    QR-Code:3
    QR-Code:h
    QR-Code:_
    QR-Code:Q
    QR-Code:R
    QR-Code:s
    QR-Code:_
    QR-Code:P
    QR-Code:l
    QR-Code:z
    QR-Code:}
    scanned 30 barcode symbols from 30 images in 0.27 seconds
    

The `--raw` flag and a quick `tr` to remove newlines prints the flag
completely:

    
    
    oxdf@hacky$ zbarimg --raw 326b39e0-ccf5-4b94-88ff-e1b654e2c5b9.gif | tr -d '\n'
    scanned 30 barcode symbols from 30 images in 0.23 seconds
    
    HV22{I_CaN_HaZ_Al_T3h_QRs_Plz}
    

## HV22.02

### Challenge

![hv22-ball02](https://0xdfimages.gitlab.io/img/hv22-ball02.png) | HV22.02 Santa's song  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | easy  
Author: |  kuyaya   
  
> Santa has always wanted to compose a song for his elves to cherish their
> hard work. Additionally, he set up a vault with a secret access code only he
> knows!
>
> The elves say that Santa has always liked to hide secret messages in his
> work and they think that the vaults combination number may be hidden in the
> magnum opus of his.
>
> What are you waiting for? Go on, help the elves!

There’s also a button to spin up an individual copy of a website. Visiting the
URL in a browser returns this page:

![image-20221202091301424](https://0xdfimages.gitlab.io/img/image-20221202091301424.png)

The PDF download is simple:

![image-20221202091316555](https://0xdfimages.gitlab.io/img/image-20221202091316555.png)

### Solution

#### Rabbit Holes

It’s clear from the description that the code is a number (and later by a hint
given).

I went down a lot of rabbit holes on this one, including but not limited to:

  * Looking at `strings` and the `exiftool` metadata for the PDF.
  * Looking at the various object in the PDF source using `pdf-parser.py`.
  * Use the various time signatures (3/4, 5/4, etc) to build a pin.
  * Brute forcing the pin with `wfuzz` (getting about 5 results per second, guessing a 4 or 5 digit pin)

#### Success

These music notes represent notes typically labels as A-G:

![Treble Clef - Music Theory Academy - Learn the notes of the Treble
Clef](https://0xdfimages.gitlab.io/img/Treble-Clef-Notes.jpg)

Mapping that onto these notes:

![image-20221202092643684](https://0xdfimages.gitlab.io/img/image-20221202092643684.png)

That message is a hint that this is the right track. To get this into a
number, I can note that all the characters are valid hex. If I treat it as a
hex int, converting it to base-10 gives 13470175147275968237:

    
    
    >>> int('baefacedabaddeed', 16)
    13470175147275968237
    

And that solves it:

![image-20221202092953095](https://0xdfimages.gitlab.io/img/image-20221202092953095.png)

**Flag:`HV22{13..s0me_numb3rs..37}`**

## HV22.03

### Challenge

![hv22-ball03](https://0xdfimages.gitlab.io/img/hv22-ball03.png) | HV22.03 gh0st  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO  
![fun](../img/hv-cat-fun.png)FUN  
Level: | easy  
Author: |  0xdf   
  
> The elves found this Python script that Rudolph wrote for Santa, but it’s
> behaving very strangely. It shouldn’t even run at all, and yet it does! It’s
> like there’s some kind of ghost in the script! Can you figure out what’s
> going on and recover the flag?

The download is a python script:

    
    
    #!/usr/bin/env python3.7
    
    import random
    import sys
    
    
    if len(sys.argv) != 2:
        print(f'''usage: {sys.argv[0]} flag''')
        sys.exit()
        print('''Things ^@are not^@ what they seem?''')
    
    # only one in a million shall pass
    if random.randrange(1000000):
       sys.exit()
    
    # this isn't going to work
    print(''')#%^$&*(#$%@^&*(#@!''')
    print('''Nice job getting lucky there! But did you get the flag?''')
    
    # Santa only wants every third line!
    song =  """You know Dasher, and Dancer, and^@"""
    #song += """#Prancer, and Vixen,^@"""
    #song += """#Comet, and Cupid, and"""
    song += """Donder and Blitzen^@"""
    #song += """#But do you recall^@"""
    #song += """#The most famous reindeer of all"""
    song += """Rudolph, the red-nosed reindeer^@"""
    #song += """#had a very shiny nose^@"""
    #song += """#and if you ever saw it"""
    song += """you would even say it glows.^@"""
    #song += """#All of the other reindeer^@"""
    #song += """#used to laugh and call him names"""
    song += """They never let poor Rudolph^@"""
    #song += """#play in any reindeer games.^@"""
    #song += """#Then one foggy Christmas eve"""
    song += """Santa came to say:^@"""
    #song += """    #Rudolph with your nose so bright,^@"""
    #song += """    #won't you guide my sleigh tonight?"""
    song += """Then all the reindeer loved him^@"""
    #song += """#as they shouted out with glee,^@"""
    #song += """#Rudolph the red-nosed reindeer,"""
    song += """you'll go down in history!"""
    
    flag = list(map(ord, sys.argv[1]))
    correct = [17, 55, 18, 92, 91, 10, 38, 8, 76, 127, 17, 12, 17, 2, 20, 49, 3, 4, 16, 8, 3, 58, 67, 60, 10, 66, 31, 95, 1, 93]
    
    for i,c in enumerate(flag):
        flag[i] ^= ord(song[i*10 % len(song)])
    
    if all([c == f for c,f in zip(correct, flag)]):
        print('''Congrats!''')
    else:
        print('''Try again!''')
    

### Background

As the author of this challenge, I’ll take a minute to talk about the
motivation, [this video](https://www.youtube.com/watch?v=sjf2poVpdYc):

It’s all about how a null byte can make Python act really strangely. I knew
right away on seeing this that I wanted to make a challenge out of it. Making
an actually challenging challenge turned out to be quite…a challenge. I had
ideas about putting it in base64 encoded data and then passing it to `eval`,
but that doesn’t work (`eval` throws an exception). So the best I could do was
make some Python that behaved oddly.But hopefully it turned out interesting.

### Solution

#### Nulls

The script has a bunch of null bytes in it. Different editors will display
these different ways. For example, in Vim:

![image-20221203113328993](https://0xdfimages.gitlab.io/img/image-20221203113328993.png)

Or Notepad++:

![image-20221203113429832](https://0xdfimages.gitlab.io/img/image-20221203113429832.png)

#### random

At the top of the script there’s a check that on first glance should only pass
one in a million times:

    
    
    if random.randrange(1000000):
    	sys.exit()
    

Only if `randrange(1000000)` returns 0 would this not exit. And yet, it always
does. What the null byte does is effectively end the line. In this case, its
in the null in the “things are not what they seem” message that leaves an open
`"""`. Effectively, that makes this:

![image-20221203114332983](https://0xdfimages.gitlab.io/img/image-20221203114332983.png)

The `print` that is never reached after the help message and exit includes the
`randrange` check as part of the string!

#### song

The next part of the script defines a string, `song`. It’s got a mix of
comments and `"""`. Looking at it, one might thing it would be something like:

    
    
    You know Dasher, and Dancer, andDonder and BlitzenRudolph, the red-nosed reindeeryou would even say it glows.They never let poor RudolphSanta came to say:Then all the reindeer loved himyou'll go down in history!
    

But if I run this and add a line to print `song` before the flag check, it
comes out as:

    
    
    You know Dasher, and Dancer, and#song += Donder and Blitzen#song += Rudolph, the red-nosed reindeer#song += you would even say it glows.#song += They never let poor Rudolph#song += Santa came to say:#song += Then all the reindeer loved him#song += you'll go down in history!
    

#### Flag

Once the `song` string has been built, the last bit of code uses it to xor the
input and check if the result matches a static list:

    
    
    flag = list(map(ord, sys.argv[1]))
    correct = [17, 55, 18, 92, 91, 10, 38, 8, 76, 127, 17, 12, 17, 2, 20, 49, 3, 4, 16, 8, 3, 58, 67, 60, 10, 66, 31, 95, 1, 93]
    
    for i,c in enumerate(flag):
        flag[i] ^= ord(song[i*10 % len(song)])
    
    if all([c == f for c,f in zip(correct, flag)]):
        print('''Congrats!''')
    else:
        print('''Try again!''') 
    

#### Solve

There are many ways to solve from this understanding. The key is to have the
right value as `song`, and then work backwards from `correct` to get the right
input. The simplest way is to just put a `print` inside the loop:

    
    
    for i,c in enumerate(flag):
        flag[i] ^= ord(song[i*10 % len(song)])
        print(chr(ord(song[i*10 % len(song)]) ^ correct[i]), end="", flush=True)
    print()
    

This will then get the flag characters back out, printed on one line. I know
that the flag is 30 characters, so I’ll put in 30 `a` as input, and it gives
the flag:

    
    
    oxdf@hacky$ python ~/Downloads/gh0st.py aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    Nice job getting lucky there! But did you get the flag?
    HV22{nUll_bytes_st0mp_cPy7h0n}
    Try again!
    

**Flag:`HV22{nUll_bytes_st0mp_cPy7h0n}`**

## HV22.04

### Challenge

![hv22-ball04](https://0xdfimages.gitlab.io/img/hv22-ball04.png) | HV22.04 Santas radians  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | easy  
Author: |  dr_nick   
  
> Santa, who is a passionate mathematician, has created a small website to
> train his animation coding skills. Although Santa lives in the north pole,
> where the **degrees** are very low, the website’s animation luckily did not
> freeze. It just seems to move very slooowww. But how does this help…? The
> elves think there might be a flag in the application…

The instance shows a webpage:

![image-20221204151145298](https://0xdfimages.gitlab.io/img/image-20221204151145298.png)

The disks turn as my mouse moves across the page.

### Solution

The source for this page is actually quite simple:

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>The UPICode</title>
    </head>
    <body>
    
    <h3>[HV22.04] Santa's radians</h3>
    
    <canvas width="1200" height="200" id="canvasPiCode" style="border: 1px solid black"></canvas>
    <script>
        const canvas = document.getElementById("canvasPiCode");
        const context = canvas.getContext("2d");
        let clientX = 0;
    
        canvas.addEventListener('mousemove', e => {
            clientX = e.clientX*7/1000;
        });
    
        let rot = [2.5132741228718345, 0.4886921905584123, -1.2566370614359172, 0, 2.548180707911721, -1.9547687622336491, -0.5235987755982988, 1.9547687622336491, -0.3141592653589793, 0.6283185307179586, -0.3141592653589793, -1.8151424220741028, 1.361356816555577, 0.8377580409572781, -2.443460952792061, 2.3387411976724013, -0.41887902047863906, -0.3141592653589793, -0.5235987755982988, -0.24434609527920614, 1.8151424220741028];
        let size = canvas.width / (rot.length+2);
    
        context.strokeStyle = "black";
        context.lineWidth = size*5/16;
        context.shadowOffsetX = size/4;
        context.shadowOffsetY = size/4;
        context.shadowColor = "gray";
        context.shadowBlur = size/4;
    
        let animCount = 0;
    
        function anim() {
            context.clearRect(0,0,canvas.width,canvas.height);
            for (let i = 0; i < rot.length; i++) {
                context.beginPath();
                context.arc((i + 1) * size, canvas.height / 2, size * 2 / 7, rot[i]+animCount+clientX, rot[i] + 5 +animCount+clientX);
                context.stroke();
            }
            animCount+=0.001;
            requestAnimationFrame(anim);
        }
        anim();
    
    </script>
    
    </body>
    </html>
    

The `rot` array is the list of radians offset for each disk. It’s also the
only place I can see that a flag could be hidden. I’ll drop into a Python
interpreter and load these numbers:

    
    
    >>> rot = [2.5132741228718345, 0.4886921905584123, -1.2566370614359172, 0, 2.548180707911721, -1.9547687622336491, -0.5235987755982988, 1.9547687622336491, -0.3141592653589793, 0.6283185307179586, -0.3141592653589793, -1.8151424220741028, 1.361356816555577, 0.8377580409572781, -2.443460952792061, 2.3387411976724013, -0.41887902047863906, -0.3141592653589793, -0.5235987755982988, -0.24434609527920614, 1.8151424220741028];
    

The challenge has the word “degrees” in bold, so I’ll convert to degrees:

    
    
    >>> import math
    >>> deg = [r * 180 / math.pi for r in rot]
    >>> deg
    [144.0, 28.0, -72.0, 0.0, 146.0, -112.0, -29.999999999999996, 112.0, -18.0, 36.0, -18.0, -104.00000000000001, 78.0, 48.0, -140.0, 133.99999999999997, -24.0, -18.0, -29.999999999999996, -14.0, 104.00000000000001]
    

Each is basically a round number. I’ll force them to be ints:

    
    
    >>> deg = [round(r * 180 / math.pi) for r in rot]
    >>> deg
    [144, 28, -72, 0, 146, -112, -30, 112, -18, 36, -18, -104, 78, 48, -140, 134, -24, -18, -30, -14, 104]
    

At this point, it’s not clear how this translates to a flag. I was noting that
it can’t be one-to-one, as both -72 and 0 would have to be “2” for the flag
format `HV22{}`. But that’s where the 0 is interesting. What if these are
deltas, or changes from the previous character?

“H” is 72, which is half of 144. “V” is 86. 86 is 14 more than “H”, and the
number here is 28 (twice 14).

I’ll get a flag like this:

    
    
    >>> for i in range(len(deg)):
    ...     print(chr(sum(deg[:i+1])//2), end='', flush=True)
    ... 
    HV22{C4lcul8_w1th_PI}
    

**Flag:`HV22{C4lcul8_w1th_PI}`**

## HV22.05

### Challenge

![hv22-ball05](https://0xdfimages.gitlab.io/img/hv22-ball05.png) | HV22.05 Missing gift  
---|---  
Categories: |  ![forensic](../img/hv-cat-forensic.png)FORENSIC  
![fun](../img/hv-cat-fun.png)FUN  
![network_security](../img/hv-cat-network_security.png)NETWORK_SECURITY  
Level: | easy  
Author: |  wangibangy   
  
> Introduction:
>
> Like every year the elves were busy all year long making the best toys in
> Santas workshop. This year they tried some new fabrication technology. They
> had fun using their new machine, but it turns out that the last gift is
> missing.
>
> Unfortunately, Alabaster who was in charge of making this gift is not
> around, because he had to go and fulfill his scout elf duty as an elf on the
> shelf.
>
> But due to some very lucky circumstances the IT-guy elf was capturing the
> network traffic during this exact same time.
>
> Goal:
>
> Can you help Santa and the elves to fabricate this toy and find the secret
> message?

There is a resource named `tcpdump.pcap` to download that is a PCAP file:

    
    
    oxdf@hacky$ file tcpdump.pcap 
    tcpdump.pcap: pcap capture file, microsecond ts (little-endian) - version 2.4 (Linux cooked v2, capture length 262144)
    

### Solution

#### Open In Wireshark

When I try to open this file in Wireshark, I get a message about “network type
276 unknown or unsupported Error”. I used the instructions on [this
post](https://nickvsnetworking.com/fixing-wireshark-tcpdump-pcap-network-
type-276-unknown-or-unsupported-error/) to update to the latest version of
Wireshark, and then that goes away.

#### Enumerate PCAP

The PCAP has a bunch of conversations initiating from 10.0.2.15, as well as
some from 172.18.0.2:

![image-20221204192455930](https://0xdfimages.gitlab.io/img/image-20221204192455930.png)

There’s a bunch of HTTP and HTTPS traffic:

![image-20221204192546835](https://0xdfimages.gitlab.io/img/image-20221204192546835.png)

#### Find GCode File

Looking through the streams, the sessions between 10.0.2.15 and 10.0.2.2 seem
most interesting. Most of the others are just loading real pages on the
internet and downloading things, and much is under TLS, which I have no way to
access.

Looking at the exchange between these two, starting in TCP stream 21, there’s
a web request with a bunch of objects pulled down to support the page.
Eventually, in TCP stream 28, there’s a POST request that’s a form submission
uploading a file:

    
    
    POST /api/files/local HTTP/1.1
    Host: localhost:8080
    Connection: keep-alive
    Content-Length: 8753748
    sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
    X-CSRF-Token: ImQyMjdiOWZkYmJjZGIyY2MyMDkxYjhjZmE2Y2EyMzdlNWMyOTA3NzAi.Y3v-SA.UxLqR4O4zRoXA5Hp7SFDnnTwxLE
    sec-ch-ua-mobile: ?0
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryAsNAHrCNGBeryZ8A
    Accept: application/json, text/javascript, */*; q=0.01
    Cache-Control: no-cache
    X-Requested-With: XMLHttpRequest
    sec-ch-ua-platform: "Windows"
    Origin: http://localhost:8080
    Sec-Fetch-Site: same-origin
    Sec-Fetch-Mode: cors
    Sec-Fetch-Dest: empty
    Accept-Encoding: gzip, deflate, br
    Accept-Language: en-US,en;q=0.9,de-CH;q=0.8,de;q=0.7
    Cookie: remember_token_P8080=octoprint|1669069481.04053|96ea00738dd00764e087fbb48833e56663004b7ec2aee05a28a6eb56ca7deee70db8fefc4bd9ac49d242fd2d82f1878dd38124b986a741358172f0af7da80467; csrf_token_P8080=ImQyMjdiOWZkYmJjZGIyY2MyMDkxYjhjZmE2Y2EyMzdlNWMyOTA3NzAi.Y3v-SA.UxLqR4O4zRoXA5Hp7SFDnnTwxLE; session_P8080=.eJxlUUGKIzEM_IvPy2JZtiXlFgj5RrAtedKQ6YRu92EY9u_rYS7D7kUIlUoqqT7drW-2391pbIf9crdF3ckBCcQKMVHPFCAr99oKJgLfi1I1jZWAzWNQSqHGzI3YZ0gxEifJxmARqq89Ehj2SlZ8ltnK6BlQOaj1WSaeKc3RoBhaidqbanNTyLHb9q3m2cbztS3rmOVFbR3L-PhdjnG_jY-XudN6PB4_kP84j-fbst7erd3LuuzvE72P8ZrA14rd9n15rt8suCZ_RR9CAImXJHyldJkBzul8viD-w9mXt7WMY5saXKo5CJd5Zm1aIitYMy4Fo0D2Pom2jL60UFWMK1LggFrnGyBG8bE3IfGNKosQ5V5YsVDNiGINgCN7xulGL9MFztYVG0ixhgECBXF__gIXtYjp.Y3v-UA.dZvtJkgqUrSHlDZ-hkKNZ5CShDU
    
    ------WebKitFormBoundaryAsNAHrCNGBeryZ8A
    Content-Disposition: form-data; name="file"; filename="hv22.gcode"
    Content-Type: application/octet-stream
    
    ; GL HV - by Wangibangi
    M107
    G92 E0
    M190 S65
    M104 S216
    G28
    G1 Z5 F5000
    ...[snip]...
    

The file name being uploaded is `hv22.gcode`.

I’ll download this file from File -> Export Objects -> HTTP. It’s the largest
file, with the filename `local`:

![image-20221204193810837](https://0xdfimages.gitlab.io/img/image-20221204193810837.png)

#### View G-Code File

G-Code files are [3D printer job files(https://fileinfo.com/extension/gcode).
Googling for a way to open one online, I found
[ncviewer.com](https://ncviewer.com/). I’ll load the file in there, and after
a bit of messing with the orientation, I’ll find this:

![image-20221204191458863](https://0xdfimages.gitlab.io/img/image-20221204191458863.png)

**Flag:`HV22{this-is-a-w4ste-of-pl4stic}`**

## HV22.H1

### Challenge

![hv22-ballH1](https://0xdfimages.gitlab.io/img/hv22-ballH1.png) | HV22.H1 Santa's Secret  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | easy  
Author: |  wangibangy   
  
> _S4nt4444…..s0m3wh3r3 1n th3 34sy ch4ll4ng3sss…..th3r3s 4n 34sy fl4g
> h1ddd3333nnnn…..sssshhhhh_

There are three hidden flags this year (they show up on the scoreboard right
away). This means that there are three challenges that have a second flag in
them somewhere. The first comes in Day 05.

### Solution

Looking at the G-Code file, there are a ton of lines, but almost all of them
start with `G1` or `G92`:

    
    
    oxdf@hacky$ wc -l local
    311837 local
    oxdf@hacky$ cat local | cut -d' ' -f1 | sort | uniq -c | sort -nr
     308145 G1
       3664 G92
          5 
          4 ;G1
          3 M104
          2 M140
          1 ------WebKitFormBoundaryAsNAHrCNGBeryZ8A--
          1 ------WebKitFormBoundaryAsNAHrCNGBeryZ8A
          1 M84
          1 M82
          1 M190
          1 M109
          1 M107
          1 G90
          1 G28
          1 G28
          1 G21
          1 Content-Type:
          1 Content-Disposition:
          1 ;
    

I’ll filter those out and take a look:

    
    
    oxdf@hacky$ cat local | grep -Ev "^G(1|92) "
    ------WebKitFormBoundaryAsNAHrCNGBeryZ8A
    Content-Disposition: form-data; name="file"; filename="hv22.gcode"
    Content-Type: application/octet-stream
    
    ; GL HV - by Wangibangi
    M107
    M190 S65
    M104 S216
    G28
    
    M109 S216 
    G21
    G90
    M82
    M104 S210 ; set temperature
    M140 S60 ; set bed temperature
    ;G1 X34.st3r E36 ;)
    ;G1 X72.86 Y50.50 E123.104
    ;G1 X49.100 Y100.51 E110.45
    ;G1 X102.108 Y52.103 E33,125
    
    M104 S0 ; turn off temperature
    G28 X0  ; home X axis
    M84     ; disable motors
    
    M140 S0 ; set bed temperature
    
    ------WebKitFormBoundaryAsNAHrCNGBeryZ8A--
    

I’ll note that lines starting with `;` are comments, and the top one, “; GL HV
- by Wangibangi”, looks like a message (“Good luck, Hackvent”) from the
author.

The other commented lines are interesting. The first has a winky emoji, `:)`.
Looking closely, the string is also l33t-speak for “easter egg” (“34st3r
E36”).

The next line has two recognizable numbers, 72 and 86, or “HV”. I’ll convert
the rest to ASCII, and it’s a flag:

    
    
    >>> x = [72, 86, 50, 50, 123, 104, 49, 100, 100, 51, 110, 45, 102, 108, 52, 103, 33, 125]
    >>> ''.join([chr(c) for c in x])
    'HV22{h1dd3n-fl4g!}'
    

**Flag:`HV22{h1dd3n-fl4g!}`**

## HV22.06

### Challenge

![hv22-ball06](https://0xdfimages.gitlab.io/img/hv22-ball06.png) | HV22.06 privacy isn't given  
---|---  
Categories: |  ![exploitation](../img/hv-cat-exploitation.png)EXPLOITATION   
Level: | easy  
Author: |  HaCk0   
  
> As every good IT person, Santa doesn’t have all his backups at one place.
> Instead, he spread them all over the world. With this new blockchain
> unstoppable technology emerging (except Solana, this chain stops all the
> time) he tries to use it as another backup space. To test the feasibility,
> he only uploaded one single flag. Fortunately for you, he doesn’t understand
> how blockchains work.
>
> Can you recover the flag?
>
> Start the Docker in the `Resources` section. You will be able to connect to
> a newly created Blockchain. Use the following information to interact with
> the challenge.
>
> Wallet public key `0x28a8746e75304c0780e011bed21c72cd78cd535e` Wallet
> private key
> `0xa453611d9419d0e56f499079478fd72c37b251a94bfde4d19872c44cf65386e3`
> Contract address: `0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab`
>
> The source code of the contract is the following block of code:
>  
>  
>      // SPDX-License-Identifier: UNLICENSED
>      pragma solidity ^0.8.9;
>  
>      contract NotSoPrivate {
>          address private owner;
>          string private flag;
>  
>          constructor(string memory _flag) {
>              flag = _flag;
>              owner = msg.sender;
>          }
>  
>          modifier onlyOwner() {
>              require(msg.sender == owner);
>              _;
>          }
>  
>          function setFlag(string calldata _flag) external onlyOwner {
>              flag = _flag;
>          }
>      }
>  

There’s also a section called “Blockchain 101” about setting this all up, and
a button to spin up a docker instance.

### Solution

#### Video

I’ll walk through this solution in [this
video](https://www.youtube.com/watch?v=MpCd9hZu8bE):

#### Architecture / Contract

I’ll follow the instructions in the 101 section to setup a Metamask account,
and bring in the Docker as my network. In this scenario, the blockchain is
hosted on the personal docker instance, and that same instance creates
(“deploys”) an instance of the contract. I can also compile the contract and
deploy instances of it myself.

When I deploy my own version, it shows up under deployed contracts in remix:

![image-20221206142156324](https://0xdfimages.gitlab.io/img/image-20221206142156324.png)

I can load the given contract as well using the “At Address” field and the
given address in the prompt, and it shows up in the same place.

I’m able to call `setFlag` on the contracts I deployed, but not on the
challenge one.

#### Solve By Reading Storage

To solve the challenge, I’ll read the private variables even though they are
marked as private and no function exposes them. That’s because data on the
block chain is still public.

I’ll use Python:

    
    
    #!/usr/bin/env python3
    
    import json
    from web3 import Web3
    
    
    web3 = Web3(Web3.HTTPProvider('http://152.96.7.12:8545'))
    print(f'Connected: {web3.isConnected()}')
    
    address = "0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab"
    print(web3.eth.getStorageAt(contract.address, 1).decode())
    

I use `web3` to get what’s stored at the first slot of the given address. The
0 slot has the owner for this contract, the other variable.

Running this prints the flag:

    
    
    oxdf@hacky$ python solve.py 
    Connected: True
    HV22{Ch41nS_ar3_Publ1C}.
    

**Flag:`HV22{Ch41nS_ar3_Publ1C}`**

#### Solve by Dumping Blockchain

Alternatively, the flag is just readable on the blockchain, which I can read
using `curl` with the JSONRPC API function
[getTransactionByBlockNumberAndIndex](https://ethereum.org/en/developers/docs/apis/json-
rpc/#eth_gettransactionbyblocknumberandindex):

    
    
    oxdf@hacky$ curl -s --data-raw '{"jsonrpc":"2.0","method":"eth_getTransactionByBlockNumberAndIndex","params":["0x1","0x0"],"id":1}' -H 'Content-Type: application/json' -X POST http://152.96.7.2:8545/ | jq .
    {
      "id": 1,
      "jsonrpc": "2.0",
      "result": {
        "type": "0x2",
        "hash": "0x3d1803506b360496ac1174130a550576bd4fea778463cd2b64ea31fa542fe491",
        "chainId": "0x539",
        "nonce": "0x0",
        "blockHash": "0xed4f24e302f5a5da90a08279d46d8d916004350c0f9bd018fe38357ba79dce2f",
        "blockNumber": "0x1",
        "transactionIndex": "0x0",
        "from": "0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1",
        "to": null,
        "value": "0x0",
        "maxPriorityFeePerGas": "0x59682f00",
        "maxFeePerGas": "0xd09dc300",
        "gasPrice": "0x0",
        "gas": "0x3f85d",
        "input": "0x608060405234801561001057600080fd5b50604051610619380380610619833981810160405281019061003291906102b0565b806001908051906020019061004892919061008f565b50336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505061035a565b82805461009b90610328565b90600052602060002090601f0160209004810192826100bd5760008555610104565b82601f106100d657805160ff1916838001178555610104565b82800160010185558215610104579182015b828111156101035782518255916020019190600101906100e8565b5b5090506101119190610115565b5090565b5b8082111561012e576000816000905550600101610116565b5090565b6000604051905090565b600080fd5b600080fd5b600080fd5b600080fd5b6000601f19601f8301169050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b61019982610150565b810181811067ffffffffffffffff821117156101b8576101b7610161565b5b80604052505050565b60006101cb610132565b90506101d78282610190565b919050565b600067ffffffffffffffff8211156101f7576101f6610161565b5b61020082610150565b9050602081019050919050565b60005b8381101561022b578082015181840152602081019050610210565b8381111561023a576000848401525b50505050565b600061025361024e846101dc565b6101c1565b90508281526020810184848401111561026f5761026e61014b565b5b61027a84828561020d565b509392505050565b600082601f83011261029757610296610146565b5b81516102a7848260208601610240565b91505092915050565b6000602082840312156102c6576102c561013c565b5b600082015167ffffffffffffffff8111156102e4576102e3610141565b5b6102f084828501610282565b91505092915050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b6000600282049050600182168061034057607f821691505b60208210811415610354576103536102f9565b5b50919050565b6102b0806103696000396000f3fe608060405234801561001057600080fd5b506004361061002b5760003560e01c80633438e82c14610030575b600080fd5b61004a600480360381019061004591906101cc565b61004c565b005b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16146100a457600080fd5b8181600191906100b59291906100ba565b505050565b8280546100c690610248565b90600052602060002090601f0160209004810192826100e8576000855561012f565b82601f1061010157803560ff191683800117855561012f565b8280016001018555821561012f579182015b8281111561012e578235825591602001919060010190610113565b5b50905061013c9190610140565b5090565b5b80821115610159576000816000905550600101610141565b5090565b600080fd5b600080fd5b600080fd5b600080fd5b600080fd5b60008083601f84011261018c5761018b610167565b5b8235905067ffffffffffffffff8111156101a9576101a861016c565b5b6020830191508360018202830111156101c5576101c4610171565b5b9250929050565b600080602083850312156101e3576101e261015d565b5b600083013567ffffffffffffffff81111561020157610200610162565b5b61020d85828601610176565b92509250509250929050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b6000600282049050600182168061026057607f821691505b6020821081141561027457610273610219565b5b5091905056fea264697066735822122006d79705697cc43c480982ff5fe156b1e30f4d9ef246b621b479de48a80383ae64736f6c6343000809003300000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000017485632327b436834316e535f6172335f5075626c31437d000000000000000000",
        "accessList": [],
        "v": "0x0",
        "r": "0xe680815322c470942f7f54d64e85169a9313dfaa58dc0f871ef722b594f57b2b",
        "s": "0x3c42cbcf89cf9505d1d7d3610098d31d9f21c810cea07420540ae3bf5984a8d5"
      }
    }
    

There’s only a single block, which I believe is the creation of the object.
The `result.input` field has a hex encoded binary blob that includes the
plaintext parameters passwed in. I’ll get that field with `jq`, remove the
`0x` with `cut`, and then decode it with `xxd -r -p`:

    
    
    oxdf@hacky$ curl -s --data-raw '{"jsonrpc":"2.0","method":"eth_getTransactionByBlockNumberAndIndex","params":["0x1","0x0"],"id":1}' -H 'Content-Type: application/json' -X POST http://152.96.7.2:8545/ | jq -r '.result.input' | cut -c3- | xxd -r -p
    `�`@R4�aW`��[P`@Qa8�a�9��`@R��a2��a�V[�`��Q�` �aH���a�V[P3`�a
    �T�s����������������������s���������������������UPPaZV[��Ta��a(V[�`R` ` �`` ����a�W`�UaV[�`a�W�Q`����UaV[��`�U�aW��[��aW�Q�U�` ��`�a�V[[P�Pa��aV[P�V[[��a.W`�`�UP`aV[P�V[``@Q�P�V[`��[`��[`��[`��[```��P��PV[NH{q`RV[P��PPPV[`�`�a�Wa�aFV[[�Qa���` �a@V[�PP��PPV[`` ��a�Wa�a<V[[`�Qg���������a�Wa�aAV[[a����a�V[�PP��PPV[NH{q`R`"`R`$`�[``��P`��a@W`��P[` ��aTWaSa�V[[P��PV[a��ai`9`��`�`@R4�aW`��[P`6a+W`5`��c48�,a0W[`��[aJ`�6��aE��a�V[aLV[[`�T�a
    �s��������������������s��������������������3s��������������������a�W`��[��`��a����a�V[PPPV[��TaƐaHV[�`R` ` �`` ����a�W`�Ua/V[�`aW�5`����Ua/V[��`�U�a/W��[��a.W�5�U�` ��`�aV[[P�Pa<��a@V[P�V[[��aYW`�`�UP`aAV[P�V[`����avV[�P�PP�P��PV[NH{q`R`"`R`$`�[``��P`��a`W`��P[` ��atWasaV[[P��PV��dipfsX" חi|�<H�` ���_�V��M��F�!�y�H���dsolcCaabV[[3 HV22{Ch41nS_ar3_Publ1C}
    

There’s a bunch of other stuff in there, but at the end, the flag is there:

    
    
    oxdf@hacky$ curl -s --data-raw '{"jsonrpc":"2.0","method":"eth_getTransactionByBlockNumberAndIndex","params":["0x1","0x0"],"id":1}' -H 'Content-Type: application/json' -X POST http://152.96.7.2:8545/ | jq -r '.result.input' | cut -c3- | xxd -r -p | tail -c 120
    ��F�!�y�H���dsolcC      3 HV22{Ch41nS_ar3_Publ1C}
    

## HV22.07

### Challenge

![hv22-ball07](https://0xdfimages.gitlab.io/img/hv22-ball07.png) | HV22.07 St. Nicholas's animation  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | easy  
Author: |  kuyaya   
  
> Santa has found a weird device called an “Oxocard Blockly”, which seems to
> display a sequence of images. He believes it has got something to do with a
> QR code, but it doesn’t seem complete…
>
> You can’t fly to the north pole, so Santa sent you a video of the device in
> action.
>
> The elves are having a karaoke and left with in a hurry while singing into
> their micro. This means that they aren’t there to help him, so now is your
> chance to make a good impression and find the flag!

It includes [this
video](https://drive.google.com/u/1/uc?id=1bLinhrz2lK5LI9MQrBM_xDV5c8l5dXsD&export=download):

### Solution

#### Understand Video

The video shows some patterns, then what might be a battery:

![image-20221206201400533](https://0xdfimages.gitlab.io/img/image-20221206201400533.png)

Then some more patterns, before showing four full boxes, top left, top right,
bottom left, bottom right:

![image-20221206201435215](https://0xdfimages.gitlab.io/img/image-20221206201435215.png)
![image-20221206201451929](https://0xdfimages.gitlab.io/img/image-20221206201451929.png)
![image-20221206201505297](https://0xdfimages.gitlab.io/img/image-20221206201505297.png)
![image-20221206201519246](https://0xdfimages.gitlab.io/img/image-20221206201519246.png)

The next four look like pieces of a QR code:

![image-20221206201652190](https://0xdfimages.gitlab.io/img/image-20221206201652190.png)
![image-20221206201700951](https://0xdfimages.gitlab.io/img/image-20221206201700951.png)
![image-20221206201710786](https://0xdfimages.gitlab.io/img/image-20221206201710786.png)
![image-20221206201722558](https://0xdfimages.gitlab.io/img/image-20221206201722558.png)

#### Micro QR Code Background

Some Googling for small QR codes leads to Micro QR Codes. [This
page](https://www.accusoft.com/barcodes/micro-qr-quick-response-codes/) from
accusoft describes them:

> The Quick Response (QR) code was revolutionary for its ability to store far
> more information than was possible with traditional, one dimensional
> barcodes. In some use cases, this ability to encode so much data makes the
> QR Code larger than necessary. That’s why Denso Wave created a smaller, more
> compact version in 1994 called the Micro QR Code. The code is frequently
> used to track very small components like circuit boards and other electronic
> parts. Micro QR Code is a public domain 2D barcode covered under the
> [ISO/IEC 18004:2015 standard](https://www.iso.org/standard/62021.html). Like
> their bigger cousins, Micro QR Codes can encode Japanese Kanji, Kana, and
> Hiragana characters.
>
> While a conventional QR Code uses three finder pattern squares to enable
> barcode readers to orient the image properly, a Micro QR Code uses a single
> finder pattern square in the upper-left corner. It also requires only a two-
> module wide “quiet zone” around the edge of the symbol, as opposed to the
> four-module wide margin needed for a regular QR Code. These differences,
> along with the fact that Micro QR Codes encode data more efficiently,
> prevent the code from becoming much larger even as the amount of data stored
> increases, which is a challenge with regular QR Codes.

Some examples from their page are:

![image-20221206201330260](https://0xdfimages.gitlab.io/img/image-20221206201330260.png)

#### Build Micro QR Code

I tried a few ways to build the QR code. I started by copying and pasting into
Gimp, but I couldn’t get something that would read. I also tried using a
[Conway’s Game of Life](https://playgameoflife.com/) simulator, since it’s
easy to turn boxes on and off. That didn’t work either (and was a pain when I
accidentally hit play).

I’ll open KolourPaint, and zoom in as far as it will go (1600%). Then
selecting the smallest pencil tip, I can color one pixel at a time. It makes
this:

![image-20221206202208881](https://0xdfimages.gitlab.io/img/image-20221206202208881.png)

When I save this, it looks like this:

![](https://0xdfimages.gitlab.io/img/hv22-07-code-tiny.png)

That’s too small to be reliably read, but I’ll take a screenshot of the zoomed
in image and save it as a larger size:

![](https://0xdfimages.gitlab.io/img/hv22-07-code.png)

#### Read Code

Finding a reader that would understand a Micro QR was a bit of a challenge.
Eventually I’ll find [this one](https://www.dynamsoft.com/barcode-
reader/barcode-types/micro-qr-code/) from Dynamsoft. I’ll give it that image,
and it returns the flag:

![image-20221206202511257](https://0xdfimages.gitlab.io/img/image-20221206202511257.png)

**Flag:`HV22{b0f}`**

[medium »](/hackvent2022/medium)

[](/hackvent2022/easy)

