# Flare-On 2022: darn_mice

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-darn-
mice](/tags#flare-on-darn-mice ) [reverse-engineering](/tags#reverse-
engineering ) [ghidra](/tags#ghidra ) [x32dbg](/tags#x32dbg )
[python](/tags#python )  
  
Nov 11, 2022

  * [[1] Flaredle](/flare-on-2022/flaredle)
  * [[2] Pixel Poker](/flare-on-2022/pixel_poker)
  * [[3] Magic 8 Ball](/flare-on-2022/magic_8_ball)
  * [4] darn_mice
  * [[5] T8](/flare-on-2022/t8)
  * [[6] à la mode](/flare-on-2022/alamode)
  * [[7] anode](/flare-on-2022/anode)
  * [[8] backdoor](/flare-on-2022/backdoor)
  * [[9] encryptor](/flare-on-2022/encryptor)
  * [[10] Nur geträumt](/flare-on-2022/nur_getraumt)
  * [[11] The challenge that shall not be named](/flare-on-2022/challenge_that_shall_not_be_named)

![known](https://0xdfimages.gitlab.io/img/flare2022-darnmice-cover.png)

darn_mice involves reversing a Windows binary that doesn’t do anything when
run without arguments. I’ll have to find the correct argument to pass it to
get it to spit out the flag.

## Challenge

> “If it crashes its user error.” -Flare Team

The download contains a 32-bit Windows exe file:

    
    
    oxdf@hacky$ file darn_mice.exe 
    darn_mice.exe: PE32 executable (console) Intel 80386, for MS Windows
    

## Run It

Double-clicking the exe shows a quick flash of something, and then it dies or
at least doesn’t show any window.

Running it via a terminal doesn’t show anything either:

![image-20221003085733490](https://0xdfimages.gitlab.io/img/image-20221003085733490.png)

## RE

### Orienting

#### Strings

At the bottom of the strings view in Ghidra there’s a few interesting ones
that appear like output text:

![image-20221003142948732](https://0xdfimages.gitlab.io/img/image-20221003142948732.png)

Starting with the first one, it’s referenced in `FUN_00401000`. Working back
up, that’s called from `FUN_004011d0`, which is called from `entry`.

#### entry

At the top of `entry`, there’s a lot of setting up of globals and calls to
things that look like security stuff.

There’s a bunch more functions that just return pointers to globals. For
example, at 0x401d3c, it just returns a pointer to 0x41a44c:

    
    
    undefined * get_DAT41a44c(void)
    
    {
      return &DAT_0041a44c;
    }
    

### Identify argc/argv

#### Find Function Call

There are some other potentially interesting blocks, but I’ll focus on where
the call into functions that leads to the string is located:

    
    
          piVar7 = (int *)get_DAT419f74();
          iVar4 = *piVar7;
          piVar7 = (int *)get_DAT419f70();
          FID_conflict:__get_initial_narrow_environment();
          unaff_ESI = FUN_004011d0(*piVar7,iVar4);
    

I’ll put a breakpoint at the call to `FUN_004011d0` and run. I’m looking at
two arguments, the first is 1, and the second is 0125bbf0:

[![image-20221003144749340](https://0xdfimages.gitlab.io/img/image-20221003144749340.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221003144749340.png)

The second is a pointer to the string
`C:\\Users\\0xdf\\Desktop\\darn_mice.exe`.

It’s not unreasonable to think this might be `argc` and `argv`. It’s common
for the first item in `argv` (the command line arguments) to be the full path
to the calling binary, and since I called with no additional args, the length
(`argc`) of 1 makes sense.

#### Test Theory

To test this, I’ll go to File -> Change Command Line and add some args:

![image-20221003145111578](https://0xdfimages.gitlab.io/img/image-20221003145111578.png)

Running to the break, now the first arg is 5:

![image-20221003145431233](https://0xdfimages.gitlab.io/img/image-20221003145431233.png)

Looking at the second one in the dump, I’ll see five pointers followed by a
null word, and those each point to one of the args:

![image-20221003145646017](https://0xdfimages.gitlab.io/img/image-20221003145646017.png)

### FUN_004011d0

This function is very simple. It checks that `argc` is 2, and if so, calls
`FUN_00401000` with the only argument:

    
    
    int __cdecl FUN_004011d0(int argc,int argv)
    
    {
      if (argc == 2) {
        FUN_00401000(*(PUCHAR *)(argv + 4));
      }
      return 0;
    }
    

If I run the program with one argument, it does print some, and then stops:

![image-20221003145902109](https://0xdfimages.gitlab.io/img/image-20221003145902109.png)

If I run this the same way in the debugger, it prints:

![image-20221003150014924](https://0xdfimages.gitlab.io/img/image-20221003150014924.png)

Then it crashes:

![image-20221003150027611](https://0xdfimages.gitlab.io/img/image-20221003150027611.png)

[![image-20221003150045786](https://0xdfimages.gitlab.io/img/image-20221003150045786.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221003150045786.png)

It’s trying to run `add byte ptr ds:[eax], 0`, which will add 0 to what’s
stored at EAX’s address. But EAX is 0x30, which isn’t a valid address in
memory, so it crashes. It’s also very suspect that this entire block after the
first byte is all 0x00.

### FUN_00401000

#### Overview

This function starts out with a buffer of hex values on the stack:

![image-20221003150539360](https://0xdfimages.gitlab.io/img/image-20221003150539360.png)

That buffer is 35 long, with the last being a null byte. After that, a check
on my input length. If it’s longer than 0x23 (35) bytes, it prints something
else and doesn’t do other stuff:

![image-20221003150735101](https://0xdfimages.gitlab.io/img/image-20221003150735101.png)

I can verify this, as it prints “No, nevermind.” instead of “You leave the
room…”:

![image-20221003150813499](https://0xdfimages.gitlab.io/img/image-20221003150813499.png)

Otherwise, it prints the “You leave the room…” message and calls this loop:

![image-20221003151428872](https://0xdfimages.gitlab.io/img/image-20221003151428872.png)

#### Loop Analysis

The `for` loop is the interesting part. It’s looping from `i` of 0 to i < 0x24
(36), also breaking if `local_2c[i]` is null or `user_input[i]` is null. The
then allocates a buffer using `VirtualAlloc` to create 0x1000 bytes, with the
flags `MEM_COMMIT|MEM_RESERVE` (0x3000,
[details](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-
memoryapi-virtualalloc)), and setting it as `PAGE_EXECUTE_READWRITE`.

Then it stores `local_2c[i] + user_input[i]` in that buffer, and then calls
it. That explains the crashing. In the example above, the first byte of my
input, “0xdf”, is “0” or 0x30, which when added to 0x50, shows 0x80, which was
the first byte in the crash.

## Solve

### Strategy

There’s really only one instruction that I could write into that new buffer
that won’t result in a crash - `RET`. Anything other than a return will
continue to the next byte, which will be `add byte ptr ds:[eax], al` (0x00),
which will crash because EAX isn’t in a valid memory space.

Therefore, I need to figure out how to give it input for all 35 bytes that
leads to `RET`, which is 0xc3.

### Script

I’ll grab the stack buffer from Ghidra and paste it into a Python script,
using some `vim` macros to quickly clean it up. Then I just need to loop over
each byte, subtract it from 0xc3, and get the result:

    
    
    #!/usr/bin/env python3
    
    bytes = [0x50, 0x5e, 0x5e, 0xa3, 0x4f, 0x5b, 0x51, 0x5e, 0x5e, 0x97, 0xa3, 0x80, 0x90, 0xa3, 0x80, 0x90, 0xa3, 0x80, 0x90, 0xa3, 0x80, 0x90, 0xa3, 0x80, 0x90, 0xa3, 0x80, 0x90, 0xa3, 0x80, 0x90, 0xa2, 0xa3, 
    0x6b, 0x7f]
    
    print(''.join([chr(0xc3 - x) for x in bytes]))
    

The result is a string that’s joking about “C3” (the op code for `RET`):

    
    
    oxdf@hacky$ python decode_input.py 
    see three, C3 C3 C3 C3 C3 C3 C3! XD
    

### Get Flag

I’ll run with that string as input, and it prints the flag (after a bunch of
“Nibbles…”):

    
    
    PS > .\darn_mice.exe 'see three, C3 C3 C3 C3 C3 C3 C3! XD'
    On your plate, you see four olives.
    You leave the room, and a mouse EATS one!
    Nibble...
    ...[snip]...
    Nibble...
    When you return, you only: see three, C3 C3 C3 C3 C3 C3 C3! XD
    i_w0uld_l1k3_to_RETurn_this_joke@flare-on.com
    

**Flag: i_w0uld_l1k3_to_RETurn_this_joke@flare-on.com**

[](/flare-on-2022/darn_mice)

