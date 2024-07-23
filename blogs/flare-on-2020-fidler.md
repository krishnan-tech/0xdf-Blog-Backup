# Flare-On 2020: Fidler

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-fidler](/tags#flare-
on-fidler ) [python](/tags#python ) [pygame](/tags#pygame ) [reverse-
engineering](/tags#reverse-engineering )  
  
Oct 26, 2020

  * [1] Fidler
  * [[2] garbage](/flare-on-2020/garbage)
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [[4] report.xls](/flare-on-2020/report)
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [[10] break](/flare-on-2020/break)

![garbage](https://0xdfimages.gitlab.io/img/flare2020-fidler-cover.png)

Flare-On 7 got off to an easy start with a Windows executable that was
generated with PyGame, and included the Python source. That made this
challenge more of a Python source code analysis exercise than a reversing
challenge. I’ll find the password and the win conditions in the source, and
win both by decrypting the flag and by modifying the source.

## Challenge

> Welcome to the Seventh Flare-On Challenge!
>
> This is a simple game. Win it by any means necessary and the victory screen
> will reveal the flag. Enter the flag here on this site to score and move on
> to the next level.
>
> This challenge is written in Python and is distributed as a runnable EXE and
> matching source code for your convenience. You can run the source code
> directly on any Python platform with PyGame if you would prefer.

The file is an x64 binary:

    
    
    root@kali# file fidler.exe 
    fidler.exe: PE32+ executable (console) x86-64, for MS Windows
    

As the prompt mentioned, there’s also a Python version with the supporting
files:

    
    
    root@kali# ls
    1_-_fidler.7z  controls.py  fidler.exe  fidler.py  fonts  img  Message.txt
    

## Running It

Because this is a CTF, it’s worth giving this a run in a Windows VM. A
password prompt pops:

![](https://0xdfimages.gitlab.io/img/image-20200913145425224.png)

Guessing at a password pops up an “FBI” warning:

![](https://0xdfimages.gitlab.io/img/image-20200913145500567.png)

On a Linux VM, I did `pip3 install pygame` and then ran `python3 fidler.py` ,
and I get the same behavior. I’ll work out of this one because if I need to
modify the program (and I will want to), it’s just easier than patching
compiled Python.

## RE

### Find Password

Because I have the source I can take a look. The first two functions defined
are `password_check(input)` and `password_screen`. `password_check` gives away
the password:

    
    
    def password_check(input):
        altered_key = 'hiptu'
        key = ''.join([chr(ord(x) - 1) for x in altered_key])
        return input == key
    

I can jump into a Python repl and get the key:

    
    
    >>> altered_key = 'hiptu'
    >>> ''.join([chr(ord(x) - 1) for x in altered_key])
    'ghost'
    

### Gave Overview

On entering that password, now it goes to the game screen:

![](https://0xdfimages.gitlab.io/img/image-20200913150037775.png)

Clicking on the cat adds one coin:

![](https://0xdfimages.gitlab.io/img/image-20200913150110452.png)

If I have at least 10 coins, I can click the Buy button, and then I get 10
less coins, but now my coins increase at a rate of one per second. Buying a
second autoclicker will have my coins increase at two per second, etc. Even
buying autoclickers as fast as possible, getting to 100 billion is going to
take forever.

### Static Analysis

There’s a function towards the bottom of the code, `decode_flag(frob)`:

    
    
    def decode_flag(frob):
        last_value = frob
        encoded_flag = [1135, 1038, 1126, 1028, 1117, 1071, 1094, 1077, 1121, 1087, 1110, 1092, 1072, 1095, 1090, 1027,
                        1127, 1040, 1137, 1030, 1127, 1099, 1062, 1101, 1123, 1027, 1136, 1054]
        decoded_flag = []
    
        for i in range(len(encoded_flag)):
            c = encoded_flag[i]
            val = (c - ((i%2)*1 + (i%3)*2)) ^ last_value
            decoded_flag.append(val)
            last_value = c
    
        return ''.join([chr(x) for x in decoded_flag])
    

This function is called in `victory_screen(token)`, and the unmodified `token`
variable is passed into it. `victory_screen` is called from `game_screen()`,
at the top of the main `while True` loop:

    
    
        while not done:
            target_amount = (2**36) + (2**35)
            if current_coins > (target_amount - 2**20):
                while current_coins >= (target_amount + 2**20):
                    current_coins -= 2**20
                victory_screen(int(current_coins / 10**8))
                return
    ...[snip rest of the game]...
    

There’s a `target_amount` variable that is set to 103079215104. To get to the
call of `victory_screen`, first, `current_coins` must be greater than
`target_amount` minus 220, 103078166528. If `current_coins` is more than 220
more than `target_amount`, it will subtract 220 from `current_coins` until it
isn’t. Then, `victory_screen` is called, with `token` as the floor of
`current_coins` / 108. That means to get to `victory_screen`, `current_coins`
will be between 103078166529 and 103080263679 (inclusive). Anything in that
range will result in a `token` of 1030:

    
    
    >>> ((2**36 + 2**35) + 2**20 - 1) // 10**8
    1030
    >>> ((2**36 + 2**35) - 2**20 + 1) // 10**8
    1030
    

## Solve

### Decrypt Flag

I can solve from here knowing the token and having the `decrpyt_flag`
function. In fact, I can just import the Python file and call the function:

    
    
    root@kali# python3
    Python 3.8.5 (default, Aug  2 2020, 15:09:07) 
    [GCC 10.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import fidler
    pygame 1.9.6
    Hello from the pygame community. https://www.pygame.org/contribute.html
    >>> fidler.decode_flag(1030)
    'idle_with_kitty@flare-on.com'
    

### Modify the Program

Alternatively, I can modify the program to win. At the top of the code, the
`current_coins` variable is initialized to 0:

    
    
    import pygame as pg
    pg.init()
    from controls import *
    
    current_coins = 0
    current_autoclickers = 0
    buying = False
    

I’ll just drop 110,000,000,000 in:

    
    
    current_coins = 110000000000
    

Now, on running the game, it goes right to the victory screen:

![image-20200922132124802](https://0xdfimages.gitlab.io/img/image-20200922132124802.png)

**Flag: idle_with_kitty@flare-on.com**

[](/flare-on-2020/fidler)

