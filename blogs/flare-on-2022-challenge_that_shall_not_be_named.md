# Flare-On 2022: The challenge that shall not be named

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-the-challenge-that-
shall-not-be-named](/tags#flare-on-the-challenge-that-shall-not-be-named )
[reverse-engineering](/tags#reverse-engineering ) [memory-dump](/tags#memory-
dump ) [pyinstaller](/tags#pyinstaller ) [pyarmor](/tags#pyarmor )
[pyinstxtractor](/tags#pyinstxtractor ) [uncompyle6](/tags#uncompyle6 )
[pyarmor-unpacker](/tags#pyarmor-unpacker ) [hook](/tags#hook )
[python](/tags#python )  
  
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
  * [[10] Nur geträumt](/flare-on-2022/nur_getraumt)
  * [11] The challenge that shall not be named

![The challenge that shall not be
named](https://0xdfimages.gitlab.io/img/flare2022-notnamed-cover.png)

The challenge that shall not be named is a Windows executable generated with
PyArmor, a tool that aims to create unreversible binarys from Python. The
binary makes an HTTP request with an encrypted flag. I’ll first solve it by
holding open that web request and dumping the process memory to find the flag
in plaintext. I’ll also show how to hook the crypt Python library to read the
flag as it’s being encrypted.

## Challenge

> Protection, Obfuscation, Restrictions… Oh my!!
>
> The good part about this one is that if you fail to solve it I don’t need to
> ship you a prize.

The download contains a 64-bit Windows executable:

    
    
    $ file 11.exe 
    11.exe: PE32+ executable (console) x86-64, for MS Windows
    

## Video

This challenge has a bunch of interesting interactive parts, and it’s
surprisingly quick to solve for a last challenge, so I’ll show the entire
thing in a [video solution](https://www.youtube.com/watch?v=oqS3aj2yS68) as
well:

## Run It

### Nothing

Nothing visible happens on a double click or running via terminal:

![image-20221021101636776](https://0xdfimages.gitlab.io/img/image-20221021101636776.png)

### Network

With WireShark open, I’ll catch a single request before the process finishes:

![image-20221021124736297](https://0xdfimages.gitlab.io/img/image-20221021124736297.png)

I’ll add `www.evil.flare-on.com` to my hosts file
(`C:\Windows\System32\drivers\etc\hosts`):

    
    
    127.0.0.1 www.evil.flare-on.com
    

On running the binary again, there’s no DNS (because the `hosts` file answers
before it tries DNS), but now failed attempts to talk to 127.0.0.1 on port 80:

![image-20221021125008067](https://0xdfimages.gitlab.io/img/image-20221021125008067.png)

I’ll start `nc` listening on 80, and catch the incoming HTTP request:

![image-20221021125136155](https://0xdfimages.gitlab.io/img/image-20221021125136155.png)

The POST body has a `flag` parameter that holds some base64-encoded data. It
doesn’t decode to anything interesting.

### Crash

If I start `11.exe` without `nc` listening, it hangs waiting to connect. If I
Ctrl-c while that is happening, it prints a crash dump:

    
    
    PS > .\11.exe
    Traceback (most recent call last):
      File "urllib3\util\connection.py", line 85, in create_connection
    ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it
    
    During handling of the above exception, another exception occurred:
    
    Traceback (most recent call last):
      File "<dist\obf\11.py>", line 2, in <module>
      File "<frozen 11>", line 19, in <module>
      File "<frozen 11>", line 16, in <module>
      File "requests\api.py", line 115, in post
      File "requests\api.py", line 59, in request
      File "requests\sessions.py", line 587, in request
      File "requests\sessions.py", line 701, in send
      File "requests\adapters.py", line 499, in send
      File "urllib3\connectionpool.py", line 710, in urlopen
      File "urllib3\connectionpool.py", line 398, in _make_request
      File "urllib3\connection.py", line 239, in request
      File "http\client.py", line 1277, in request
      File "http\client.py", line 1323, in _send_request
      File "http\client.py", line 1272, in endheaders
      File "http\client.py", line 1032, in _send_output
      File "http\client.py", line 972, in send
      File "urllib3\connection.py", line 205, in connect
      File "urllib3\connection.py", line 175, in _new_conn
      File "urllib3\util\connection.py", line 85, in create_connection
    KeyboardInterrupt
    [6572] Failed to execute script '11' due to unhandled exception!
    

This is clearly a Python crash dump.

## Read Flag From Memory

I don’t believe this is the intended path for the challenge, but the flag is
available in clear text inside the process memory while it’s running. The
easiest ways to get a memory dump require that the process run for more than a
second. I’ll hang the TCP port 80 connection so that the program waits for it
to respond by listening with `nc` and catching the web connect, but not
responding. The process hangs waiting for the server to respond.

In task manager, I’ll find the process:

![image-20221021133738826](https://0xdfimages.gitlab.io/img/image-20221021133738826.png)

There’s two there. I’ll right click on the larger one and select “Create dump
file”:

![image-20221021133817583](https://0xdfimages.gitlab.io/img/image-20221021133817583.png)

It produces `AppData\Local\Temp\11.DMP`, which I’ll open with a hex editor (I
use `HxD`). I’ll do a search for “flare”, and use the “Search all” option to
get the flag:

[![image-20221021134221572](https://0xdfimages.gitlab.io/img/image-20221021134221572.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221021134221572.png)

`strings` will fetch the flag as well:

    
    
    oxdf@hacky$ strings 11.DMP | grep '@flare-on.com'
    Pyth0n_Prot3ction_tuRn3d_Up_t0_11@flare-on.coms
    Pyth0n_Prot3ction_tuRn3d_Up_t0_11@flare-on.com
    

## RE

### strings

When `strings` is run on the binary that there’s tons of Python references.
The first important set of strings is:

    
    
    PyInstaller: FormatMessageW failed.
    PyInstaller: pyi_win32_utils_to_utf8 failed.
    

The binary uses [PyInstaller](https://pyinstaller.org/en/stable/) to build a
Windows executable from Python code. PyInstaller will package everything the
binary will need, including a Python interpreter, into the exe. The other is:

    
    
    pyarmor
    PYARMOR
    

[PyArmor](https://pyarmor.dashingsoft.com/) is a tool for obfuscating and
packing Python scripts into binaries in a manner meant to be unreversable.

### Extract Python

#### PyInstxtractor

I’ve run into PyInstaller [before](/tags#pyinstaller). I’ll extract it with
`pyinstxtractor.py` from [this repo](https://github.com/extremecoders-
re/pyinstxtractor):

    
    
    oxdf@hacky$ python /opt/pyinstxtractor/pyinstxtractor.py 11.exe     
    [+] Processing 11.exe
    [+] Pyinstaller version: 2.1+
    [+] Python version: 307
    [+] Length of package: 8807847 bytes
    [+] Found 80 files in CArchive
    [+] Beginning extraction...please standby
    [+] Possible entry point: pyiboot01_bootstrap.pyc
    [+] Possible entry point: pyi_rth_subprocess.pyc
    [+] Possible entry point: pyi_rth_inspect.pyc
    [+] Possible entry point: 11.pyc
    [!] Warning: This script is running in a different Python version than the one used to build the executable.
    [!] Please run this script in Python307 to prevent extraction errors during unmarshalling                               
    [!] Skipping pyz extraction
    [+] Successfully extracted pyinstaller archive: 11.exe
    
    You can now use a python decompiler on the pyc files within the extracted directory
    

It identifies the Python version in the challenge as 3.7, and complains that I
used a different version. My system is running 3.8:

    
    
    oxdf@hacky$ python -V
    Python 3.8.10
    

I’ll extract again using 3.7:

    
    
    oxdf@hacky$ python3.7 /opt/pyinstxtractor/pyinstxtractor.py 11.exe     
    [+] Processing 11.exe
    [+] Pyinstaller version: 2.1+
    [+] Python version: 307
    [+] Length of package: 8807847 bytes
    [+] Found 80 files in CArchive
    [+] Beginning extraction...please standby
    [+] Possible entry point: pyiboot01_bootstrap.pyc
    [+] Possible entry point: pyi_rth_subprocess.pyc
    [+] Possible entry point: pyi_rth_inspect.pyc
    [+] Possible entry point: 11.pyc
    [+] Found 250 files in PYZ archive
    [+] Successfully extracted pyinstaller archive: 11.exe
    
    You can now use a python decompiler on the pyc files within the extracted directory
    

The result is a bunch of DLLs and compiled Python byte code:

    
    
    oxdf@hacky$ ls 11.exe_extracted/
    11.pyc                                         api-ms-win-core-timezone-l1-1-0.dll    libcrypto-1_1.dll
    api-ms-win-core-console-l1-1-0.dll             api-ms-win-core-util-l1-1-0.dll        libssl-1_1.dll
    api-ms-win-core-datetime-l1-1-0.dll            api-ms-win-crt-conio-l1-1-0.dll        _lzma.pyd
    api-ms-win-core-debug-l1-1-0.dll               api-ms-win-crt-convert-l1-1-0.dll      pyiboot01_bootstrap.pyc
    api-ms-win-core-errorhandling-l1-1-0.dll       api-ms-win-crt-environment-l1-1-0.dll  pyimod01_os_path.pyc
    api-ms-win-core-file-l1-1-0.dll                api-ms-win-crt-filesystem-l1-1-0.dll   pyimod02_archive.pyc
    api-ms-win-core-file-l1-2-0.dll                api-ms-win-crt-heap-l1-1-0.dll         pyimod03_importers.pyc
    api-ms-win-core-file-l2-1-0.dll                api-ms-win-crt-locale-l1-1-0.dll       pyimod04_ctypes.pyc
    api-ms-win-core-handle-l1-1-0.dll              api-ms-win-crt-math-l1-1-0.dll         pyi_rth_inspect.pyc
    api-ms-win-core-heap-l1-1-0.dll                api-ms-win-crt-process-l1-1-0.dll      pyi_rth_subprocess.pyc
    api-ms-win-core-interlocked-l1-1-0.dll         api-ms-win-crt-runtime-l1-1-0.dll      python37.dll
    api-ms-win-core-libraryloader-l1-1-0.dll       api-ms-win-crt-stdio-l1-1-0.dll        python3.dll
    api-ms-win-core-localization-l1-2-0.dll        api-ms-win-crt-string-l1-1-0.dll       pytransform.pyd
    api-ms-win-core-memory-l1-1-0.dll              api-ms-win-crt-time-l1-1-0.dll         PYZ-00.pyz
    api-ms-win-core-namedpipe-l1-1-0.dll           api-ms-win-crt-utility-l1-1-0.dll      PYZ-00.pyz_extracted
    api-ms-win-core-processenvironment-l1-1-0.dll  base_library.zip                       _queue.pyd
    api-ms-win-core-processthreads-l1-1-0.dll      bcrypt                                 select.pyd
    api-ms-win-core-processthreads-l1-1-1.dll      _bz2.pyd                               _socket.pyd
    api-ms-win-core-profile-l1-1-0.dll             certifi                                _ssl.pyd
    api-ms-win-core-rtlsupport-l1-1-0.dll          _cffi_backend.cp37-win_amd64.pyd       struct.pyc
    api-ms-win-core-string-l1-1-0.dll              cryptography                           ucrtbase.dll
    api-ms-win-core-synch-l1-1-0.dll               cryptography-36.0.1.dist-info          unicodedata.pyd
    api-ms-win-core-synch-l1-2-0.dll               crypt.pyc                              VCRUNTIME140.dll
    api-ms-win-core-sysinfo-l1-1-0.dll             _hashlib.pyd
    

`11.pyc` is the main program.

#### Uncompyle6 (Linux)

Typically I’d use `uncompyle6` to extract Python code from the `.pyc` files.
It fails here:

    
    
    oxdf@hacky$ uncompyle6 11.pyc 
    Traceback (most recent call last):
      File "/home/oxdf/.local/bin/uncompyle6", line 5, in <module>
        from uncompyle6.bin.uncompile import main_bin
      File "/home/oxdf/.local/lib/python3.8/site-packages/uncompyle6/__init__.py", line 48, in <module>
        import uncompyle6.semantics.pysource
      File "/home/oxdf/.local/lib/python3.8/site-packages/uncompyle6/semantics/pysource.py", line 75, in <module>
        from xdis.code import iscode
    ModuleNotFoundError: No module named 'xdis.code'
    

I’ll try a handful of things, like `pip install xdis`, `pip install pyarmor`,
starting a Python virtual environment and installing in there. This error
persists.

#### Uncompyle6 (Windows)

Shifting to my Windows VM, `uncompyle6` works great:

    
    
    PS > uncompyle6.exe .\11.pyc
    # uncompyle6 version 3.8.0
    # Python bytecode 3.7.0 (3394)
    # Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
    # Embedded file name: dist\obf\11.py
    from pytransform import pyarmor
    pyarmor(__name__, __file__, b'PYARMOR\x00\x00\x03\x07\x00B\r\r\n\t0\xe0\x02\x01\x00\x00\x00\x01\x00\x00\x00@\x00\x00\x00a\x02\x00\x00\x0b\x00\x00x\xa7\xf5\x80\x15\x8c\x1f\x90\xbb\x16Xu\x86\x9d\xbb\xbd\x8d\x00\x00\x00\x00\x00\x00\x00\x0054$\xf1\xeb,\nY\xa9\x9b\xa5\xb3\xba\xdc\xd97\xba\x13\x0b\x89 \xd2\x14\xa7\xccH0\x9b)\xd4\x0f\xfb\xe4`\xbd\xcf\xa28\xfc\xf1\x08\x87w\x1a\xfb%+\xc1\xbe\x8b\xc0]8h\x1f\x88\xa6CB>*\xdd\xf6\xec\xf5\xe30\xf9\x856\xfa\xd9P\xc8C\xc1\xbdm\xca&\x81\xa9\xfb\x07HE\x1b\x00\x9e\x00a\x0c\xf2\xd0\x87\x0c<\xf8\xddZf\xf1,\x84\xce\r\x14*s\x11\x82\x88\x8d\xa7\x00k\xd9s\xae\xd3\xfc\x16v\x0f\xb9\xd1\xd3\xd02\xecQ\x9a\xd7aL\xdf\xc1~u\xca\x8a\xd4xk\xde\x030;\xb2Q\xc8$\xddQ\xd3Jj\xd1U\xccV\xd1\x03\xa9\xbf\x9f\xed\xe68n\xac&\xd67\x0c\xfd\xc6^\x0e\xb40\x07\x97|\xab\xadBc<T\x0b d$\x94\xf9\x90Oq\x027\xe4\xf2\xec\xc9\xbc\xfaL7dN\x83\x96X\xab\xf7\x18\xad\xfc\xf7\x992\x87\x1d\xe8p\x97C\xd4D.\x1b;F_ \x91t\tM\x155\x0c\xb9\x9f\xd0W C\x19oz4.\x998\xe7\xa9\x98\xd4\xd2\x9f\x95H\x91\xf2`\x1c\xfa\xa4,\xa9d?day\xc4\xf3\xcb\xc8r\xf7\x97\xd1u\xfe\xec\x91\xc1\xe6V\xa3j\x0f\xb9\xd5\xa1a\xd5\x17\x8b!\xc4{A\xb2t\x85\xfe\x88\xffaO\x05\xc5\xacg\xed;]\xb9\xdd\x7fS\xef\xe4F\xf9"\x0c\xd9\x1a\xb6\x88-Y \xdd\xea\xc9\xf1>:\xbf][\xdf[\x07\xb9\xe2@\xeeq\xf9Ho\xc3\xc4sD\xcd\xcc\x8a\x11tq\xf6;\xe9\x84\x7fb\xe9\xf4t\x80\xe4l)_\xeaQ\x10\x8f^-\xc5\x11\xe7\x84x\xe7-\xb2\x15[5\xb0\xdck\x1awh\r;\x9by\x14\x1a\xe0:\xbd\x904\xa2\xfap[\xe0\x9fn3\x7fk;3n\xf8\xe3%\xc6t\xbf|\x12\x9a\x1b\xe2\xf1C\x10\xbe\xee\xe7.\x98>k\xb9r\xf9\x9cN8\xae\xc0\x8bA\x0f\xbb\x8d\xf4\x04\xb0\x01,\x05\xaa\xc5\r\xce\x91\'\x98\xc6\xd3Y\x1b\xd1U\xd3\xd7d|{I\x18JG\xa63\xd6\'r\xcf!7\x17qd\xb7|\x1f\x7f\x17\xb4\xa8\xb9\xa8\xdaz\x02g\xc7+]F\x10\x18l\x0c\x91g\xd0e\x1f\xe4\xa67\xb2\xba\x9f\xef\xba\xc7[3_\x12C\xe9\xf4s\x87q\xa3\xec\xa0\xcc\x06\xf4\x9f\xe1\xb3\xe6R\x93\xf2\xd57i\xf8\x96\xb3x\xa7uEw\x12D\x8c\xc6XkdfY\xe0J2N\xbf\x85o\x8e\x81|C\xa91#y\xd9u\xf1\xd1BC\xcc}\xe8;?\x12S\x16', 2)
    

Unfortunately, it’s not really useful. It’s two lines, first importing a
function for PyArmor and then calling `pyarmor` on a buffer. This is the
result of PyArmor.

### PyArmor-Unpacker

There are a handful of repositories that claim to be able to unpack PyArmor
binaries, but only one, [PyArmor-
Unpacker](https://github.com/Svenskithesource/PyArmor-Unpacker) that seems
maintained and updated. It works by running the PyArmor exe and then injecting
a DLL into the process memory. I did give it a try here, but it fails, only
showing:

![image-20221108062745259](https://0xdfimages.gitlab.io/img/image-20221108062745259.png)

In talking to the tools author, it seems this is happening because the
executable is protected by “Super Mode”, the paid version of PyArmor, and the
tool only supports the free version. So this tool is a dead end.

### Get PYC Running

#### Strategy

[This blog post](https://0x727.xyz/how-to-extract-values-from-programs-
protected-with-pyarmor/) talks about how to peak into PyArmor applications by
hooking library calls. Basically, I’ll get the program running as `.pyc`
files, and then modify libraries to make them report their actions.

#### Running .pyc

I’ll try to run this `.pyc` file. Just like how it wouldn’t decompile on
Linux, I’ll need to run it from Windows as well. However, when I do, I get an
error:

    
    
    PS > python .\11.pyc
    RuntimeError: Bad magic number in .pyc file
    

This is because the `.pyc` file is bytecode for a Python3.7 interpreter, but
my Windows system has 3.9:

    
    
    PS > python -V
    Python 3.9.13
    

I’ll download and install Python3.7 from
[here](https://www.python.org/downloads/release/python-379/), and try again:

    
    
    PS > C:\Python37\python.exe .\11.pyc
    Traceback (most recent call last):
      File "<dist\obf\11.py>", line 2, in <module>
      File "<frozen 11>", line 3, in <module>
      File "C:\Python37\lib\crypt.py", line 3, in <module>
        import _crypt
    ModuleNotFoundError: No module named '_crypt'
    

#### Fixing Imports

This same thing happens in the blog post. It’s failing to get the `_crypt`
module. In the blog post, it was `pytransform`. I’ll grab `crypt.pyc` from
`PYZ-00.pyz_extracted` and put it in the current directory:

    
    
    PS > copy .\PYZ-00.pyz_extracted\crypt.pyc .
    PS > C:\Python37\python.exe .\11.pyc
    

Now the file runs without issue, making the connection to port 80.

### Hook

Instead of fixing the `_crypt` import with the proper file, I’ll build my own.
A cryptography module seems like a good place to target where a flag is
involved. I’ll start by removing the new copy of `crypt.pyc` and creating a
`crypt.py` with only one line:

    
    
    pass
    

Now when I run `11.pyc`, it successfully imports `crypto.py` (which does
nothing), and then fails when it tries to access a `ARC4` object:

    
    
    PS > C:\Python37\python.exe .\11.pyc
    Traceback (most recent call last):
      File "<dist\obf\11.py>", line 2, in <module>
      File "<frozen 11>", line 12, in <module>
    AttributeError: module 'crypt' has no attribute 'ARC4'
    

With some more iterating through error messages (for details see [this
point](https://www.youtube.com/watch?v=oqS3aj2yS68&t=386s) in the video
solution), I’ll create:

    
    
    class ARC4:
        def __init__(self, arg):
            pass
            
        def encrypt(self, arg):
            import pdb;pdb.set_trace()
    

When I run this, it hits the break point, and drops into the Python debugger:

    
    
    PS > C:\Python37\python.exe .\11.pyc
    --Return--
    > z:\flareon-2022\11-the_challenge_that_shall_not_be_named\11.exe_extracted\crypt.py(6)encrypt()->None
    -> import pdb;pdb.set_trace()
    (Pdb) l
      1     class ARC4:
      2         def __init__(self, arg):
      3             pass
      4
      5         def encrypt(self, arg):
      6  ->         import pdb;pdb.set_trace()
    

Checking `arg`, it’s the flag:

    
    
    (Pdb) !arg
    b'Pyth0n_Prot3ction_tuRn3d_Up_t0_11@flare-on.com'
    

**Flag: Pyth0n_Prot3ction_tuRn3d_Up_t0_11@flare-on.com**

[](/flare-on-2022/challenge_that_shall_not_be_named)

