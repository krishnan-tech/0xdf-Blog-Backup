# Flare-On 2022: Magic 8 Ball

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
magic-8-ball](/tags#flare-on-magic-8-ball ) [reverse-
engineering](/tags#reverse-engineering ) [sdl](/tags#sdl ) [simple-
directmedia](/tags#simple-directmedia ) [ghidra](/tags#ghidra )
[x32dbg](/tags#x32dbg )  
  
Nov 11, 2022

  * [[1] Flaredle](/flare-on-2022/flaredle)
  * [[2] Pixel Poker](/flare-on-2022/pixel_poker)
  * [3] Magic 8 Ball
  * [[4] darn_mice](/flare-on-2022/darn_mice)
  * [[5] T8](/flare-on-2022/t8)
  * [[6] à la mode](/flare-on-2022/alamode)
  * [[7] anode](/flare-on-2022/anode)
  * [[8] backdoor](/flare-on-2022/backdoor)
  * [[9] encryptor](/flare-on-2022/encryptor)
  * [[10] Nur geträumt](/flare-on-2022/nur_getraumt)
  * [[11] The challenge that shall not be named](/flare-on-2022/challenge_that_shall_not_be_named)

![magic 8 ball](https://0xdfimages.gitlab.io/img/flare2022-magic8ball-
cover.png)

Magic 8 Ball presents a 32 bit Windows executable that will return a flag
shaken the right number of times and in the right directions.

## Challenge

> You got a question? Ask the 8 ball!

The download contains a 32-bit Windows exe file as well as a bunch of DLLs:

    
    
    oxdf@hacky$ ls
    03_magic8ball.7z  libpng16-16.dll  libwebp-7.dll   SDL2.dll        SDL2_ttf.dll
    libjpeg-9.dll     libtiff-5.dll    Magic8Ball.exe  SDL2_image.dll  zlib1.dll
    oxdf@hacky$ file Magic8Ball.exe 
    Magic8Ball.exe: PE32 executable (GUI) Intel 80386, for MS Windows
    

## Run It

Running the application shows a window with a crude [magic 8
ball](https://en.wikipedia.org/wiki/Magic_8_Ball):

![image-20221002173538125](https://0xdfimages.gitlab.io/img/image-20221002173538125.png)

When I press an arrow key, the light blue triangle jumps a bit. If I type, a
question comes out under the prompt:

![image-20221002173718792](https://0xdfimages.gitlab.io/img/image-20221002173718792.png)

Hitting enter clears that text, and a message appears on the triangle:

![image-20221002173813606](https://0xdfimages.gitlab.io/img/image-20221002173813606.png)

## RE

### Starting Strategy

#### SDL Background

Simple DirectMedia Layer, or [SDL](https://www.libsdl.org/) describes itself
as:

> Simple DirectMedia Layer is a cross-platform development library designed to
> provide low level access to audio, keyboard, mouse, joystick, and graphics
> hardware via OpenGL and Direct3D. It is used by video playback software,
> emulators, and popular games including [Valve](http://valvesoftware.com/)’s
> award winning catalog and many [Humble
> Bundle](https://www.humblebundle.com/) games.
>
> SDL officially supports Windows, Mac OS X, Linux, iOS, and Android. Support
> for other platforms may be found in the source code.
>
> SDL is written in C, works natively with C++, and there are [bindings
> available](https://www.libsdl.org/languages.php) for several other
> languages, including C# and Python.
>
> SDL 2.0 is distributed under the [zlib
> license](https://www.libsdl.org/license.php). This license allows you to use
> SDL freely in any software.

#### Orienting

I’m going to start with the assumption that all these DLLs are part of the
framework necessary to get the graphics and interaction running, and focus on
`Magic8Ball.exe`. I’ll load it into Ghidra, do the initial analysis, and then
look at the strings. I’m looking for the various phrases that print on the
triangle, and I find them:

![image-20221002174539806](https://0xdfimages.gitlab.io/img/image-20221002174539806.png)

They are all in a row, though no evenly spaced:

![image-20221002174732094](https://0xdfimages.gitlab.io/img/image-20221002174732094.png)

Looking at references to one of the strings leads to a function at 0x4012b0
that I’ve named `initResponses`:

    
    
    int __fastcall initResponses(int responses)
    
    {
      *(undefined4 *)(responses + 4) = 0;
      *(undefined4 *)(responses + 8) = 0;
      *(char **)(responses + 0xc) = "\t\tIt is\n\tcertain";
      *(char **)(responses + 0x10) = "\t\tIt is\n\tdecidedly\n\t\t\tso";
      *(char **)(responses + 0x14) = "Without a\n\t\tdoubt";
      *(char **)(responses + 0x18) = "\t\tYes\n\tdefinitely";
      *(char **)(responses + 0x1c) = "\tYou may\n\trely on\n\t\t\tit";
      *(char **)(responses + 0x20) = "\tAs I see\n\t\tit, yes";
      *(char **)(responses + 0x24) = "Most likely";
      *(char **)(responses + 0x28) = "\tOutlook\n\t\tgood";
      *(char **)(responses + 0x2c) = "\n\t\t\tYes";
      *(char **)(responses + 0x30) = "Signs point\n\t\tto yes";
      *(char **)(responses + 0x34) = "Reply hazy,\n\ttry again";
      *(char **)(responses + 0x38) = "Ask again\n\t\tlater";
      *(char **)(responses + 0x3c) = "Better not\n\ttell you\n\t\tnow";
      *(char **)(responses + 0x40) = "\tCannot\t\n\tpredict\n\t\tnow";
      *(char **)(responses + 0x44) = "Concentrate\n\tand ask\n\t\tagain";
      *(char **)(responses + 0x48) = "Don\'t count\n\t\ton it";
      *(char **)(responses + 0x4c) = "My reply is\n\t\t\tno";
      *(char **)(responses + 0x50) = "My sources\n\t\t\tsay\n\t\t\tno";
      *(char **)(responses + 0x54) = "Outlook not\n\tso good";
      *(char **)(responses + 0x58) = "\t\tVery\n\tdoubtful";
      *(undefined4 *)(responses + 0xe0) = 0;
      *(undefined4 *)(responses + 0xf0) = 0;
      *(undefined4 *)(responses + 0xf4) = 0xf;
      *(undefined *)(responses + 0xe0) = 0;
      *(undefined4 *)(responses + 0xf8) = 0;
      *(undefined4 *)(responses + 0x108) = 0;
      *(undefined4 *)(responses + 0x10c) = 0xf;
      *(undefined *)(responses + 0xf8) = 0;
      *(undefined4 *)(responses + 0x110) = 0;
      *(undefined4 *)(responses + 0x120) = 0;
      *(undefined4 *)(responses + 0x124) = 0xf;
      *(undefined *)(responses + 0x110) = 0;
      *(undefined4 *)(responses + 0x128) = 0;
      *(undefined4 *)(responses + 0x138) = 0;
      *(undefined4 *)(responses + 0x13c) = 0xf;
      *(undefined *)(responses + 0x128) = 0;
      *(undefined4 *)(responses + 0x140) = 0;
      *(undefined4 *)(responses + 0x150) = 0;
      *(undefined4 *)(responses + 0x154) = 0xf;
      *(undefined *)(responses + 0x140) = 0;
      return responses;
    }
    

It’s creating some kind of game object. Looking at the references to this
function, it is called from a function I’m naming `mainLoop` (0x4027a0).

### Main Loop

The `mainLoop` function does some init (including calling `initResponses`),
and then enters a loop:

    
    
      _Dst = (void *)FUN_0040296d(0x174);
      if (_Dst == (void *)0x0) {
        responses = (char *)0x0;
      }
      else {
        memset(_Dst,0,0x174);
        responses = (char *)initResponses((int)_Dst);
      }
      uVar3 = 0;
      FUN_004018f0(&stack0xffffffe4,"Magic 8 Ball",(int *)0xc);
      uVar2 = FUN_00402090(responses,(undefined4 *)&stack0xffffffe4,0x2fff0000,0x2fff0000,800,600);
      if ((char)uVar2 != '\0') {
        cVar1 = *responses;
        while (cVar1 != '\0') {
          ticks_start = SDL_GetTicks();
                process_events(responses,unaff_ESI,uVar3,in_stack_ffffffe8,in_stack_ffffffec,in_stack_fffffff0
                        );
          check_flag_condition(responses);
          render((int)responses);
          ticks_stop = SDL_GetTicks();
          if (ticks_stop - ticks_start < 0x10) {
            SDL_Delay(0x10 - (ticks_stop - ticks_start));
          }
          cVar1 = *responses;
        }
      }
      exit((int)responses);
      return 0;
    }
    

Inside the loop, it is calling `SDL_GetTicks()`, doing some stuff, and then
calling it again. Initially I thought that an anti-debug technique, but on a
closer look, it’s actually taking some action if it moves too fast - if less
than 10 ticks have passed, then it calls `SDL_Delay` to get to 10. It seems
logical to me that this is the main processing of input, making sure not to
peg the CPU when there’s nothing to do.

There are three functions called between the tick measurements, each with
names I’ve assigned them:

  * `process_events` [0x491e50]
  * `check_flag_conditions` [0x4024e0]
  * `render` [0x4022a0]

### processmessage

The function at 0x401e50 (I’ve named it `processmessage`) seems to call
`SDL_PollEvent`, and then enter a big set of switch statements based on the
result.

![image-20221002180028148](https://0xdfimages.gitlab.io/img/image-20221002180028148.png)

This is clearly handling the input and managing what is done with it. While
it’s tempting to look at this in detail, I’ll look at the other functions in
`mainLoop` first, as it’s possible this just reads input into a structure, and
I can just look at the structure later and now worry about the how.

### render

The third function is full of calls to `SDL_Render*`:

![image-20221003062006377](https://0xdfimages.gitlab.io/img/image-20221003062006377.png)

I won’t put too much effort into this yet, as it seems like it’s job is just
to display what it’s supposed to display.

### check_flag_condition

At the top there is some data setting and getting, but 68 lines in, there
starts what is clearly a byte by byte validation of something:

![image-20221003062147502](https://0xdfimages.gitlab.io/img/image-20221003062147502.png)

The character comparisons are to `L`, `R`, `U`, and `D`, which in hindsight
seems to obvious correspond to left, right, up, and down.

But even without noticing that, I can set a break point at this point in
x32dbg, hit some arrows and enter some text, and run to it, and see that it’s
comparing a buffer of my arrows (I entered UUDDRLRL here) in ECX to hardcoded
values:

![image-20221003062628192](https://0xdfimages.gitlab.io/img/image-20221003062628192.png)

The full string of comparison is `LLURULDUL`.

At the end of the comparisons, there’s a `strncmp` on 15 characters, and if it
matches, it calls two more functions:

![image-20221003062843311](https://0xdfimages.gitlab.io/img/image-20221003062843311.png)

I’ll put a break point at the `strncmp` and do again, hit the arrow keys to
match the pattern above, and enter a question. It makes it to the `strncmp`,
and it’s comparing my input (“hello?”) with the string “gimme flag pls?”:

![image-20221001064351626](https://0xdfimages.gitlab.io/img/image-20221001064351626.png)

Running a third time with the correct arrows and the correct question renders
the flag:

![image-20221001064449776](https://0xdfimages.gitlab.io/img/image-20221001064449776.png)

**Flag: U_cRackeD_th1$_maG1cBaLL_!!_@flare-on.com**

[](/flare-on-2022/magic_8_ball)

