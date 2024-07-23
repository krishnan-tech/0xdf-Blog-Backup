# Flare-On 2020: garbage

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-garbage](/tags#flare-
on-garbage ) [upx](/tags#upx ) [pe](/tags#pe ) [cff-explorer](/tags#cff-
explorer ) [ghidra](/tags#ghidra ) [reverse-engineering](/tags#reverse-
engineering ) [resource-hacker](/tags#resource-hacker )  
  
Oct 26, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [2] garbage
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [[4] report.xls](/flare-on-2020/report)
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [[10] break](/flare-on-2020/break)

![garbage](https://0xdfimages.gitlab.io/img/flare2020-garbage-cover.png)

garbage was all about understanding the structure of an exe file, and how to
repair it when the last few hundred bytes were truncated. I’ll troubleshoot
the binary and eventually get it working to the point that I can unpack it, do
static analysis, and get the flag. I’ll also show how to fix the binary so
that it will just run and print the flag in a message box.

## Challenge

> One of our team members developed a Flare-On challenge but accidentally
> deleted it. We recovered it using extreme digital forensic techniques but it
> seems to be corrupted. We would fix it but we are too busy solving today’s
> most important information security threats affecting our global economy.
> You should be able to get it working again, reverse engineer it, and acquire
> the flag.

The file is an x86 executable, and it’s UPX packed:

    
    
    root@kali# file garbage.exe 
    garbage.exe: PE32 executable (console) Intel 80386, for MS Windows, UPX compressed
    

## Running It

As indicated, it doesn’t run:

    
    
    PS F:\02-garbage > .\garbage.exe
    Program 'garbage.exe' failed to run: The specified executable is not a valid application for this OS platform.At
    line:1 char:1
    + .\garbage.exe
    + ~~~~~~~~~~~~~.
    At line:1 char:1
    + .\garbage.exe
    + ~~~~~~~~~~~~~
        + CategoryInfo          : ResourceUnavailable: (:) [], ApplicationFailedException
        + FullyQualifiedErrorId : NativeCommandFailed
    

Or double clicking it:

![image-20200916085959786](https://0xdfimages.gitlab.io/img/image-20200922121900423.png)

It doesn’t unpack either:

    
    
    root@kali# upx -d garbage.exe -o garbage_unpacked.exe
                           Ultimate Packer for eXecutables
                              Copyright (C) 1996 - 2020
    UPX 3.96        Markus Oberhumer, Laszlo Molnar & John Reiser   Jan 23rd 2020
    
            File size         Ratio      Format      Name
       --------------------   ------   -----------   -----------
    upx: garbage.exe: OverlayException: invalid overlay size; file is possibly corrupt
    
    Unpacked 1 file: 0 ok, 1 error.
    

## Identify the Issue

There are a few ways to look at this and see what might be broken. First,
thinking about how it was a memory dump, it seems likely the the corruption is
that it cuts off at the end (or maybe goes too far at the end?). Looking at
the end of the file, it ends right in the middle of some XML:

    
    
    root@kali# xxd garbage.exe | tail -20
    00009df0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
    00009e00: 0000 0000 0000 0000 0000 0000 0000 0100  ................
    00009e10: 1800 0000 1800 0080 0000 0000 0000 0000  ................
    00009e20: 0000 0000 0000 0100 0100 0000 3000 0080  ............0...
    00009e30: 0000 0000 0000 0000 0000 0000 0000 0100  ................
    00009e40: 0904 0000 4800 0000 5c90 0100 7d01 0000  ....H...\...}...
    00009e50: 0000 0000 0000 0000 6050 0100 3c3f 786d  ........`P..<?xm
    00009e60: 6c20 7665 7273 696f 6e3d 2731 2e30 2720  l version='1.0' 
    00009e70: 656e 636f 6469 6e67 3d27 5554 462d 3827  encoding='UTF-8'
    00009e80: 2073 7461 6e64 616c 6f6e 653d 2779 6573   standalone='yes
    00009e90: 273f 3e0d 0a3c 6173 7365 6d62 6c79 2078  '?>..<assembly x
    00009ea0: 6d6c 6e73 3d27 7572 6e3a 7363 6865 6d61  mlns='urn:schema
    00009eb0: 732d 6d69 6372 6f73 6f66 742d 636f 6d3a  s-microsoft-com:
    00009ec0: 6173 6d2e 7631 2720 6d61 6e69 6665 7374  asm.v1' manifest
    00009ed0: 5665 7273 696f 6e3d 2731 2e30 273e 0d0a  Version='1.0'>..
    00009ee0: 2020 3c74 7275 7374 496e 666f 2078 6d6c    <trustInfo xml
    00009ef0: 6e73 3d22 7572 6e3a 7363 6865 6d61 732d  ns="urn:schemas-
    00009f00: 6d69 6372 6f73 6f66 742d 636f 6d3a 6173  microsoft-com:as
    00009f10: 6d2e 7633 223e 0d0a 2020 2020 3c73 6563  m.v3">..    <sec
    00009f20: 7572 6974                                urit
    

That’s the manifest that is a part of any [SxS Windows
binary](https://en.wikipedia.org/wiki/Side-by-side_assembly#Manifest_format).
I’ll need to fix that.

I can also use [CFF Explorer](https://ntcore.com/?page_id=388) to look at the
binary properties. For comparison, I’ll show `calc.exe`, a UPX-packed
`calc.exe`, and `garbage.exe`:

`calc.exe` | UPX `calc.exe` | `garbage.exe`  
---|---|---  
![](../img/image-20200922121917287.png) | ![](/img/image-20200922121943637.png) | ![](/img/image-20200922122025559.png)  
  
`garbage.exe` is missing the Import Directory, Exception Directory, and
Relocation Directory. Clicking on “Data Directories” for `garbage.exe`, the
Import Directory and Relocation Directory are both invalid:

![image-20200922122044441](https://0xdfimages.gitlab.io/img/image-20200922122044441.png)

An even more clear way is to look in the [UPX
source](https://github.com/upx/upx/blob/d7ba31cab8ce8d95d2c10e88d2ec787ac52005ef/src/packer.cpp#L577)
at that error message, and see it is coming up because `overlay > file_size`,
which is to say that headers say the file is bigger than it is! This is
visible in CFF Explorer as well:

![image-20201026153048341](https://0xdfimages.gitlab.io/img/image-20201026153048341.png)

There are 41472−40740 = 732 bytes missing from the file.

## Solve

At this point, there are two ways to continue:

  * Fix the binary to get it to un-upx and then do static analysis.
  * Fix the binary to get it to run and present the flag.

### Solve With RE

I originally had a tough time fixing the binary to the point where it would
work. But, I managed to fix it to the point that it would UPX unpack, and then
I could RE the result.

#### “Fix” the Binary

`calc.exe` is a SxS binary. I’ll make an assumption that the UPX packing would
give it a similar manifest and other stuff that follows. I’ll create a packed
version:

    
    
    root@kali# upx -o calc-upx.exe calc.exe
                           Ultimate Packer for eXecutables
                              Copyright (C) 1996 - 2020
    UPX 3.96        Markus Oberhumer, Laszlo Molnar & John Reiser   Jan 23rd 2020
    
            File size         Ratio      Format      Name
       --------------------   ------   -----------   -----------
         27648 ->     25088   90.74%    win64/pe     calc-upx.exe
    
    Packed 1 file.  
    

The last 13 lines seem to be what I need:

    
    
    root@kali# tail -13 calc-packed.exe | less
        <security>
            <requestedPrivileges>
                <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
            </requestedPrivileges>
        </security>
    </trustInfo>
    <application xmlns="urn:schemas-microsoft-com:asm.v3">
        <windowsSettings>
            <dpiAware  xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
        </windowsSettings>
    </application>
    </assembly>
    ^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@H(^A^@<C0>'^A^@^@^@^@^@^@^@^@^@^@^@^@^@U(^A^@<D0>'^A^@^@^@^@^@^@^@^@^@^@^@^@^@~(^A^@<E0>'
    ^A^@^@^@^@^@^@^@^@^@^@^@^@^@<A8>(^A^@<F0>'^A^@^@^@^@^@^@^@^@^@^@^@^@^@<C9>(^A^@^@(^A^@^@^@^@^@^@^@^@^@^@^@^@^@<D6>(^A^@((^A^@^@^@^@^@^@^@^@^@^@^@^@^@<E1>(^A^@8(^A^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@<EE>(^A^@^@^@^@^@^@^@^@^@^@^@^@^@
    <FE>(^A^@^@^@^@^@^@^@^@^@^@^@^@^@^P)^A^@^@^@^@^@^@^@^@^@^@^@^@^@")^A^@^@^@^@^@^@^@^@^@^@^@^@^@H)^A^@^@^@^@^@*)^A^@^@^@^@^@8)^A^@^@^@^@^@V)^A^@^@^@^@^@^@^@^@^@^@^@^@^@f)^A^@^@^@^@^@^@^@^@^@^@^@^@^@l)^A^@^@^@^@^@^@^@^@^@^@^@^@^@ADVAPI32.dll^@api-ms-win-core-libraryloader-l1-2-0.dll^@api-ms-win-core-processthreads-l1-1-0.dll^@api-ms-win-core-synch-l1-2-0.dll^@KERNEL32.DLL^@msvcrt.dll^@SHELL32.dll^@^@^@^@EventRegister^@^@^@GetModuleHandleW^@^@GetStartupInfoW^@^@^@Sleep^@^@^@ExitProcess^@^@^@GetProcAddress^@^@LoadLibraryA^@^@VirtualProtect^@^@exit^@^@ShellExecuteW^@^@<D0>^@^@^P^@^@^@<90><A1><A8>
    <A1><B0><A1><B8><A1>^@<D0>^@^@^P^@^@^@<90><A1><A8><A1><B0><A1><B8><A1>^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@
    (END)
    

I’ll make a copy of `garbage.exe` and append the manifest etc:

    
    
    root@kali# cp garbage{,-mod}.exe 
    root@kali# tail -13 hello-packed.exe >> garbage-mod.exe
    

Next I’ll need to go in in a hex editor (or `vim`) and fix what was the end of
the original `garbage.exe` by removing the extra `<securit` and following
spaces:

![image-20200922122108844](https://0xdfimages.gitlab.io/img/image-20200922122108844.png)

That is enough to unpack the file:

    
    
    root@kali# upx -d garbage-mod.exe -o garbage-mod-unpacked.exe
                           Ultimate Packer for eXecutables
                              Copyright (C) 1996 - 2020
    UPX 3.96        Markus Oberhumer, Laszlo Molnar & John Reiser   Jan 23rd 2020
    
            File size         Ratio      Format      Name
       --------------------   ------   -----------   -----------
         79771 <-     41883   52.50%    win32/pe     garbage-mod-unpacked.exe
    
    Unpacked 1 file.
    

#### RE

In Ghidra, I did a search for strings, and these two jumped out:

![image-20200922122121752](https://0xdfimages.gitlab.io/img/image-20200922122121752.png)

(Interesting little easter egg right below them, “covid19-sucks”, doesn’t seem
to be referenced by the binary.)

Looking for references to them led me to `FUN_0040106b`, which has the two
static strings, and two stack-strings. It copies the two static strings into
`local_12c` and `local_c4`:

    
    
      iVar1 = 0x19;
      puVar2 = (undefined4 *) "nPTnaGLkIqdcQwvieFQKGcTGOTbfMjDNmvibfBDdFBhoPaBbtfQuuGWYomtqTFqvBSKdUMmciqKSGZaosWCSoZlcIlyQpOwkcAgw ";
      puVar3 = local_12c;
      while (iVar1 != 0) {
        iVar1 = iVar1 + -1;
        *puVar3 = *puVar2;
        puVar2 = puVar2 + 1;
        puVar3 = puVar3 + 1;
      }
      iVar1 = 0x19
      *(undefined2 *)puVar3 = *(undefined2 *)puVar2;;
      puVar2 = (undefined4 *) "KglPFOsQDxBPXmclOpmsdLDEPMRWbMDzwhDGOyqAkVMRvnBeIkpZIhFznwVylfjrkqprBPAdPuaiVoVugQAlyOQQtxBNsTdPZgDH ";
      puVar3 = local_c4;
      while (iVar1 != 0) {
        iVar1 = iVar1 + -1;
        *puVar3 = *puVar2;
        puVar2 = puVar2 + 1;
        puVar3 = puVar3 + 1;
      }
    

The two stack strings are defined throughout the function:

    
    
      local_5c = 0x2c332323;  /* Stack string 1 - local_5c */
      local_58 = 0x49643f0e;
      local_54 = 0x40a1e0a;
      local_50 = 0x1a021623;
      local_4c = 0x24086644;
      local_48 = 0x2c741132;
      local_44 = 0xf422d2a;
      local_40 = 0xd64503e;
      local_3c = 0x171b045d;
      local_38 = 0x5033616;
      local_34 = 0x8092034;
      local_30 = 0xe242163;
      local_2c = 0x58341415;
      local_28 = 0x3a79291a;
      local_24 = 0x58560000;
    
      local_1c = 0x3b020e38; /* Stack string 1 - local_1c */
      local_18 = 0x341b3b19;
      local_14 = 0x3e230c1b;
      local_10 = 0x42110833;
      local_c = 0x731e1239;
    

There’s some other stuff going on with a file, but I zeroed in on two function
calls:

    
    
    FUN_00401000(local_13c,(int)&local_1c,0x14,(int)local_c4);
    FUN_00401000(local_13c,(int)&local_5c,0x3d,(int)local_12c);
    

`local_c4` and `local_12c` hold the two long strings. `local_1c` and
`local_5c` both hold stack strings set throughout the function.

Looking at `FUN_00401000`, it looks a bit more complicated than it is because
of the
[thiscall](https://en.wikipedia.org/wiki/X86_calling_conventions#thiscall)
calling convention:

    
    
    int * __thiscall FUN_00401000(void *this,int param_1,int param_2,int param_3)
    
    {
      uint uVar1;
      
      uVar1 = 0;
      *(int *)this = param_1;
      *(int *)((int)this + 4) = param_2;
      *(int *)((int)this + 8) = param_3;
      *(undefined4 *)((int)this + 0xc) = 0x66;
      if (param_2 != 0) {
        do {
          *(byte *)(*(int *)this + uVar1) =
               *(byte *)(*(int *)this + uVar1) ^
               *(byte *)(uVar1 % *(uint *)((int)this + 0xc) + *(int *)((int)this + 8));
          uVar1 = uVar1 + 1;
        } while (uVar1 < *(uint *)((int)this + 4));
      }
      return (int *)this;
    }
    

This simplifies to a loop for `i` from 0 to less than `param2`:

    
    
    param1[i] = param1[i] ^ param3[i % 0x66]
    

This function is a simple xor.

I can dump the flag in a Python Repl using these static values:

    
    
    root@kali# python3
    Python 3.8.5 (default, Aug  2 2020, 15:09:07) 
    [GCC 10.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import struct
    >>> stack1_ints = [0x2c332323, 0x49643f0e, 0x40a1e0a, 0x1a021623, 0x24086644, 0x2c741132, 0xf422d2a, 0xd64503e, 0x171b045d, 0x5033616, 0x8092034, 0xe242163, 0x58341415, 0x3a79291a, 0x58560000 ] 
    >>> stack1 = b''.join([struct.pack('<L', x) for x in stack1_ints])
    >>> str1 = b'nPTnaGLkIqdcQwvieFQKGcTGOTbfMjDNmvibfBDdFBhoPaBbtfQuuGWYomtqTFqvBSKdUMmciqKSGZaosWCSoZlcIlyQpOwkcAgw'
    >>> ''.join([chr(x^y) for x,y in zip(stack1, str1)])
    'MsgBox("Congrats! Your key is: C0rruptGarbag3@flare-on.com")'
    >>> 
    >>> stack2_ints = [ 0x3b020e38, 0x341b3b19, 0x3e230c1b, 0x42110833, 0x731e1239 ]
    >>> stack2 = b''.join([struct.pack('<L', x) for x in stack2_ints])
    >>> str2 = b'KglPFOsQDxBPXmclOpmsdLDEPMRWbMDzwhDGOyqAkVMRvnBeIkpZIhFznwVylfjrkqprBPAdPuaiVoVugQAlyOQQtxBNsTdPZgDH'
    >>> ''.join([chr(x^y) for x,y in zip(stack2, str2)])
    'sink_the_tanker.vbs\x00'
    

I suspect the code is writing the file `sink_the_tanker.vbs` with the code
`'MsgBox("Congrats! Your key is: C0rruptGarbag3@flare-on.com")'`, and then
running it.

**Flag: C0rruptGarbag3@flare-on.com**

### Fixing Binary

In trying to learn more post solving, some people gave me some hints about how
this can be fixed. First, I’ll just add 732 nulls to the end of the file (I’ll
start with a new copy named `garbage-mod.exe`):

    
    
    root@kali# python3 -c "print('\x00' * 732, end='')" >> garbage-mod.exe 
    

I can now unpack it without error:

    
    
    root@kali# upx -d garbage-mod.exe -o garbage-mod-unpacked.exe
                           Ultimate Packer for eXecutables
                              Copyright (C) 1996 - 2020
    UPX 3.96        Markus Oberhumer, Laszlo Molnar & John Reiser   Jan 23rd 2020
    
            File size         Ratio      Format      Name
       --------------------   ------   -----------   -----------
         79360 <-     41472   52.26%    win32/pe     garbage-mod-unpacked.exe
    
    Unpacked 1 file.
    

Now running it doesn’t give the same error, but a new one:

![image-20201026162246517](https://0xdfimages.gitlab.io/img/image-20201026162246517.png)

That makes sense, since whatever was trancated I replaced with nulls. I can
see it in Resource Hacker:

![image-20201026162319288](https://0xdfimages.gitlab.io/img/image-20201026162319288.png)

I’ll right click on the resource and just delete it:

![image-20201026162016471](https://0xdfimages.gitlab.io/img/image-20201026162016471.png)

Now I get a different error:

![image-20201026162346723](https://0xdfimages.gitlab.io/img/image-20201026162346723.png)

Actually, this same error pops twice.

If I check out the Import Directory for the latest file in CFF Explorer, I can
see the module names are missing:

![image-20201026162612888](https://0xdfimages.gitlab.io/img/image-20201026162612888.png)

Clicking on either of them shows the functions from those dlls:

![image-20201026162651294](https://0xdfimages.gitlab.io/img/image-20201026162651294.png)

Seeing those function names, I can figure out that the first one is
`kernel32.dll` and the second is `shell32.dll`. I’ll update them:

![image-20201026163037314](https://0xdfimages.gitlab.io/img/image-20201026163037314.png)

Now I have a working exe that will print the flag:

![image-20201026163000635](https://0xdfimages.gitlab.io/img/image-20201026163000635.png)

[](/flare-on-2020/garbage)

