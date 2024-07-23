# Flare-On 2020: wednesday

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
wednesday](/tags#flare-on-wednesday ) [reverse-engineering](/tags#reverse-
engineering ) [ghidra](/tags#ghidra ) [nimlang](/tags#nimlang )
[x64dbg](/tags#x64dbg ) [patching](/tags#patching )  
  
Oct 26, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [[2] garbage](/flare-on-2020/garbage)
  * [3] wednesday
  * [[4] report.xls](/flare-on-2020/report)
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [[10] break](/flare-on-2020/break)

![wednesday](https://0xdfimages.gitlab.io/img/flare2020-wednesday-cover.png)

wednesday was a game that involved getting my dude to the end jumping over and
going under blocks. The game was written in Nim lang, and had a lot of complex
functions to manage the game. It was a long way to go, so I patched it to just
let me run through blocks and not worry about under vs over.

## Challenge

> Be the wednesday. Unlike challenge 1, you probably won’t be able to beat
> this game the old fashioned way. Read the README.txt file, it is very
> important.

The archive contains a `README.txt` and a directory `wednesday` with
`mydude.exe` and a bunch of `.dll` files:

    
    
    root@kali# ls
    data               libogg-0.dll     libvorbis-0.dll      MUSIC.md    SDL2.dll      SDL2_image.dll  SDL2_ttf.dll
    libfreetype-6.dll  libpng16-16.dll  libvorbisfile-3.dll  mydude.exe  SDL2_gfx.dll  SDL2_mixer.dll  zlib1.dll
    

`README.txt` contains tips about getting the file running, and to focus
analysis on `mydude.exe`:

    
    
    ██╗    ██╗███████╗██████╗ ███╗   ██╗███████╗███████╗██████╗  █████╗ ██╗   ██╗
    ██║    ██║██╔════╝██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝
    ██║ █╗ ██║█████╗  ██║  ██║██╔██╗ ██║█████╗  ███████╗██║  ██║███████║ ╚████╔╝ 
    ██║███╗██║██╔══╝  ██║  ██║██║╚██╗██║██╔══╝  ╚════██║██║  ██║██╔══██║  ╚██╔╝  
    ╚███╔███╔╝███████╗██████╔╝██║ ╚████║███████╗███████║██████╔╝██║  ██║   ██║   
     ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   
    
                            --- BE THE WEDNESDAY ---
    
                                       S
                                       M
                                       T
                                      DUDE
                                       T
                                       F
                                       S
    
                    --- Enable accelerated graphics in VM ---
                      --- Attach sound card device to VM ---
                        --- Only reverse mydude.exe ---
                           --- Enjoy it my dudes ---
    

`mydude.exe` is a 32-bit executable:

    
    
    root@kali# file mydude.exe 
    mydude.exe: PE32 executable (console) Intel 80386, for MS Windows
    

## Background

In googling around for some of the DLL names, it looks like this binary is
writing in [nim lang](https://nim-lang.org/), which its authors describe as:

> a statically typed compiled systems programming language. It combines
> successful concepts from mature languages like Python, Ada and Modula.

## Running It

On running the executable, a welcome screen comes up:

![image-20200916085959786](https://0xdfimages.gitlab.io/img/image-20200916085959786.png)

When I click the “Dude” button, the game starts with a dude running and the
screen scrolling at a constant speed. I can push up to jump or down to duck to
avoid the blocks:

![image-20200916090031304](https://0xdfimages.gitlab.io/img/image-20200916090031304.png)

There are two ways that the game ends (other than presumably winning):

  1. Dude runs into a block
  2. Dude takes the wrong way around a block, over vs. under. There’s a pattern of how to clear the blocks. It seems to start with under under over over, but I stopped checking after that.

When the game ends, it just resets to the beginning and starts again.

## RE

### Program Structure

#### Ghidra

I opened this file in Ghidra. There’s a _ton_ of functions, many of which
starting with `@`:

![image-20200916092510821](https://0xdfimages.gitlab.io/img/image-20200916092510821.png)

Poking around a bit and looking at the function names, I was drawn to
`@resetEverything__Q1G0gjmnsnF8mVSgZnKS4w_3@4` (which I’ll refer to as
`resetEverything` from here on).

#### Debug

I opened `mydude.exe` in x32dbg. I had to jump through a bunch of break points
to get to the menu, but eventually I got there. I also needed to switch to the
context of (double click on) the right thread, which was the one with Priority
“TimeCritical”:

![image-20200916130220395](https://0xdfimages.gitlab.io/img/image-20200916130220395.png)

I spent a bunch of time setting break points inside of `resetEverything` and
trying to find something I could null out or skip over, but couldn’t make much
sense of it.

#### Function Analysis

I eventually tried to look at the larger context. `resetEverything` is called
from `@update__giAKdkRYJ1A0Qn9asB8s9ajA@12` (though there are a bunch other
`@update__...` functions, I’ll refer to this one as `update` from here on). At
the very bottom of `update`, there’s the check for the win screen:

    
    
      if ((piVar2 != (int *)0x0) && (*piVar2 == 0x128)) {
        @sceneeq___HC7o4hYar8OQigU09cNyehg@8
                  (_game__7aozTrKmb7lwLeRmW9a9cs9cQ,_winScene__eVaCVkG1QBiYVChMxpMGBQ);
      }
    

It also does things like check if the current score is greater than the
highscore and update that, or if that internal score has changed and it should
update the displayed score.

The call to `resetEverything` is after this check:

    
    
      if (*(char *)(*(int *)((int)this + 0x28) + 0xf9) == '\x01') {
        @resetEverything__Q1G0gjmnsnF8mVSgZnKS4w_3@4((int)this);
      }
    

This check is looking at a one byte variable to see if it is equal to 0x01.
This check is at 0x433D55:

![image-20200916131330026](https://0xdfimages.gitlab.io/img/image-20200916131330026.png)

I set a breakpoint here and ran to it. It is there immediately. I did a right
click on `ds:[eax+F9]` and selected “Follow in Dump” –> “Address: EAX+F9”.
Then in the dump, I right clicked on the first byte, went to “Breakpoint” –>
“Hardware, write” –> “Byte” to stop whenever anything writes to this byte. A
hardware breakpoint will stop on the line after the write, as opposed to
logical break point which stop before that line is executed.

I let it run. I found three places it writes to this address. To get the
latter two, I found it worked best to disable the break point, wait for the
dude to start running, and then enable it.

  * On the start of a run, it writes a 0 to this address at 0x432673. Back in Ghidra, this is in `@reset__sGe9c9bxuFSjBvFwh9bgm9cTTg_4@4`. This makes sense as it is setting the “this needs to be reset” bit to off to start.
  * When dude runs into a block, there’s a write at 0x432247.
  * When dude clears a block the wrong way (was supposed to go over but went under, or the opposite), it write a 0x01 at 0x43235e.

Both of the last two are in the function
`@onCollide__BN6X9bI9aXYgG1H4BavWOusg@8` (henceforth `onCollide`). The
`onCollide` function also has a place where the score is incremented:

    
    
    _score__h34o6jaI3AO6iOQqLKaqhw = _score__h34o6jaI3AO6iOQqLKaqhw + 1;
    

I think of the `onCollide` function more as the “passingABlock” function. It
checks if you die, or if you get points.

### Fail #1 - Jump to Win

My goal here is to patch the binary so that I can win easily. I notice the win
condition was checking that a value was equal to 0x128. I put a break point at
that check and enabled it after scoring a couple points to see that it was, as
I suspected, my score. I tried patching (select the command in x32dbg and hit
space bar) the if so that it always directed to the win screen and started. I
got a win screen, but no flag:

![img](https://0xdfimages.gitlab.io/img/unknown.png)

Thinking maybe it needed the score to be 0x128, I changed the increment such
that it jumped by much more, but the entire program crashed when it reached
this point.

At this point, knowing how the Flare-on team likes to protect flags in this
kind of challenge, I can assume that the flag is being decrypted in the
background as I pass certain blocks, and only once I go the full 296 blocks
will the win screen help.

### Fail #2 - 0 Out Flag

I went back to tracing why `resetEverything` was called - Only when it looped
and found that specific flag byte was equal to 0x01. I also had found the two
places there that byte was set to one. The first was at 0x432247, in this
code:

    
    
    if (-1 < iVar6) {
        *(undefined *)((int)param_1 + 0xf9) = 1;
        puVar4 = @X5BX5D___m13cHDTNyHJWI0nfsypQew@8(ppuVar3,(int **)&_TM__E4euemHcWzC1bcQ69azK2pw_8);
        @play__ekc9cEXgy7z9cRAqIYID39ccg@8(*puVar4,0);
    }
    

The second was at 0x43235e, in this code:

    
    
    if ((int)*(char *)(param_2 + 0x3e) != (uint)*(byte *)(param_1 + 0x3e)) {
        *(undefined *)((int)param_1 + 0xf9) = 1;
        puVar4 = @X5BX5D___m13cHDTNyHJWI0nfsypQew@8
        (_sfxData__L0NEb9bbVaCJg09cSf9auviJQ,
        (int **)&_TM__E4euemHcWzC1bcQ69azK2pw_8);
        @play__ekc9cEXgy7z9cRAqIYID39ccg@8(*puVar4,0);
        return;
    }
    

I modified both lines that set the flag to set it to 0 instead of 1:

    
    
    *(undefined *)((int)param_1 + 0xf9) = 0;
    

With the first one set, the dude can now run through blocks. With the second
one set, the dude doesn’t have to worry about going over or under in the right
order. I started the game and let it run the full 296 blocks, and then the
program crashed. Clearly the flag was not decrypting correctly.

### Success

Looking at those two blocks of code again (just above) - The first
modification is actually fine. It just avoids setting the fail flag, which is
what I want. In the second block, on whatever conditions cause that `if` to be
entered, not only is fail set, but it then `returns`, skipping over the rest
of the function, where I think that flag decryption is going on.

The assembly for this `if` is at 0x432358 in the form of a jump if equal,
where jumping avoids this block. I’ll just patch from `je` to `jmp`
(unconditional jump) by hitting space and changing `je` to `jmp` (preserving
the size and filling with nops):

Original | Patched  
---|---  
[![image-20200916140818791](https://0xdfimages.gitlab.io/img/image-20200916140818791.png)_Click for full size image_](https://0xdfimages.gitlab.io/img/image-20200916140818791.png) | [![image-20200916140840174](https://0xdfimages.gitlab.io/img/image-20200916140840174.png)_Click for full size image_](https://0xdfimages.gitlab.io/img/image-20200916140840174.png)  
  
This means it will never think it hits a block, and just skip this part.

Now I can start the program and let it run without touching anything. After a
long while, the score reaches 296, and the win screen comes on with the flag:

![image-20200916070949302](https://0xdfimages.gitlab.io/img/image-20200916070949302.png)

**Flag: 1t_i5_wEdn3sd4y_mY_Dud3s@flare-on.com**

[](/flare-on-2020/wednesday)

