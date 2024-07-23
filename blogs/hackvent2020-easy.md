# Hackvent 2020 - Easy

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [encoding](/tags#encoding )
[gimp](/tags#gimp ) [python](/tags#python ) [stegsolve](/tags#stegsolve )
[steganography](/tags#steganography ) [cyberchef](/tags#cyberchef )
[crypto](/tags#crypto ) [known-plaintext](/tags#known-plaintext )
[bkcrack](/tags#bkcrack ) [binwalk](/tags#binwalk ) [steghide](/tags#steghide
)  
  
Jan 1, 2021

  * Hackvent 2020  
easy

  * [medium](/hackvent2020/medium)
  * [hard](/hackvent2020/hard)
  * [leet(ish)](/hackvent2020/leet)

![](https://0xdfimages.gitlab.io/img/hackvent2020-easy-cover.png)

Hackvent started out early with a -1 day released on 29 November. There were
seven easy challenges, including -1, one hidden, and five daily challenges.
These challenges were heavy in crypto, image editing / steg, and encoding. My
favorite in the group was Chinese Animals, where I spent way more figuring out
what was going on after solving than actually solving.

## HV20.(-1)

### Challenge

![hv20-ball-1](https://0xdfimages.gitlab.io/img/hv20-ball-1.png) | HV20.-1 Twelve steps of christmas  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | easy  
Author: |  [Bread](https://twitter.com/nonsxd)  
  
> IOn the third day of christmas my true love sent to me…
>
> three caesar salads, two to (the) six basic arguments, one quick response.

There’s also an attached message. It has two parts, separated by an empty
line:

    
    
    $ head -5 db47d0fc-3dde-4f97-9362-df01946699d9.txt
    Sbopb 3 alkb! Lcc tfqe vlr! Dbq yxzh ql tloh! Vlr'ob klq alkb ebob...
    
    fSYLOt0HDdlXXXXKPReBRdXXXWlXXXDxZXXXXXXQyan/XXXGfUmRTEOPVUzdzEGsWjipWPY0bUYi
    FDS4xTVXXEgxoSeyhrP4AcwkHUtBdf+Nu+Bwtgct8W0Gnnlc07sbfUCUiHPfHYYBGeGNr/2ccu/3
    I/vCCouITTqmmUg8mWWx6Ifl/s41L4mMaouA/yjPo+MrcPMdEEDL94y2buybwu8MsKxN8UUz1baL
    ...[snip]...
    

The base64-encoded looking blob continues for many more lines.

### Solution

#### First Line

The message has two parts. The top line is:

    
    
    Sbopb 3 alkb! Lcc tfqe vlr! Dbq yxzh ql tloh! Vlr'ob klq alkb ebob...
    

The top line of the song, “three caesar salads” applies here. The [Caesar
Cipher](https://en.wikipedia.org/wiki/Caesar_cipher) involves shifting each
letter by a constant number, so for example if the key was three, A –> D, B –>
E, C –> F, and Z –> C. When the key is 13, this transform is known as ROT13.

I dumped the message into
[cyberchef](https://gchq.github.io/CyberChef/#recipe=ROT13\(true,true,3\)&input=U2JvcGIgMyBhbGtiISBMY2MgdGZxZSB2bHIhIERicSB5eHpoIHFsIHRsb2ghIFZscidvYiBrbHEgYWxrYiBlYm9iLi4uCg)
with the ROT13 operation (which offers a key parameter for non-13 keys), and
when the key is three (fits the clue), a message pops out:

    
    
    Verse 3 done! Off with you! Get back to work! You're not done here...
    

#### Rest

The rest looks like a base64 encoded blob:

    
    
    $ head -5 db47d0fc-3dde-4f97-9362-df01946699d9.txt
    Sbopb 3 alkb! Lcc tfqe vlr! Dbq yxzh ql tloh! Vlr'ob klq alkb ebob...
    
    fSYLOt0HDdlXXXXKPReBRdXXXWlXXXDxZXXXXXXQyan/XXXGfUmRTEOPVUzdzEGsWjipWPY0bUYi
    FDS4xTVXXEgxoSeyhrP4AcwkHUtBdf+Nu+Bwtgct8W0Gnnlc07sbfUCUiHPfHYYBGeGNr/2ccu/3
    I/vCCouITTqmmUg8mWWx6Ifl/s41L4mMaouA/yjPo+MrcPMdEEDL94y2buybwu8MsKxN8UUz1baL
    

The blob doesn’t decode to anything interesting. The first line is the clue,
when it says “You’re not done here…”. It is a way to check that I’m
successfully applying the first line, but I still need to apply that to the
blob.

Switching to the command-line, I’ll use `grep` to remove the first and empty
line, then `tr` to do that Caesar translation, then `base64` to decode. Once I
do that, `xxd` provides a hex dump, which shows the results is a PNG:

    
    
    $ cat db47d0fc-3dde-4f97-9362-df01946699d9.txt | grep -v -E -e '^$' -e Sbopb | tr 'A-Za-z' 'D-ZA-Cd-za-c' | base64 -d | xxd | head
    00000000: 8950 4e47 0d0a 1a0a 0000 000d 4948 4452  .PNG........IHDR
    00000010: 0000 019a 0000 019a 0800 0000 0013 6dda  ..............m.
    00000020: bf00 0009 897a 5458 7452 6177 2070 726f  .....zTXtRaw pro
    00000030: 6669 6c65 2074 7970 6520 6578 6966 0000  file type exif..
    00000040: 78da ad58 5b92 e4b8 0dfc e729 7c04 822f  x..X[......)|../
    00000050: 90c7 e133 c237 f0f1 9d09 aaaa 1fd3 bbde  ...3.7..........
    00000060: 8971 5794 a4a2 2810 4426 1250 bbfd 9f7f  .qW...(.D&.P....
    00000070: 1ff7 2ffc 8516 bc4b 596b 69a5 78fc a596  ../....KYki.x...
    00000080: 5ae8 b8a8 fefe 353b 8a4f 76bc 43fd b992  Z.....5;.Ov.C...
    00000090: afe3 ee7d 23e0 1c71 8ef7 86f6 7b16 decf  ...}#..q....{...
    

#### Contrast

After removing `xxd` and `head`, and directing the output to a file, the image
looks just white:

![](https://0xdfimages.gitlab.io/img/hv2020--1-solve.png)

Still, the last line suggests I should get one quick response (QR). Looking at
it in Gimp, I’ll select Color -> Auto -> Stretch Contrast …, and it pops out
as a QR Code:

![](https://0xdfimages.gitlab.io/img/hv2020--1-solve-contrast.png)

This image contains the flag:

**Flag:`HV20{34t-sl33p-haxx-rep34t}`**

## HV20.01

### Challenge

![hv20-ball01](https://0xdfimages.gitlab.io/img/hv20-ball01.png) | HV20.01 Happy HACKvent 2020  
---|---  
Categories: |  ![forensic](../img/hv-cat-forensic.png)FORENSIC   
Level: | easy  
Author: |  [mij-the-dj](https://twitter.com/janicmikes)  
  
> Welcome to this year’s HACKvent.
>
> Attached you can find the “Official” invitation to the HackVent.

![letter](https://0xdfimages.gitlab.io/img/7c432457-ed44-4ebe-84bf-
cb6966e7a3dc.png)

> One of my very young Cyber Elves cut some parts of the card with his alpha
> scissors.
>
> Have a great HACKvent,
>
> – Santa

### Solution

I’ll show three ways to solve, using StegSolve, Gimp, and Python.

#### StegSolve

On seeing the image, along with the mention of messing with alpha, which is a
[channel in an image](https://www.techopedia.com/definition/1945/alpha-
channel), and immediately I loaded the file in
[Stegsolve](https://github.com/eugenekolo/sec-
tools/tree/master/stego/stegsolve/stegsolve).

The first transform is Color Inversion (XOR) pops the flag right out:

![image-20201130182716637](https://0xdfimages.gitlab.io/img/image-20201130182716637.png)

A bunch of the other filters solve it as well.

#### Gimp

To really see what’s going on, I’ll open the image in Gimp, and also open the
Pointer dialog from Windows –> Dockable Dialogs –> Pointer. This will show
information about whatever pixel my cursor is currently over:

![image-20201201093713232](https://0xdfimages.gitlab.io/img/image-20201201093713232.png)

Gimp shows the image with transparency boxes over where I’d expect the flag to
be:

![image-20201201093812987](https://0xdfimages.gitlab.io/img/image-20201201093812987.png)

Moving the cursor around the picture, the alpha value is set to 255 everywhere
except in those boxes, where it’s 0. The alpha channel represents the
transparency or opacity of the color at that pixel, where 0 is completely
transparent and 255 is full opacity. Because the sections with the flag are
fully transparent, it isn’t possible to read their values.

Selecting the eraser tool, setting the Opacity to 100, and dragging it over
the checkerboard boxes removes the transparency, leaving the flag:

![image-20201201094348715](https://0xdfimages.gitlab.io/img/image-20201201094348715.png)

#### Python

To solve this with Python, I can open the image using Pillow, and just edit
the alpha channel to 255 for each pixel. [This
post](https://nerdparadise.com/programming/pythonpil) gives a good intro on
editing an image. I’ll open it, convert to to RGBA (to include the Alpha
channel), and then loop over the pixels, for each setting Alpha to 255:

    
    
    #!/usr/bin/env python3
    
    from PIL import Image
    
    
    image = Image.open("7c432457-ed44-4ebe-84bf-cb6966e7a3dc.png").convert('RGBA')
    pixels = image.load()
    
    for i in range(image.width):
        for j in range(image.height):
            pixel = pixels[i, j]
            pixels[i, j] = (pixel[0], pixel[1], pixel[2], 255)
    
    image.save("no_alpha.png")
    

The resulting image has the flag:

![](https://0xdfimages.gitlab.io/img/hv2020-1-no_alpha.png)

**Flag:`HV20{7vxFXB-ItHnqf-PuGNqZ}`**

## HV20.02

### Challenge

![hv20-ball02](https://0xdfimages.gitlab.io/img/hv20-ball02.png) | HV20.02 Chinese Animals  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | easy  
Author: |  [The Compiler](https://twitter.com/the_compiler)  
  
> I’ve received this note from a friend, who is a Chinese CTF player:
>

>> 恭喜！收旗爲：ＨＶ２０｛獭慬氭敬敧慮琭扵瑴敲晬礭汯癥猭杲慳猭浵搭桯牳ｅ｝

>
> Unfortunately, Google Translate wasn’t of much help:

![](https://0xdfimages.gitlab.io/img/9362e5e7-61d3-4060-81e6-da9fbf5327d3.png)

> ![](https://0xdfimages.gitlab.io/img/e496ffb6-ee2d-45bc-
> aa6b-3a81a2de4618.png)

> I suspect the data has somehow been messed up while transmitting it.
>
> Sadly, I can’t ask my friend about more details. The Great Chinese Firewall
> is thwarting our attempts to reach each other, and there’s no way I’m going
> to install WeChat on my phone.

### Solution

#### Flag

The solution is pretty easy to come by, playing around with different
encodings with `iconv` or in
[cyberchef](https://gchq.github.io/CyberChef/#recipe=Encode_text\('UTF-16BE%20\(1201\)'\)&input=542t5oWs5rCt5pWs5pWn5oWu55Ct5om155G05pWy5pms56St5rGv55ml54yt5p2y5oWz54yt5rW15pCt5qGv54mz)
dumps the flag when the data is converted to UTF-16:

    
    
    $ echo "獭慬氭敬敧慮琭扵瑴敲晬礭汯癥猭杲慳猭浵搭桯牳" | iconv --to-code=utf-16be
    small-elegant-butterfly-loves-grass-mud-hors
    

![image-20201202072229728](https://0xdfimages.gitlab.io/img/image-20201202072229728.png)

So the flag is:

**Flag:`HV20{small-elegant-butterfly-loves-grass-mud-horse}`**

#### Why?

I spent way longer looking at why this worked than actually solving the
challenge. [This post](https://kunststube.net/encoding/) is a really good
primer on how Unicode works.

I started off by looking at the input and output lengths:

    
    
    $ echo -n "獭慬氭敬敧慮琭扵瑴敲晬礭汯癥猭杲慳猭浵搭桯牳" | xxd
    00000000: e78d ade6 85ac e6b0 ade6 95ac e695 a7e6  ................
    00000010: 85ae e790 ade6 89b5 e791 b4e6 95b2 e699  ................
    00000020: ace7 a4ad e6b1 afe7 99a5 e78c ade6 9db2  ................
    00000030: e685 b3e7 8cad e6b5 b5e6 90ad e6a1 afe7  ................
    00000040: 89b3                                     ..
    $ echo -n "獭慬氭敬敧慮琭扵瑴敲晬礭汯癥猭杲慳猭浵搭桯牳" | iconv --to-code=utf-16be | xxd
    00000000: 736d 616c 6c2d 656c 6567 616e 742d 6275  small-elegant-bu
    00000010: 7474 6572 666c 792d 6c6f 7665 732d 6772  tterfly-loves-gr
    00000020: 6173 732d 6d75 642d 686f 7273            ass-mud-hors
    

The raw input is 66 bytes, whereas the output is 44 bytes. Just counting the
Chinese characters shows 22 characters. This implies that each Chinese
characters is three bytes, and that each is converted to two bytes of ascii.
And looking at a single character, that seems to be right:

    
    
    $ echo -n "獭" | xxd
    00000000: e78d ad                                  ...
    $ echo -n "獭" | iconv --to-code=utf-16be | xxd
    00000000: 736d                                     sm
    

So the question that remains is how does 0xe78dad become 0x736d?

[This page](https://www.fileformat.info/info/unicode/char/736d/index.htm)
about the otter character shows that I’m on the right track in how I’m
thinking about this:

![image-20201202073414638](https://0xdfimages.gitlab.io/img/image-20201202073414638.png)

UTF encodings are quite complicated. UTF-8 can have between 1 and 4 bytes per
character. For characters up to 0xFFFF, they map 1:1 to UTF-16 characters
(which are typically two bytes). But once it goes above that, the mapping is
no longer so transparent.

[This code in C](https://github.com/PetropoulakisPanagiotis/utf-
converter/blob/master/utf8_to_utf16.c) from GitHub reads in UTF-8 characters
and translates them in to UTF-16. It starts by reading in on character. If the
top bit is 0, then it converts that to 16 bits (0 filling the top), and prints
it. Otherwise, based on the high bits, it can tell if the character is two,
three, or four bytes. It reads in the right number, does some math, and
outputs the result.

For this case, all of the characters start with `1110`, which indicates a
three-byte character. Looking in the hex dump of the input above, you’ll
notice that every third character starts with hex `e`.

To convert to UTF-16 from UTF-8, I’ll take the low four bits from the first
character, the low six bits from the next two, and put them together, like
this in Python:

    
    
    >>> c1 = 0xe7; c2 = 0x8d; c3 = 0xad
    >>> f'{c1 & 0xf:04b}'
    '0111'
    >>> f'{c2 & 0x3f:06b}'
    '001101'
    >>> f'{c3 & 0x3f:06b}'
    '101101'
    >>> f'{c1 & 0xf:04b}{c2 & 0x3f:06b}{c3 & 0x3f:06b}' 
    '0111001101101101'
    >>> hex(int(f'{c1 & 0xf:04b}{c2 & 0x3f:06b}{c3 & 0x3f:06b}', 2))
    '0x736d'
    

It could also be expressed as:

    
    
    >>> hex(((c1 & 0xf) << 12) | ((c2 & 0x3f) << 6) | (c3 & 0x3f))
    '0x736d'
    

Interestingly, in Python, `ord` will also convert a character to it’s raw
code, which happens to be the two bytes used for UTF-16:

    
    
    >>> hex(ord('獭'))
    '0x736d'
    

So this challenge could also be solved with a one-liner using list
comprehension, `ord`, and `binascii`:

    
    
    >>> binascii.unhexlify(''.join([hex(ord(c))[2:] for c in '獭慬氭敬敧慮琭扵瑴敲晬礭汯癥猭杲慳猭浵搭桯牳']))
    b'small-elegant-butterfly-loves-grass-mud-hors'
    

## HV20.03

### Challenge

![hv20-ball03](https://0xdfimages.gitlab.io/img/hv20-ball03.png) | HV20.03 Packed gifts  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO   
Level: | easy  
Author: |  [darkstar](https://twitter.com/___darkstar__)  
  
> One of the elves has unfortunately added a password to the last presents
> delivery and we cannot open it. The elf has taken a few days off after all
> the stress of the last weeks and is not available. Can you open the package
> for us?
>
> We found the following packages:
>
>   * [Package 1](/files/790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip)
>   * [Package 2](/files/941fdd96-3585-4fca-a2dd-e8add81f24a1.zip)
>

The two files are both zip archives:

    
    
    $ file *.zip
    790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip: Zip archive data, at least v?[0x314] to extract
    941fdd96-3585-4fca-a2dd-e8add81f24a1.zip: Zip archive data, at least v?[0x314] to extract
    

### Solution

#### Examine the Zips

The first package contains 100 files, all the same size, same timestamp:

    
    
    $ unzip -l 790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip
    Archive:  790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip
      Length      Date    Time    Name    
    ---------  ---------- -----   ----    
          172  2020-11-24 09:07   0000.bin
          172  2020-11-24 09:07   0001.bin
          172  2020-11-24 09:07   0002.bin
          172  2020-11-24 09:07   0003.bin
          172  2020-11-24 09:07   0004.bin
    ...[snip]...
          172  2020-11-24 09:07   0097.bin
          172  2020-11-24 09:07   0098.bin
          172  2020-11-24 09:07   0099.bin
    ---------                     -------
        17200                     100 files
    
    

The second looks exactly the same, but there’s one extra file, `flag.bin`:

    
    
    $ unzip -l 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip                                         
    Archive:  941fdd96-3585-4fca-a2dd-e8add81f24a1.zip
      Length      Date    Time    Name    
    ---------  ---------- -----   ----    
          172  2020-11-24 09:07   0000.bin 
          172  2020-11-24 09:07   0001.bin
          172  2020-11-24 09:07   0002.bin
          172  2020-11-24 09:07   0003.bin
          172  2020-11-24 09:07   0004.bin
    ...[snip]...
          172  2020-11-24 09:07   0097.bin
          172  2020-11-24 09:07   0098.bin
          172  2020-11-24 09:07   0099.bin
          172  2020-11-24 09:25   flag.bin
    ---------                     -------
        17372                     101 files
    

The first will unzip, and I can look at the contents of the files. They each
contain a single 172 character base64-encoded string, and they each decode to
what looks like random garbage.

The second archive is encrypted with a password.

#### Known Plaintext - Fail

The challenge is screaming known plaintext attack. Some googling for “known
plaintext zip” led to some [academic
papers](https://math.ucr.edu/~mike/zipattacks.pdf) as well as a tool
[bkcrack](https://github.com/kimci86/bkcrack). This tool takes two zips, one
encrypted and the other not, as well as the names of files in each zip that
are the same content. It then generates the encryption keys needed to pull
files from the password protected archive.

I originally assumed that all the bin files were the same, and gave it a run:

    
    
    $ ./bkcrack -C 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip  -c 0000.bin -P 790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip -p 0000.bin
    bkcrack 1.0.0 - 2020-11-11
    Generated 4194304 Z values.                                                                                          
    [21:02:13] Z reduction using 151 bytes of known plaintext
    100.0 % (151 / 151)
    54497 values remaining.
    [21:02:14] Attack on 54497 Z values at index 8
    100.0 % (54497 / 54497)
    [21:05:32] Could not find the keys.
    

It ran for a few minutes and failed.

#### Find Same File

Eventually it is worth questioning the assumption that all the files with the
same names were the same. To check, I looked at the CRCs for each file in each
archive. Zip archives store the CRC of the plaintext file, even for encrypted
archives. That means if the files are the same, the CRCs should match.

I wrote a short Python script to check each file in the encrypted archive and
see if the file with the same name in the unencrypted archive had the same
CRC:

    
    
    #!/usr/bin/env python3
    
    from zipfile import ZipFile
    
    
    crcs = {}
    
    with ZipFile('790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip', 'r') as arc:
        for meta in arc.infolist():
            crcs[meta.filename] = meta.CRC
    
    
    with ZipFile('941fdd96-3585-4fca-a2dd-e8add81f24a1.zip', 'r') as arc:
        for meta in arc.infolist():
            if meta.filename in crcs and crcs[meta.filename] == meta.CRC:
                print(meta.filename)
    

It turns out that only one file had a matching CRC:

    
    
    $ python3 check_CRCs.py 
    0053.bin
    

In talking with a friend after the challenge, he mentioned using `zip2john` to
get the CRCs and manually compare. I wanted to see if I could turn that into a
Bash one-liner. I had all the `.bin` files from the first package in a folder,
so I’ll use `crc32` to calculate their CRCs, and after some formatting, use
those as a file of `grep` inputs on the `zip2john` output to find the file:

    
    
    $ zip2john 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip 2>&1 | grep -f <(crc32 package1/*.bin | awk '{print $1}' | tr '[:lower:]' '[:upper:]')
    ver 78.8 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip/0053.bin PKZIP Encr: cmplen=171, decmplen=172, crc=FCD6B08A
    

This breaks down to:

  * `zip2john [encrypted zip] 2>&1` \- generate hashes and information for each file in the archive, including the CRC.
  * `<(crc32 package1/*.bin | awk '{print $1}' | tr '[:lower:]' '[:upper:]')` \- generate CRCs for each of the unzipped files, isolating them one per line, and making the letters upper case (to match `zip2john` output); the `<( )` will have the terminal treat the output as the contents of a file.
  * `grep -f [file]` \- grep for any lines that contain any of the values in the given file, which in this case is the CRC values.

#### bkcrack

I’ll re-run `bkcrack` this time using `0053.bin`, and it finds the keys:

    
    
    $ bkcrack-1.0.0-Linux/bkcrack -C 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip  -c 0053.bin -P 790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip -p 0053.bin                                                                    
    bkcrack 1.0.0 - 2020-11-11
    Generated 4194304 Z values.
    [21:54:02] Z reduction using 151 bytes of known plaintext
    100.0 % (151 / 151)
    53880 values remaining.
    [21:54:04] Attack on 53880 Z values at index 7
    Keys: 2445b967 cfb14967 dceb769b
    68.8 % (37074 / 53880)
    [21:56:07] Keys
    2445b967 cfb14967 dceb769b   
    

I can use those keys to pull `flag.bin` from the encrypted zip:

    
    
    $ bkcrack-1.0.0-Linux/bkcrack -c flag.bin -d flag.bin -C 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip -k 2445b967 cfb14967 dceb769b
    bkcrack 1.0.0 - 2020-11-11
    Wrote deciphered text.
    

The resulting file is still compressed, and I’ll use the `inflate.py` script
from the same repo to decompress it, and grab the flag:

    
    
    $ python3 bkcrack-1.0.0-Linux/tools/inflate.py < flag.bin > flag.txt
    $ cat flag.txt
    SFYyMHtaaXBDcnlwdDBfdzF0aF9rbjB3bl9wbGExbnRleHRfMXNfZWFzeV90MF9kZWNyeXB0fSAgICAgICAgICAgICAgICAgSFYyMHtaaXBDcnlwdDBfdzF0aF9rbjB3bl9wbGExbnRleHRfMXNfZWFzeV90MF9kZWNyeXB0fQo=
    $ cat flag.txt | base64 -d
    HV20{ZipCrypt0_w1th_kn0wn_pla1ntext_1s_easy_t0_decrypt}                 HV20{ZipCrypt0_w1th_kn0wn_pla1ntext_1s_easy_t0_decrypt}
    

**Flag:`HV20{ZipCrypt0_w1th_kn0wn_pla1ntext_1s_easy_t0_decrypt}`**

## HV20.H1

### Challenge

![hv20-ballH1](https://0xdfimages.gitlab.io/img/hv20-ballH1.png) | HV20.H1 It's a secret  
---|---  
Categories: |  ![hidden](../img/hv-cat-hidden.png)HIDDEN   
Level: | easy  
Author: |  [darkstar](https://twitter.com/___darkstar__)  
  
This appeared with HV20.03:

> Who knows where this could be hidden… Only the best of the best shall find
> it!
>
> We hide additional flags in some of the challenges! This is the place to
> submit them. There is no time limit for secret flags.

### Solution

Typically when the hidden challenges appear with a specific challenge, it’s a
good idea to dig further into that challenge. I had already run a loop over
all the `.bin` files in the unencrypted archive seeing if there were any clues
in the base64 decoded data. Now I turned to the encrypted zip.

I used the following loop to pull all the files from the encrypted archive
(using my directory with the bin files from the other package to get the
names):

    
    
    $ for f in $(ls package1/); do bkcrack-1.0.0-Linux/bkcrack -C 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip -k 2445b967 cfb14967 dceb769b -c $f -d package2/$f; done
    

Next I needed to inflate them all:

    
    
    $ for f in $(ls package1/); do bkcrack-1.0.0-Linux/tools/inflate.py < package2/$f > package2/${f}.inf; done
    

Now I’ll loop over each file, base64 decoding, and grepping for a flag (and
printing the filename if the `grep` matches):

    
    
    $ for f in $(ls package2/*.inf); do cat ${f} | base64 -d | grep -a HV20 && echo $f; done
    FU>>>>   HV20{it_is_always_worth_checking_everywhere_and_congratulations,_you_have_found_a_hidden_flag}   <<<<iaO^7
    package2/0042.bin.inf
    

It’s located in file number 42, the [Answer to the Ultimate Question of Life,
the Universe, and
Everything](https://en.wikipedia.org/wiki/Phrases_from_The_Hitchhiker's_Guide_to_the_Galaxy#Answer_to_the_Ultimate_Question_of_Life,_the_Universe,_and_Everything_\(42\)).

**Flag:`HV20{it_is_always_worth_checking_everywhere_and_congratulations,_you_have_found_a_hidden_flag}`**

## HV20.04

### Challenge

![hv20-ball04](https://0xdfimages.gitlab.io/img/hv20-ball04.png) | HV20.04 Br❤️celet  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | easy  
Author: |  brp64   
  
### Challenge

> Santa was given a nice bracelet by one of his elves. Little does he know
> that the secret admirer has hidden a message in the pattern of the bracelet…

![img](https://0xdfimages.gitlab.io/img/7a95aa57-0faf-4eab-
bbc3-b9d350795966.jpg)

Over the 24 hours after release, Hackvent added five hints:

>   1. No internet is required - only the bracelet
>   2. The message is encoded in binary
>   3. Violet color is the delimiter
>   4. Colors have a fixed order
>   5. Missing colors matter
>

### Solution - Fail

I (along with everyone else) spent a long time flailing on this one before
they issued hints. My best guess was to look at the five bead colors as a kind
of base5 digit set. The challenge there is that how to assign each bead a
value from 0-4. I wrote a Python script to brute force that:

    
    
    #!/usr/bin/env python3
    
    import binascii
    from itertools import permutations
    
    s = 'vpyvgbvpgvgbvpgbyvgbyvgbvbyvbyvgbyvpyvbyvvgbyvgyvgyvbyvbyvgvgbvpgbvbyvgbyvbyvgv'
    
    chars = sorted(set(s))
    
    for perm in permutations(range(len(chars))):
        num = int(''.join([f'{perm[chars.index(c)]}' for c in s]), 5)
        h = f'{num:x}'
        print(h)
        try:
            asc = binascii.unhexlify(h)
            if sum(x < 128 for x in asc) > 10 or True:
                print(asc)
        except binascii.Error:
            pass
    

I’m going to loop over all permutations of 0-4, to get all possible color
mappings. For each one, I create a string and convert it to an int base5. Then
I convert to hex and `unhexlify` it, printing the result if there’s more than
10 characters in the ASCII range.

This produced no results.

### Solution

Eventually Hackvent added five hints. When I woke up, there were three:

> No internet is required - only the bracelet The message is encoded in binary
> Violet color is the delimiter

Using violet as a delimiter was what tipped me off. Looking at the result when
I replace `v` with space, the fact that the colors are always in the same
order jumps out at me:

    
    
    >>> s.replace('v', ' ')
    ' py gb pg gb pgby gby gb by by gby py by  gby gy gy by by g gb pgb by gby by g '
    

Pink, green, blue, yellow. If I look at those as bits that are present or not
present, then each section between the spaces is nibble (4 bits).

I wrote a script to find the flag:

    
    
    #!/usr/bin/env python3
    
    import binascii
    
    
    s = 'gvpyvgbvpgvgbvpgbyvgbyvgbvbyvbyvgbyvpyvbyvvgbyvgyvgyvbyvbyvgvgbvpgbvbyvgbyvbyvgv'
    key = {'p': 8, 'g': 4, 'b': 2, 'y': 1}
    
    hex_res = ''
    
    for nibble in s[:-1].split('v'):
        hex_res += f'{sum([key[c] for c in nibble]):x}'
        
    print('HV20{' + binascii.unhexlify(hex_res).decode() + '}')
    

I started with the idea that p would be the highest value since it came first,
but had that not worked, I would have next tried the opposite order (p = 1, y
= 8), and if that failed, then tried a brute force over all orderings.

It did work on this first order:

    
    
    $ python3 solve.py 
    HV20{Ilov3y0uS4n74}
    

**Flag:`HV20{Ilov3y0uS4n74}`**

## HV20.05

### Challenge

![hv20-ball05](https://0xdfimages.gitlab.io/img/hv20-ball05.png) | HV20.05 Image DNA  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO  
![forensic](../img/hv-cat-forensic.png)FORENSIC  
Level: | easy  
Author: |  blaknyte0   
  
> Santa has thousands of Christmas balls in stock. They all look the same, but
> he can still tell them apart. Can you see the difference?

![img](https://0xdfimages.gitlab.io/img/6bbc452b-6a32-4a72-b74f-07b7ad7b181d.jpg)
![img](https://0xdfimages.gitlab.io/img/cf505372-330b-4b34-a95b-59fa33db37f8.jpg)

### Fails

I tried a handful of things that didn’t work. I was keyed in on the word
difference, so I tried opening the files in Gimp and subtracting them and
other ways of combining them (kind of like
[HV19.09](/hackvent2019/medium#day-9)) , but just got pictures like:

![image-20201218145933012](https://0xdfimages.gitlab.io/img/image-20201218145933012.png)
![image-20201218145912187](https://0xdfimages.gitlab.io/img/image-20201218145912187.png)

I also wrote a Python script to do a pixel by pixel comparison. But there were
over 22-thousand different pixels, which was too much to turn into a code of
some sort.

### Solution

To solve this, I needed to find two strings, and there were two clues
available.

The strings literally strings in the image file:

    
    
    $ strings 6bbc452b-6a32-4a72-b74f-07b7ad7b181d.jpg
    ...[snip]...
    CTGTCGCGAGCGGATACATTCAAACAATCCTGGGTACAAAGAATAAAACCTGGGCAATAATTCACCCAAACAAGGAAAGTAGCGAAAAAGTTCCAGAGGCCAAA
    $ strings cf505372-330b-4b34-a95b-59fa33db37f8.jpg
    ...[snip]...
    ATATATAAACCAGTTAATCAATATCTCTATATGCTTATATGTCTCGTCCGTCTACGCACCTAATATAACGTCCATGCGTCACCCCTAGACTAATTACCTCATTC
    

Without any hints, I could guess this is a base-4 number system and try to
decode, but there were two hints.

Running `binwalk` against one of the images shows there’s a small zip archive
attached to the end:

    
    
    $ binwalk cf505372-330b-4b34-a95b-59fa33db37f8.jpg 
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------
    0             0x0             JPEG image data, JFIF standard 1.01
    8723          0x2213          Zip archive data, at least v2.0 to extract, uncompressed size: 3, name: A
    8886          0x22B6          End of Zip archive, footer length: 22
    

Extracting that file (using the `-e` option in `binwalk`) shows it’s a zip
with one file, named `A`, with the contents `00`.

The other image has an embedded in it with a common CTF tool, `steghide`,
using no password. I’ll use `steghide` to extract an image:

    
    
    $ steghide extract -sf 6bbc452b-6a32-4a72-b74f-07b7ad7b181d.jpg 
    Enter passphrase: 
    wrote extracted data to "T.png".
    

The image is tiny, containing only two digits:

![](https://0xdfimages.gitlab.io/img/hv2020-T.png)

Now I’ll take the two strings, and the two hints at what the values will be,
and the knowledge that the flag will start with `HV` or `01 00 10 00 01 01 01
10`. Both strings had `T` at index 1 and 3, and it should be `00` in those
places. I looked at subtracting the strings, but that got complex with
negatives. Then I looked at xor, and that was promising:

    
    
    CTGT --> ?? 11 ?? 11
    ATAT --> 00 11 00 11
             -----------
    want     01 00 10 00         
    

To get `01 00 10 00`, let C = 01 and G = 10, making an ASCII H. To check, look
at the second letter, V:

    
    
    CGCG --> 01 10 01 10
    ATAA --> 00 11 00 00
             -----------
             01 01 01 10 == V
    

It works. Python can convert the rest:

    
    
    #!/usr/bin/env python3
    
    import binascii
    
    str1 = "CTGTCGCGAGCGGATACATTCAAACAATCCTGGGTACAAAGAATAAAACCTGGGCAATAATTCACCCAAACAAGGAAAGTAGCGAAAAAGTTCCAGAGGCCAAA"
    str2 = "ATATATAAACCAGTTAATCAATATCTCTATATGCTTATATGTCTCGTCCGTCTACGCACCTAATATAACGTCCATGCGTCACCCCTAGACTAATTACCTCATTC"
    
    codes = {"A": 0, "C": 1, "G": 2, "T": 3}
    
    res = ""
    for x, y in zip(str1, str2):
        diff = codes[x] ^ codes[y]
        res += f"{diff:02b}"
    
    print(binascii.unhexlify(f"{int(res, 2):x}").decode())
    

That prints the full flag:

    
    
    $ python3 solve.py 
    HV20{s4m3s4m3bu7diff3r3nt}
    

**Flag:`HV20{s4m3s4m3bu7diff3r3nt}`**

[](/hackvent2020/easy)

