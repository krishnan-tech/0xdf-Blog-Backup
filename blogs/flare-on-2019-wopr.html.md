# Flare-On 2019: wopr

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-wopr](/tags#flare-on-
wopr ) [python](/tags#python ) [pyinstaller](/tags#pyinstaller ) [python-exe-
unpacker](/tags#python-exe-unpacker ) [uncompyle6](/tags#uncompyle6 )
[pdb](/tags#pdb ) [exe](/tags#exe ) [z3](/tags#z3 ) [reverse-
engineering](/tags#reverse-engineering )  
  
Oct 10, 2019

  * [[1] Memecat Battlestation](/flare-on-2019/memecat-battlestation.html)
  * [[2] Overlong](/flare-on-2019/overlong.html)
  * [[3] Flarebear](/flare-on-2019/flarebear.html)
  * [[4] DNS Chess](/flare-on-2019/dnschess.html)
  * [[5] demo](/flare-on-2019/demo.html)
  * [[6] bmphide](/flare-on-2019/bmphide.html)
  * [7] wopr

![](https://0xdfimages.gitlab.io/img/flare2019-7-cover.png)

wopr was like an onion - the layers kept peeling back revealing more layers.
I’m given an exe which was created by PyInstaller, which I’ll unpack to get to
the Python code. That code has a layer of unpacking based on a binary
implementation of tabs and spaces in the doc strings. Once I get to the next
layer, I need to calculate the hash of the text segment for the currently
running binary, and use that as a key to some equations. Using a solver to
solve the system, I can find the input necessary to return the flag.

## Challenge

> We used our own computer hacking skills to “find” this AI on a military
> supercomputer. It does strongly resemble the classic 1983 movie WarGames.
> Perhaps life imitates art? If you can find the launch codes for us, we’ll
> let you pass to the next challenge. We promise not to start a thermonuclear
> war.

The file is an x86 Windows executable:

    
    
    $ file wopr.exe 
    wopr.exe: PE32 executable (console) Intel 80386, for MS Windows
    

The exe also comes with a icon:

![1569056647911](https://0xdfimages.gitlab.io/img/1569056647911.png)

## Running It

Running the binary shows “LOADING…” for a few seconds, and then prints a
message, and then a prompt:

    
    
    C:\Users\0xdf\Desktop>wopr.exe
    LOADING...
    
          _/\/\______/\/\____/\/\/\/\____/\/\/\/\/\____/\/\/\/\/\___
         _/\/\__/\__/\/\__/\/\____/\/\__/\/\____/\/\__/\/\____/\/\_
        _/\/\/\/\/\/\/\__/\/\____/\/\__/\/\/\/\/\____/\/\/\/\/\___
       _/\/\/\__/\/\/\__/\/\____/\/\__/\/\__________/\/\__/\/\___
      _/\/\______/\/\____/\/\/\/\____/\/\__________/\/\____/\/\_
     __________________________________________________________
    
    GREETINGS PROFESSOR FALKEN.
    
    >
    

If I enter `help`, it lists commands:

    
    
    > help
    AVAILABLE COMMANDS:
    HELP
    HELP GAMES
    LIST GAMES
    PLAY <game>
    

When I hit `ctrl-c` to exit, I get errors:

    
    
    > Traceback (most recent call last):
      File "pyiboot02_cleanup.py", line 201, in <module>
      File "<string>", line 94, in <module>
      File "<string>", line 73, in read
    KeyboardInterrupt
    [7440] Failed to execute script pyiboot02_cleanup
    

I’ll note that script name for later.

## Analysis

### RE

I’ll open in IDA and take a look. There are a ton of functions:

![1569136431630](https://0xdfimages.gitlab.io/img/1569136431630.png)

pyinstallerI’ll open the strings window, and look for the strings I had in the
terminal. But I don’t find any. What I do see if a ton of strings that start
with `Py`:

![1569136495675](https://0xdfimages.gitlab.io/img/1569136495675.png)

My theory now is that this is a Python program, wrapped with something like
[py2exe](http://www.py2exe.org/) or
[pyinstaller](https://www.pyinstaller.org/). I don’t want to waste more time
looking at this in IDA or x32dbg, as the code is just unpacking and setting up
a Python environment.

### python-exe-unpacker

#### Installation

I’ll grab a copy of [python-exe-
unpacker](https://github.com/countercept/python-exe-unpacker) from
Countercept’s GitHub page using `git clone
https://github.com/countercept/python-exe-unpacker.git`. Then, I’ll install
the requirements using `python -m pip install -r requirements.txt`. I had some
issues with older versions of libraries not being able to be uninstalled, but
I got around that by adding the `--ignore-installed` flag.

Given the comments on the GitHub README file, I wanted to install for both
Python2 and Python3 so that I could match the version used for the exe. The
same `pip` command above works for Python3, but it turns out the
`requirements.txt` file [has an outdated version of
`uncompyle6`](https://github.com/countercept/python-exe-unpacker/issues/5). So
after running `python3 -m pip install -r requirements.txt`, I ran `python3 -m
pip install --upgrade uncompyle6`, and then `python-exe-unpacker` would run in
both legacy Python and Python3.

#### Unpacking

Now I ran the unpacker. First I tried legacy Python:

    
    
    $ python /opt/python-exe-unpacker/python_exe_unpack.py -i wopr.exe 
    [*] On Python 2.7
    [*] Processing wopr.exe
    [*] Pyinstaller version: 2.1+
    [*] This exe is packed using pyinstaller
    [*] Unpacking the binary now
    [*] Python version: 37
    [*] Length of package: 5068358 bytes
    [*] Found 64 files in CArchive
    [*] Beginning extraction...please standby
    [!] Warning: The script is running in a different python version than the one used to build the executable
        Run this script in Python37 to prevent extraction errors(if any) during unmarshalling
    [!] Unmarshalling FAILED. Cannot extract PYZ-00.pyz. Extracting remaining files.
    [*] Successfully extracted pyinstaller exe.
    

Given the warnings about the python versions not matching, I switched to
Python3.

    
    
    $ python3 /opt/python-exe-unpacker/python_exe_unpack.py -i wopr.exe
    [*] On Python 3.7
    [*] Processing wopr.exe
    [*] Pyinstaller version: 2.1+
    [*] This exe is packed using pyinstaller
    [*] Unpacking the binary now
    [*] Python version: 37
    [*] Length of package: 5068358 bytes
    [*] Found 64 files in CArchive
    [*] Beginning extraction...please standby
    [*] Found 135 files in PYZ archive
    [*] Successfully extracted pyinstaller exe.     
    

Inside `unpacked/wopr.exe` I can see the files:

    
    
    $ ls 
     api-ms-win-core-console-l1-1-0.dll         api-ms-win-core-namedpipe-l1-1-0.dll            api-ms-win-crt-convert-l1-1-0.dll       _bz2.pyd                                           python37.dll
     api-ms-win-core-datetime-l1-1-0.dll        api-ms-win-core-processenvironment-l1-1-0.dll   api-ms-win-crt-environment-l1-1-0.dll   _ctypes.pyd                                        PYZ-00.pyz
     api-ms-win-core-debug-l1-1-0.dll           api-ms-win-core-processthreads-l1-1-0.dll       api-ms-win-crt-filesystem-l1-1-0.dll    _hashlib.pyd                                       PYZ-00.pyz_extracted
     api-ms-win-core-errorhandling-l1-1-0.dll   api-ms-win-core-processthreads-l1-1-1.dll       api-ms-win-crt-heap-l1-1-0.dll          libcrypto-1_1.dll                                  select.pyd
     api-ms-win-core-file-l1-1-0.dll            api-ms-win-core-profile-l1-1-0.dll              api-ms-win-crt-locale-l1-1-0.dll        libssl-1_1.dll                                     _socket.pyd
     api-ms-win-core-file-l1-2-0.dll            api-ms-win-core-rtlsupport-l1-1-0.dll           api-ms-win-crt-math-l1-1-0.dll          _lzma.pyd                                          _ssl.pyd
     api-ms-win-core-file-l2-1-0.dll            api-ms-win-core-string-l1-1-0.dll               api-ms-win-crt-process-l1-1-0.dll       pyexpat.pyd                                        struct
     api-ms-win-core-handle-l1-1-0.dll          api-ms-win-core-synch-l1-1-0.dll                api-ms-win-crt-runtime-l1-1-0.dll       pyiboot01_bootstrap                               'this\__init__.py'
     api-ms-win-core-heap-l1-1-0.dll            api-ms-win-core-synch-l1-2-0.dll                api-ms-win-crt-stdio-l1-1-0.dll         pyiboot02_cleanup                                 'this\key'
     api-ms-win-core-interlocked-l1-1-0.dll     api-ms-win-core-sysinfo-l1-1-0.dll              api-ms-win-crt-string-l1-1-0.dll        pyimod01_os_path                                   ucrtbase.dll
     api-ms-win-core-libraryloader-l1-1-0.dll   api-ms-win-core-timezone-l1-1-0.dll             api-ms-win-crt-time-l1-1-0.dll          pyimod02_archive                                   unicodedata.pyd
     api-ms-win-core-localization-l1-2-0.dll    api-ms-win-core-util-l1-1-0.dll                 api-ms-win-crt-utility-l1-1-0.dll       pyimod03_importers                                 VCRUNTIME140.dll
     api-ms-win-core-memory-l1-1-0.dll          api-ms-win-crt-conio-l1-1-0.dll                 base_library.zip                       'pyi-windows-manifest-filename wopr.exe.manifest'   wopr.exe.manifest
    

These are all the Python files needed to run Python when it isn’t installed on
the host.

#### Magic

The GitHub page suggests using their tool with `-p` to add magic bytes to the
various pyc files that are missing it. It doesn’t work here for me:

    
    
    $ python3 /opt/python-exe-unpacker/python_exe_unpack.py -p pyiboot02_cleanup
    [*] On Python 3.7
    Traceback (most recent call last):
      File "/opt/python-exe-unpacker/python_exe_unpack.py", line 381, in <module>
        main()
      File "/opt/python-exe-unpacker/python_exe_unpack.py", line 374, in main
        magic_prepend.prepend(prepend_file)
      File "/opt/python-exe-unpacker/python_exe_unpack.py", line 325, in prepend
        (total, okay, failed, verify_failed) = PythonExectable.decompile_pyc(None, [edited_pyc.name], edited_py_name)
      File "/opt/python-exe-unpacker/python_exe_unpack.py", line 85, in decompile_pyc
        return uncompyle6.main.main(dir_decompiled, dir_decompiled, pyc_files, None, output_file)
      File "/usr/local/lib/python3.7/dist-packages/uncompyle6/main.py", line 201, in main
        for source_path in source_files:
    TypeError: 'NoneType' object is not iterable
    

Based on [this article](https://infosecuritygeek.com/reversing-a-simple-
python-ransomware/), I need to add the magic bytes back in.

    
    
    $ (echo 420d 0d0a 0000 0000 e8be 875d 6830 0000 | xxd -p -r ; cat pyiboot02_cleanup) > pyiboot02_cleanup.pyc
    

Now I can `uncompyle6`:

    
    
    $ uncompyle6 pyiboot02_cleanup.pyc > pyiboot02_cleanup.py
    

## pyiboot02_cleanup.py

### Overview

Now I can open up Python code. There’s a long DocString with lots of weird
whitespace that I’ll snip out here:

    
    
    # uncompyle6 version 3.4.0
    # Python bytecode 3.7 (3394)
    # Decompiled from: Python 3.7.3 (default, Apr  3 2019, 05:39:12) 
    # [GCC 8.3.0]
    # Embedded file name: pyiboot02_cleanup.py
    # Size of source mod 2**32: 12392 bytes
    """
    Once upon a midnight dreary, while I pondered, weak and                                                                                                                                                                                                                         weary,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    Over many a quaint and curious volume of forgotten                                                                                                                                                                                                                              lore-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
    """
    ...[snip]...
    import hashlib, io, lzma, pkgutil, random, struct, sys, time
    from ctypes import *
    print('LOADING...')
    BOUNCE = pkgutil.get_data('this', 'key')
    
    def ho(h, g={}):
        k = bytes.fromhex(format(h, 'x')).decode()
        return g.get(k, k)
    
    
    a = 1702389091
    b = 482955849332
    g = ho(29516388843672123817340395359, globals())   # g = __builtins__
    aa = getattr(g, ho(a))                             # aa = exec
    bb = getattr(g, ho(b))                             # bb = print
    a ^= b
    b ^= a                                             # b now is int for exec
    a ^= b                                             # a now is int for print
    setattr(g, ho(a), aa)                              # swap exec and print in builtins
    setattr(g, ho(b), bb)
    
    def eye(face):
       ...[snip]...
    
    
    def fire(wood, bounce):
       ...[snip]...
    
    for i in range(256):
        try:
            print(lzma.decompress(fire(eye(__doc__.encode()), bytes([i]) + BOUNCE)))
        except Exception:
            pass
    

There’s a few sections to this code:

  * The docstrings at the top appear to be [The Raven](https://www.poetryfoundation.org/poems/48860/the-raven) by Edgar Allen Poe. There’s also a bunch of whitespace at the end of each line.
  * It imports some libraries, and uses `pkgutil.get_data` to load the file `key` from the package `this` and saves it as `BOUNCE`.
  * There are lines that swap the `exec` and `print` functions in the Python builtins. I’ll show this in a bit.
  * Two functions are defined, `fire` and `eye`.
  * There’s a loop over 0 to 255. For each, the DocStrings are passed to `eye`, and the result is passed to `fire` along with the current `i` value and `BOUNCE`. The result is LZMA decompressed, and passed to `print`, which is actually `exec`. Any exceptions are caught and ignored.

### Debug

Next I tried to step through the program with a debugger. I ran into a couple
issues.

#### this\key

First I get an error when `pkgutil` tries to load `key` from the package
`this`:

    
    
    $ python3 -mpdb pyiboot02_cleanup.py
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(132)<module>()
    -> Shall be lifted-nevermore!                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        """
    (Pdb) n
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(133)<module>()
    -> import hashlib, io, lzma, pkgutil, random, struct, sys, time
    (Pdb) 
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(134)<module>()
    -> from ctypes import *
    (Pdb) 
    > /thttp://www.py2exe.org/mp/unpacked/wopr.exe/pyiboot02_cleanup.py(135)<module>()
    -> print('LOADING...')
    (Pdb) 
    LOADING...
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(136)<module>()
    -> BOUNCE = pkgutil.get_data('this', 'key')
    (Pdb) 
    ...[snip]...
    FileNotFoundError: [Errno 2] No such file or directory: '/usr/lib/python3.7/key'
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(136)<module>()
    -> BOUNCE = pkgutil.get_data('this', 'key')
    

One of the files that I retrieved from the unpacking was named `this\key`. If
I create a folder, `this`, and copy that into it as `key`, and then also add
an empty `__init__.py` file to the directory, then `pkgutils` will be able to
load the key.

    
    
    $ python3 -mpdb pyiboot02_cleanup.py
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(132)<module>()
    -> Shall be lifted-nevermore!                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        """
    (Pdb) n
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(133)<module>()
    -> import hashlib, io, lzma, pkgutil, random, struct, sys, time
    (Pdb) 
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(134)<module>()
    -> from ctypes import *
    (Pdb) 
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(135)<module>()
    -> print('LOADING...')
    (Pdb) 
    LOADING...
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(136)<module>()
    -> BOUNCE = pkgutil.get_data('this', 'key')
    (Pdb) 
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(138)<module>()
    -> def ho(h, g={}):
    (Pdb) BOUNCE
    b"\xaf\xbcbU\xfb\t\xd0Uf\x17JEQ\x12\xcc\x14I\t\xc8\xff\xe9\x92H\x9e\x9cs\x00\xa8\x84S\xb4E\x9d;!\xb9e\x10@\x0c\xca,:X)\x9e\x08\xf3t\x86\xbb\xbf\x8e\x8d\xd8\xe1\xd8\xce\x03x[\xa4\xd3\xaf\xff\x8b,\xc9\x0bHv\xbf\x1a\x8ah\x04]:;\xd9\xd7B\xb0\xac\xb8}`\xde\x0f\x16\xc4\xe1\x01\xb4\xbb\xe5pmx\xc6\x94\x1c\x83\xd9\xfed's\xe2b\x84\x94\x8fC\x83\xeb\xcf\x87\xb2\x01~\x9b\xaf\x00\xac\x98I\xf21\xc8r\x18\x8c@\xe2\xc65\n\xdc6\x96\xfb\xb8ru\x83\xf4\xf3v.\xbb`\x0e]\xcb\xa8w(\x18\x8e/\xaeP\xb5\xe4\xe1J\x066\xa9\xf8Fl\xbe\xd4\x0b6\xb2\xdeo\xb9\xf8)4\xdb\xb0V=\xb6\x81y\x02\xcd\xb3\xe1\xae\xf7\x85\x82\x84\x8c\x95\x9d\xdeC\x8f\x8c\x03\xad\xc8X\x99\xe8\x86\xf4c\xa7'\x1d\x86\xfe\x0f\xfb\x1f\x12&\xcdS\x91\xbd\x11\x88\xb2c\xcb\x8d\xa9g\xee\xffr\xb2\xef\xbc\x96\xaf\xaa\xf7\xbe\x8f\xf0h\x1e\x86\xbdS"
    

#### __builtins__

From the above session, I’ll keep stepping, and come to the next section. The
function `ho` takes an int, formats it as hex, then converts that to bytes and
then to a string. It then gets that string from the other passed in object.

In practice, that means that `g` is the `__builtins__` object from `globals`,
which includes the build in functions:

    
    
    (Pdb) g
    {'__name__': 'builtins', '__doc__': "Built-in functions, exceptions, and other objects.\n\nNoteworthy: None is the `nil' object; Ellipsis represents `...' in slices.", '__package__': '', '__loader__': <class '_frozen_importlib.BuiltinImporter'>, '__spec__': ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>), '__build_class__': <built-in function __build_class__>, '__import__': <built-in function __import__>, 'abs': <built-in function abs>, 'all': <built-in function all>, 'any': <built-in function any>, 'ascii': <built-in function ascii>, 'bin': <built-in function bin>, 'breakpoint': <built-in function breakpoint>, 'callable': <built-in function callable>, 'chr': <built-in function chr>, 'compile': <built-in function compile>, 'delattr': <built-in function delattr>, 'dir': <built-in function dir>, 'divmod': <built-in function divmod>, 'eval': <built-in function eval>, 'exec': <built-in function exec>, 'format': <built-in function format>, 'getattr': <built-in function getattr>, 'globals': <built-in function globals>, 'hasattr': <built-in function hasattr>, 'hash': <built-in function hash>, 'hex': <built-in function hex>, 'id': <built-in function id>, 'input': <built-in function input>, 'isinstance': <built-in function isinstance>, 'issubclass': <built-in function issubclass>, 'iter': <built-in function iter>, 'len': <built-in function len>, 'locals': <built-in function locals>, 'max': <built-in function max>, 'min': <built-in function min>, 'next': <built-in function next>, 'oct': <built-in function oct>, 'ord': <built-in function ord>, 'pow': <built-in function pow>, 'print': <built-in function print>, 'repr': <built-in function repr>, 'round': <built-in function round>, 'setattr': <built-in function setattr>, 'sorted': <built-in function sorted>, 'sum': <built-in function sum>, 'vars': <built-in function vars>, 'None': None, 'Ellipsis': Ellipsis, 'NotImplemented': NotImplemented, 'False': False, 'True': True, 'bool': <class 'bool'>, 'memoryview': <class 'memoryview'>, 'bytearray': <class 'bytearray'>, 'bytes': <class 'bytes'>, 'classmethod': <class 'classmethod'>, 'complex': <class 'complex'>, 'dict': <class 'dict'>, 'enumerate': <class 'enumerate'>, 'filter': <class 'filter'>, 'float': <class 'float'>, 'frozenset': <class 'frozenset'>, 'property': <class 'property'>, 'int': <class 'int'>, 'list': <class 'list'>, 'map': <class 'map'>, 'object': <class 'object'>, 'range': <class 'range'>, 'reversed': <class 'reversed'>, 'set': <class 'set'>, 'slice': <class 'slice'>, 'staticmethod': <class 'staticmethod'>, 'str': <class 'str'>, 'super': <class 'super'>, 'tuple': <class 'tuple'>, 'type': <class 'type'>, 'zip': <class 'zip'>, '__debug__': True, 'BaseException': <class 'BaseException'>, 'Exception': <class 'Exception'>, 'TypeError': <class 'TypeError'>, 'StopAsyncIteration': <class 'StopAsyncIteration'>, 'StopIteration': <class 'StopIteration'>, 'GeneratorExit': <class 'GeneratorExit'>, 'SystemExit': <class 'SystemExit'>, 'KeyboardInterrupt': <class 'KeyboardInterrupt'>, 'ImportError': <class 'ImportError'>, 'ModuleNotFoundError': <class 'ModuleNotFoundError'>, 'OSError': <class 'OSError'>, 'EnvironmentError': <class 'OSError'>, 'IOError': <class 'OSError'>, 'EOFError': <class 'EOFError'>, 'RuntimeError': <class 'RuntimeError'>, 'RecursionError': <class 'RecursionError'>, 'NotImplementedError': <class 'NotImplementedError'>, 'NameError': <class 'NameError'>, 'UnboundLocalError': <class 'UnboundLocalError'>, 'AttributeError': <class 'AttributeError'>, 'SyntaxError': <class 'SyntaxError'>, 'IndentationError': <class 'IndentationError'>, 'TabError': <class 'TabError'>, 'LookupError': <class 'LookupError'>, 'IndexError': <class 'IndexError'>, 'KeyError': <class 'KeyError'>, 'ValueError': <class 'ValueError'>, 'UnicodeError': <class 'UnicodeError'>, 'UnicodeEncodeError': <class 'UnicodeEncodeError'>, 'UnicodeDecodeError': <class 'UnicodeDecodeError'>, 'UnicodeTranslateError': <class 'UnicodeTranslateError'>, 'AssertionError': <class 'AssertionError'>, 'ArithmeticError': <class 'ArithmeticError'>, 'FloatingPointError': <class 'FloatingPointError'>, 'OverflowError': <class 'OverflowError'>, 'ZeroDivisionError': <class 'ZeroDivisionError'>, 'SystemError': <class 'SystemError'>, 'ReferenceError': <class 'ReferenceError'>, 'MemoryError': <class 'MemoryError'>, 'BufferError': <class 'BufferError'>, 'Warning': <class 'Warning'>, 'UserWarning': <class 'UserWarning'>, 'DeprecationWarning': <class 'DeprecationWarning'>, 'PendingDeprecationWarning': <class 'PendingDeprecationWarning'>, 'SyntaxWarning': <class 'SyntaxWarning'>, 'RuntimeWarning': <class 'RuntimeWarning'>, 'FutureWarning': <class 'FutureWarning'>, 'ImportWarning': <class 'ImportWarning'>, 'UnicodeWarning': <class 'UnicodeWarning'>, 'BytesWarning': <class 'BytesWarning'>, 'ResourceWarning': <class 'ResourceWarning'>, 'ConnectionError': <class 'ConnectionError'>, 'BlockingIOError': <class 'BlockingIOError'>, 'BrokenPipeError': <class 'BrokenPipeError'>, 'ChildProcessError': <class 'ChildProcessError'>, 'ConnectionAbortedError': <class 'ConnectionAbortedError'>, 'ConnectionRefusedError': <class 'ConnectionRefusedError'>, 'ConnectionResetError': <class 'ConnectionResetError'>, 'FileExistsError': <class 'FileExistsError'>, 'FileNotFoundError': <class 'FileNotFoundError'>, 'IsADirectoryError': <class 'IsADirectoryError'>, 'NotADirectoryError': <class 'NotADirectoryError'>, 'InterruptedError': <class 'InterruptedError'>, 'PermissionError': <class 'PermissionError'>, 'ProcessLookupError': <class 'ProcessLookupError'>, 'TimeoutError': <class 'TimeoutError'>, 'open': <built-in function open>, 'quit': Use quit() or Ctrl-D (i.e. EOF) to exit, 'exit': Use exit() or Ctrl-D (i.e. EOF) to exit, 'copyright': Copyright (c) 2001-2019 Python Software Foundation.
    All Rights Reserved.
    
    Copyright (c) 2000 BeOpen.com.
    All Rights Reserved.
    
    Copyright (c) 1995-2001 Corporation for National Research Initiatives.
    All Rights Reserved.
    
    Copyright (c) 1991-1995 Stichting Mathematisch Centrum, Amsterdam.
    All Rights Reserved., 'credits':     Thanks to CWI, CNRI, BeOpen.com, Zope Corporation and a cast of thousands
        for supporting Python development.  See www.python.org for more information., 'license': Type license() to see the full license text, 'help': Type help() for interactive help, or help(object) for help about object.}
    
    (Pdb) g['print']
    <built-in function print>
    

The `aa` is the `exec` function, and `bb` is the `print` function. For some
reason, this code doesn’t work in `pdb`, but will run fine outside the
debugger. I can’t figure out why (let me know if you know!).

    
    
    (Pdb) n
    AttributeError: 'dict' object has no attribute 'exec'
    > /tmp/unpacked/wopr.exe/pyiboot02_cleanup.py(146)<module>()
    -> aa = getattr(g, ho(a))
    

At least continuing to look at it statically, knowing what I now know, it’s
clear that `a` and `b` are swapped using the three xor trick:

    
    
    >>> a = 124235
    >>> b = 223
    >>> a = a ^ b
    >>> b = b ^ a
    >>> a = a ^ b
    >>> a
    223
    >>> b
    124235
    

If you’ve not seen that before, it’s a fun trick to work out why it works.

Next the functions are set back into the `__builtins__` but swapped,
effectively making the `print` call at the end an `exec` call. I’ll keep that
in mind going forward.

### Run

Since I can’t run in `pdb`, I checked if I could run the program. It will run,
but it just prints `LOADING...`, hangs for a minute, and exits (shown with
`time` to see it takes about 30 seconds):

    
    
    $ time python3 pyiboot02_cleanup.py
    LOADING...
    
    real    0m29.054s
    user    0m28.910s
    sys     0m0.056s
    

I added a print statements before and after the call in the loop to see what
was happening. I didn’t want to use `print` since the code already messed with
that, so I used `sys.stdout.write`:

    
    
    for i in range(256):
        try:
            sys.stdout.write(f"before {i}\n")
            print(lzma.decompress(fire(eye(__doc__.encode()), bytes([i]) + BOUNCE)))
            sys.stdout.write(f"after {i}\n")
        except Exception:
            pass
    

It runs, and the before statement is reached, but never the after:

    
    
    $ python3 pyiboot02_cleanup-mod.py
    LOADING...
    before 0
    before 1
    before 2
    before 3
    before 4
    before 5
    before 6
    ...[snip]...
    
    $ python3 pyiboot02_cleanup-mod.py | grep after | wc -l
    0
    

This tells me that there’s an exception at each run in the loop.

### eye()

Now I turned to what was going on in the called functions. First, I looked at
`eye`, to which the `__doc__` is passed as bytes.

    
    
    def eye(face):
        leg = io.BytesIO()
        for arm in face.splitlines():
            arm = arm[len(arm.rstrip(b' \t')):]
            leg.write(arm)
            
        face = leg.getvalue()
        bell = io.BytesIO()
        x, y = (0, 0)
        for chuck in face:
            taxi = {9:0,
             32:1}.get(chuck)
            if taxi is None:
                continue
            x, y = x | taxi << y, y + 1
            if y > 7:
                bell.write(bytes([x]))
                x, y = (0, 0)
                
        return bell.getvalue()
    

This part is neat, and not that difficult to figure out. It reading the passed
in data (the DocStrings), and for each line, it gets the length of that line
with the tabs and spaces stripped from the end. Then it takes the line from
that point to the end, so capturing only the tabs and spaces, and writes it to
a buffer. By the end of the first loop, `leg` is a buffer with all the
trailing tabs and spaces.

Next, it loops over `leg`. This ends up taking 8 characters at a time, and
converting them into an eight bit word. The first character is the low bit,
then the next is the second lowest, etc, where space is 1 and tab is 0. So
`.\t.\t..\t\t` (where space is shown as `.` for readability) would become
`00110101` or 0x35.

Looking at the `.py` file that came out of `uncompyle6`, I can see there are
no tabs. But when I look at the `.pyc` file, there’s a mix of tabs (0x09) and
spaces (0x20):

    
    
    $ for f in pyiboot02_cleanup.py*; do grep -a "Once upon a midnight" $f | xxd | head -20; done
    00000000: 4f6e 6365 2075 706f 6e20 6120 6d69 646e  Once upon a midn
    00000010: 6967 6874 2064 7265 6172 792c 2077 6869  ight dreary, whi
    00000020: 6c65 2049 2070 6f6e 6465 7265 642c 2077  le I pondered, w
    00000030: 6561 6b20 616e 6420 7765 6172 792c 2020  eak and weary,
    00000040: 2020 2020 2020 2020 2020 2020 2020 2020
    00000050: 2020 2020 2020 2020 2020 2020 2020 2020
    00000060: 2020 2020 2020 2020 2020 2020 2020 2020
    00000070: 2020 2020 2020 2020 2020 2020 2020 2020
    00000080: 2020 2020 2020 2020 2020 2020 2020 2020
    00000090: 2020 2020 2020 2020 2020 2020 2020 2020
    000000a0: 2020 2020 2020 2020 2020 2020 2020 2020
    000000b0: 2020 2020 2020 2020 2020 2020 2020 2020
    000000c0: 2020 2020 2020 2020 2020 2020 2020 2020
    000000d0: 2020 2020 2020 2020 2020 2020 2020 2020
    000000e0: 2020 2020 2020 2020 2020 2020 2020 2020
    000000f0: 2020 2020 2020 2020 2020 2020 2020 2020
    00000100: 2020 2020 2020 2020 2020 2020 2020 2020
    00000110: 2020 2020 2020 2020 2020 2020 2020 2020
    00000120: 2020 2020 2020 2020 2020 2020 2020 2020
    00000130: 2020 2020 2020 2020 2020 2020 2020 2020
    00000000: 4f6e 6365 2075 706f 6e20 6120 6d69 646e  Once upon a midn
    00000010: 6967 6874 2064 7265 6172 792c 2077 6869  ight dreary, whi
    00000020: 6c65 2049 2070 6f6e 6465 7265 642c 2077  le I pondered, w
    00000030: 6561 6b20 616e 6420 7765 6172 792c 0909  eak and weary,..
    00000040: 2009 0909 2020 0909 2020 2020 0920 0920   ...  ..    . .
    00000050: 2009 0909 2020 2020 2020 0909 0909 2009   ...      .... .
    00000060: 0909 0909 0920 0909 2020 2009 2020 0909  ..... ..   .  ..
    00000070: 0920 0909 2020 2009 0909 0920 0909 0920  . ..   .... ...
    00000080: 0909 0909 0920 0920 0920 2009 2009 0920  ..... . .  . ..
    00000090: 0909 2009 2020 2020 0909 0920 2020 0909  .. .    ...   ..
    000000a0: 2009 2020 2020 0920 0920 2009 0920 0920   .    . .  .. .
    000000b0: 2020 2020 2009 2009 0920 2020 0909 2009       . ..   .. .
    000000c0: 2020 2020 2020 0920 0909 0909 2009 0909        . .... ...
    000000d0: 2020 0920 0920 2009 0920 2020 0909 2009    . .  ..   .. .
    000000e0: 2009 2020 0909 2009 0920 0909 2020 2009   .  .. .. ..   .
    000000f0: 2009 2009 0909 2020 0920 0920 0909 2020   . ...  . . ..
    00000100: 2009 0909 0920 2020 2009 2009 2020 2020   ....    . .
    00000110: 0909 0920 2020 0920 0909 2020 0920 2009  ...   . ..  .  .
    00000120: 2020 2020 0909 2009 0909 2020 0909 0a        .. ...  ...
    

I created a version of the script which is the `__doc__` from the `.pyc` but
the code from the `.py`. I started to try to understand `fire`, but instead, I
commented out section that swaps `exec` and `print`, and let it run. I also
modified the loop slightly, adding a `.decode()` so the result would print
more nicely, and a `print(i)` after the decompress so I could see which of the
256 attempts to decode actually succeeded (as opposed to throwing an exception
that’s silently caught):

    
    
    for i in range(256):
        try:
            print(lzma.decompress(fire(eye(__doc__.encode()), bytes([i]) + BOUNCE)).decode())
            print(i)
        except Exception:
            pass
    

When I run it, I get the code when `i` is 74!

## Game Code

### Analysis

The output code is as follows:

    
    
    GREETINGS = ["HI", "HELLO", "'SUP", "AHOY", "ALOHA", "HOWDY", "GREETINGS", "ZDRAVSTVUYTE"]
    STRATEGIES = ['U.S. FIRST STRIKE', 'USSR FIRST STRIKE', 'NATO / WARSAW PACT', 'FAR EAST STRATEGY', 'US USSR ESCALATION', 'MIDDLE EAST WAR', 'USSR CHINA ATTACK', 'INDIA PAKISTAN WAR', 'MEDITERRANEAN WAR', 'HONGKONG VARIANT', 'SEATO DECAPITATING', 'CUBAN PROVOCATION', 'ATLANTIC HEAVY', 'CUBAN PARAMILITARY', 'NICARAGUAN PREEMPTIVE', 'PACIFIC TERRITORIAL', 'BURMESE THEATERWIDE', 'TURKISH DECOY', 'ARGENTINA ESCALATION', 'ICELAND MAXIMUM', 'ARABIAN THEATERWIDE', 'U.S. SUBVERSION', 'AUSTRALIAN MANEUVER', 'SUDAN SURPRISE', 'NATO TERRITORIAL', 'ZAIRE ALLIANCE', 'ICELAND INCIDENT', 'ENGLISH ESCALATION', 'MIDDLE EAST HEAVY', 'MEXICAN TAKEOVER', 'CHAD ALERT', 'SAUDI MANEUVER', 'AFRICAN TERRITORIAL', 'ETHIOPIAN ESCALATION', 'TURKISH HEAVY', 'NATO INCURSION', 'U.S. DEFENSE', 'CAMBODIAN HEAVY', 'PACT MEDIUM', 'ARCTIC MINIMAL', 'MEXICAN DOMESTIC', 'TAIWAN THEATERWIDE', 'PACIFIC MANEUVER', 'PORTUGAL REVOLUTION', 'ALBANIAN DECOY', 'PALESTINIAN LOCAL', 'MOROCCAN MINIMAL', 'BAVARIAN DIVERSITY', 'CZECH OPTION', 'FRENCH ALLIANCE', 'ARABIAN CLANDESTINE', 'GABON REBELLION', 'NORTHERN MAXIMUM', 'DANISH PARAMILITARY', 'SEATO TAKEOVER', 'HAWAIIAN ESCALATION', 'IRANIAN MANEUVER', 'NATO CONTAINMENT', 'SWISS INCIDENT', 'CUBAN MINIMAL', 'CHAD ALERT', 'ICELAND ESCALATION', 'VIETNAMESE RETALIATION', 'SYRIAN PROVOCATION', 'LIBYAN LOCAL', 'GABON TAKEOVER', 'ROMANIAN WAR', 'MIDDLE EAST OFFENSIVE', 'DENMARK MASSIVE', 'CHILE CONFRONTATION', 'S.AFRICAN SUBVERSION', 'USSR ALERT', 'NICARAGUAN THRUST', 'GREENLAND DOMESTIC', 'ICELAND HEAVY', 'KENYA OPTION', 'PACIFIC DEFENSE', 'UGANDA MAXIMUM', 'THAI SUBVERSION', 'ROMANIAN STRIKE', 'PAKISTAN SOVEREIGNTY', 'AFGHAN MISDIRECTION', 'ETHIOPIAN LOCAL', 'ITALIAN TAKEOVER', 'VIETNAMESE INCIDENT', 'ENGLISH PREEMPTIVE', 'DENMARK ALTERNATE', 'THAI CONFRONTATION', 'TAIWAN SURPRISE', 'BRAZILIAN STRIKE', 'VENEZUELA SUDDEN', 'MALAYSIAN ALERT', 'ISREAL DISCRETIONARY', 'LIBYAN ACTION', 'PALESTINIAN TACTICAL', 'NATO ALTERNATE', 'CYPRESS MANEUVER', 'EGYPT MISDIRECTION', 'BANGLADESH THRUST', 'KENYA DEFENSE', 'BANGLADESH CONTAINMENT', 'VIETNAMESE STRIKE', 'ALBANIAN CONTAINMENT', 'GABON SURPRISE', 'IRAQ SOVEREIGNTY', 'VIETNAMESE SUDDEN', 'LEBANON INTERDICTION', 'TAIWAN DOMESTIC', 'ALGERIAN SOVEREIGNTY', 'ARABIAN STRIKE', 'ATLANTIC SUDDEN', 'MONGOLIAN THRUST', 'POLISH DECOY', 'ALASKAN DISCRETIONARY', 'CANADIAN THRUST', 'ARABIAN LIGHT', 'S.AFRICAN DOMESTIC', 'TUNISIAN INCIDENT', 'MALAYSIAN MANEUVER', 'JAMAICA DECOY', 'MALAYSIAN MINIMAL', 'RUSSIAN SOVEREIGNTY', 'CHAD OPTION', 'BANGLADESH WAR', 'BURMESE CONTAINMENT', 'ASIAN THEATERWIDE', 'BULGARIAN CLANDESTINE', 'GREENLAND INCURSION', 'EGYPT SURGICAL', 'CZECH HEAVY', 'TAIWAN CONFRONTATION', 'GREENLAND MAXIMUM', 'UGANDA OFFENSIVE', 'CASPIAN DEFENSE', 'CRIMEAN GAMBIT', 'BRITISH ANTICS', 'HUNGARIAN EXPULSION', 'VENEZUELAN COLLAPSE']
    
    def wrong():
        trust = windll.kernel32.GetModuleHandleW(None)
    
        computer = string_at(trust, 1024)
        dirty, = struct.unpack_from('=I', computer, 60)
    
        _, _, organize, _, _, _, variety, _ =  struct.unpack_from('=IHHIIIHH', computer, dirty)
        assert variety >= 144
    
        participate, = struct.unpack_from('=I', computer, dirty + 40)
        for insurance in range(organize):
            name, tropical, inhabitant, reader, chalk, _, _, _, _, _ = struct.unpack_from('=8sIIIIIIHHI', computer, 40 * insurance + dirty + variety + 24)
            if inhabitant <= participate < inhabitant + tropical:
                break
    
        spare = bytearray(string_at(trust + inhabitant, tropical))
       
        issue, digital = struct.unpack_from('=II', computer, dirty + 0xa0)
        truth = string_at(trust + issue, digital)
    
        expertise = 0
        while expertise <= len(truth) - 8:
            nuance, seem = struct.unpack_from('=II', truth, expertise)
    
            if nuance == 0 and seem == 0:
                break
    
            slot = truth[expertise + 8:expertise + seem]
    
            for i in range(len(slot) >> 1):
                diet, = struct.unpack_from('=H', slot, 2 * i)
                fabricate = diet >> 12
                if fabricate != 3: continue
                diet = diet & 4095
                ready = nuance + diet - inhabitant
                if 0 <= ready < len(spare):
                    struct.pack_into('=I', spare, ready, struct.unpack_from('=I', spare, ready)[0] - trust)
    
            expertise += seem
    
        return hashlib.md5(spare).digest()
    
    class Terminal(object):
           
        DELAY = 0.02
    
        def write(self, text):
            for line in text.splitlines(True):
                sys.stdout.write(line)
                sys.stdout.flush()
                time.sleep(self.DELAY)    
    
        def typewrite(self, text):
            for char in text:
                if char == '\n':
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(self.DELAY)
                else:
                    sys.stdout.write(char.lower())
                    sys.stdout.flush()
                    time.sleep(self.DELAY)
                    sys.stdout.write('\b' + char)
                    sys.stdout.flush()
           
        def typewriteln(self, text):
            self.typewrite(text + '\n')
           
        def read(self):
            return ' '.join(''.join(_ for _ in input().upper() if _ in ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXZY?').split())
    t = Terminal()
    
    xor = [212, 162, 242, 218, 101, 109, 50, 31, 125, 112, 249, 83, 55, 187, 131, 206]
    h = list(wrong())
    h = [h[i] ^ xor[i] for i in range(16)]
    
    t.write('''
          _/\/\______/\/\____/\/\/\/\____/\/\/\/\/\____/\/\/\/\/\___
         _/\/\__/\__/\/\__/\/\____/\/\__/\/\____/\/\__/\/\____/\/\_
        _/\/\/\/\/\/\/\__/\/\____/\/\__/\/\/\/\/\____/\/\/\/\/\___
       _/\/\/\__/\/\/\__/\/\____/\/\__/\/\__________/\/\__/\/\___
      _/\/\______/\/\____/\/\/\/\____/\/\__________/\/\____/\/\_
     __________________________________________________________
    
    ''')
    
    t.typewrite('GREETINGS PROFESSOR FALKEN.\n')
    
    while True:
        t.typewrite('\n> ')
        cmd = t.read()
        if cmd.rstrip('!?') in GREETINGS:
            t.typewriteln(random.choice(GREETINGS))
        elif cmd == 'HELP GAMES':
            t.typewriteln("'GAMES' REFERS TO MODELS, SIMULATIONS AND GAMES\nWHICH HAVE TACTICAL AND STRATEGIC APPLICATIONS.")
        elif cmd == 'LIST GAMES':
            t.typewriteln('FALKEN\'S MAZE\nTIC-TAC-TOE\nGLOBAL THERMONUCLEAR WAR')
        elif cmd in ('HELP', '?'):
            t.typewriteln('AVAILABLE COMMANDS:\nHELP\nHELP GAMES\nLIST GAMES\nPLAY <game>')
        elif cmd.startswith('HELP '):
            t.typewriteln('HELP NOT AVAILABLE')
        elif cmd == 'PLAY':
            t.typewriteln('WHICH GAME?')
        elif cmd.startswith('PLAY F') or cmd == 'PLAY 1':
            t.typewriteln('GAME IS TEMPORARILY UNAVAILABLE DUE TO MAINTENANCE')
        elif cmd.startswith('PLAY T') or cmd == 'PLAY 2':
            t.typewriteln('GAME IS TEMPORARILY UNAVAILABLE DUE TO MAINTENANCE')
        elif cmd.startswith('PLAY G') or cmd in ('PLAY ARMAGEDDON', 'PLAY 3'):
            t.typewriteln('*** GAME ROUTINE RUNNING ***')
            break
        elif cmd.startswith('PLAY '):
            t.typewriteln('THAT GAME IS NOT AVAILABLE')
        else:
            t.typewriteln('COMMAND NOT RECOGNIZED')
    
    
    t.write('''
    r"""""""""""""""""""7ooooo"""oooooo"""""""""""""""""""""""""""""""""""""""""""7
    |           .__Looooooo ""7oooooooo`     'ooo"   ""._,    .JooL_,    .___     |
    o  __L______oLoooooooo7o_, |oooor""       ._____,,Jo__JoooooooooooooJoooL_____J
    r7._ooooooooooooooo"JoJoo|  oor   'o`   .Jooo7oooooooooooooooooooooooooooo"oo"7
    | '`"'`   ooooooooooL,Jooo_,         _oL.ooLoooooooooooooooooooooooooo_  |r`  |
    |         ''ooooooooooooooJo         ""oooooooooor"ooooooooooooooooooo7       |
    |           7oooooooooo"             |or`oo'ooJoJo |ooooooooooooooro ./       |
    |            "oooooo7o`              JooooJ_JLJoooLJoooooooooooooo, or        |
    |             '"oo|  oo            .oooooooooooroooJo"7oooooooooo7,           |
    |   ""          ""`oorL|L,         |ooooooooooooooo"`  7or` 7ooo |,           |
    |                   '\_oL__         7ooooooooooooLr     7|   L"` |o|          |
    |                    .Jooooo|            7ooooooo"       `  'o|_oL"L          |
    |                    |oooooooooL         'oooooo|            'o_J7Lrooo_J_,   |
    |                     7oooooooo`          Jooooo|._            "`"7LJ/7r  "`, |
    |                       oooooor           7oooo|.o|             __oooooo_  _| 7
    |                      |ooooo             'ooor  "              7oooooooo|    |
    |                      Jooor               |o|                  '""  "oor    .J
    |                      oo|                                            "o|   _oo
    |                     'or _                           |                     " |
    |                      ""`                                                    |
    |                       .,'                       ___.   .______________      |
    |        ______________ooo`        ._JLooooooooooooooooooooooooooooooooooooo" |
    |  |L7ooooooooooooooooL___,.Jo_Jooooooooooooooooooooooooooooooooooooooooooor` |
    ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    
    AWAITING FIRST STRIKE COMMAND
    -----------------------------
                   
    PLEASE SPECIFY PRIMARY TARGET
    BY CITY AND/OR COUNTRY NAME:
    
    ''')
    target = input()
    
    t.typewriteln("\nPREPARING NUCLEAR STRIKE FOR " + target.upper())
    t.typewrite("ENTER LAUNCH CODE: ")
    launch_code = input().encode()
    
    # encoding map coordinates
    x = list(launch_code.ljust(16, b'\0'))
    b = 16 * [None]
    
    # calculate missile trajectory
    b[0] = x[2] ^ x[3] ^ x[4] ^ x[8] ^ x[11] ^ x[14]
    b[1] = x[0] ^ x[1] ^ x[8] ^ x[11] ^ x[13] ^ x[14]
    b[2] = x[0] ^ x[1] ^ x[2] ^ x[4] ^ x[5] ^ x[8] ^ x[9] ^ x[10] ^ x[13] ^ x[14] ^ x[15]
    b[3] = x[5] ^ x[6] ^ x[8] ^ x[9] ^ x[10] ^ x[12] ^ x[15]
    b[4] = x[1] ^ x[6] ^ x[7] ^ x[8] ^ x[12] ^ x[13] ^ x[14] ^ x[15]
    b[5] = x[0] ^ x[4] ^ x[7] ^ x[8] ^ x[9] ^ x[10] ^ x[12] ^ x[13] ^ x[14] ^ x[15]
    b[6] = x[1] ^ x[3] ^ x[7] ^ x[9] ^ x[10] ^ x[11] ^ x[12] ^ x[13] ^ x[15]
    b[7] = x[0] ^ x[1] ^ x[2] ^ x[3] ^ x[4] ^ x[8] ^ x[10] ^ x[11] ^ x[14]
    b[8] = x[1] ^ x[2] ^ x[3] ^ x[5] ^ x[9] ^ x[10] ^ x[11] ^ x[12]
    b[9] = x[6] ^ x[7] ^ x[8] ^ x[10] ^ x[11] ^ x[12] ^ x[15]
    b[10] = x[0] ^ x[3] ^ x[4] ^ x[7] ^ x[8] ^ x[10] ^ x[11] ^ x[12] ^ x[13] ^ x[14] ^ x[15]
    b[11] = x[0] ^ x[2] ^ x[4] ^ x[6] ^ x[13]
    b[12] = x[0] ^ x[3] ^ x[6] ^ x[7] ^ x[10] ^ x[12] ^ x[15]
    b[13] = x[2] ^ x[3] ^ x[4] ^ x[5] ^ x[6] ^ x[7] ^ x[11] ^ x[12] ^ x[13] ^ x[14]
    b[14] = x[1] ^ x[2] ^ x[3] ^ x[5] ^ x[7] ^ x[11] ^ x[13] ^ x[14] ^ x[15]
    b[15] = x[1] ^ x[3] ^ x[5] ^ x[9] ^ x[10] ^ x[11] ^ x[13] ^ x[15]
    
    if b == h:
        t.typewriteln("LAUNCH CODE ACCEPTED.\n\n*** RUNNING SIMULATION ***\n")
        random.shuffle(STRATEGIES)
        for i in range(0, len(STRATEGIES), 6):
            t.write('\n'.join('{:24} {:8}'.format(k, v) for k, v in ([('STRATEGY:', 'WINNER:'), ('-' * 24, '-' * 8)] + [(_, 'NONE') for _ in STRATEGIES[i:i+6]])) + '\n\n')
            time.sleep(0.5)
        t.typewriteln("*** SIMULATION COMPLETED ***\n")
        t.typewriteln('\nA STRANGE GAME.\nTHE ONLY WINNING MOVE IS\nNOT TO PLAY.\n')
        eye = [219, 232, 81, 150, 126, 54, 116, 129, 3, 61, 204, 119, 252, 122, 3, 209, 196, 15, 148, 173, 206, 246, 242, 200, 201, 167, 2, 102, 59, 122, 81, 6, 24, 23]
        flag = fire(eye, launch_code).decode()
        t.typewrite(f"CONGRATULATIONS! YOU FOUND THE FLAG:\n\n{flag}\n")
    else:
        t.typewrite("\nIDENTIFICATION NOT RECOGNIZED BY SYSTEM\n--CONNECTION TERMINATED--\n")
    

This code looks a lot like the game I played when I ran the original program.
It does the following:

  * Calculates a value, `h` as the output of the function `wrong()`, then xored against an array of 16 one-byte ints. I’ll look at `wrong()` in more detail, but it returns an md5 hash, or 16 raw bytes.
  * Starts a `terminal` object to handle input and output. Prints the ASCII art, the greeting, and then the prompt. All of the options for the prompt keep the user in a `while True:` loop, except for any string starting with `PLAY G` or `PLAY ARMAGEDDON` or `PLAY 3`.
  * Once the user selects the right game to break out of the loop, more ASCII art, then it reads a country (which is printed back to the user), and then asks for the launch code.
  * The received launch code is turned into an array of ints of ordinal values of the input, `x`. `x` is appended with 0s to fill to 16 values.
  * A new 16 value array, `b` is created, with each value being a combination of different `x` values xored together.
  * If `b == h`, I win and get the flag.

### wrong()

#### Dump exe

The first thing that is called in `wrong` is:

    
    
    trust = windll.kernel32.GetModuleHandleW(None)
    

According to the [GetModuleHandle
documentation](https://docs.microsoft.com/en-
us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulehandlew):

> If this parameter is NULL, **GetModuleHandle** returns a handle to the file
> used to create the calling process (.exe file).

So it is getting the location of this executable in memory. Dumping out this
memory is a bit tricky, as the unpacker will eventually call `CreateProcess`,
and I want to catch after that point. I can do this one of two ways:

  * Put a break point at `CreateProcessA` in x32dbg. Then run until that call, and change the fifth argument from 0 to 4, which sets it to create suspended. Then continue, and attach to the new process. Then, I’ll add breakpoints at `GetModuleHandle`, and resume the thread.
  * Start the program on it’s own, and when it gets to the prompts, attach the debugger.

In the Memory Maps tab, I can dump the different sections of memory related to
`wopr.exe`, and then `cat` them together into a single file.

#### Walk wrong

Next I’ll walk through `wrong()`, copying that function into it’s own file,
`wrong.py`, and then adding `print(''.join(["%X" % x for x in wrong()]))` at
the end. I’ll replace the call to `GetModuleHandleW` with the following:

    
    
    with open('wopr_dump.bin', 'rb') as f:
        trust = f.read()
    

I’ll use `pdb` to step through the code by running `python3 -mpdb wrong.py`.

After loading the first 1024 bytes of the dump into `computer`, it gets an
unsigned integer (`I`) from 60 bytes in, which [is the offset to the PE
header](https://en.wikibooks.org/wiki/X86_Disassembly/Windows_Executable_Files#PE_Header),
and saves that as `dirty`.

Next it parses the PE Header and [COFF
Header](https://en.wikibooks.org/wiki/X86_Disassembly/Windows_Executable_Files#COFF_Header)
that immediately follows the PE header, saving the number of sections as
`organize` and the size of options header as `variety`. There’s an assertion
that `variety` is greater than 144, which it is at 224.

Next it goes 40 bytes after the PE header, which is in the PE Optional Header
(which isn’t optional for an exe). If I look 24 bytes into that header, I see
267:

    
    
    (Pdb) struct.unpack_from('=H', computer, dirty+24)
    (267,)
    

That matches the
[signature](https://en.wikibooks.org/wiki/X86_Disassembly/Windows_Executable_Files#PE_Optional_Header)
for a 32-bit exe, as expected. So 40 bytes is the `long AddressOfEntryPoint;
//The RVA of the code entry point`.

In my case, that’s:

    
    
    (Pdb) participate
    30618
    (Pdb) "%X" % participate
    '779A'
    

Now, it’s going to loop over each section in a `for` loop over
`range(organize)`. For each section, it will unpack:

    
    
    name, tropical, inhabitant, reader, chalk, _, _, _, _, _ = struct.unpack_from('=8sIIIIIIHHI', computer, 40 * insurance + dirty + variety + 24)
    

I’ll break down that offset:

  * `dirty` is the offset of the PE header
  * `24` gets past the PE header
  * `variety` is the length of the PE Optional header
  * `insurance` is the counter of each section, and multiplied by 40 since that’s the size of the `IMAGE_SECTION_HEADER` structures in the [section table](https://en.wikibooks.org/wiki/X86_Disassembly/Windows_Executable_Files#Section_Table).

For each entry, it will store:

  * `name` \- up to 8 byte ascii string name of the section, padded with null bytes.
  * `tropical` \- the Physical Address / Virtual Size as an int.
  * `inhabitant` \- the Virtual Address
  * `reader` \- the size of the section
  * `chalk` \- pointer to the section

It will then check if the entry point (`participate`) is in the raw data for
this section, and if so, break.

In my debugging, I’ll break in the first section, `.text`, as expected.

Next, the entire `.text` section is read into spare. I had to make an edit
here to adjust for how I’m reading the dump:

    
    
    spare = bytearray(string_at(trust[inhabitant:], tropical))
    

Next, the code goes back to 0xA0 bytes after the PE header and reads two ints,
which are, [according to another reference](https://www.aldeid.com/wiki/PE-
Portable-executable), the Base Relocation Table address and size, which are
saved as `issue` and `digital` respectively. Those two values are used to
store the table as `truth`.

Next there’s a loop over the entries in the Relocation Table, fixing the
addresses so that the `.text` section stored in `spare` is the same regardless
of where the exe is loaded into memory.

Finally, the md5 hash of `spare` is taken and returned.

The final modified code looks like:

    
    
      1 import hashlib
      2 import struct
      3 from ctypes import *
      4 
      5 def wrong():
      6     with open('wopr_dump.bin', 'rb') as f:
      7         trust = f.read()
      8 
      9     computer = string_at(trust, 1024)
     10     dirty, = struct.unpack_from('=I', computer, 60)
     11 
     12     _, _, organize, _, _, _, variety, _ =  struct.unpack_from('=IHHIIIHH', computer, dirty)
     13     assert variety >= 144
     14 
     15     participate, = struct.unpack_from('=I', computer, dirty + 40)
     16     for insurance in range(organize):
     17         name, tropical, inhabitant, reader, chalk, _, _, _, _, _ = struct.unpack_from('=8sIIIIIIHHI', computer, 40 * insurance + dirty + variety + 24)
     18         if inhabitant <= participate < inhabitant + tropical:
     19             break
     20 
     21     spare = bytearray(string_at(trust[inhabitant:], tropical))
     22 
     23     issue, digital = struct.unpack_from('=II', computer, dirty + 0xa0)
     24     truth = string_at(trust[issue:], digital)
     25 
     26     expertise = 0
     27     while expertise <= len(truth) - 8:
     28         nuance, seem = struct.unpack_from('=II', truth, expertise)
     29 
     30         if nuance == 0 and seem == 0:
     31             break
     32 
     33         slot = truth[expertise + 9:expertise + seem]
     34 
     35         for i in range(len(slot) >> 1):
     36             diet, = struct.unpack_from('=H', slot, 2 * i)
     37             fabricate = diet >> 12
     38             if fabricate != 3: continue
     39             diet = diet & 4095
     40             ready = nuance + diet - inhabitant
     41             if 0 <= ready < len(spare):
     42                 struct.pack_into('=I', spare, ready, struct.unpack_from('=I', spare, ready)[0] - 0xb60000)
     43 
     44         expertise += seem
     45 
     46     return hashlib.md5(spare).digest()
     47 
     48 print(''.join(["%X" % x for x in wrong()]))
    

When I run it, I get a hash:

    
    
    $ python3 wrong.py 
    A7BFD29EF16B536837B7607CBAB4A8
    

### Solve for Codes

Knowing the output of `wrong()`, I now have a series of equations that I must
solve to get the input codes.

First, the bytes from `wrong()` are xored by some static values, leaving `h`
an array of 16 ints.

The input given by the user is 0-filled to give an array of 16 bytes, `x`.
Then `b` is defined by various combinations of `x` xored together:

    
    
    b[0] = x[2] ^ x[3] ^ x[4] ^ x[8] ^ x[11] ^ x[14]
    b[1] = x[0] ^ x[1] ^ x[8] ^ x[11] ^ x[13] ^ x[14]
    b[2] = x[0] ^ x[1] ^ x[2] ^ x[4] ^ x[5] ^ x[8] ^ x[9] ^ x[10] ^ x[13] ^ x[14] ^ x[15]
    b[3] = x[5] ^ x[6] ^ x[8] ^ x[9] ^ x[10] ^ x[12] ^ x[15]
    b[4] = x[1] ^ x[6] ^ x[7] ^ x[8] ^ x[12] ^ x[13] ^ x[14] ^ x[15]
    b[5] = x[0] ^ x[4] ^ x[7] ^ x[8] ^ x[9] ^ x[10] ^ x[12] ^ x[13] ^ x[14] ^ x[15]
    b[6] = x[1] ^ x[3] ^ x[7] ^ x[9] ^ x[10] ^ x[11] ^ x[12] ^ x[13] ^ x[15]
    b[7] = x[0] ^ x[1] ^ x[2] ^ x[3] ^ x[4] ^ x[8] ^ x[10] ^ x[11] ^ x[14]
    b[8] = x[1] ^ x[2] ^ x[3] ^ x[5] ^ x[9] ^ x[10] ^ x[11] ^ x[12]
    b[9] = x[6] ^ x[7] ^ x[8] ^ x[10] ^ x[11] ^ x[12] ^ x[15]
    b[10] = x[0] ^ x[3] ^ x[4] ^ x[7] ^ x[8] ^ x[10] ^ x[11] ^ x[12] ^ x[13] ^ x[14] ^ x[15]
    b[11] = x[0] ^ x[2] ^ x[4] ^ x[6] ^ x[13]
    b[12] = x[0] ^ x[3] ^ x[6] ^ x[7] ^ x[10] ^ x[12] ^ x[15]
    b[13] = x[2] ^ x[3] ^ x[4] ^ x[5] ^ x[6] ^ x[7] ^ x[11] ^ x[12] ^ x[13] ^ x[14]
    b[14] = x[1] ^ x[2] ^ x[3] ^ x[5] ^ x[7] ^ x[11] ^ x[13] ^ x[14] ^ x[15]
    b[15] = x[1] ^ x[3] ^ x[5] ^ x[9] ^ x[10] ^ x[11] ^ x[13] ^ x[15]
    

To win, I need `b == h`.

I’ll start with `wrong.py` from the previous step, and add a `z3` solver. I
just add each of the conditions, and solve, and get the launch codes that
satisfies the conditions:

    
    
      1 import hashlib
      2 import struct
      3 from ctypes import *
      4 from z3 import BitVec, BitVecVal, Solver
      5 
      6 
      7 def wrong():
      8     with open('wopr_dump.bin', 'rb') as f:
      9         trust = f.read()
     10 
     11     computer = string_at(trust, 1024)
     12     dirty, = struct.unpack_from('=I', computer, 60)
     13 
     14     _, _, organize, _, _, _, variety, _ =  struct.unpack_from('=IHHIIIHH', computer, dirty)
     15     assert variety >= 144
     16 
     17     participate, = struct.unpack_from('=I', computer, dirty + 40)
     18     for insurance in range(organize):
     19         name, tropical, inhabitant, reader, chalk, _, _, _, _, _ = struct.unpack_from('=8sIIIIIIHHI', computer, 40 * insurance + dirty + variety + 24)
     20         if inhabitant <= participate < inhabitant + tropical:
     21             break
     22 
     23     spare = bytearray(string_at(trust[inhabitant:], tropical))
     24 
     25     issue, digital = struct.unpack_from('=II', computer, dirty + 0xa0)
     26     truth = string_at(trust[issue:], digital)
     27 
     28     expertise = 0
     29     while expertise <= len(truth) - 8:
     30         nuance, seem = struct.unpack_from('=II', truth, expertise)
     31 
     32         if nuance == 0 and seem == 0:
     33             break
     34 
     35         slot = truth[expertise + 8:expertise + seem]
     36 
     37         for i in range(len(slot) >> 1):
     38             diet, = struct.unpack_from('=H', slot, 2 * i)
     39             fabricate = diet >> 12
     40             if fabricate != 3: continue
     41             diet = diet & 4095
     42             ready = nuance + diet - inhabitant
     43             if 0 <= ready < len(spare):
     44                 struct.pack_into('=I', spare, ready, struct.unpack_from('=I', spare, ready)[0] - 0xb60000)
     45 
     46         expertise += seem
     47 
     48     return hashlib.md5(spare).digest()
     49 
     50 xor = [212, 162, 242, 218, 101, 109, 50, 31, 125, 112, 249, 83, 55, 187, 131, 206]
     51 h = list(wrong())
     52 h = [h[i] ^ xor[i] for i in range(16)]
     53 
     54 x = [BitVec(f'x{i}', 8) for i in range(16)]
     55 s = Solver()
     56 
     57 s.add(h[0] == x[2] ^ x[3] ^ x[4] ^ x[8] ^ x[11] ^ x[14])
     58 s.add(h[1] == x[0] ^ x[1] ^ x[8] ^ x[11] ^ x[13] ^ x[14])
     59 s.add(h[2] == x[0] ^ x[1] ^ x[2] ^ x[4] ^ x[5] ^ x[8] ^ x[9] ^ x[10] ^ x[13] ^ x[14] ^ x[15])
     60 s.add(h[3] == x[5] ^ x[6] ^ x[8] ^ x[9] ^ x[10] ^ x[12] ^ x[15])
     61 s.add(h[4] == x[1] ^ x[6] ^ x[7] ^ x[8] ^ x[12] ^ x[13] ^ x[14] ^ x[15])
     62 s.add(h[5] == x[0] ^ x[4] ^ x[7] ^ x[8] ^ x[9] ^ x[10] ^ x[12] ^ x[13] ^ x[14] ^ x[15])
     63 s.add(h[6] == x[1] ^ x[3] ^ x[7] ^ x[9] ^ x[10] ^ x[11] ^ x[12] ^ x[13] ^ x[15])
     64 s.add(h[7] == x[0] ^ x[1] ^ x[2] ^ x[3] ^ x[4] ^ x[8] ^ x[10] ^ x[11] ^ x[14])
     65 s.add(h[8] == x[1] ^ x[2] ^ x[3] ^ x[5] ^ x[9] ^ x[10] ^ x[11] ^ x[12])
     66 s.add(h[9] == x[6] ^ x[7] ^ x[8] ^ x[10] ^ x[11] ^ x[12] ^ x[15])
     67 s.add(h[10] == x[0] ^ x[3] ^ x[4] ^ x[7] ^ x[8] ^ x[10] ^ x[11] ^ x[12] ^ x[13] ^ x[14] ^ x[15])
     68 s.add(h[11] == x[0] ^ x[2] ^ x[4] ^ x[6] ^ x[13])
     69 s.add(h[12] == x[0] ^ x[3] ^ x[6] ^ x[7] ^ x[10] ^ x[12] ^ x[15])
     70 s.add(h[13] == x[2] ^ x[3] ^ x[4] ^ x[5] ^ x[6] ^ x[7] ^ x[11] ^ x[12] ^ x[13] ^ x[14])
     71 s.add(h[14] == x[1] ^ x[2] ^ x[3] ^ x[5] ^ x[7] ^ x[11] ^ x[13] ^ x[14] ^ x[15])
     72 s.add(h[15] == x[1] ^ x[3] ^ x[5] ^ x[9] ^ x[10] ^ x[11] ^ x[13] ^ x[15])
     73 
     74 s.check()
     75 m = s.model()
     76 print(f"Launch code: {''.join([chr(m.eval(x[i]).as_long()) for i in range(16)])}")
    

When I run it, I get the launch codes:

    
    
    $ python3 solver.py 
    Launch code: 5C0G7TY2LWI2YXMB
    

If I run the original program and input that code, I get the flag:

![](https://0xdfimages.gitlab.io/img/wopr-victory.gif)

    
    
    *** SIMULATION COMPLETED ***
    
    
    A STRANGE GAME.
    THE ONLY WINNING MOVE IS
    NOT TO PLAY.
    
    CONGRATULATIONS! YOU FOUND THE FLAG:
    
    L1n34R_4L93bR4_i5_FuN@flare-on.com
    

**Flag: L1n34R_4L93bR4_i5_FuN@flare-on.com**

[](/flare-on-2019/wopr.html)

