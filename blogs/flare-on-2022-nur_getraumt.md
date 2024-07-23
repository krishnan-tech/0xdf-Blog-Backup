# Flare-On 2022: Nur geträumt

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-nur-
getraumt](/tags#flare-on-nur-getraumt ) [mac](/tags#mac ) [mini-
vmac](/tags#mini-vmac ) [emulation](/tags#emulation ) [super-
resedit](/tags#super-resedit )  
  
Nov 11, 2022

  * [[1] Flaredle](/flare-on-2022/flaredle)
  * [[2] Pixel Poker](/flare-on-2022/pixel_poker)
  * [[3] Magic 8 Ball](/flare-on-2022/magic_8_ball)
  * [[4] darn_mice](/flare-on-2022/darn_mice)
  * [[5] T8](/flare-on-2022/t8)
  * [[6] à la mode](/flare-on-2022/alamode)
  * [[7] anode](/flare-on-2022/anode)
  * [[8] backdoor](/flare-on-2022/backdoor)
  * [[9] encryptor](/flare-on-2022/encryptor)
  * [10] Nur geträumt
  * [[11] The challenge that shall not be named](/flare-on-2022/challenge_that_shall_not_be_named)

![Nur geträumt](https://0xdfimages.gitlab.io/img/flare2022-nurgetraumt-
cover.png)

Nur geträumt is mostly a challenge about getting an old Mac disk image running
in an emulator, and then poking around to get enough clues to solve a trivia
problem. There’s no real reversing involved, but rather reading what is
available from reading resources with Super ResEdit, a tool for reversing
these old Mac application.

## Challenge

> This challenge is a Macintosh disk image (Disk Copy 4.2 format, for those
> who need to know) containing a 68K Macintosh program. You must determine the
> passphrase used to decode the flag contained within the application. Super
> ResEdit, an augmented version of Apple’s ResEdit resource editor which adds
> a disassembler, is also included on the disk image to help you complete the
> challenge, though you will likely also need to do some outside research to
> guess the passphrase. This application can be run on any Macintosh emulator
> (or any real Macintosh from as far back as a Mac Plus running System 6.0.x
> up to a G5 running Classic). The setup of the emulation environment is part
> of the challenge, so few spoilers live here, but if you want to save
> yourself some headaches, Mini vMac is a pretty good choice that doesn’t take
> much effort to get up and running compared to some other options. This
> application was written on a Power Macintosh 7300 using CodeWarrior Pro 5,
> ResEdit, and Resourcerer (my old setup from roughly 1997, still alive!). It
> was tested on a great many machines and emulators, and validated to run well
> on Mac OS from 6.0.8 through 10.4. Happy solving! Be curious!

The download contains a Mac disk image:

    
    
    $ file Nur\ geträumt.img 
    Nur geträumt.img: Apple DiskCopy 4.2 image Nur getr\212umt, 1474560 bytes, MFM CAV dshd (1440k), 0x2 format
    

## Run It

### Configure Emulation

I’ll download Mini vMac from their [downloads
page](https://www.gryphel.com/c/minivmac/dnld_std.html). On running it, it
complains that it needs a ROM:

![image-20221021085056043](https://0xdfimages.gitlab.io/img/image-20221021085056043.png)

The [start page](https://www.gryphel.com/c/minivmac/start.html) for Mini vMac
recommends the file `vMac.ROM`, which can be found on [this
GitHub](https://github.com/nyteshade/mini-vmac-setup/blob/master/vMac.ROM).
With the ROM in the same directory, it loads to this:

![image-20221021085231542](https://0xdfimages.gitlab.io/img/image-20221021085231542.png)

Continuing from the start page, I’ll download the `System Startup` file
([here](https://github.com/nyteshade/mini-vmac-
setup/blob/master/Disks/System%20Startup)), and drag it onto Mini vMac. It
shows an old-school Mac desktop:

![image-20221021111912390](https://0xdfimages.gitlab.io/img/image-20221021111912390.png)

### Mount Image

I’ll drag the challenge `Nur geträumt.img` file onto the emulator, and it
shows up as a disk:

![image-20221021111929440](https://0xdfimages.gitlab.io/img/image-20221021111929440.png)

Double clicking it opens it as a folder with three items:

![image-20221022062938135](https://0xdfimages.gitlab.io/img/image-20221022062938135.png)

`Desktop Folder` is empty. `Super ResEdit 2.1.3` is the reverse engineering
tool mentioned in the prompt.

### Nur geträumt

Running the `Nur geträumt` program fills the screen with a prompt asking for
a password:

![image-20221022063030035](https://0xdfimages.gitlab.io/img/image-20221022063030035.png)

Entering a password and clicking “Try” (or pushing Enter) shows a flag value:

![image-20221022063104836](https://0xdfimages.gitlab.io/img/image-20221022063104836.png)

## Analysis

### Password Analysis

#### Byte By Byte

Playing around with different passwords, I can identify some properties of the
result. For example, changing the last character above seems to update every
forth character:

![image-20221022063717905](https://0xdfimages.gitlab.io/img/image-20221022063717905.png)

This implies there is some initial state of a password, and it’s being
modified by my input on a cycle, something like:

    
    
    plain[i] = enc[i] ? input[i % len(input)]
    

I don’t know what the operation is yet (hence the `?`).

Corroborating this is the fact that “diffpass” and “diffpassdiffpass” return
the same result, but removing the last “s” changes a lot:

![image-20221022064006090](https://0xdfimages.gitlab.io/img/image-20221022064006090.png)
![image-20221022064023886](https://0xdfimages.gitlab.io/img/image-20221022064023886.png)
![image-20221022064038910](https://0xdfimages.gitlab.io/img/image-20221022064038910.png)

The third image is the same through the first round, but then gets out of
alignment after the 16th character, where it starts back with the first “d”,
and the others still have an “s” left.

#### Operation

The most common operation to use for encryption would be an XOR, so I’ll start
there and see if I can prove or disprove it. With “a” entered as the password,
the first letter in the output is “m”:

![image-20221022064314895](https://0xdfimages.gitlab.io/img/image-20221022064314895.png)

If it’s as simple as `plain[0] = enc[0] ^ input[0]`, then `m ^ a` would give
the encrypted value, so 12:

    
    
    >>> ord('m') ^ ord('a')
    12
    

If the theory is correct, then I can predict what would come from any other
input. So a “$” would make a “(“:

    
    
    >>> chr(12 ^ ord('$'))
    '('
    

It does:

![image-20221022064631006](https://0xdfimages.gitlab.io/img/image-20221022064631006.png)

I’ll note above that the second character XOR with “a” (because a one
character input just XORs each byte with that character) results in “a”, which
implies the encrypted password is null there. That’s validated as well, as the
second output character with “$” is also “$”.

#### Recover (Almost) Full Encrypted Password

I can work down the input calculating the values of the encrypted password. I
already found it starts with 12, then 0. I may need to change the input a bit
to get an ASCII output I can XOR. For example, “a” returns a box for the 5th
character, but “$” doesn’t. Changing the character while I work will allow me
to get all the characters except for two:

    
    
    12, 0, 29, 26, 127, 23, 28, 78, 2, 17, 40, 8, 16, 72, 5, 0, 0, 26, 127, 42, ?, 23, 68, 50, 15, ?, 26, 96, 44, 8, 16, 28, 96, 2, 25, 65, 23, 17, 90, 14, 29, 14, 57, 10, 4
    

The 21st and 26th characters aren’t normal 7-bit ascii:

![image-20221022065857156](https://0xdfimages.gitlab.io/img/image-20221022065857156.png)

All the other characters involve XORing numbers less than 127, meaning the top
bit is off in both cases, and thus the result is off as well. If the encrypted
number is greater than 127, than either I need to input something greater than
127 to turn that bit off and get ASCII, or the result is supposed to be
greater than 127.

It turns out that apple introduced its [own extended eight-bit ASCII codes in
Mac OS](https://www.barcodefaq.com/knowledge-base/mac-exten). But I’ll skip
this for now.

#### Recover Partial Password

With this, I can recover the part of the password that’s XORed to get the
known part of the flag, “@flare-on.com”. I’ll load these numbers into a Python
terminal (I’ll just use 255 for the two unknowns, and remember they are in
there):

    
    
    >>> ''.join([chr(e^ord(f)) for e,f in zip(enc[-13:], flag_end)])
    ' du etwas Zei'
    

That’s…something? It looks German, which is the theme of the challenge.
Googling it shows it’s something like “What time is it?”:

![image-20221022071838565](https://0xdfimages.gitlab.io/img/image-20221022071838565.png)

### ResEdit

#### Overview

[ResEdit](https://en.wikipedia.org/wiki/ResEdit) is an old-school Mac dev tool
for viewing Mac OS binaries, their assembly, and their resources.

Opening it shows a nice splash screen:

![image-20221022124439796](https://0xdfimages.gitlab.io/img/image-20221022124439796.png)

Then it opens a windows to ask me what I want to look at, and I’ll select `Nur
geträumt`. The result shows 12 options:

![image-20221022124551130](https://0xdfimages.gitlab.io/img/image-20221022124551130.png)

#### CODE

The code section shows three options:

![image-20221022124859384](https://0xdfimages.gitlab.io/img/image-20221022124859384.png)

The longest one called “Application” seems like the place to work. Clicking on
it gives an assembly for the binary:

![image-20221022124811693](https://0xdfimages.gitlab.io/img/image-20221022124811693.png)

Looking at this assembly, it looks like perhaps the [68000 instruction
set](https://www.nxp.com/files-static/archives/doc/ref_manual/M68000PRM.pdf),
though I’m not 100% sure. I could reverse this if I had to, but I won’t have
to.

#### FLAG

This option offers one 48-byte object named “99 Luftballons” (this is an
important clue I’ll come back to):

![image-20221022133646233](https://0xdfimages.gitlab.io/img/image-20221022133646233.png)

Opening it shows the string which looks like it could be my buffer, and it
says to try viewing it in hex:

![image-20221022133617309](https://0xdfimages.gitlab.io/img/image-20221022133617309.png)

Closing that, I’ll select the “99 Luftballons” row and go to “Resource” >
“Open Using Hex Editor”:

![image-20221022133839570](https://0xdfimages.gitlab.io/img/image-20221022133839570.png)

This is the encrypted flag buffer, starting with a length (45 == 0x2D) and
ending with a checksum (matching what was shown above):

![image-20221022134355232](https://0xdfimages.gitlab.io/img/image-20221022134355232.png)

I can update the `enc` variable in Python for future references know that I
know the two bytes > 127.

#### TEXT

This one has a note (which I can’t view all at once because of the tiny Mini
vMac window, but I’ll edit the image together for readability here):

![image-20221022135934318](https://0xdfimages.gitlab.io/img/image-20221022135934318.png)

Two huge hints in here:

  * “1983 was a pretty good year for music”
  * “maybe try asking the program if it has a bit of time for you; perhaps it will sing you a song”

#### Others

The DATA option offers one 225-byte section. It’s got a lot of strings in it:

![image-20221022132811554](https://0xdfimages.gitlab.io/img/image-20221022132811554.png)

I feel like I should fine the initial buffer in this section, but I don’t.

dctb shows how the dialog is configured:

![image-20221022132928978](https://0xdfimages.gitlab.io/img/image-20221022132928978.png)

Nothing useful here, but neat.

DITL sends my system into a loop of errors because the image is not writable.
I’m not sure if that’s because of how I set up, or normal, but I’ll have to
kill Mini vMac to get out of the loop.

DLGX offers two sections of memory, both of which are very sparse.

## Research

### 99 Luftballons

#### Google

With a bunch of clues picked up so far, and the prompt saying “you will likely
also need to do some outside research to guess the passphrase”, I’ll turn to
Google. The big hit is “99 Luftballons”:

![image-20221022140906802](https://0xdfimages.gitlab.io/img/image-20221022140906802.png)

This is a German song released in 1983 (which was one of the hints), so this
is clearly the right path ([here](https://www.youtube.com/watch?v=Fpu5a0Bl8eY)
is the awesome 1980s music video, though I’ve always been a much bigger fan of
the [Goldfinger adaptation](https://www.youtube.com/watch?v=p-qfzH0vnOs)).

#### Lyrics

The
[lyrics](https://www.google.com/search?q=99+Luftballons&oq=99+Luftballons&aqs=chrome..69i57j69i61l2.1073j0j7&sourceid=chrome&ie=UTF-8#wptab=si:AC1wQDAmhH4WxhqkLyzXLNCgm7uMlL-
cwjtGo7YoiLsJI42k1Zt3T5h9PClNLNtt0Z7jv--
0M2d4GQyjpp3F13XwP4N0sSYRX56cgm0_9yN2GaRASqLfuARPCdkMVmjclh8Ke_yl-
lWA68b079E1r9NlrD_K3ICNww%3D%3D) for the song start with:

    
    
    Hast du etwas Zeit für mich
    Dann singe ich ein Lied für dich
    Von neunundneunzig Luftballons, auf ihrem Weg zum Horizont
    

The first line matches up nicely with the partial password recovered earlier,
“ du etwas Zei”.

On top of that, that line translates to “Do you have some time for me”:

![image-20221022141403054](https://0xdfimages.gitlab.io/img/image-20221022141403054.png)

### Flag

As the hint says to ask the program if it has some time for me, I will:

![image-20221022141503278](https://0xdfimages.gitlab.io/img/image-20221022141503278.png)

My “u” in “fur” should be “ü”, which is causing the “i” to show up as “É”.
Still, the flag is the second line of the song, so I can get it from there.
Also, the site doesn’t accept it with the ü” in the flag, but when I replace
that with a “u”, it works.

**Flag: Dann_singe_ich_ein_Lied_fur_dich@flare-on.com**

[](/flare-on-2022/nur_getraumt)

