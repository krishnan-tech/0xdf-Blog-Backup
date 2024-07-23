# FunWare [CactusCon 2022 CTF]

[ctf](/tags#ctf ) [cactuscon](/tags#cactuscon ) [ctf-funware](/tags#ctf-
funware ) [forensics](/tags#forensics ) [malware](/tags#malware ) [reverse-
engineering](/tags#reverse-engineering ) [ftk-imager](/tags#ftk-imager )
[access-data-file](/tags#access-data-file ) [ransomeware](/tags#ransomeware )
[pyinstaller](/tags#pyinstaller ) [pyinstxtractor](/tags#pyinstxtractor )
[flare-on-wopr](/tags#flare-on-wopr ) [uncompyle6](/tags#uncompyle6 )
[python](/tags#python ) [firefox](/tags#firefox ) [firepwd](/tags#firepwd )
[sqlite](/tags#sqlite )  
  
Feb 7, 2022

FunWare [CactusCon 2022 CTF]

![cascade](https://0xdfimages.gitlab.io/img/cactuscon-ctf-2022-cover.png)

Over the weekend, a few of us from Neutrino Cannon competed in the CactusCon
2022 CTF by ThreatSims. PolarBearer and I worked on a challenge called
Funware, which was a interesting forensics challenge that starts with a disk
image of a system that’d been ransomwared, and leads to understanding the
malware, decrypting the files, and finding where it was downloaded from. It
was a fun forensics challenge. Thanks to [@pwnEIP](https://twitter.com/pwnEIP)
and [@Cone_Virus](https://twitter.com/Cone_Virus) for the challenge and for
getting me the questions after it was over so I could write this up.

## Funware

### Overview

This challenge was 13 questions long, and all based on the provided an
AccessData AD1 forensic disk image, which I’ve hosted
[here](https://drive.google.com/file/d/1ha9pPSGZNCSIz-
NTIFKDMjaEw3BGf5vB/view?usp=sharing).

**_Note: There is malware that will do malwarish things inside this image.
Play with it at your own risk._**

The initial prompt says:

> Well shoot. Looks like our IT Technician has been compromised. We took an
> image of his system and zipped it up with the password fUnW4R34L1fe.

### Tools

To get started in this challenge, I used a Windows VM and installed FTK
Imager, which can be downloaded [here](https://accessdata.com/product-
download/ftk-imager-version-4-5) (an email is needed, but as far as I can
tell, doesn’t have to be a working email). I also used a Linux VM for
programming, but that could have been done in the Windows VM as well.

Alternatives:

  * It also seems like FTK Imager may have a Linux version.
  * Autopsy could be another Linux alternative to look at these files (that I just don’t have experience with yet).
  * `pyad1` is a [neat looking tool](https://github.com/pcbje/pyad1) for interacting with AccessData files.
  * [Forensic7z](https://www.tc4shell.com/en/7zip/forensic7z/) is a plugin for [7zip](https://www.7-zip.org/) that allows it to open and interact with image files.

## File System Analysis

The first three challenges were solved by exploring the file system in the
disk image.

### #0: Username

_Can you figure out what his username is?_

I’ll open `Evidence.ad1` in FTK Imager, and it looks like it’s a capture of
the `C:\Users` folder from a Windows machine:

![image-20220206141930761](https://0xdfimages.gitlab.io/img/image-20220206141930761.png)

Right away I can answer the question, as the only non-standard folder name
there is `Anime-Lover99`, so that’s the username.

**Flag:`Anime-Lover99`**

### #1: Read Flag

_If you can figure out his username im sure you can find his flag._

On the user’s desktop, there’s a handful of files ending in `.miku`, an
executable (`musiware.exe`), and a text file, `user,txt`:

![image-20220206142606598](https://0xdfimages.gitlab.io/img/image-20220206142606598.png)

Clicking on `user.txt`, the contents are displayed in the window below, giving
the flag:

![image-20220206142627014](https://0xdfimages.gitlab.io/img/image-20220206142627014.png)

**Flag:`flag{aN1m3_f0r_l1f3}`**

### #2: Find Malware

_What is the name of the malware?_

As I noted above, there’s also an executable unencrypted on the desktop,
`musiware.exe`.

**Flag:`musiware.exe`**

## Malware Analysis

### Running It

I never actually run the malware in solving the challenge, but it would make
sense to give it a run on a clean system, so for completeness in writing this
post, I created a dummy user, took a snapshot, and logged in as dummy to run
it.

On double clicking, it actually won’t run because I don’t have audio enabled
on my VM:

![image-20220207115128448](https://0xdfimages.gitlab.io/img/image-20220207115128448.png)

After adjusting the settings and trying again, it hangs for a minute (while
it’s encrypting the files in the home directory), and then this pops up:

![image-20220207114821302](https://0xdfimages.gitlab.io/img/image-20220207114821302.png)

When I click “Play!”, it just dies. I could try more to get it working, but I
didn’t need to.

### #3: Malware Language

_Damn this malware looks somewhat familiar. Can you tell me what it is written
in?_

Running `strings` on the binary produces all kinds of hints that this binary
is running in Python:

    
    
    oxdf@hacky$ strings -n 12 musiware.exe
    ...[snip]...
    _pyi_main_co
    pyi-disable-windowed-traceback
    ...[snip]...
    Py_DontWriteBytecodeFlag
    Failed to get address for Py_DontWriteBytecodeFlag
    GetProcAddress
    Py_FileSystemDefaultEncoding
    Failed to get address for Py_FileSystemDefaultEncoding
    Py_FrozenFlag
    Failed to get address for Py_FrozenFlag
    Py_IgnoreEnvironmentFlag
    Failed to get address for Py_IgnoreEnvironmentFlag
    Py_NoSiteFlag
    Failed to get address for Py_NoSiteFlag
    Py_NoUserSiteDirectory
    Failed to get address for Py_NoUserSiteDirectory
    Py_OptimizeFlag
    Failed to get address for Py_OptimizeFlag
    Py_VerboseFlag
    Failed to get address for Py_VerboseFlag
    Py_UnbufferedStdioFlag
    Failed to get address for Py_UnbufferedStdioFlag
    Py_BuildValue
    Failed to get address for Py_BuildValue
    Failed to get address for Py_DecRef
    Failed to get address for Py_Finalize
    Failed to get address for Py_IncRef
    Py_Initialize
    Failed to get address for Py_Initialize
    Failed to get address for Py_SetPath
    Failed to get address for Py_GetPath
    Py_SetProgramName
    Failed to get address for Py_SetProgramName
    Py_SetPythonHome
    Failed to get address for Py_SetPythonHome
    PyDict_GetItemString
    Failed to get address for PyDict_GetItemString
    Failed to get address for PyErr_Clear
    PyErr_Occurred
    Failed to get address for PyErr_Occurred
    Failed to get address for PyErr_Print
    Failed to get address for PyErr_Fetch
    ...[snip]...
    xpygame\freesansbold.ttf
    xpygame\pygame_icon.bmp
    xpyinstaller-4.7.dist-info\COPYING.txt
    xpyinstaller-4.7.dist-info\INSTALLER
    xpyinstaller-4.7.dist-info\METADATA
    xpyinstaller-4.7.dist-info\RECORD
    xpyinstaller-4.7.dist-info\WHEEL
    xpyinstaller-4.7.dist-info\entry_points.txt
    xpyinstaller-4.7.dist-info\top_level.txt
    3python37.dll
    

And not just Python, but [pygame](https://www.pygame.org/news) and
[pyinstaller](https://pyinstaller.readthedocs.io/en/stable/) are both
referenced. PyGame is a framework for creating GUI games in Python.
PyInstaller is a framework for converting Python scripts into stand-alone
executables (Windows or Linux).

**Flag:`Python`**

### Extract Python Script

#### Fail Extracting PYC Files

I need to pull the Python source out of the executable in order to take a look
at it. In the 2019 Flare-On challenge, [wopr](/flare-on-2019/wopr.html#python-
exe-unpacker), I used [python-exe-
unpacker](https://github.com/countercept/python-exe-unpacker). That will work
here, but it hasn’t been updated in four years, so I’ll use
[pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor), which
looks like it’s actively being developed.

When I run this on the executable, it kind of works:

    
    
    oxdf@hacky$ python /opt/pyinstxtractor/pyinstxtractor.py musiware.exe
    [+] Processing musiware.exe
    [+] Pyinstaller version: 2.1+
    [+] Python version: 307
    [+] Length of package: 42552565 bytes
    [+] Found 115 files in CArchive
    [+] Beginning extraction...please standby
    [+] Possible entry point: pyiboot01_bootstrap.pyc
    [+] Possible entry point: pyi_rth_pkgutil.pyc    
    [+] Possible entry point: pyi_rth_inspect.pyc
    [+] Possible entry point: pyi_rth_pkgres.pyc    
    [+] Possible entry point: musiware.pyc
    [!] Warning: This script is running in a different Python version than the one used to build the executable.
    [!] Please run this script in Python307 to prevent extraction errors during unmarshalling
    [!] Skipping pyz extraction
    [+] Successfully extracted pyinstaller archive: musiware.exe
    
    You can now use a python decompiler on the pyc files within the extracted directory 
    

There is a directory with a bunch of extracted files, but there’s also an
error message in the output above:

    
    
    [!] Please run this script in Python307 to prevent extraction errors during unmarshalling
    

Running `file` on the main file just thinks it’s data, because the magic bytes
are messed up:

    
    
    oxdf@hacky$ file musiware.pyc 
    musiware.pyc: data
    

Trying to decompile this back to Python code fails:

    
    
    oxdf@hacky$ uncompyle6 musiware.pyc 
    Traceback (most recent call last):
      File "/home/oxdf/.local/lib/python3.8/site-packages/xdis/load.py", line 300, in load_module_from_file_object
        co = marshal.loads(bytecode)
    ValueError: bad marshal data (unknown type code)
    Ill-formed bytecode file musiware.pyc
    <class 'ValueError'>; bad marshal data (unknown type code)
    

#### Switch Python Version

There’s a hacky solution [I used in Flare-On to solve this](/flare-
on-2019/wopr.html#magic), based on [this
article](https://web.archive.org/web/20190715191218/https://infosecuritygeek.com/reversing-
a-simple-python-ransomware/) (site is no more, now based on wayback machine),
but the better way is to just install Python3.7 ([these
instructions](https://linuxize.com/post/how-to-install-python-3-7-on-
ubuntu-18-04/) worked for me). I’ll also install `sudo apt install
python3.7-venv`.

I’ll create a virtual environment based on Python3.7:

    
    
    oxdf@hacky$ python3.7 -mvenv venv
    oxdf@hacky$ source venv/bin/activate
    (venv) oxdf@hacky$ python -V
    Python 3.7.12
    

I’ll `pip install uncompyle6` to get that in the env. Now running
`pyinstxtractor` works without complaining about version:

    
    
    (venv) oxdf@hacky$ python /opt/pyinstxtractor/pyinstxtractor.py musiware.exe
    [+] Processing musiware.exe
    [+] Pyinstaller version: 2.1+
    [+] Python version: 307
    [+] Length of package: 42552565 bytes
    [+] Found 115 files in CArchive
    [+] Beginning extraction...please standby
    [+] Possible entry point: pyiboot01_bootstrap.pyc
    [+] Possible entry point: pyi_rth_pkgutil.pyc
    [+] Possible entry point: pyi_rth_inspect.pyc
    [+] Possible entry point: pyi_rth_pkgres.pyc
    [+] Possible entry point: musiware.pyc
    [+] Found 256 files in PYZ archive
    [+] Successfully extracted pyinstaller archive: musiware.exe
    
    You can now use a python decompiler on the pyc files within the extracted directory
    

And `uncompyle6` works great:

    
    
    (venv) oxdf@hacky$ uncompyle6 musiware.pyc > musiware.py
    

The full script can be found [here](/files/cactuscon22-musiware.py).

### Script Analysis

After defining constants and several functions, the script sets up for and
then executes it’s main loop:

    
    
    fun_enforcer()
    screen = pygame.display.set_mode([600, 600])
    Icon = pygame.image.load(resource_path('assets/images/favicon.png'))
    pygame.display.set_icon(Icon)
    pygame.display.set_caption('Musiware')
    state = ['Main', True]
    game_state = 0
    score = 0
    while 1:
        if game_state == 6:
            state[0] = 'End'
            state[1] = True
        else:
            if state[0] == 'Main':
                if state[1]:
                    main_setup(screen)
                    state[1] = False
            if state[0] == 'End':
                if state[1]:
                    screen = pygame.display.set_mode([600, 600])
                    end_setup(screen, score)
                    state[1] = False
            if state[0] == 'Game':
                if state[1]:
                    state[1] = False
                    game_current = game_state
                    game = game(game_current)
                else:
                    game_state, score = game.run(score, screen)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state[0] == 'Main' and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if x > 260 and 550 > x and 505 > y and y > 455:
                    screen = pygame.display.set_mode([600, 800])
                    state[0] = 'Game'
                    state[1] = True
    # okay decompiling musiware.pyc
    

### #4: Score

_Well now that we know what it is written in. What is the score needed for
this seemingly impossible game?_

At the very top of the Python script, it defines several global variables:

    
    
    # uncompyle6 version 3.8.0
    # Python bytecode 3.7.0 (3394)
    # Decompiled from: Python 3.7.12 (default, Jan 15 2022, 18:42:10) 
    # [GCC 9.3.0]
    # Embedded file name: musiware.py
    import pygame, time, os, sys, random
    from pygame import mixer
    from PIL import Image
    RED = [
     255, 0, 0]
    WHITE = [255, 255, 255]
    BLACK = [0, 0, 0]
    MAX = 10000000000000000000000000000000000000000000000000000000000000000
    pygame.init()
    pygame.mixer.init()
    ...[snip]...
    

That `MAX` variable is interesting. Looking at where it’s used, it’s in the
function `end_setup`:

    
    
    def end_setup(screen, score):
        back = Button(0, 0, 'assets/images/end.jpg')
        back.draw(screen)
        if score >= MAX:
            font = pygame.font.Font(resource_path('assets/sans.ttf'), 50)
            text = font.render('Congrats!', True, RED)
            screen.blit(text, [200, 10])
            font = pygame.font.Font(resource_path('assets/sans.ttf'), 30)
            text = font.render('You got a score of ' + str(score) + '/' + str(MAX) + '!', True, RED)
            screen.blit(text, [130, 100])
            if score > MAX:
                font = pygame.font.Font(resource_path('assets/sans.ttf'), 30)
                text = font.render('You did cheat.... Oh Well', True, RED)
                screen.blit(text, [120, 175])
            else:
                font = pygame.font.Font(resource_path('assets/sans.ttf'), 30)
                text = font.render("And it seems like you didn't cheat!", True, RED)
                screen.blit(text, [50, 175])
            font = pygame.font.Font(resource_path('assets/sans.ttf'), 30)
            text = font.render('Get the Decryption Application at:', True, RED)
            screen.blit(text, [50, 250])
            font = pygame.font.Font(resource_path('assets/sans.ttf'), 20)
            text = font.render('http://musiware.threatsims.com/5963decodenow5345/', True, RED)
            screen.blit(text, [35, 325])
        else:
            font = pygame.font.Font(resource_path('assets/sans.ttf'), 50)
            text = font.render(' Uh Oh!! ', True, RED)
            screen.blit(text, [210, 10])
            font = pygame.font.Font(resource_path('assets/sans.ttf'), 70)
            text = font.render('You Failed!', True, RED)
            screen.blit(text, [125, 250])
    

It’s looking for a score of exactly `MAX` to win.

Flag:`10000000000000000000000000000000000000000000000000000000000000000`

### #5: URL

_If we even had a chance of beating this malware. Where is the URL it would of
given us?_

In the `end_setup` function, it prints the URL:

    
    
    font = pygame.font.Font(resource_path('assets/sans.ttf'), 30)
    text = font.render('Get the Decryption Application at:', True, RED)
    screen.blit(text, [50, 250])
    font = pygame.font.Font(resource_path('assets/sans.ttf'), 20)
    text = font.render('http://musiware.threatsims.com/5963decodenow5345/',
    

**Flag:`http://musiware.threatsims.com/5963decodenow5345/`**

### #6: Key

_It seems that the maker of this malware had somewhat of a sense of humor.
What is used to create entropy for the encryption?_

The first function called was `fun_enforcer()`, which is defined as:

    
    
    def fun_enforcer():
        img = open(resource_path('assets/images/miku.png'), 'rb').read() * 50
        home = os.path.expanduser('~')
        for root, dirs, files in os.walk(home, topdown=False):
            for name in files:
                if not name == 'musiware.exe':
                    if 'assets' in root:
                        continue
                    fileN = os.path.join(root, name)
                    try:
                        fileD = open(fileN, 'rb').read()
                        os.remove(fileN)
                        result = bytes((a ^ b for a, b in zip(fileD, img)))
                        f = open(fileN + '.miku', 'wb')
                        f.write(result)
                        f.close()
                    except:
                        continue
    

It reads in a buffer that is the bytes from an image carried in the
executable’s resources, `miku.png`, five times. That image was unpacked
earlier into my file system as well, and is about 110kb in size:

    
    
    (venv) oxdf@hacky$ ls -l assets/images/miku.png
    -rw-rw-r-- 1 oxdf oxdf 110363 Feb  6 16:21 assets/images/miku.png
    

Then it walks the files in the users home directory and subdirectories, for
each of them opening the file, reading it, removing the original file, xoring
the file by the image file, and writing the result the the same file name plus
`.miku`.

So the answer is `miku.png`.

**Flag:`miku.png`**

### #7: Levels

_How many levels is in this malware “game”?_

In the main loop, it starts at level 0, and ends at level 6:

    
    
    game_state = 0
    score = 0
    while 1:
        if game_state == 6:
            state[0] = 'End'
            state[1] = True
        else:
            if state[0] == 'Main':
                if state[1]:
                    main_setup(screen)
                    state[1] = False
            if state[0] == 'End':
                if state[1]:
                    screen = pygame.display.set_mode([600, 600])
                    end_setup(screen, score)
                    state[1] = False
            if state[0] == 'Game':
                if state[1]:
                    state[1] = False
                    game_current = game_state
                    game = game(game_current)
                else:
                    game_state, score = game.run(score, screen)
    

So the number of levels is 7.

**Flag:`7`**

## Data Recovery

### #8: Encrypted Images

_How many of the IT Tech’s image files on his desktop got encrypted?_

Back to the image and FTK Imager, there are nine image files on the Desktop
with the `.miku` extension:

![image-20220206200240605](https://0xdfimages.gitlab.io/img/image-20220206200240605.png)

**Flag:`9`**

### Recover Files

I’ll grab a copy of `miku.png` from the `assets/images` extracted directory,
and write this very simple Python script to decrypt files:

    
    
    #!/usr/bin/env python3
    
    import sys
    from itertools import cycle
    
    with open(sys.argv[1], 'rb') as f:
        enc = f.read()
    
    with open('miku.png', 'rb') as f:
        key = f.read()
    
    pt = bytes([x^y for x,y in zip(enc, cycle(key))])
    
    orig_name = '.'.join(sys.argv[1].split('.')[:-1])
    
    with open(orig_name, 'wb') as f:
        f.write(pt)
    
    print(f'[+] Wrote {orig_name}')
    

First, it reads in the file passed in via the command line into the `enc`
variable. Then it reads `miku.png` into `key`.

`zip(enc, cycle(key))` will take each byte of `enc` and pair it with the same
offset byte in `key`. `zip` stops when either of the two buffers reaches the
end, so the `cycle` function will effectively endless stack `key` until the
end of `enc`. Technically if the file was larger than five times the size of
`miku.png`, this would make some incorrect output, but it’s ok here.

The list comprehension will loop over each pair of bytes, xoring them, which
results a list of integers, which `bytes` will convert into a byte string,
saved at `pt`.

I’ll get the original file name by dropping the `.miku` extension, and write
the result to that file.

### #9: Recover Images

_I’m sure a forensics expert like you can decrypt these files. Can you find
the flag hidden among the image files?_

In FTK Imager, I’ll select all the `.miku` files, and then “File” -> “Export
Files…”:

![image-20220207095531304](https://0xdfimages.gitlab.io/img/image-20220207095531304.png)

I’ll save the files and copy them to my Linux VM. There I can use a `find`
command to decrypt them all:

    
    
    oxdf@hacky$ find . -name '*.miku' -exec python decrpyt.py {} \;
    [+] Wrote ./Anime10.jpg
    [+] Wrote ./Anime1.jpg
    [+] Wrote ./Anime12.jpg
    [+] Wrote ./desktop.ini
    [+] Wrote ./Anime3.png
    [+] Wrote ./Anime4.jpg
    [+] Wrote ./Anime11.jpg
    [+] Wrote ./Anime6.webp
    [+] Wrote ./Anime2.jpg
    [+] Wrote ./Anime9.jpg
    [+] Wrote ./Backup.zip
    

There’s some text written across `Anime12.jpg`:

![image-20220207100109890](https://0xdfimages.gitlab.io/img/image-20220207100109890.png)

It does have the flag printed on it:

![](https://0xdfimages.gitlab.io/img/Anime12.jpg)

**Flag:`flag{aN1m3_i5_th3_b3sT}`**

### #10: Recover Zip

_It seems the IT Tech had a backup zip folder. Can you grab his password in
it? Yes, it’s a valid zip, maybe your archive tool is having issues, find
another one._

Both `unzip` and `7z` error out on the command line:

    
    
    oxdf@hacky$ unzip Backup.zip
    Archive:  Backup.zip
      End-of-central-directory signature not found.  Either this file is not
      a zipfile, or it constitutes one disk of a multi-part archive.  In the
      latter case the central directory and zipfile comment will be found on
      the last disk(s) of this archive.
    note:  Backup.zip may be a plain executable, not an archive
    unzip:  cannot find zipfile directory in one of Backup.zip or
            Backup.zip.zip, and cannot find Backup.zip.ZIP, period.
    oxdf@hacky$ 7z x Backup.zip
    
    7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
    p7zip Version 16.02 (locale=en_US.UTF-8,Utf16=on,HugeFiles=on,64 bits,4 CPUs AMD Ryzen 9 5900X 12-Core Processor             (A20F10),ASM,AES-NI)
    
    Scanning the drive for archives:
    1 file, 5518150 bytes (5389 KiB)
    
    Extracting archive: Backup.zip
    
    ERRORS:
    Unexpected end of archive
    
    --
    Path = Backup.zip
    Type = zip
    ERRORS:
    Unexpected end of archive
    Physical Size = 7177945
    
    ERROR: Data Error : Firefox-Backup/tfe16msd.default-release/storage/permanent/chrome/idb/3870112724rsegmnoittet-es.sqlite
                                                                               
    Sub items Errors: 1
    
    Archives with Errors: 1
    
    Open Errors: 1
    
    Sub items Errors: 1
    

On Windows, 7z GUI opens it just fine:

![image-20220207103644210](https://0xdfimages.gitlab.io/img/image-20220207103644210.png)

Double clicking on `pass.txt` opens it in `notepad.exe`:

![image-20220207103712230](https://0xdfimages.gitlab.io/img/image-20220207103712230.png)

That password is the flag.

**Flag:`an1m3l0v3r`**

### #11: Browser History

_Can you find out the URL that the malware was downloaded from?_

The rest of the zip is a `Firefox-Backup` folder. It contains two profiles,
one of which is basically empty:

    
    
    oxdf@hacky$ ls
    6vz210rr.default  tfe16msd.default-release
    oxdf@hacky$ ls 6vz210rr.default/
    times.json
    oxdf@hacky$ ls tfe16msd.default-release/
    addons.json               cert9.db              crashes                     features            logins.json         places.sqlite          security_state           shield-preference-experiments.json
    addonStartup.json.lz4     compatibility.ini     datareporting               formhistory.sqlite  minidumps           prefs.js               serviceworker.txt        SiteSecurityServiceState.txt
    AlternateServices.txt     containers.json       extension-preferences.json  gmp-gmpopenh264     parent.lock         protections.sqlite     sessionCheckpoints.json  storage
    bookmarkbackups           content-prefs.sqlite  extensions.json             handlers.json       permissions.sqlite  saved-telemetry-pings  sessionstore-backups     storage.sqlite
    broadcast-listeners.json  cookies.sqlite        favicons.sqlite             key4.db             pkcs11.txt          search.json.mozlz4     sessionstore.jsonlz4
    

`places.sqlite` holds the browser history. It has a bunch of tables:

    
    
    oxdf@hacky$ sqlite3 places.sqlite 
    SQLite version 3.31.1 2020-01-27 19:55:54
    Enter ".help" for usage hints.
    sqlite> .tables
    moz_anno_attributes                    
    moz_annos                              
    moz_bookmarks                          
    moz_bookmarks_deleted                  
    moz_historyvisits                      
    moz_inputhistory                       
    moz_items_annos                        
    moz_keywords                           
    moz_meta                               
    moz_origins                            
    moz_places                             
    moz_places_metadata                    
    moz_places_metadata_groups_to_snapshots
    moz_places_metadata_search_queries     
    moz_places_metadata_snapshots          
    moz_places_metadata_snapshots_extra    
    moz_places_metadata_snapshots_groups   
    moz_session_metadata                   
    moz_session_to_places 
    

The `moz_places` tables has the urls visited, along with many other columns:

    
    
    sqlite> .schema moz_places
    CREATE TABLE moz_places (   id INTEGER PRIMARY KEY, url LONGVARCHAR, title LONGVARCHAR, rev_host LONGVARCHAR, visit_count INTEGER DEFAULT 0, hidden INTEGER DEFAULT 0 NOT NULL, typed INTEGER DEFAULT 0 NOT NULL, frecency INTEGER DEFAULT -1 NOT NULL, last_visit_date INTEGER , guid TEXT, foreign_count INTEGER DEFAULT 0 NOT NULL, url_hash INTEGER DEFAULT 0 NOT NULL , description TEXT, preview_image_url TEXT, origin_id INTEGER REFERENCES moz_origins(id));
    CREATE INDEX moz_places_url_hashindex ON moz_places (url_hash);
    CREATE INDEX moz_places_hostindex ON moz_places (rev_host);
    CREATE INDEX moz_places_visitcount ON moz_places (visit_count);
    CREATE INDEX moz_places_frecencyindex ON moz_places (frecency);
    CREATE INDEX moz_places_lastvisitdateindex ON moz_places (last_visit_date);
    CREATE UNIQUE INDEX moz_places_guid_uniqueindex ON moz_places (guid);
    CREATE INDEX moz_places_originidindex ON moz_places (origin_id);
    

Looks like the admin visited `mozilla.org`, `youtube.com`, and one suspect URL
where the malware was downloaded:

    
    
    sqlite> select id,url from moz_places;
    id|url
    1|https://support.mozilla.org/en-US/products/firefox
    2|https://support.mozilla.org/en-US/kb/customize-firefox-controls-buttons-and-toolbars?utm_source=firefox-browser&utm_medium=default-bookmarks&utm_campaign=customize
    3|https://www.mozilla.org/en-US/contribute/
    4|https://www.mozilla.org/en-US/about/
    5|https://www.mozilla.org/en-US/firefox/central/
    6|https://www.mozilla.org/privacy/firefox/
    7|https://www.mozilla.org/en-US/privacy/firefox/
    8|https://www.google.com/search?client=firefox-b-1-d&q=anime
    9|https://www.google.com/search?q=anime+youtube&client=firefox-b-1-d&ei=VTPCYZO-EtaXwbkPoNK4qAE&ved=0ahUKEwjTvKGe2PX0AhXWSzABHSApDhUQ4dUDCA4&uact=5&oq=anime+youtube&gs_lcp=Cgdnd3Mtd2l6EAMyBQgAEJECMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEOgcIABBHELADOgcIABCwAxBDOggIABDkAhCwAzoKCC4QyAMQsAMQQzoQCC4QxwEQ0QMQyAMQsAMQQzoHCAAQsQMQQzoECAAQQzoICAAQgAQQsQM6CAgAEIAEEMkDOgUIABCSAzoICC4QsQMQkQI6BQguEIAESgQIQRgASgQIRhgBULoHWMASYI8UaAFwAngAgAGqAogB0gmSAQUyLjAuNJgBAKABAcgBE8ABAQ&sclient=gws-wiz
    10|https://www.youtube.com/c/netflixanime
    11|https://www.youtube.com/watch?v=n8u1SEVj7kU
    12|https://www.youtube.com/watch?v=7L3DQU74v_s
    13|https://www.youtube.com/
    14|https://www.youtube.com/watch?v=WItvH4Hoyag
    15|https://www.youtube.com/watch?v=xohAPIRNzuo
    16|http://musiware.threatsims.com/musiware.exe
    17|https://www.mozilla.org/firefox/welcome/13
    18|https://www.mozilla.org/en-US/firefox/welcome/13
    19|https://www.mozilla.org/en-US/firefox/welcome/13/
    

Looking at the entries, this one took me a minute because I expected the flag
to be the full URL, but the system was looking for only the start.

**Flag:`https://musiware.threatsims.com`**

### #12: Password Recovery

_Well, the IT Tech can’t remember what his password was, can you recover it
for him?_

Staying in the zip, Firefox can save passwords for sites.

[This post](https://apr4h.github.io/2019-12-20-Harvesting-Browser-
Credentials/) does a really nice job walking through how Firefox (and Chrome)
passwords can be decrypted. [This
Diagram](https://raw.githubusercontent.com/lclevy/firepwd/master/mozilla_pbe.pdf)
is also really useful:

[![](https://0xdfimages.gitlab.io/img/mozilla_pbe-1.png)_Click for full size
image_](https://0xdfimages.gitlab.io/img/mozilla_pbe-1.png)

The process is quite complicated, so I’ll use a too like
[Firepwd](https://github.com/lclevy/firepwd) to extract and decrypt passwords:

    
    
    oxdf@hacky$ python3 /opt/firepwd/firepwd.py -d tfe16msd.default-release/
    ...[snip]...
    decrypting login/password pairs
    https://musiware.threatsims.com:b'Anime-Lover99',b'1t5jUstAgAm3'
    

**Flag:`1t5jUstAgAm3`**

[](/2022/02/07/funware-cactuscon-2022-ctf.html)

