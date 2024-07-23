# Flare-On 2019: demo

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-demo](/tags#flare-on-
demo ) [x64dbg](/tags#x64dbg ) [reverse-engineering](/tags#reverse-engineering
)  
  
Oct 6, 2019

  * [[1] Memecat Battlestation](/flare-on-2019/memecat-battlestation.html)
  * [[2] Overlong](/flare-on-2019/overlong.html)
  * [[3] Flarebear](/flare-on-2019/flarebear.html)
  * [[4] DNS Chess](/flare-on-2019/dnschess.html)
  * [5] demo
  * [[6] bmphide](/flare-on-2019/bmphide.html)
  * [[7] wopr](/flare-on-2019/wopr.html)

![](https://0xdfimages.gitlab.io/img/flare2019-5-cover.png)

demo really threw me, to the point that I almost skipped writing it up. The
file given is a demoscene, which is a kind of competition to get the best
visual performce out of an executable limited in size. To achieve this,
packers are used to compress the binary. In the exe for this challenge, a 3D
Flare logo comes up and spins, but the flag is missing. I’ll have to unpack
the binary and start messing with random DirectX functions until I find two
ways to make the flag show up.

## Challenge

> Someone on the Flare team tried to impress us with their demoscene skills.
> It seems blank. See if you can figure it out or maybe we will have to fire
> them. No pressure.

I’m given a Windows executable:

    
    
    $ file 4k.exe 
    4k.exe: MS-DOS executable
    

## Background

### Packed

Right away I’ll notice that the output of `file` is a bit off. Compare that to
the output for the last two Windows challenges:

    
    
    $ file MemeCatBattlestation.exe 
    MemeCatBattlestation.exe: PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows
    $ file Overlong.exe
    Overlong.exe: PE32 executable (GUI) Intel 80386, for MS Windows
    

This reports as an MS-DOS executable, not even a PE32 or PE32+. That’s a good
hint that there’s something odd about this binary. Further, running `strings
-n 10 4k.exe` returns nothing. Not even the standard “This program cannot be
run in DOS mode.”

### Demoscenes

This would be a good time to make sure i understand all the clues in the
challenge. I was not familiar with demoscenes, and had a spent some time at
this point reading about them, I think I would have been less confused later.

[Wikipedia](https://en.wikipedia.org/wiki/Demoscene) explains it well:

> Prior to the popularity of IBM PC compatibles, most home computers of a
> given line had relatively little variance in their basic hardware, which
> made their capabilities practically identical. Therefore, the variations
> among demos created for one computer line were attributed to programming
> alone, rather than one computer having better hardware. This created a
> competitive environment in which [demoscene
> groups](https://en.wikipedia.org/wiki/Demo_group) would try to outperform
> each other in creating outstanding
> [effects](https://en.wikipedia.org/wiki/Demo_effect), and often to
> demonstrate why they felt one machine was better than another (for example
> [Commodore 64](https://en.wikipedia.org/wiki/Commodore_64) or
> [Amiga](https://en.wikipedia.org/wiki/Amiga) versus [Atari 8-bit
> family](https://en.wikipedia.org/wiki/Atari_8-bit_family) or [Atari
> ST](https://en.wikipedia.org/wiki/Atari_ST)).
>
> Demo writers went to great lengths to get every last bit of performance out
> of their target machine. Where games and application writers were concerned
> with the stability and functionality of their software, the demo writer was
> typically interested in how many CPU cycles a routine would consume and,
> more generally, how best to squeeze great activity onto the screen. Writers
> went so far as to exploit known hardware errors to produce effects that the
> manufacturer of the computer had not intended. The perception that the demo
> scene was going to extremes and charting new territory added to its draw.

Common categories of competition were 64K and 4K, which lines up with the file
name nicely. If I look at the file, I can see it does come in under 4096 bytes
in size:

    
    
    C:\Users\0xdf\Desktop>dir 4k.exe
    
     Directory of C:\Users\0xdf\Desktop
    
    05/09/2019  09:14 PM             3,872 4k.exe
    

In googling about demoscenes, I came across Crinkler, a well known and one of
the best compressors (packers) used in demoscenes. [This
post](http://code4k.blogspot.com/2010/12/crinkler-secrets-4k-intro-
executable.html) gives a ton of detail about how it works, though that level
of detailed understanding isn’t necessary to solve the challenge.

## Running It

### DirectX 9

To get the program to run, I needed to install DirectX9. To do that, I found
the DirectX End-User Runtime Web Installer from Microsoft,
[here](https://www.microsoft.com/en-us/download/details.aspx?id=35), and it
installed into my Windows 10 VM just fine.

### Demo

When I run the exe, a window pops up with a nice 3D Flare logo, spinning
around:

![](https://0xdfimages.gitlab.io/img/demo.gif)

This binary is a bit unstable. It will regularly freeze and Windows will
report it is not responding and kill it.

## RE / Debugging

### Crinkler

It isn’t critical to understand the compressor to move forward, but it never
hurts to verify. I did some goolging to see if I could find a Crinkler
unpacker, and didn’t find much. [This stackexchange
post](https://reverseengineering.stackexchange.com/questions/13912/trying-to-
decompress-a-hello-world-program-using-ollydbg-v201) did help me confirm (or
at least suspect) Crinkler is in use, as in the example they give a hex dump
of the Crinkler compressed binary:

    
    
    00000000  4D 5A 32 30 50 45 00 00 4C 01 00 00 01 DB 61 7F  MZ20PE..L....Ûa.
    00000010  10 D0 17 73 75 47 EB F9 08 00 02 00 0B 01 11 C9  .Ð.suGëù.......É
    00000020  45 85 C0 79 1F 01 D3 50 F7 E2 90 3D 5C 00 00 00  E…Ày..ÓP÷â.=\...
    00000030  F7 F3 39 C1 19 DB EB 48 00 00 40 00 04 00 00 00  ÷ó9Á.ÛëH..@.....
    00000040  04 00 00 00 0F A3 2D 29 01 40 00 8D 04 00 EB CE  .....£-).@....ëÎ
    00000050  00 00 00 00 EB B6 42 06 40 00 00 00 53 31 ED BB  ....ë¶B.@...S1í»
    

That looks almost exactly the same as `4k.exe`:

    
    
    00000000  4d 5a 32 31 50 45 00 00 4c 01 00 00 01 db 61 7f  MZ21PE..L.....a.
    00000010  10 d0 17 73 75 47 eb f9 08 00 02 00 0b 01 11 c9  ...suG..........
    00000020  45 85 c0 79 1f 01 d3 50 f7 e2 90 3d 5c 00 00 00  E..y...P...=\...
    00000030  f7 f3 39 c1 19 db eb 48 00 00 40 00 04 00 00 00  ..9....H..@.....
    00000040  04 00 00 00 0f a3 2d 6a 01 40 00 8d 04 00 eb ce  ......-j.@......
    00000050  00 00 00 00 eb b6 43 1f 40 00 00 00 53 31 ed bb  ......C.@...S1..
    

### Unpacking Loop

Giving up on finding a Crinkler unpacker, I took at look at the main function
in Ida:

![1568968754548](https://0xdfimages.gitlab.io/img/1568968754548.png)

That entire loop will end up at that return in the middle, after all the
unpacking is done.

I’ll open it in `x32dbg`, and tell it to run, so that it get to the automatic
break point at the entry point. Then I’ll set a break point on the `retn` at
0x4000D3, and let it run. When it breaks, I’ll step one instruction forward,
and return to 0x420000 (which is the unpacked starting address also referenced
in the stackexchange post above), and now I’m at the start of the actual code.

![1568969377631](https://0xdfimages.gitlab.io/img/1568969377631.png)

### Unpacked Code

I don’t really understand most of what’s going on for the first 80% of this
unpacked code. I did a lot of googling function names, trying to understand
what’s being passed in, and what I might change to get it to work. By stepping
through it, I got a feel for where the Window was created (showing an empty
window), and when the mesh graphics are added to it. I zeroed in on this loop
at the very end:

![1570384763392](https://0xdfimages.gitlab.io/img/1570384763392.png)

It’s in that first function that the object show up on the open window.

Largely with a lot of trial and error, I found that I could nop out one
function call as follows. Start with this:

![1567837686606](https://0xdfimages.gitlab.io/img/1567837686606.png)

And change to:

![1567837704039](https://0xdfimages.gitlab.io/img/1567837704039.png)

Now let it keep running, and the flag is visible:

![](https://0xdfimages.gitlab.io/img/demo-solve.gif)

![1567837731810](https://0xdfimages.gitlab.io/img/1567837731810.png)

**Flag: moar_pouetry@flare-on.com**

There is an alternative path I stumbled on without really knowing what I was
doing involved the call to `D3DXMatrixTranslation`. [This
function](https://docs.microsoft.com/en-
us/windows/win32/direct3d9/d3dxmatrixtranslation) is involved with positioning
the flag on the canvas with x, y, and z positions (in 3-dimensional space). It
is called as:

    
    
    D3DXMATRIX* D3DXMatrixTranslation(
      _Inout_ D3DXMATRIX *pOut,
      _In_    FLOAT      x,
      _In_    FLOAT      y,
      _In_    FLOAT      z
    );
    

In this case, the z position is _huge_ :

![1570385396648](https://0xdfimages.gitlab.io/img/1570385396648.png)

I can set a breakpoint there (hardware break point if I want it to survive
restarting the program), and patch it to 0:

![1570385467574](https://0xdfimages.gitlab.io/img/1570385467574.png)

Now I just let the program run, and I get the same result with the flag.

[](/flare-on-2019/demo.html)

